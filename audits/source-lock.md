# GoldRail Stage 1 source lock | 2026-11-19

## Binary identity: verified distribution, source mapping not proven

| Field | Evidence |
|---|---|
| Released file | `MTR-fabric-4.1.0-beta.2+1.21.1.jar` |
| SHA-256 (read-only local client JAR) | `5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94` |
| SHA-1 (locally calculated, matches official Modrinth version API) | `d7ba5e7371c45514fb58156fe16d971a4e32d788` |
| Size | 111,620,655 bytes; 10,921 ZIP entries |
| Second verification location | Same SHA-256 from read-only **live server mod JAR**, no server files modified and no world data opened |
| Modrinth release | [JSuVAgAb](https://modrinth.com/mod/minecraft-transit-railway/version/JSuVAgAb), published **2026-07-04T23:21:26Z** |
| Official API identity | `https://api.modrinth.com/v2/version/JSuVAgAb`; SHA-1 and size agree |
| In-JAR `fabric.mod.json` | id `mtr`, version `4.1.0-beta.2`, `minecraft=1.21.1`, Fabric entrypoints and `mtr.mixins.json` |
| JAR manifest | `Stonecutter-Node-Project: 1.21.1-fabric`, intermediary mappings, Fabric Loader 0.18.4, Java 21 compatible |
| Class verification | JDK21 `javap` found `org.mtr.core.Main`, `Simulator`, `FileLoader`, `OperationProcessor`, `MTR` and packet records with expected signatures |

**Status: release binary VERIFIED; exact source build UNRESOLVED.** SHA-1 matching Modrinth verifies distributed bytes, *not* source reproducibility or an embedded TSC commit.

## MTR source lock candidates (not proof of correspondence)

- Correct source tree: [Minecraft-Transit-Railway/Minecraft-Transit-Railway](https://github.com/Minecraft-Transit-Railway/Minecraft-Transit-Railway), branch `stonecutter`. The default `master` is a different line, not the beta.
- Strong *time-constrained source candidate*: `009b0ce8316b8b1adfaebad22ed5ffe2ee80b81b` (2026-07-04T22:11:00Z), latest `stonecutter` commit at/before Modrinth release publication.
- Latest checked branch head: `f05d99efab6f27b3868913438fce2da381e5798f` (2026-07-15, later than release). It must **not** be treated as the released code.
- Source candidate `gradle.properties` has `mod.version=4.1.0-beta.2`; `build-fabric.gradle.kts` uses `implementationAndShadow("org.mtr:transport-simulation-core:+")`.
- No specific 4.1.0-beta.2 Git tag/release appeared in GitHub tag or release API at time of audit; tags found were `3.x.x` and `2.x.x`.
- Source files and public binary method signatures agree for entrypoints, packets and core APIs, but builds are not byte-identical verified. Generated sources, CI dependency resolution and remapping can differ.

## Embedded Transport Simulation Core (TSC)

- Correct upstream: [Transport-Simulation-Core](https://github.com/Minecraft-Transit-Railway/Transport-Simulation-Core), Java 21.
- Candidate at publication date: `020cf90d8604a12e07521abf1ad397b5675031d8` (2026-07-04T02:10:54Z).
- HEAD observed 2026-11-19: `40d757109860b26f9ed6f3a3e92c8226ad5dcc86`; **too new to pin to the beta**.
- Build dependency `org.mtr:transport-simulation-core:+` is **dynamic** and not a fixed commit/version. The package/repository's resolved version at release build time was not obtained. Confirm via CI dependency resolution or reproducible rebuild before treating candidate as exact.
- The distributed JAR embeds `org/mtr/core/` and shaded libraries under `org/mtr/libraries/`. Do not replace those classes with current TSC HEAD untested.

## Reproduce without touching production

```bash
sha256sum /path/to/READ_ONLY_CLIENT_JAR.jar
sha1sum /path/to/READ_ONLY_CLIENT_JAR.jar
python3 scripts/inspect_mtr_jar.py /path/to/READ_ONLY_CLIENT_JAR.jar --output audits/artifact-report.json
# Re-run pinned metadata query, no private input:
python3 - <<'PY'
import json, urllib.request
with urllib.request.urlopen("https://api.modrinth.com/v2/version/JSuVAgAb") as r:
    v = json.load(r)
print(v["date_published"], v["files"][0]["size"], v["files"][0]["hashes"]["sha1"])
PY
```

Local upstream clones and JDK are ignored under `.audit-cache/`; never commit upstream binaries/worlds. Locally verified release SHA-1/size and the time-constrained source candidate are independent kinds of evidence. Upstream SHA values and GitHub API dates remain subject to history rewrites.

## Provenance/licensing gaps

MTR upstream `LICENSE` is MIT (2022 Jonathan Ho); TSC upstream `LICENSE` is MIT (2023 Jonathan Ho). Preserve both license notices and copyright attribution if reusing code. The release JAR contains Elementa 743, UniversalCraft 497 and Kotlin stdlib 2.4.20-Beta1 nested JARs; their `fabric.mod.json` entries do not state licenses and nested JARs do not expose conventional LICENSE files. Identify authoritative upstream license notices and redistribution requirements before shipping. Assets (`assets/mtr/` includes 4,436 ZIP entries), fonts, textures, train models, shader-related files and third-party content require independent rights review; MIT root code license alone is not clearance. No third-party assets have been copied into GoldRail.


## Stage 1 evidence remediation provenance update | 2026-11-19

**Still UNRESOLVED**: no exact source/TSC package lock. New official-release download into a separate ignored research cache matched SHA-256 `5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94`. The Modrinth `JSuVAgAb` SHA-1 and byte length again match.

A fresh GitHub API check of [MTR CI run 28721258101](https://github.com/Minecraft-Transit-Railway/Minecraft-Transit-Railway/actions/runs/28721258101) confirmed successful `stonecutter@009b0ce8` source at 2026-07-04T22:11Z, but its public artifacts array was empty. The workflow uploads artifacts only if a private `BUILD_ARTIFACTS` variable is set, and neither the distributed SHA nor Gradle's resolved `org.mtr:transport-simulation-core:+` is published. [TSC CI run 28691701011](https://github.com/Minecraft-Transit-Railway/Transport-Simulation-Core/actions/runs/28691701011) is scheduled at SHA `0dfd201b`; the upstream workflow publishes to GitHub Packages on **push only**, not schedule. Anonymous requests for GitHub Maven metadata and packages versions returned **401**. No release source correspondence can be derived from timing.

**Declared fallback oracle**: hash-gated published class bytes and `javap -p -c` in `audits/released-core-oracle.json`, regenerated by `scripts/released_oracle.py` for nine selected `org.mtr.core` classes. This **does not verify source identity**, route/vehicle behavior or full compatibility. The V2 deterministic private `tick(long)` clock and count-only save/reload are narrow first golden observations. Remaining golden fixture suite must exercise full serialized bytes, operation sequences, train states, packet payloads, unknown fields, and error handling before source-dependent porting. An isolated Fabric bootstrap displayed a `+1.21.4` banner despite verified release metadata/loader for 1.21.1; do not use banners to infer a source lock.
