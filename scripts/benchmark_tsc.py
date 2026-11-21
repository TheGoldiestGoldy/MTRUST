#!/usr/bin/env python3
"""Run the exact released MTR embedded Java core on synthetic scratch data only.

Does not launch Fabric/Minecraft, read world data, or connect to a server.
Requires JDK 21 (javac + java). Never pass any production world directory.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import statistics
import subprocess
import tempfile
import time

PROJECT = Path(__file__).resolve().parent.parent
ARTIFACT_SHA256 = "5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94"
FIELDS = "timestamp_utc,git_commit,artifact_sha256,scenario,role,metric,unit,samples,median,p95,p99,tool,warmup_seconds,notes".split(",")
SCENARIOS = {"S0_empty": 0, "T1_rail_topology_64": 64, "T2_rail_topology_512": 512}


def quantiles(values: list[float]) -> tuple[str, str, str]:
    if not values:
        return "", "", ""
    ordered = sorted(values)
    median = statistics.median(ordered)
    if len(ordered) < 2:
        return f"{median:.6f}", "", ""
    def nearest_rank(fraction: float) -> float:
        import math
        return ordered[math.ceil(len(ordered) * fraction) - 1]
    return f"{median:.6f}", f"{nearest_rank(.95):.6f}", f"{nearest_rank(.99):.6f}"


def proc_kib(pid: int) -> tuple[int | None, int | None]:
    """Read only aggregate process memory, never process argv/maps or file paths."""
    try:
        text = Path(f"/proc/{pid}/smaps_rollup").read_text()
        values = {}
        for line in text.splitlines():
            if line.startswith(("Rss:", "Pss:")):
                key, val, *_ = line.split()
                values[key.rstrip(":")] = int(val)
        return values.get("Rss"), values.get("Pss")
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None, None


def verify_artifact(path: Path) -> None:
    if not path.is_file() or path.suffix != ".jar":
        raise ValueError("An existing MTR JAR is required (read-only)")
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    if sha.hexdigest() != ARTIFACT_SHA256:
        raise ValueError("Refusing to benchmark a JAR with a different SHA-256")


def run_core(java: Path, build: Path, jar: Path, root: Path, rails: int, warmup: int, ticks: int) -> dict:
    # The Java harness refuses an existing scratch root. No command receives a world path.
    command = [
        str(java), "-Xms128m", "-Xmx512m", "-XX:ActiveProcessorCount=2",
        "-cp", os.pathsep.join((str(build), str(jar))),
        "CoreSyntheticBenchmark", str(root), str(rails), str(warmup), str(ticks),
    ]
    process = subprocess.Popen(command, cwd=PROJECT, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, bufsize=1)
    rss, pss = [], []
    received: str | None = None
    warmed_at: float | None = None
    started = time.monotonic()
    lines = []
    try:
        while True:
            if time.monotonic() - started > 90:
                raise TimeoutError("Synthetic subprocess exceeded 90 seconds")
            readable, _, _ = select.select([process.stdout], [], [], 0.015)
            if readable:
                line = process.stdout.readline().strip()
                if line:
                    lines.append(line)
                    if line == "WARMED":
                        warmed_at = time.monotonic()
                    if line.startswith("RESULT|"):
                        received = line
            if warmed_at is not None and process.poll() is None:
                r, p = proc_kib(process.pid)
                if r is not None:
                    rss.append(float(r * 1024))
                if p is not None:
                    pss.append(float(p * 1024))
            if process.poll() is not None:
                break
        _, stderr = process.communicate(timeout=2)
        if process.returncode != 0 or received is None:
            raise RuntimeError("Embedded core failed: " + (stderr[-1800:] if stderr else str(lines[-3:])))
    finally:
        if process.poll() is None:
            process.kill()  # only the subprocess launched by this harness
            process.wait(timeout=3)
    values = received.split("|")
    if len(values) != 11 or int(values[1]) != rails or int(values[10]) != rails:
        raise RuntimeError("Invalid result or synthetic save/load count")
    samples = [float(val) for val in values[3].split(",")]
    if len(samples) != ticks or not all(0 <= val < 10000 for val in samples):
        raise RuntimeError("Invalid tick sample array")
    return {
        "rail_count": rails,
        "active_trains": 0,
        "players": 0,
        "sample_tsc_tick_ms": samples,
        "sample_rss_bytes": rss,
        "sample_pss_bytes": pss,
        "heap_used_bytes": int(values[4]),
        "heap_committed_bytes": int(values[5]),
        "direct_buffer_bytes": int(values[6]),
        "gc_collections": int(values[7]),
        "gc_collection_time_ms": int(values[8]),
        "allocated_bytes_per_tsc_tick": int(values[9]) / ticks if int(values[9]) >= 0 else None,
        "save_reload_rails": int(values[10]),
        "warmup_wall_seconds": round((warmed_at or started) - started, 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jar", type=Path, required=True, help="Read-only released client-side JAR")
    parser.add_argument("--jdk", type=Path, default=Path(os.environ.get("JAVA_HOME", "/usr/lib/jvm/default-java")))
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=12, help="Simulation ticks per run")
    parser.add_argument("--samples", type=int, default=40, help="Measured simulation ticks per run")
    parser.add_argument("--out", type=Path, default=PROJECT / "metrics/baseline.csv")
    parser.add_argument("--raw", type=Path, default=PROJECT / "metrics/stage1-raw.json")
    args = parser.parse_args()
    if not 1 <= args.runs <= 8 or not 1 <= args.warmup <= 100 or not 5 <= args.samples <= 500:
        parser.error("Run/warmup/sample count outside safety limits")
    verify_artifact(args.jar)
    java, javac = args.jdk / "bin/java", args.jdk / "bin/javac"
    if not java.is_file() or not javac.is_file():
        parser.error("JDK 21 java and javac must both exist under --jdk")
    java_version = subprocess.run([str(javac), "-version"], text=True, capture_output=True, check=True).stdout
    if "21." not in java_version:
        parser.error("JDK 21 required")
    cache = PROJECT / ".audit-cache"
    cache.mkdir(exist_ok=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT, text=True).strip()
    now = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, str | int]] = []
    raw = {"artifact_sha256": ARTIFACT_SHA256, "harness_commit": commit,
           "timestamp_utc": now, "jdk": java_version.strip(),
           "setting": "embedded TSC only, no Minecraft, no active trains, no players",
           "runs": []}
    with tempfile.TemporaryDirectory(prefix="goldrail-synthetic-", dir=cache) as temp:
        root = Path(temp)
        build = root / "classes"
        build.mkdir()
        subprocess.run([str(javac), "--release", "21", "-proc:none", "-cp", str(args.jar),
                        "-d", str(build), str(PROJECT / "scripts/CoreSyntheticBenchmark.java")], check=True)
        for scenario, rail_count in SCENARIOS.items():
            for repeat in range(args.runs):
                report = run_core(java, build, args.jar, root / f"{scenario}-{repeat}-unique",
                                  rail_count, args.warmup, args.samples)
                report["scenario"] = scenario
                report["repeat"] = repeat + 1
                raw["runs"].append(report)
                print(f"{scenario} run {repeat + 1}: tick median={statistics.median(report['sample_tsc_tick_ms']):.4f}ms; "
                      f"rails={report['rail_count']} saved+reloaded={report['save_reload_rails']}")
                metrics = (
                    ("tsc_tick_invocation_ms", "ms", report["sample_tsc_tick_ms"], "java nanoTime; 1 simulated second"),
                    ("rss_bytes", "bytes", report["sample_rss_bytes"], "Linux /proc/smaps_rollup; after warmup"),
                    ("pss_bytes", "bytes", report["sample_pss_bytes"], "Linux /proc/smaps_rollup; after warmup"),
                    ("java_heap_used_bytes", "bytes", [report["heap_used_bytes"]], "JMX snapshot after tick loop"),
                    ("java_heap_committed_bytes", "bytes", [report["heap_committed_bytes"]], "JMX snapshot"),
                    ("direct_buffer_used_bytes", "bytes", [report["direct_buffer_bytes"]], "BufferPoolMXBean snapshot"),
                    ("gc_collections", "count", [report["gc_collections"]], "MXBean count delta"),
                    ("gc_collection_time_ms", "ms", [report["gc_collection_time_ms"]], "MXBean time delta; not pause percentile"),
                    ("allocated_bytes_per_tsc_tick", "bytes/tick", [report["allocated_bytes_per_tsc_tick"]] if report["allocated_bytes_per_tsc_tick"] is not None else [], "ThreadMXBean main thread only"),
                )
                for metric, unit, numbers, note in metrics:
                    median, p95, p99 = quantiles(numbers)
                    rows.append({
                        "timestamp_utc": now, "git_commit": commit, "artifact_sha256": ARTIFACT_SHA256,
                        "scenario": f"{scenario}/run{repeat+1}", "role": "server_core_standalone",
                        "metric": metric, "unit": unit, "samples": len(numbers), "median": median,
                        "p95": p95, "p99": p99, "tool": "GoldRail synthetic Java21 + procfs",
                        "warmup_seconds": report["warmup_wall_seconds"],
                        "notes": f"{note}; rails={rail_count}; active_trains=0; players=0; {args.warmup} warmup ticks",
                    })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    args.raw.parent.mkdir(parents=True, exist_ok=True)
    args.raw.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {len(rows)} metric rows, {len(raw['runs'])} raw runs")


if __name__ == "__main__":
    main()
