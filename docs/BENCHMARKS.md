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
