#!/usr/bin/env python3
"""Create a PRIVATE GoldRail A0 client lab using installed PollyMC executable.

Never execute the user's normal pollymc-local wrapper: it forces the user's
existing game root. The AppRun --dir switch creates a separate app root.
Existing user mods, accounts, world saves and resource packs are untouched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from prepare_isolated_client import ISOLATION_PARENT, provision

DEFAULT_ROOT = ISOLATION_PARENT / "stage1-polly-v1"


def validate_polly_executable(executable: Path):
    if not executable.is_file() or not executable.stat().st_mode & 0o111:
        raise ValueError("Expected an installed executable PollyMC AppRun binary")
    result = subprocess.run([str(executable), "--help"], capture_output=True,
                            text=True, timeout=10, check=True)
    description = result.stdout + result.stderr
    if "--dir" not in description or "--launch" not in description:
        raise ValueError("This launcher lacks the required isolated --dir/--launch interface")
    if "PollyMC" not in description:
        raise ValueError("Executable did not identify itself as PollyMC")
    return description.splitlines()[0:2]


def provision_polly(root: Path, launcher: Path, java: Path, public_cache: Path):
    # Validate before creating any directory. The public MTR and Fabric API
    # blobs are checked cryptographically inside provision().
    validate_polly_executable(launcher)
    manifest = provision(root, java, public_cache)
    old = root / "prism-root"
    new = root / "polly-root"
    old.rename(new)
    launch = root / "launch-a0.sh"
    launch.write_text('''#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
launcher="${GOLDRAIL_POLLYMC_APP:?Set GOLDRAIL_POLLYMC_APP to the isolated PollyMC AppRun path}"
[[ -x "$launcher" ]] || { echo "PollyMC AppRun is missing"; exit 2; }
case "${1:-menu}" in
  menu) exec "$launcher" --dir "$here/polly-root" ;;
  mtr) exec "$launcher" --dir "$here/polly-root" --launch goldrail-a0-mtr ;;
  control) exec "$launcher" --dir "$here/polly-root" --launch goldrail-a0-control ;;
  mtr-offline) exec "$launcher" --dir "$here/polly-root" --launch goldrail-a0-mtr --offline GoldRailLab ;;
  control-offline) exec "$launcher" --dir "$here/polly-root" --launch goldrail-a0-control --offline GoldRailLab ;;
  *) echo "Usage: $0 [menu|mtr|control|mtr-offline|control-offline]"; exit 2 ;;
esac
''')
    launch.chmod(0o755)
    manifest.pop("prism", None)
    manifest["launcher"] = "PollyMC-Continued, independent --dir polly-root"
    manifest["isolation"] = "Separate PollyMC root; never use normal pollymc-local wrapper"
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--launcher", type=Path, required=True,
                        help="Actual PollyMC AppRun executable, not normal pollymc-local wrapper")
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--public-cache", type=Path,
                        default=ISOLATION_PARENT.parent / "isolated-fabric" / "stage1-v1")
    args = parser.parse_args()
    provision_polly(args.root, args.launcher, args.java, args.public_cache)
    print("PollyMC A0 original-MTR client provisioned under ignored isolated-client lab.")
    print("Separate PollyMC UI/game runtime and frame times: NOT YET VERIFIED.")


if __name__ == "__main__":
    main()
