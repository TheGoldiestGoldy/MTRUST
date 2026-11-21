# GoldRail

A proposed compatible replacement for Minecraft Transit Railway 4.1.0-beta.2 on Minecraft 1.21.1 / Fabric / Java 21, with an optional Rust simulation engine only if controlled measurements justify it.

## Verified project state - 2026-11-21

- Stage 1 binary, architecture, compatibility and performance audits are complete as research handoffs.
- The Coding Agent repaired the standalone Java-core measurement harness. These are synthetic internal TSC measurements, not Minecraft server MSPT.
- The isolated A0 reference lab booted original-MTR and no-MTR Fabric servers and initialized a separate PollyMC client. No moving-train gameplay or valid client frame capture has been demonstrated.
- Independent Product Review rejected G1. **G1 remains CLOSED.**
- No Rust/JNI engine, GoldRail replacement Fabric JAR, playable A2 alpha, or measured Rust-vs-Java improvement exists.
- The local full Python suite passed 39/39 tests on 2026-11-21. This validates helper and safety tests, not gameplay or compatibility.

## Non-negotiable boundaries

- Never modify a production server, world, installed mod, ordinary launcher profile, or unrelated server-operations repository.
- Use newly generated isolated test data only. Never publish private seeds, account data, local paths, machine addresses, logs, or world files.
- Do not infer train performance from static rail-count microbenchmarks or empty-world server queries.
- Keep Java heap, native memory, process RSS/PSS, server MSPT and client frame times separate.
- No merge, release, migration or deployment without independent Product Review and explicit PM approval.

## Read first

1. AGENTS.md
2. docs/ARCHITECTURE.md
3. docs/ROADMAP.md and docs/ROAD_TO_FINISH.md
4. docs/BENCHMARKS.md
5. docs/HANDOFFS.md
6. docs/COMPATIBILITY.md
7. docs/RELEASE_SAFETY.md
8. The exact assigned prompt in prompts/

The current authorized planning scope is W0 evidence completion only. See docs/START_HERE.md. W1 Rust/JNI work is blocked until independent review and an explicit PM G1 decision.
