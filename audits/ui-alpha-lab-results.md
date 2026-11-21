# Stage 1 UI A0 reference-lab results - 2026-11-19

**Scope:** original MTR reference lab only. This is not a GoldRail replacement or A2 alpha. G1 remains CLOSED.

## Verified execution

- Original MTR Fabric 4.1.0-beta.2+1.21.1 archive identity: SHA-256 5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94.
- Two newly generated Fabric 1.21.1 / Loader 0.18.4 server profiles, one with the exact MTR release and one without, reached the server-ready state, answered a tick query, stopped and saved generated flat worlds.
- The first host-bound MTR probe exposed a separate wildcard-bound HTTP service even though the Minecraft listener was loopback-only. That probe was stopped. Subsequent server tests ran inside a private network namespace; no new MTR HTTP listener was visible from the host namespace. Do not launch the MTR reference server directly on an ordinary host interface.
- A separate PollyMC-Continued client root launched Minecraft 1.21.1 with Fabric 0.18.4 and MTR 4.1.0-beta.2. Logs showed LWJGL backend initialization, resource reload and sound-engine startup. No menu screenshot, in-world gameplay, server join or moving train was verified.
- The client launcher and server launch wrappers used in the local lab are intentionally not included in this public snapshot. They require separate security review and a PM-supplied isolated runner.

## Exploratory server query - not a performance comparison

Each profile received one 100-tick vanilla query in a newly generated empty flat world. Both had zero trains, routes, rails, passengers and players.

| Profile | p50 / p95 / p99 query MSPT | One RSS/PSS snapshot (kB) |
|---|---:|---:|
| Original MTR | 0.2 / 0.3 / 0.8 ms | 899124 / 891380 |
| Fabric control | 0.1 / 0.1 / 2.9 ms | 985268 / 977133 |

These were single, unmatched runs on a busy host with different startup and GC phases. The vanilla tick-query output is not a raw per-tick trace. The memory values are not phase-matched. **Do not infer MTR overhead, a RAM reduction or a performance win from this table.**

## Explicit non-measurements

- Actual moving trains, routes, sidings, stations and passengers in a Fabric world: **NOT MEASURED**.
- Matched S0-S4 server MSPT/TPS, RSS/PSS and heap/GC comparisons: **NOT MEASURED**.
- Client frame-time median/p95/p99, 1%-low FPS, GPU timing, draw counts, VRAM and shader A/B: **NOT MEASURED**.
- Client-server joined gameplay, riding, controls, packet parity and GoldRail replacement: **NOT TESTED**.

The frame-time parser now rejects invalid, non-finite, duplicate, reversed and badly gapped timestamps and requires sufficient post-warmup samples. Its tests validate arithmetic and input handling, not real gameplay. See metrics/ui-baseline-v2.csv; every client scenario remains NOT MEASURED.

## Safety and compatibility

Only generated test profiles/worlds were used. No production world, installed mod, ordinary launcher profile, account credential or resource pack was copied. EULA acceptance was limited to the two already authorized isolated test profiles; it does not authorize new profiles. The test server's private network namespace and offline pairing configuration must never be copied to a public server.

The A0 lab proves limited startup feasibility only. It does not prove visual parity, add-on compatibility, save compatibility or GoldRail functionality.
