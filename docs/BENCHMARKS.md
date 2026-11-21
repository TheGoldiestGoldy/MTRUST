# Benchmark protocol: evidence, not vibes

Never benchmark against the live server or copy private world files. Use isolated synthetic, seeded worlds and version-pinned modpacks. Include a clean upstream control and a candidate build under identical conditions.

## Metrics

- **Server Java heap:** used, committed, GC allocation rate and pauses from JFR/JMX or equivalent, with tool and interval recorded.
- **Native/off-heap:** direct buffers and native memory tracking where supported; no assumption that JNI reduces process memory.
- **Total memory:** RSS and preferably PSS from OS proc accounting, sampling both idle and train-dense periods.
- **Server tick:** MSPT median/p95/p99, TPS, active train counts, station/routes and players, warmup time, GC details.
- **Client:** render-thread frame times median/p95/p99, 1% low FPS with stated method; GPU/CPU utilization and GPU model, shader+Sodium/Iris versions, resolution and draw distance.
- **Compatibility:** deterministic operation replay snapshot diff, saves round-trip, packets, content packs, addon interactions.

## Scenarios

S0: no trains / baseline. S1: isolated train. S2: representative active routes. S3: train-dense scene with client camera fixed. S4: many players/interest regions. Keep same seed, timestamp/tick sequence, topology and data sizes between candidates; publish only synthetic fixtures.

## Standard record

`metrics/baseline.csv` columns: timestamp_utc,git_commit,artifact_sha256,scenario,role,metric,unit,samples,median,p95,p99,tool,warmup_seconds,notes. An empty header is not a measurement. Document missing instrumentation as **not measured** in the handoff.

## Acceptance

Require raw reproducible commands, hardware characteristics without identifiers, repeat runs, defined warmup, uncertainty/variance and side-by-side baseline before declaring gain. Do not equate JAR disk size with resident memory.

## GoldRail Stage 1 reproducible embedded-core harness

`scripts/CoreSyntheticBenchmark.java` and `scripts/benchmark_tsc.py` exercise the **actual released, shaded Java Transport Simulation Core** in a new temporary directory (never a world copy). The Python launcher verifies the exact SHA-256 before invoking the JDK, compiles against the official JAR, and uses isolated `-Xmx512m` / two active processors. Synthetic fixtures are generated in-memory: S0 is empty; T1 has 64 connected rails; T2 has 512 connected rails. Rail coordinates are deterministic, at y=64, each 16 blocks long, on a line. There are **zero moving trains, routes, passengers or players** in these tests. T1/T2 are topology probes, not S1/S2 from the full test matrix.

```bash
# Example on a test workstation: choose an existing READ-ONLY client JAR.
export MTR_JAR=/absolute/path/to/MTR-fabric-4.1.0-beta.2+1.21.1.jar
export JAVA_HOME=/absolute/path/to/jdk-21
python3 scripts/benchmark_tsc.py --jar "$MTR_JAR" --jdk "$JAVA_HOME" \
  --runs 3 --warmup 12 --samples 40
python3 -m unittest discover -s tests -v
```

Output: `metrics/baseline.csv` plus `metrics/stage1-raw.json` with each 40-sample TSC invocation series and aggregate process memory samples. `java_heap_used_bytes` / committed are MXBean snapshots; `rss_bytes` and `pss_bytes` come from `/proc/<pid>/smaps_rollup` **after warmup**, direct buffer use from `BufferPoolMXBean`, main-thread allocation from `ThreadMXBean`, and GC count/time from `GarbageCollectorMXBean`. This **does not** measure native allocation by origin, total peak RSS or CPU frame time; do not treat direct buffers as total native memory. Single snapshots have no p95 or p99. Nearest-rank 95/99 percentiles apply to actual time series. Java GC collection time is **not** a pause-percentile measurement.

Each measured tick forces a nominal one-second simulation catch-up via the exposed protected clock setter in a test subclass. `tsc_tick_invocation_ms` is **not server MSPT**; actual Minecraft thread scheduling, networking, actual vehicle motion, and client visuals are absent. Synthetic save/reload validates **rail counts only**. No performance gain can be claimed: there is no optimized candidate yet. Because this is a shared workstation, run-to-run noise and background load are possible even with repeat runs. Core results cannot establish that MTR caused the observed live server memory or FPS drops.

**Still NOT MEASURED:** full Fabric server MSPT/TPS and train counts, actual active train S1-S4, client FPS/1% lows/render thread, shader-specific GPU frame times, full JVM native allocation (NMT), save unknown-field fidelity, and addon/game load compatibility. G1 remains closed until independent review and PM approval.


## Stage 1 Coding Evidence Repair (V2, 2026-11-19)

**Gate G1 remains CLOSED.** The preceding V1 instructions are retained as historical reproduction only: V1's `warmup_wall_seconds` is time until a `WARMED` marker, not 12 seconds of warmup; its public `Simulator.tick()` calls repeatedly reset the clock to wall time minus ~1000ms, and its pooled post-`WARMED` RSS/PSS mixes timed ticks with save/reload and later idle. Do not report the original memory medians as tick steady-state or infer a V1/V2 speedup.

For corrected experimental core-only evidence use **new** `scripts/CoreEvidenceBenchmark.java`, `scripts/benchmark_tsc_v2.py`, `metrics/stage1-core-v2.csv` and `the raw V2 phase trace (not included in this public snapshot; its digest is retained in metrics/stage1-core-v2-provenance.json)`. V2 enforces 30 actual wall seconds of paced warmup, calls the *released private* `Simulator.tick(long)` reflectively with consecutive +1000ms virtual steps, records distinct JVM phase markers and phase-tagged procfs RSS/PSS (100ms boundary guard), samples NMT committed JVM categories once in ticks, labels maximum observed RSS/PSS across all phases, and refuses to overwrite outputs. The measured phase contains paced calls and sleeps. This is not public `Simulator.tick()`, Fabric MSPT, active trains, a GPU/FPS capture or optimized Java/Rust comparator. NMT includes the JVM heap; all Java/RSS/PSS totals are whole-process values. Save/reload memory remained NOT MEASURED due their short phases.

Nine independent Java processes (3 per synthetic 0/64/512 rails, each 600 warmup/120 measured internal calls) completed. Pooled internal-tick p50/p95/p99 (ms): **0.018990/0.042504/0.072684** (S0), **0.027014/0.043602/0.060104** (T1), **0.134271/0.215008/0.302726** (T2). Pooled tick-phase RSS medians: **62.57/69.21/148.37 MiB**; PSS **59.49/66.13/145.28 MiB**. See `audits/stage1-server-evidence-repair.md` for counts, per-run noise, NMT, historical arithmetic, hard blockers and reproduction. `metrics/stage1-core-v2-provenance.json` hashes the executed uncommitted source and measured files; raw `harness_git_commit` refers to PM base, **not** the new source commit. The following is a fresh-output reproducibility example:

```bash
python3 scripts/benchmark_tsc_v2.py --jar /path/to/verified-official-release.jar \
  --jdk /path/to/jdk21 --runs 3 --warmup-seconds 30 --samples 120 \
  --pacing-ms 50 --out .audit-cache/recheck-v2.csv \
  --raw .audit-cache/recheck-v2.json
```

Fabric profile creation (no game execution or EULA acceptance) is provided by `scripts/create_isolated_fabric_fixture.py` and `scripts/provision_isolated_fabric.py`. Both paired profiles reach the EULA gate; real moving-train scenes S1-S4, measured MSPT/TPS, causal MTR-on/off attribution, game tick allocation, and client frame rates remain **NOT MEASURED**.


**Public-data minimization:** V2 summary rows and source hashes are published. The multi-megabyte raw V2 process trace is intentionally withheld from this public snapshot. The older V1 raw synthetic series is retained because the published unit test independently recomputes its historical summary. No world data, fixture seed, installed-mod inventory or machine log is published.
