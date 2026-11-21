#!/usr/bin/env python3
"""Phase-tagged, deterministic *internal TSC* Java21 microbenchmark V2.

Not Fabric server MSPT, train movement, nor a basis for server RAM attribution.
Historical scripts/benchmark_tsc.py and metrics/stage1-raw.json are immutable evidence.
Only accepts the exact official release hash, uses new scratch paths, never a world.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
import os
import re
from pathlib import Path
import select
import statistics
import subprocess
import tempfile
import time

from benchmark_tsc import ARTIFACT_SHA256, PROJECT, SCENARIOS, proc_kib, quantiles, verify_artifact

PHASES = ("startup", "warmup", "ticks", "save", "reload", "idle", "done")
FIELDS = ("timestamp_utc git_commit artifact_sha256 scenario role metric unit samples "
          "median p95 p99 tool warmup_seconds notes phase").split()
# Keep 100ms away from a phase boundary; procfs read and stdout delivery are not atomic.
TRANSITION_GUARD_NS = 100_000_000


def validate_clock(events: list[dict]) -> None:
    """Ensure Linux JVM nanoTime/Python monotonic_ns epochs align before labeling samples."""
    if [e["phase"] for e in events] != list(PHASES):
        raise ValueError("Missing, duplicate, or out-of-order JVM phase events")
    times = [e["java_monotonic_ns"] for e in events]
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("Non-increasing phase monotonic timestamps")
    for event in events:
        lag = event["received_monotonic_ns"] - event["java_monotonic_ns"]
        if not 0 <= lag < 500_000_000:
            raise ValueError("Cannot align JVM and Python monotonic clocks within 500ms")


def classify_samples(samples: list[dict], events: list[dict],
                     guard_ns: int = TRANSITION_GUARD_NS) -> list[dict]:
    """Use JVM-origin transition instants, not the buffered time a line was received."""
    validate_clock(events)
    for item in samples:
        t = item["monotonic_ns"]
        phase = "unclassified"
        for i, event in enumerate(events[:-1]):
            left = event["java_monotonic_ns"]
            right = events[i + 1]["java_monotonic_ns"]
            if left <= t < right:
                phase = event["phase"] if (t - left >= guard_ns and
                        right - t >= guard_ns) else "transition_excluded"
                break
        if t >= events[-1]["java_monotonic_ns"]:
            phase = "done"
        item["phase"] = phase
    return samples


def safe_result_fields(value: str, rails: int, samples: int, warmup_seconds: int) -> dict:
    v = value.split("|")
    if len(v) != 16 or v[0] != "RESULT":
        raise ValueError("Malformed RESULT protocol")
    ints = [int(x) for x in v[1:3]]
    if ints != [rails, samples] or int(v[10]) != rails:
        raise ValueError("Scenario or count-only reload failed")
    durations = [float(x) for x in v[3].split(",")]
    if len(durations) != samples or any(not math.isfinite(x) or x <= 0 or x >= 10000 for x in durations):
        raise ValueError("Invalid measured tick invocation")
    warmup_calls, warmup_ns, measured_ns = int(v[11]), int(v[12]), int(v[13])
    clock_before, clock_after = int(v[14]), int(v[15])
    if (warmup_calls <= 0 or warmup_ns < warmup_seconds * 1_000_000_000
        or measured_ns < 0 or clock_after - clock_before != samples * 1000):
        raise ValueError("Warmup or deterministic internal clock semantics invalid")
    return {
        "rail_count": rails, "save_reload_rails": int(v[10]),
        "sample_private_tsc_tick_ms": durations,
        "heap_used_bytes": int(v[4]), "heap_committed_bytes": int(v[5]),
        "direct_buffer_bytes": int(v[6]), "gc_collections": int(v[7]),
        "gc_collection_time_ms": int(v[8]),
        "main_thread_allocated_bytes": int(v[9]),
        "warmup_calls": warmup_calls, "warmup_wall_seconds": round(warmup_ns / 1e9, 6),
        "measure_wall_seconds": round(measured_ns / 1e9, 6),
        "virtual_clock_before_ms": clock_before, "virtual_clock_after_ms": clock_after,
        "internal_tick_step_ms": 1000, "active_trains": 0, "players": 0,
    }


def summarize_memory(samples: list[dict]) -> dict:
    output = {}
    for phase in ("startup", "warmup", "ticks", "save", "reload", "idle",
                  "transition_excluded", "unclassified"):
        selected = [s for s in samples if s["phase"] == phase]
        output[phase] = {
            "count": len(selected),
            "rss_bytes": [s["rss_bytes"] for s in selected if s["rss_bytes"] is not None],
            "pss_bytes": [s["pss_bytes"] for s in selected if s["pss_bytes"] is not None],
        }
    output["sampled_process_peak"] = {
        "rss_bytes": max((s["rss_bytes"] for s in samples if s["rss_bytes"] is not None), default=None),
        "pss_bytes": max((s["pss_bytes"] for s in samples if s["pss_bytes"] is not None), default=None),
        "note": "MAX observed at procfs sampling cadence across ALL phases; NOT actual RSS high-water mark",
    }
    return output


def parse_nmt_summary(output: str) -> dict:
    """NMT reserved/committed KB, not allocation rate or an MTR attribution."""
    totals = re.search(r"Total: reserved=(\d+)KB, committed=(\d+)KB", output)
    if not totals:
        raise ValueError("NMT output has no native memory Total")
    categories = {}
    for name, reserved, committed in re.findall(
        r"^\s*-\s+(.+?)\s+\(reserved=(\d+)KB, committed=(\d+)KB\)",
        output, re.MULTILINE,
    ):
        categories[name.strip()] = {"reserved_kb": int(reserved),
                                    "committed_kb": int(committed)}
    return {"reserved_kb": int(totals[1]), "committed_kb": int(totals[2]),
            "categories": categories, "scope": "whole JVM; not isolated TSC native memory"}


def run_core(java: Path, build: Path, jar: Path, root: Path,
             rails: int, warmup_seconds: int, sample_count: int, pacing_ms: int) -> dict:
    cmd = [
        str(java), "-Xms128m", "-Xmx512m", "-XX:ActiveProcessorCount=2",
        "-XX:NativeMemoryTracking=summary",
        "-cp", os.pathsep.join((str(build), str(jar))),
        "CoreEvidenceBenchmark", str(root), str(rails), str(warmup_seconds),
        str(sample_count), str(pacing_ms),
    ]
    process = subprocess.Popen(cmd, cwd=PROJECT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               bufsize=0)
    events: list[dict] = []
    samples: list[dict] = []
    result = None
    nmt = None
    nmt_attempted = False
    stderr = b""
    pending = b""
    done_reading = False
    start = time.monotonic()
    timeout = warmup_seconds + sample_count * pacing_ms / 1000 + 50
    try:
        while True:
            if time.monotonic() - start > timeout:
                raise TimeoutError("Evidence subprocess exceeded bounded runtime")
            readable, _, _ = select.select([process.stdout], [], [], 0.025)
            if readable:
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    done_reading = True
                else:
                    pending += chunk
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        text = line.decode("utf-8", errors="replace").strip()
                        receipt = time.monotonic_ns()
                        if text.startswith("PHASE|"):
                            tokens = text.split("|")
                            if len(tokens) != 3 or tokens[1] not in PHASES:
                                raise ValueError("Unknown phase protocol")
                            events.append({
                                "phase": tokens[1], "java_monotonic_ns": int(tokens[2]),
                                "received_monotonic_ns": receipt,
                            })
                        elif text.startswith("RESULT|"):
                            if result is not None:
                                raise ValueError("Duplicate result")
                            result = text
            if (not nmt_attempted and process.poll() is None and events
                and events[-1]["phase"] == "ticks"
                and time.monotonic_ns() - events[-1]["java_monotonic_ns"] >= 500_000_000):
                nmt_attempted = True
                jcmd = java.parent / "jcmd"
                if jcmd.is_file():
                    try:
                        snapshot = subprocess.run(
                            [str(jcmd), str(process.pid), "VM.native_memory",
                             "summary", "scale=KB"],
                            text=True, capture_output=True, timeout=8,
                        )
                        if snapshot.returncode == 0:
                            nmt = parse_nmt_summary(snapshot.stdout)
                        else:
                            nmt = {"status": "NOT MEASURED", "reason": "jcmd attach failed"}
                    except (subprocess.TimeoutExpired, ValueError):
                        nmt = {"status": "NOT MEASURED", "reason": "NMT parse or attach timeout"}
                else:
                    nmt = {"status": "NOT MEASURED", "reason": "JDK21 jcmd missing"}
            if process.poll() is None:
                before = time.monotonic_ns()
                rss, pss = proc_kib(process.pid)
                after = time.monotonic_ns()
                if rss is not None and pss is not None:
                    samples.append({
                        "monotonic_ns": (before + after) // 2,
                        "proc_read_duration_ns": after - before,
                        "rss_bytes": rss * 1024, "pss_bytes": pss * 1024,
                    })
            if done_reading and process.poll() is not None:
                break
        _, stderr = process.communicate(timeout=3)
        if process.returncode != 0 or result is None:
            raise RuntimeError("Core evidence process failed (stderr tail): " +
                               stderr.decode("utf-8", errors="replace")[-1500:])
        if pending.strip():
            raise ValueError("Unterminated output protocol")
        classify_samples(samples, events)
        report = safe_result_fields(result, rails, sample_count, warmup_seconds)
        report["phase_events"] = events
        report["nmt_tick_phase_snapshot"] = nmt or {"status": "NOT MEASURED", "reason": "No tick-phase attach"}
        report["memory_samples"] = samples
        report["memory_by_phase"] = summarize_memory(samples)
        report["phase_seconds"] = {
            event["phase"]: round((events[i + 1]["java_monotonic_ns"] -
                     event["java_monotonic_ns"]) / 1e9, 6)
            for i, event in enumerate(events[:-1])
        }
        return report
    finally:
        if process.poll() is None:
            process.kill()  # strictly our own new child
            process.communicate(timeout=5)


def run(args: argparse.Namespace) -> None:
    if not 1 <= args.runs <= 8 or not 1 <= args.warmup_seconds <= 90:
        raise ValueError("Runs or warmup seconds out of bounds")
    if not 20 <= args.samples <= 1000 or not 20 <= args.pacing_ms <= 250:
        raise ValueError("Sample count or pacing out of bounds")
    if args.out.resolve() == args.raw.resolve():
        raise ValueError("CSV and raw output must differ")
    for target in (args.out, args.raw):
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite existing baseline: {target}")
    verify_artifact(args.jar)
    java, javac = args.jdk / "bin/java", args.jdk / "bin/javac"
    check = subprocess.run([str(javac), "-version"], capture_output=True, text=True, check=True)
    version = (check.stdout + check.stderr).strip()
    if not version.startswith("javac 21."):
        raise ValueError("JDK21 required")
    git = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT, text=True).strip()
    now = datetime.now(timezone.utc).isoformat()
    raw = {
        "schema": "goldrail-tsc-internal-tick-v2",
        "published_release_sha256": ARTIFACT_SHA256,
        "harness_git_commit": git,
        "timestamp_utc": now, "jdk": version,
        "controls": {
            "warmup_seconds": args.warmup_seconds, "measured_calls": args.samples,
            "pacing_ms": args.pacing_ms, "virtual_tick_ms": 1000,
            "method": "released Simulator private tick(long) invoked reflectively",
            "clock": "fixed initial virtual clock; monotonic +1000ms per call; no wall-clock catch-up",
            "scope": "standalone core synthetic rails, 0 trains/players; NOT Fabric MSPT",
            "memory": "Linux procfs smaps_rollup 25ms polling; phase guard 100ms",
            "java": "-Xms128m -Xmx512m -XX:ActiveProcessorCount=2 -XX:NativeMemoryTracking=summary",
            "nmt_caveat": "jcmd once during measured tick phase may perturb latency; total JVM committed only",
        },
        "runs": [],
    }
    rows = []
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.raw.parent.mkdir(parents=True, exist_ok=True)
    cache = PROJECT / ".audit-cache"
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="goldrail-evidence-v2-", dir=cache) as temp:
        root = Path(temp)
        build = root / "classes"
        build.mkdir()
        subprocess.run([str(javac), "--release", "21", "-proc:none",
                        "-cp", str(args.jar), "-d", str(build),
                        str(PROJECT / "scripts/CoreEvidenceBenchmark.java")], check=True)
        for scenario, rails in SCENARIOS.items():
            for repeat in range(1, args.runs + 1):
                report = run_core(java, build, args.jar, root / f"{scenario}-{repeat}-unique",
                                  rails, args.warmup_seconds, args.samples, args.pacing_ms)
                report["scenario"], report["repeat"] = scenario, repeat
                raw["runs"].append(report)
                ticks = report["memory_by_phase"]["ticks"]
                print(f"{scenario} / {repeat}: {len(report['sample_private_tsc_tick_ms'])} internal calls "
                      f"median {statistics.median(report['sample_private_tsc_tick_ms']):.4f}ms; "
                      f"tick-phase RSS/PSS n={len(ticks['rss_bytes'])}; "
                      f"warmup {report['warmup_wall_seconds']:.2f}s; save/reload count {report['save_reload_rails']}",
                      flush=True)
                metrics = [
                    ("private_tsc_internal_tick_ms", "ms", report["sample_private_tsc_tick_ms"],
                     "ticks", "reflective released private tick(long), deterministic 1000ms internal step"),
                    ("rss_tick_phase_bytes", "bytes", ticks["rss_bytes"],
                     "ticks", "procfs RSS, phase-guarded 100ms; paced synthetic ticks + sleeps"),
                    ("pss_tick_phase_bytes", "bytes", ticks["pss_bytes"],
                     "ticks", "procfs PSS, phase-guarded 100ms; paced synthetic ticks + sleeps"),
                    ("rss_process_peak_sampled_bytes", "bytes",
                     [report["memory_by_phase"]["sampled_process_peak"]["rss_bytes"]],
                     "all", "max observed across phases, sampled not OS high-water mark"),
                    ("pss_process_peak_sampled_bytes", "bytes",
                     [report["memory_by_phase"]["sampled_process_peak"]["pss_bytes"]],
                     "all", "max observed across phases, sampled not OS high-water mark"),
                    ("nmt_total_committed_bytes", "bytes",
                     [report["nmt_tick_phase_snapshot"]["committed_kb"] * 1024]
                     if "committed_kb" in report["nmt_tick_phase_snapshot"] else [],
                     "ticks", "single JVM NMT committed snapshot; includes Java heap, no TSC attribution"),
                    ("heap_used_bytes", "bytes", [report["heap_used_bytes"]], "post_ticks",
                     "single MemoryMXBean snapshot; not a percentile"),
                    ("heap_committed_bytes", "bytes", [report["heap_committed_bytes"]],
                     "post_ticks", "single MemoryMXBean snapshot"),
                    ("gc_collections", "count", [report["gc_collections"]],
                     "ticks", "MXBean delta while measured calls ran; not pause distribution"),
                    ("gc_collection_time_ms", "ms", [report["gc_collection_time_ms"]],
                     "ticks", "MXBean cumulative collection time delta; not pause p95"),
                ]
                for name, unit, values, phase, notes in metrics:
                    values = [v for v in values if v is not None]
                    if name.startswith(("rss_tick", "pss_tick")) and len(values) < 5:
                        raise ValueError("Insufficient clean tick-phase OS samples to report memory")
                    med, p95, p99 = quantiles(values)
                    rows.append({
                        "timestamp_utc": now, "git_commit": git, "artifact_sha256": ARTIFACT_SHA256,
                        "scenario": f"{scenario}/run{repeat}", "role": "server_core_standalone",
                        "metric": name, "unit": unit, "samples": len(values),
                        "median": med, "p95": p95, "p99": p99, "phase": phase,
                        "tool": "Java21 exact-release private tick; Linux procfs",
                        "warmup_seconds": report["warmup_wall_seconds"],
                        "notes": f"{notes}; rails={rails}; trains=0; players=0",
                    })
    # Only write complete evidence after every run and validation has passed.
    with args.out.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with args.raw.open("x", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)
        f.write("\n")
    print(f"Committed-candidate new outputs: {len(raw['runs'])} runs, {len(rows)} CSV rows")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--jar", type=Path, required=True)
    p.add_argument("--jdk", type=Path, required=True)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--warmup-seconds", type=int, default=30)
    p.add_argument("--samples", type=int, default=120)
    p.add_argument("--pacing-ms", type=int, default=50)
    p.add_argument("--out", type=Path, default=PROJECT / "metrics/stage1-core-v2.csv")
    p.add_argument("--raw", type=Path, default=PROJECT / "metrics/stage1-core-v2-raw.json")
    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
