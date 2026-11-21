# Stage 1 measurements | isolated released Transport Simulation Core

**Run date:** 2026-11-19 UTC. **Artifact:** MTR Fabric 4.1.0-beta.2+1.21.1; SHA-256 `5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94`. The independently verified official release JAR, not upstream HEAD, was loaded via Java 21. **Reference harness commit:** `8b01dbf31582eb3b4aaffcfc8da0e05bacb735b4`.

## Scope and repeatability

Hardware: Linux x86_64, Intel Core i7-10700F (8 physical/16 logical CPUs), ~31 GiB installed RAM. Java test-process limits: `-Xms128m -Xmx512m -XX:ActiveProcessorCount=2`. The shared workstation had background load, so these are baseline observations, **not uncontaminated machine performance**. Each scenario used **three independent Java processes**, each with **12 warmup calls and 40 measured TSC `Simulator.tick()` calls**, with a nominal one-second synthetic clock advance before each measured call. Each creates deterministic rails in a unique scratch directory and verifies a fresh core instance can reload the resulting **rail count** after a MessagePack save. There are no players, route service or moving trains, and no Minecraft server is launched. The test is intentionally low-risk, not a reproduction of the reported train-density problem.

| Synthetic core workload | TSC tick samples | Median TSC call (ms) | P95 (ms) | P99 (ms) | Median used heap (MiB)* | Median RSS (MiB)** | Median PSS (MiB)** |
|---|---:|---:|---:|---:|---:|---:|---:|
| S0 empty (0 rails) | 120 | 0.011685 | 0.029911 | 0.033664 | 4.86 | 66.36 | 63.43 |
| T1 rail topology (64 rails) | 120 | 0.043479 | 0.138011 | 0.173964 | 9.84 | 76.10 | 73.16 |
| T2 rail topology (512 rails) | 120 | 0.260449 | 0.382223 | 0.471665 | 25.21 | 174.35 | 171.43 |

\* Heap usage comprises three per-process snapshots measured after the tick loop and **before save/reload**. **Committed heap was 130.0 MiB** in each of these summary snapshots. Heap samples are not time-series percentiles.

\** RSS/PSS from Linux `/proc/<pid>/smaps_rollup` polling **after warmup**, pooled over runs (78, 87 and 111 observations respectively). These include JVM/shaded libraries and synthetic in-process state. RSS/PSS were measured **during benchmark execution**; no full-lifetime peak/idle comparisons or background-load controls were captured.

Main-thread allocation estimates from `com.sun.management.ThreadMXBean` were about **8,062**, **35,641** and **229,190 bytes per simulated TSC call** respectively (medians of per-run averages); background-thread allocation was **not measured**. The three runs in each scenario each recorded **zero GC collections** and **0 ms collection time** during measured calls; absence of GC in this short sample does not prove absence of GC pressure under realistic load. Direct-buffer memory was sampled separately, but **total native allocation and NMT categories were NOT MEASURED**.

## Per-run median TSC call times (ms)

| Workload | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| S0 empty | 0.0118 | 0.0117 | 0.0116 |
| T1 / 64 rails | 0.0435 | 0.0482 | 0.0428 |
| T2 / 512 rails | 0.2606 | 0.2608 | 0.2584 |

## Reproduce

From the GoldRail repository root, provide a **read-only copy of this same verified release JAR** and a local JDK 21 (`javac` included). The script rejects any SHA-256 mismatch, enforces synthetic rail counts, Java heap and run limits, uses an auto-cleaned local scratch root and never reaches the live server or world.

```bash
python3 scripts/benchmark_tsc.py --jar /path/to/verified-client-MTR.jar \
  --jdk /path/to/jdk-21 --runs 3 --warmup 12 --samples 40
python3 -m unittest discover -s tests -v
```

The executable harness, full raw tick samples and individual proc-memory samples are in `scripts/CoreSyntheticBenchmark.java`, `scripts/benchmark_tsc.py`, `metrics/stage1-raw.json` and `metrics/baseline.csv`. CSV rows have metric units, method, process repeat, artifact hash, warmup and sample counts. For one-off snapshots, p95/p99 are blank, not fabricated. `git_commit` in generated CSV is the executable **harness** commit, which intentionally predates this measurement/report commit.

## Explicit non-measurements and interpretation limits

- **Minecraft Fabric server:** MSPT/TPS, player counts, real client-server packet throughput and production memory attribution **NOT MEASURED**.
- **Actual moving-train load:** S1 isolated train, S2 routes, S3 train-dense scene, S4 multiple players **NOT MEASURED**. Our T1/T2 scenarios only add **static rails**; these are not substitutes.
- **Client FPS / render-thread timing:** median/p95/p99 frame times, 1% lows, graphics settings and shader-specific comparisons **NOT MEASURED**.
- **Memory:** native heap allocation by category, Java GC pause-duration distributions, NMT, peak process RSS/PSS and full heap allocation rate across threads **NOT MEASURED**; a direct-buffer snapshot does not capture all native memory.
- **Compatibility:** 0/64/512 synthetic rail save/reload counts PASS narrowly, but exact schema equivalence, unknown-field retention, real packets, addons, renderer and world compatibility **NOT TESTED**.
- **Performance effect of Rust:** **NOT MEASURED**; no Rust JNI implementation exists in Stage 1. The result is a Java baseline, not an optimization claim.

**Stage 1 completion does not imply PM Gate G1 acceptance.** The source-to-binary exact commit and dynamically resolved TSC dependency remain unproven. Independent UI audit, Product Review challenge and PM decision remain future manual dispatch work.
