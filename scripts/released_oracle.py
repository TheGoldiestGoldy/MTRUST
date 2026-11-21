#!/usr/bin/env python3
"""Exact published MTR JAR bytecode oracle manifest, NOT a source commit lock.

No decompilation to source and no production server or world access.
This pins selected class bytes plus javap outputs for later differential fixtures.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from benchmark_tsc import ARTIFACT_SHA256, verify_artifact

CORE_CLASSES = [
    "org.mtr.core.data.Position",
    "org.mtr.core.data.Rail",
    "org.mtr.core.data.Siding",
    "org.mtr.core.data.Depot",
    "org.mtr.core.data.Route",
    "org.mtr.core.data.Vehicle",
    "org.mtr.core.simulation.Simulator",
    "org.mtr.core.simulation.FileLoader",
    "org.mtr.core.servlet.OperationProcessor",
]

def make_manifest(jar: Path, jdk: Path) -> dict:
    verify_artifact(jar)
    javap = jdk / "bin/javap"
    if not javap.is_file():
        raise ValueError("Requires javap from the JDK21 used for benchmark")
    version = subprocess.run([str(javap), "-version"], text=True, capture_output=True,
                             check=True)
    reported = (version.stdout + version.stderr).strip()
    if not reported.startswith("21."):
        raise ValueError("JDK21 javap required")
    entries = {}
    with zipfile.ZipFile(jar) as archive:
        for classname in CORE_CLASSES:
            entry = classname.replace(".", "/") + ".class"
            bytecode = archive.read(entry)
            inspected = subprocess.run([str(javap), "-p", "-c", "-classpath", str(jar),
                                        classname], text=True, capture_output=True, check=True)
            text = inspected.stdout
            if classname.endswith(".Simulator") and "private void tick(long);" not in text:
                raise ValueError("Expected internal released tick method not found")
            entries[classname] = {
                "entry": entry,
                "class_sha256": hashlib.sha256(bytecode).hexdigest(),
                "class_bytes": len(bytecode),
                "javap21_disassembly_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
    return {
        "schema": "goldrail-released-bytecode-oracle-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "released_artifact_sha256": ARTIFACT_SHA256,
        "jdk_javap_version": reported,
        "source_provenance": "UNRESOLVED",
        "behavioral_oracle": "published JAR bytecode, not candidate source checkout",
        "scopes": {
            "verified": "exact 9 class bytes and javap -p -c disassemblies",
            "partially_verified": "synthetic private tick() clock and rail-count reload in core-v2",
            "not_verified": "binary/source equivalence, routes, actual moving trains, packet wire, save bytes, Fabric behavior",
        },
        "classes": entries,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--jar", type=Path, required=True)
    p.add_argument("--jdk", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError("Refusing to replace existing oracle manifest")
    result = make_manifest(a.jar, a.jdk)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(f"Release SHA256 verified; fingerprinted {len(result['classes'])} released core classes")

if __name__ == "__main__":
    main()
