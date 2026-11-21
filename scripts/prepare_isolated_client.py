#!/usr/bin/env python3
"""Stage standalone, new, private Prism Launcher Fabric 1.21.1 A0 lab.

Uses only already pinned, PUBLIC release binaries in the Git-ignored research
server cache. Does not inspect or copy any installed Minecraft client files,
credentials, installed mods, worlds, logs, resource packs or shaders. Does not
launch software, contact an existing server, or accept a EULA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from benchmark_tsc import PROJECT, ARTIFACT_SHA256
from provision_isolated_fabric import API_SHA512

ISOLATION_PARENT = PROJECT / ".audit-cache" / "isolated-client"
PUBLIC_CACHE = PROJECT / ".audit-cache" / "isolated-fabric" / "stage1-v1"
MTR_NAME = "MTR-fabric-4.1.0-beta.2+1.21.1.jar"
INSTANCES = {"goldrail-a0-mtr": True, "goldrail-a0-control": False}
FABRIC_LOADER = "0.18.4"


def validate_destination(root: Path, parent: Path = ISOLATION_PARENT) -> Path:
    target = root.expanduser().resolve(strict=False)
    if root.is_symlink() or target.parent != parent.resolve(strict=False):
        raise ValueError("Destination must be one new immediate child of isolated-client cache")
    if target.exists():
        raise FileExistsError("Refuse to overwrite an existing lab")
    return target


def validate_artifact(path: Path, digest: str, algorithm="sha256") -> int:
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing or symlinked public artifact")
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    if h.hexdigest() != digest:
        raise ValueError(f"Public artifact hash mismatch: {path.name}")
    return path.stat().st_size


def version_json() -> str:
    return json.dumps({
        "formatVersion": 1,
        "components": [
            {"uid": "net.minecraft", "version": "1.21.1",
             "cachedName": "Minecraft", "important": True},
            {"uid": "net.fabricmc.fabric-loader", "version": FABRIC_LOADER,
             "cachedName": "Fabric Loader"}
        ]
    }, indent=2) + "\n"


def instance_cfg(name: str, java: Path) -> str:
    return (
        "[General]\n"
        "ConfigVersion=1.2\n"
        "InstanceType=OneSix\n"
        f"name={name}\n"
        "iconKey=default\n"
        "OverrideJavaLocation=true\n"
        f"JavaPath={java}\n"
        "OverrideMemory=true\n"
        "MinMemAlloc=1024\n"
        "MaxMemAlloc=4096\n"
        "notes=Isolated GoldRail Stage 1 reference lab; NOT GoldRail replacement\n"
    )


def provision(root: Path, java: Path, cache: Path = PUBLIC_CACHE) -> dict:
    target = validate_destination(root)
    java = java.expanduser().resolve()
    if not java.is_file() or not java.name.startswith("java"):
        raise ValueError("Choose an existing Java 21 executable with --java")
    reported = subprocess.run([str(java), "-version"], capture_output=True,
                              text=True, timeout=10, check=True).stderr
    if 'version "21.' not in reported and "openjdk 21." not in reported:
        raise ValueError("Java executable must report major version 21")
    mtr = cache / "mtr-enabled" / "mods" / MTR_NAME
    api = cache / "downloaded-public-jars" / "fabric-api.jar"
    mtr_size = validate_artifact(mtr, ARTIFACT_SHA256)
    api_size = validate_artifact(api, API_SHA512, "sha512")
    target.mkdir(parents=True, exist_ok=False)
    # All files are newly generated; no personal credentials, options or saves.
    prism = target / "prism-root"
    for slug, with_mtr in INSTANCES.items():
        instance = prism / "instances" / slug
        mods = instance / "minecraft" / "mods"
        mods.mkdir(parents=True)
        (instance / "mmc-pack.json").write_text(version_json())
        (instance / "instance.cfg").write_text(
            instance_cfg("GoldRail A0 original MTR" if with_mtr else
                         "GoldRail A0 Fabric control", java))
        shutil.copyfile(api, mods / "fabric-api.jar")
        if with_mtr:
            shutil.copyfile(mtr, mods / MTR_NAME)
            validate_artifact(mods / MTR_NAME, ARTIFACT_SHA256)
        validate_artifact(mods / "fabric-api.jar", API_SHA512, "sha512")
    launcher = target / "launch-a0.sh"
    launcher.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"\n'
        'command -v prismlauncher >/dev/null || { echo "Install Prism Launcher"; exit 1; }\n'
        'case "${1:-menu}" in\n'
        '  menu) exec prismlauncher --dir "$here/prism-root" ;;\n'
        '  mtr) exec prismlauncher --dir "$here/prism-root" --launch goldrail-a0-mtr ;;\n'
        '  control) exec prismlauncher --dir "$here/prism-root" --launch goldrail-a0-control ;;\n'
        '  mtr-offline) exec prismlauncher --dir "$here/prism-root" --launch goldrail-a0-mtr --offline GoldRailLab ;;\n'
        '  control-offline) exec prismlauncher --dir "$here/prism-root" --launch goldrail-a0-control --offline GoldRailLab ;;\n'
        '  *) echo "Usage: $0 [menu|mtr|control|mtr-offline|control-offline]"; exit 2 ;;\n'
        'esac\n'
    )
    launcher.chmod(0o755)
    manifest = {
        "schema": "goldrail-original-mtr-client-lab-v1",
        "status": "PROVISIONED; NOT A VERIFIED GAME LAUNCH",
        "minecraft": "1.21.1", "fabric_loader": FABRIC_LOADER,
        "java": "21", "prism": "separate --dir and newly generated profiles",
        "profiles": list(INSTANCES),
        "mtr": {"sha256": ARTIFACT_SHA256, "bytes": mtr_size},
        "fabric_api": {"version": "0.116.13+1.21.1",
                       "sha512": API_SHA512, "bytes": api_size},
        "license": "Client login may require user action; no accounts or tokens copied",
        "worlds": "No world, routes, sidings or moving trains generated",
        "isolation": "Separate Prism app root; all files inside this ignored lab directory"
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ISOLATION_PARENT / "stage1-v1")
    p.add_argument("--java", type=Path, default=Path.home() / "adoptium-jdk21" / "bin" / "java")
    p.add_argument("--public-cache", type=Path, default=PUBLIC_CACHE,
                   help="Previously staged, public and independently hashed research artifacts ONLY")
    args = p.parse_args()
    manifest = provision(args.root, args.java, args.public_cache)
    print("STAGED only:", args.root)
    print("Client launch, world gameplay and real GPU/frame traces: NOT MEASURED")
    print("Profiles:", ", ".join(manifest["profiles"]))


if __name__ == "__main__":
    main()
