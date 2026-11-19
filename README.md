# MTRUST (GoldRail)

A performance-focused, compatible replacement for Minecraft Transit Railway 4.1.0-beta.2 on Minecraft 1.21.1 / Fabric / Java 21, with a **Rust native simulation engine only where measurements justify one**.

## Project state

**Stage 1: source, compatibility and performance audit.** No Rust rewrite is approved yet. No benchmark improvement has been measured. This public repository contains sanitized planning documents and development tools. **There is no functional Rust replacement, release JAR or measured performance improvement yet.**

The existing MTR v4 JAR contains the Java Transport Simulation Core. Fabric/JVM classes must remain for mod registration, networking, renderer and addon compatibility. The intended Rust component is a versioned, bounded JNI implementation after source parity and a baseline are established.

## Hard safety boundaries

- Never mutate the running server, production worlds, installed production JARs or public `goldcraft-server-ops`.
- Only use synthetic isolated test worlds for replay/benchmarks.
- Never publish tokens, IP addresses, raw world data, seeds, private files, personal usernames or identifying paths.
- No world migration or production mod switch without review.
- Work on isolated branches and PRs; PM and Product Review jointly gate merges/releases.

## Read before working

1. `AGENTS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/ROADMAP.md`
4. `docs/BENCHMARKS.md`
5. `docs/HANDOFFS.md`
6. `docs/COMPATIBILITY.md`
7. `docs/RELEASE_SAFETY.md`
8. Assigned role prompt in `prompts/`

The PM dispatches **Coding Stage 1 first**, then UI audit, then independent Product Review. The in-progress Coding audit is kept in a separate branch until reviewed. See `docs/DISPATCH.md`.

## Ground truths

- Target Java: 21; Linux x86_64; Fabric 1.21.1.
- Target upstream mod: MTR 4.1.0-beta.2; exact source tag/commit must be pinned to the installed JAR.
- Rust is not itself a Fabric mod. Final delivery, if justified, is a Fabric/Java JAR with optional native engine.
- Server RAM and client FPS are distinct outcomes. Both need baselines.
- Installed assets and third-party libraries must retain their own license obligations.

## Current owners

PM: project scope, dependencies, merge gates. Coding: exact-source audit and later engine work. UI: client rendering audit and parity. Product Review: independent evidence and regression check.

Status: **AUDIT STARTED; no replacement, no stage gate approved.**
