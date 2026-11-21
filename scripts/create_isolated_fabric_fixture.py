#!/usr/bin/env python3
"""Offline, nonstarting Fabric profile scaffolder: does NOT create working trains.

The generated profile is under GoldRail's ignored .audit-cache/ ONLY.
No reference to existing Minecraft installs, private worlds, mods, logs or seeds.
It deliberately does not accept EULA or start a server.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from benchmark_tsc import PROJECT, verify_artifact, ARTIFACT_SHA256

ISOLATION_PARENT = PROJECT / ".audit-cache" / "isolated-fabric"

SCENARIO_PLAN = {
    "S0": {"trains": 0, "rails": 0, "routes": 0, "sidings": 0, "players": 0,
           "status": "NOT MEASURED"},
    "S1": {"trains": 1, "rails": 64, "routes": 1, "sidings": 1, "players": 0,
           "status": "NOT MEASURED"},
    "S2": {"trains": 6, "rails": 256, "routes": 3, "sidings": 3, "players": 0,
           "status": "NOT MEASURED"},
    "S3": {"trains": 24, "rails": 512, "routes": 6, "sidings": 6, "players": 0,
           "status": "NOT MEASURED"},
    "S4": {"trains": 24, "rails": 512, "routes": 6, "sidings": 6, "players": 8,
           "status": "NOT MEASURED"},
}
# Target values are planning parameters only; no actual rail/train/entity counts exist.

def validate_destination(root: Path, cache_parent: Path = ISOLATION_PARENT) -> Path:
    target, allowed = root.expanduser().resolve(), cache_parent.resolve()
    if target.parent != allowed:
        raise ValueError("Target MUST be one new immediate child of GoldRail .audit-cache/isolated-fabric")
    if target.exists():
        raise FileExistsError("Never modify an existing profile")
    if target.name in (".", "..") or target.is_symlink():
        raise ValueError("Invalid fixture destination")
    return target


def profile_files(seed: str) -> dict[str, str]:
    common = (
        "server-ip=127.0.0.1\nserver-port=25586\n"
        "online-mode=true\nenable-rcon=false\nenable-query=false\n"
        "enable-command-block=false\nmax-players=8\n"
        "view-distance=8\nsimulation-distance=8\n"
        "level-type=minecraft:flat\n"
        f"level-seed={seed}\n"
        "motd=GoldRail isolated synthetic benchmark ONLY\n"
    )
    return {
        "server.properties": common,
        "eula.txt": "eula=false\n",
        "README.md": (
            "# Inert isolated Fabric test scaffold\n\n"
            "No Fabric server launcher, Fabric API or world is bundled.\n"
            "No server has started, no train data exists and no S0-S4 measurements have been taken.\n"
            "Obtain and independently hash-pin Minecraft 1.21.1 Fabric Loader, Fabric API, and"
            " server launcher into this NEW profile only. Do NOT copy from an installed client"
            " or live server. The seed is supplied at runtime; it is not embedded in source or committed.\n"
            "Before launch, an operator must separately accept the Minecraft EULA for this"
            " isolated test; this builder will never silently accept it. Bind to loopback only.\n"
            "Create tracks, stations, sidings, depots, routes and scheduled actively moving"
            " trains through a tested deterministic MTR fixture generator (not yet developed).\n"
            "Verify each achieved entity count in-game before any profiling, repeat >=3 times"
            " per scene and control, and compare same-seed isolated worlds after first generation.\n"
            "Do not claim train-moving MSPT until actual measured traces exist.\n"
        ),
    }


def create(root: Path, jar: Path, seed: str) -> Path:
    verify_artifact(jar)
    target = validate_destination(root)
    target.mkdir(parents=True, exist_ok=False)
    try:
        for variant in ("mtr-enabled", "fabric-no-mtr"):
            base = target / variant
            (base / "mods").mkdir(parents=True)
            for name, content in profile_files(seed).items():
                (base / name).write_text(content, encoding="utf-8")
        destination = target / "mtr-enabled" / "mods" / jar.name
        shutil.copyfile(jar, destination)
        if hashlib.sha256(destination.read_bytes()).hexdigest() != ARTIFACT_SHA256:
            raise RuntimeError("Copied fixture JAR digest mismatch")
        manifest = {
            "schema": "goldrail-fabric-scaffold-v1",
            "artifact_sha256": ARTIFACT_SHA256,
            "platform": "Fabric Minecraft 1.21.1 / Java21, not booted",
            "server_state": "NOT INSTALLED; NOT STARTED",
            "seed": seed,
            "profiles": ["mtr-enabled", "fabric-no-mtr"],
            "scene_targets_not_achieved": SCENARIO_PLAN,
            "blocked_until": [
                "Hash-pin and install standalone official Fabric launcher, Fabric API and Minecraft 1.21.1 server",
                "Accept Minecraft EULA for this *test profile* only",
                "Build a verified synthetic MTR track/station/siding/route/vehicle generator",
                "Validate moving cars and same-state comparator across both profiles",
                "Implement MSPT/TPS, heap/alloc/GC, procfs phase and NMT traces with 3+ repeats",
                "Supply controlled clients/bots for S4 player count, without production connection",
            ],
        }
        (target / "fixture-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    except Exception:
        shutil.rmtree(target)
        raise
    return target


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True, help="New child of .audit-cache/isolated-fabric")
    p.add_argument("--jar", type=Path, required=True, help="Published official release archive only")
    p.add_argument("--seed", required=True, help="Runtime-only synthetic seed; never commit it")
    a = p.parse_args()
    target = create(a.root, a.jar, a.seed)
    print(f"Created inert paired profiles at {target}. Fabric/trains/MSPT NOT MEASURED.")


if __name__ == "__main__":
    main()
