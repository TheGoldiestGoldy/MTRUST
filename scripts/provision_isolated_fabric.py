#!/usr/bin/env python3
"""Install hash-pinned public Fabric dependencies into a NEW GoldRail test scaffold.

Standalone 1.21.1 Fabric server launcher, pinned loader 0.18.4 and Fabric API
0.116.13+1.21.1. NEVER launches Minecraft, accepts EULA or accesses live mods.
The official Fabric meta endpoint has no documented sha256 in response here:
record the downloaded launcher SHA256, do not claim a pre-pinned distribution hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

from create_isolated_fabric_fixture import ISOLATION_PARENT

LOADER_URL = "https://meta.fabricmc.net/v2/versions/loader/1.21.1/0.18.4/1.1.2/server/jar"
API_URL = ("https://cdn.modrinth.com/data/P7dR8mSH/versions/FHknjVVa/"
           "fabric-api-0.116.13%2B1.21.1.jar")
API_SHA512 = ("87a8e136c43f03d09af96d6b2b35d27b58679d61a158585477fbcc9250ecaf8a"
              "5896a18a9b132bdd6b8bcd1ba291acd71f961d58987e770b9a73b653ac237c2f")


def fetch(url: str, destination: Path, expected_sha512: str | None = None) -> dict:
    if destination.exists():
        raise FileExistsError("Refuse to overwrite test launcher/dependencies")
    request = urllib.request.Request(url, headers={"User-Agent": "GoldRail-stage1-evidence/1.0"})
    hashes = {"sha256": hashlib.sha256(), "sha512": hashlib.sha512()}
    with urllib.request.urlopen(request, timeout=25) as source, destination.open("xb") as f:
        while block := source.read(1024 * 1024):
            for digest in hashes.values():
                digest.update(block)
            f.write(block)
    if expected_sha512 and hashes["sha512"].hexdigest() != expected_sha512:
        destination.unlink()
        raise ValueError("Official Fabric API hash does not match pinned Modrinth release")
    try:
        with zipfile.ZipFile(destination) as jar:
            if not jar.namelist():
                raise ValueError("Empty downloaded Java archive")
    except zipfile.BadZipFile:
        destination.unlink()
        raise
    return {"url": url, "sha256": hashes["sha256"].hexdigest(),
            "sha512": hashes["sha512"].hexdigest(), "bytes": destination.stat().st_size}


def provision(root: Path) -> dict:
    target = root.expanduser().resolve()
    if target.parent != ISOLATION_PARENT.resolve():
        raise ValueError("Only a GoldRail isolated-fabric child can be provisioned")
    manifest = target / "fixture-manifest.json"
    if not manifest.is_file():
        raise ValueError("Missing generated inert fixture manifest")
    for sub in ("mtr-enabled", "fabric-no-mtr"):
        if not (target / sub / "eula.txt").read_text().strip() == "eula=false":
            raise ValueError("Fixture has been started or EULA modified: refusing to touch")
        if (target / sub / "fabric-server-launch.jar").exists():
            raise FileExistsError("Loader already installed")
    bundle_dir = target / "downloaded-public-jars"
    bundle_dir.mkdir(exist_ok=False)
    fabric = fetch(LOADER_URL, bundle_dir / "fabric-server-launch.jar")
    api = fetch(API_URL, bundle_dir / "fabric-api.jar", API_SHA512)
    for sub in ("mtr-enabled", "fabric-no-mtr"):
        base = target / sub
        shutil.copyfile(bundle_dir / "fabric-server-launch.jar", base / "fabric-server-launch.jar")
        shutil.copyfile(bundle_dir / "fabric-api.jar", base / "mods" / "fabric-api.jar")
    record = {
        "status": "PUBLIC DEPENDENCIES STAGED; NOT BOOTED; EULA FALSE",
        "loader": {"minecraft": "1.21.1", "fabric_loader": "0.18.4",
                   "installer": "1.1.2", **fabric},
        "fabric_api": {"version": "0.116.13+1.21.1", "modrinth_version_id": "FHknjVVa",
                       "pinned_modrinth_sha512": API_SHA512, **api},
        "control": "Fabric API present in both paired profiles; original MTR only in enabled profile",
        "limitations": "No actual tracks/routes/sidings/active train entities/bots/MSPT",
    }
    (target / "public-dependencies.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    a = p.parse_args()
    r = provision(a.root)
    print("Public launcher + Fabric API staged in both isolated profiles.")
    print("Fabric server boot, train activation and real MSPT: NOT MEASURED.")
    print("Fabric launcher SHA256:", r["loader"]["sha256"])


if __name__ == "__main__":
    main()
