# GoldRail | Coding Agent | Stage 1 server evidence repair | 2026-11-19

**Disposition: PARTIAL REMEDIATION. G1 REMAINS REJECTED/CLOSED.** This is evidence tooling, not a Rust implementation, performance improvement, or write-capable replacement. No client UI remediation was attempted. The exact official released Java core is the experimental reference; *its matching source build remains unresolved*.

## Scope, safety and source of evidence

- Started from clean `pm/g1-decision@a404975` and created `cod/stage1-evidence-repair`. No merge, push, release or Stage 2.
- Public MTR Fabric 4.1.0-beta.2+1.21.1 archive downloaded separately from Modrinth into an ignored research cache. Independently recomputed SHA-256: `5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94`. This is not an installed-mod or live-server JAR.
- Tests and the two new Fabric scaffold profiles live entirely inside ignored `.audit-cache/`. No installed client, production mods, world, server files, remote network address, private seed, user logs or real world were opened, copied, altered or profiled. No EULA was accepted, production server contacted, or installed mod changed.
- Earlier `scripts/CoreSyntheticBenchmark.java`, `scripts/benchmark_tsc.py`, `metrics/stage1-raw.json` and `metrics/baseline.csv` remain **unchanged** so Stage 1 history can be reconstructed. Original baseline file SHA-256 values: JSON `4e5fd6cd13989b657cb0c239f10fe407ac4331b9f7498f8b001c312e30bf1e75`; CSV `4aa0d37568ba144be893e684a4299c29c99e194214ba6444d16cf0fcff5e6704`.

## GR-G1-04 and GR-G1-05: repaired evidence methods

New versioned sources: `scripts/CoreEvidenceBenchmark.java`, `scripts/benchmark_tsc_v2.py`.

1. Java prints monotonic `PHASE` markers for **startup, warmup, measured ticks, save, reload, idle, done**. Python captures timestamped RSS/PSS from `/proc/<pid>/smaps_rollup`, labels samples against JVM phase instants, validates Linux JVM/Python monotonic clock alignment, rejects corrupted/missing/out-of-order phases and excludes a 100 ms uncertainty interval around each transition.
2. **30 actual wall-clock seconds** of warmup, recorded and validated, rather than 12 calls misleadingly treated as seconds. In the recorded runs this produced **600 warmup calls per process** at a nominal 50 ms pace; measured phase includes 120 further calls. A bounded 700 ms explicitly marked idle follows save/reload. Save and reload can be too short for the sampler: all 9 processes have **zero clean save-phase and reload-phase samples**; such memory is NOT MEASURED. An observed process-sampled maximum is labeled separately from any true OS high-water mark.
3. The prior harness reset a synthetic clock to `System.currentTimeMillis()-1000` on each call and executed public `Simulator.tick()`, which performs wall-clock catch-up. V2 instead uses reflective access to the exact released **private `Simulator.tick(long)`**, starting at the same fixed virtual timestamp and passing a fixed **1000 ms delta** each call. It verifies each update advances the internal virtual clock by exactly 1000 ms; all nine measured phases advanced **120,000 virtual ms** each. This is deterministic on the measured clock path, **not a simulation of a 50 ms Minecraft server tick**. Java reflection call overhead is included.
4. V2 observes main-thread ThreadMXBean allocations and GC collection counts/time (NOT GC pause percentiles); one used/committed heap and direct-buffer snapshot follows measured ticks. It enables JVM Native Memory Tracking `summary` and captures one `jcmd VM.native_memory summary` during the timed phase. NMT's *whole-process* committed total includes Java heap; it is **not the native-only cost of MTR**, and attaching jcmd may perturb measured latency. RSS/PSS also include the whole JVM, not just core allocation.
5. Reproducibility: V2 writes new `metrics/stage1-core-v2.csv` and `the raw V2 phase-level process trace, intentionally withheld from this public snapshot; its digest remains in metrics/stage1-core-v2-provenance.json` with 90 metric rows, per-phase raw timestamps, actual warmup, microsecond-scale call distributions, peak labels, NMT categories and per-run counts. Both paths are created with exclusive mode and cannot overwrite existing files. `metrics/stage1-core-v2-provenance.json` hashes the executed Java/Python sources and both new evidence files. The CSV/JSON `harness_git_commit=a404975` is the **pre-edit base commit**, not a false claim those then-uncommitted V2 scripts lived in that commit; actual source identities are the companion SHA-256 hashes and this branch's final commit.

### Measurements (new V2, standalone exact released Java core)

Environment: Linux x86_64, JDK 21.0.13.1, two JVM active processors, Java heap Xms128m/Xmx512m, shared desktop with background load. Scenarios: synthetic 0/64/512 straight rails, **zero active trains, routes, passengers or players**. Each has **3 independent JVM processes**, 30 seconds actual warmup + 120 timed private internal calls per process. Reported percentiles are nearest-rank on 360 pooled calls per scenario; pooled OS memory samples are serial measurements, **not independent JVM-run replicates**.

| Synthetic scenario | Timed calls | Private internal `tick(long)` median / p95 / p99 ms | Clean tick-phase RSS/PSS observations | Median tick-phase RSS / PSS MiB |
|---|---:|---|---:|---|
| S0 empty | 360 | 0.018990 / 0.042504 / 0.072684 | 639 / 639 | 62.57 / 59.49 |
| T1 64 straight rails | 360 | 0.027014 / 0.043602 / 0.060104 | 640 / 640 | 69.21 / 66.13 |
| T2 512 straight rails | 360 | 0.134271 / 0.215008 / 0.302726 | 627 / 627 | 148.37 / 145.28 |

- Run-by-run tick-time medians in ms: S0 **0.020307, 0.018318, 0.018925**; T1 **0.026505, 0.027990, 0.026591**; T2 **0.147899, 0.129970, 0.126456**. T2's per-run differences are material at these short latencies.
- Observed whole-process sampled RSS peaks by run (MiB), **across all phases**, not guaranteed high-water marks: S0 **65.87, 63.71, 64.37**; T1 **83.74, 83.43, 84.68**; T2 **171.39, 159.17, 141.34**. T2 spans ~30 MiB even across matched synthetic processes.
- NMT whole-JVM committed totals at a single measured-phase instant, MiB: S0 **200.74, 200.79, 200.79**; T1 **201.27, 201.28, 201.53**; T2 **201.26, 201.15, 201.56**. These values include committed Java heap and NMT-tracked JVM categories, so they must not be interpreted as native MTR usage or compared naively against RSS.
- V1 historical numbers independently rechecked (10/10 original tests plus new independent replay assertion): S0 **0.011685/0.029911/0.033664**; T1 **0.043479/0.138011/0.173964**; T2 **0.260449/0.382223/0.471665** ms. V1's old RSS/PSS samples have **no phase timestamps** and are intrinsically mixed, not retroactively repaired or directly comparable with V2. V1 used a different public method and clock operation, so apparent V1/V2 timing differences are **NOT speedups**.

## GR-G1-03: provenance evidence and released bytecode oracle

- Official Modrinth version endpoint `https://api.modrinth.com/v2/version/JSuVAgAb`: date **2026-07-04T23:21:26Z**, release archive SHA-1 `d7ba5e7371c45514fb58156fe16d971a4e32d788`, length **111,620,655 bytes**. This matches the independently verified release.
- Public MTR GitHub Actions run [28721258101](https://github.com/Minecraft-Transit-Railway/Minecraft-Transit-Railway/actions/runs/28721258101) succeeded on source `009b0ce8...` at 22:11 UTC, before Modrinth upload. Its public artifacts API returns **zero artifacts**. The workflow only uploads conditionally on `BUILD_ARTIFACTS=true`. The associated MTR build file uses `org.mtr:transport-simulation-core:+` with no lock. A chronological association is NOT a binary source pin.
- TSC scheduled [run 28691701011](https://github.com/Minecraft-Transit-Railway/Transport-Simulation-Core/actions/runs/28691701011) ran at SHA `0dfd201b...`; its workflow's **scheduled** path does not execute the `push`-only GitHub Packages publish step. The candidate `020cf90d...` is still merely a date-constrained checkout. Unauthenticated GitHub Maven metadata and package-version API returned **HTTP 401**. Thus the **specific resolved TSC coordinate and byte-identical MTR source remain UNKNOWN**; never claim exact source provenance from current HEAD.
- Adopt the published **JAR bytecode as the behavioral oracle** until source is proven. `scripts/released_oracle.py` generated `audits/released-core-oracle.json`: fingerprints nine `org.mtr.core` class byte sequences and JDK21 `javap -p -c` disassemblies, including Simulator, Rail, Siding, Route, Depot, Vehicle, FileLoader and OperationProcessor. This proves class identities only. V2 adds a narrow deterministic internal-tick and **count-only** MessagePack reload golden observation; future gate must still develop differential serialized bytes/unknown fields, queued operations, real vehicle timetables, network envelopes and domain parity fixtures against this exact bytecode.

## GR-G1-01: isolated Fabric feasibility, no fabricated workload

- `scripts/create_isolated_fabric_fixture.py` creates **two new, paired, strictly isolated synthetic profiles** with fixed public seed, flat world setting, loopback binding, RCON/query disabled, EULA set to **false**, and one exact released MTR archive in the MTR-enabled profile only. Existing target paths are refused. The accompanying S0-S4 fixture manifest gives *intended* rail/route/siding/train/player counts, each explicitly **NOT MEASURED**.
- `scripts/provision_isolated_fabric.py` staged the official Fabric server launcher (Minecraft **1.21.1**, Fabric Loader **0.18.4**, installer **1.1.2**) and pinned Fabric API **0.116.13+1.21.1** (published 2026-07-01) from Modrinth, verifying its SHA-512. The standalone launcher download hash was recorded as SHA-256 `519ba43a17c80fe72266a6cab581bad05db0b1fd115fc1c29f29a305abbc68a9`, but unlike Fabric API it lacks a predeclared cryptographic checksum, so its origin is verified only by official HTTPS and this local hash.
- The ignored `.audit-cache/isolated-fabric/stage1-v1` was prepared and can be recreated from scripts. Both **no-MTR control and exact-MTR-enabled** Java21 Fabric startup probes loaded to the Minecraft EULA gate and exited cleanly with `eula=false`; the MTR-enabled probe listed `mtr 4.1.0-beta.2` and registered blocks, items and types before the gate. It DID NOT run a game tick or create a measured scene. The MTR banner printed a `+1.21.4` string despite verified `fabric.mod.json` and loader showing 1.21.1; this is an unresolved banner/version string discrepancy, not proof that the actual Minecraft version changed.
- **Hard blocker:** No validated deterministic generator for MTR v4 in-world rails, platforms, sidings, depots, schedules and actively moving vehicles. Merely copying the released JAR or constructing straight-line Java core rails does not create operating services in a Fabric world. Eight real S4 players additionally require controlled clients/bots and same-world comparisons. The test profiles deliberately do not accept a license or start gameplay. No safe S1-S4 real workload traces were captured.
- Therefore **actual Fabric MSPT/TPS p50/p95/p99, real train counts, per-tick full-server allocation/GC/NMT/RSS/PSS, and MTR-on/off causal attribution are NOT MEASURED**. The project must not select Rust based on these V2 numbers. Do not treat the S0 early loader/EULA probe as a benchmark.

## Validation and remaining gate conditions

- `python3 -m unittest discover -s tests -v`: **29/29 PASS** (10 existing + 19 new), including negative cases for mixed memory phases, monotonic drift, missing/out-of-order phase labels, nonfinite duration, insufficient warmup, wrong virtual clock, unwritable existing profiles and non-release JAR.
- `python3 -m py_compile scripts/*.py tests/*.py`: **PASS**. Exactly **9/9** full V2 processes passed the clock and count-only reload checks. Released oracle fingerprinted **9 classes**. `git diff --check`: PASS before handoff.
- Not fixed by this Coding assignment: **GR-G1-01 full active-car Fabric evidence**, **GR-G1-02 client UI/FPS evidence** (different agent), **GR-G1-03 exact source lock**; production write safety GR-G1-06, packet/addon parity GR-G1-07, renderer parity and license risks remain tracked but untested.
- Next steps for PM: review this branch, require an isolated EULA-authorized, replayable synthetic Fabric scenario generator or a formal blocked disposition before G1 reconsideration; assign UI remediation separately after Coding handoff; then commission independent Product Review. **No Stage 2 and no deployment authority.**

## Reproduction

From the repository root with JDK21 and **fresh, separately downloaded, exact-hash official** MTR beta JAR in ignored cache:

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py tests/*.py
python3 scripts/released_oracle.py --jar /path/to/official-release.jar \
  --jdk /path/to/jdk21 --output .audit-cache/oracle-recheck.json
python3 scripts/benchmark_tsc_v2.py --jar /path/to/official-release.jar \
  --jdk /path/to/jdk21 --runs 3 --warmup-seconds 30 --samples 120 \
  --pacing-ms 50 --out .audit-cache/v2-recheck.csv \
  --raw .audit-cache/v2-recheck.json
python3 scripts/create_isolated_fabric_fixture.py \
  --root .audit-cache/isolated-fabric/fresh-scene --jar /path/to/official-release.jar
python3 scripts/provision_isolated_fabric.py \
  --root .audit-cache/isolated-fabric/fresh-scene
```

All output names above are distinct because scripts reject overwrites. **Never point a builder or benchmark at a production world/server or install directory.** Preflight profiles do NOT authorize Minecraft EULA acceptance or active server execution.
