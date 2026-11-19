#!/usr/bin/env python3
"""Read-only inspection of an MTR Fabric JAR. Never extracts raw files or world data."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

SEARCH_TERMS = (
    "org/mtr/core/Main.class",
    "org/mtr/core/simulation/Simulator.class",
    "org/mtr/core/simulation/FileLoader.class",
    "org/mtr/core/servlet/QueueObject.class",
    "org/mtr/core/data/Vehicle.class",
    "org/mtr/core/path/SidingPathFinder.class",
    "org/mtr/render/MainRenderer.class",
    "org/mtr/client/DynamicTextureCache.class",
    "org/mtr/packet/CustomPacketC2S.class",
    "org/mtr/packet/CustomPacketS2C.class",
    "org/mtr/fabric/MTRFabric.class",
    "org/mtr/fabric/MTRFabricClient.class",
)
PREFIXES = (
    "org/mtr/core/",
    "org/mtr/packet/",
    "org/mtr/render/",
    "org/mtr/client/",
    "org/mtr/fabric/",
    "assets/mtr/",
    "META-INF/jars/",
)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def inspect(path: Path) -> dict:
    with ZipFile(path) as jar:
        names = set(jar.namelist())
        metadata = json.loads(jar.read("fabric.mod.json").decode("utf-8"))
        manifest = jar.read("META-INF/MANIFEST.MF").decode("utf-8", "replace") if "META-INF/MANIFEST.MF" in names else ""
    # Only known-safe metadata goes into the report. Never write local source paths.
    result = {
        "artifact_basename": path.name,
        "artifact_sha256": sha256(path),
        "artifact_bytes": path.stat().st_size,
        "archive_entry_count": len(names),
        "fabric": {
            key: metadata.get(key)
            for key in ("id", "version", "name", "depends", "entrypoints", "mixins", "jars")
        },
        "manifest_selected": [
            line for line in manifest.splitlines()
            if line.startswith(("Stonecutter-Node-", "Fabric-Minecraft-Version:", "Fabric-Mapping-Namespace:"))
        ],
        "class_presence": {name: name in names for name in SEARCH_TERMS},
        "prefix_entry_counts": {
            prefix: sum(name.startswith(prefix) for name in names)
            for prefix in PREFIXES
        },
        "limitations": [
            "Class-file presence is not evidence of source commit correspondence or behavioral parity.",
            "No heap, native memory, MSPT, client FPS, or licensing status is measured here.",
            "Source tag and embedded TSC binary provenance require separate verification."
        ],
    }
    return result

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("jar", type=Path, help="Read-only path to exact installed MTR JAR")
    ap.add_argument("--output", type=Path, help="Write sanitized JSON report to local audit workspace")
    args = ap.parse_args()
    if not args.jar.is_file():
        ap.error("JAR does not exist")
    report = inspect(args.jar)
    data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
        print("Wrote sanitized audit metadata:", args.output.name)
    print(data)

if __name__ == "__main__":
    main()
