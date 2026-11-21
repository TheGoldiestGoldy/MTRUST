# GoldRail assignment 10 | Reference fixture and isolated QA

Role: Coding / test-fixture specialist. Work in one explicitly assigned wave: W0, W2, W3 or W4. **Do not** execute later-wave tasks early. Base commit and branch must be given by PM; do not use another agent's mutable worktree.

## Read first

AGENTS.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, docs/ALPHA_READINESS.md, docs/ALPHA_READINESS.md, docs/BENCHMARKS.md, docs/RELEASE_SAFETY.md, audits/ui-alpha-lab-results.md, audits/stage1-server-evidence-repair.md, audits/source-lock.md, and latest role handoffs. Inspect actual scripts before changing anything.

## Ownership

You own scripts and tests for generated in-world scenarios (new filenames should begin fixture_ or qa_), immutable scenario manifests, sanitized isolated server metrics, and handoffs/cod-fixture-<wave>.md. No edits to Rust domain crates, packet protocol, client capture tool, upstream original source or shared PM docs. Do not overwrite historical baselines. All world archives/binaries stay ignored in .audit-cache/agents/<wave>-fixture.

## W0 | Get one *real* original-MTR moving train, then density variants

1. Verify the exact original MTR JAR SHA-256 from audits/source-lock.md and Minecraft 1.21.1 / Fabric / Java21. Inspect verified bytecode/API or in-world behavior before inventing generators. Existing original MTR/no-MTR isolated servers boot, but generate no actual trains.
2. Use existing specifically authorized isolated lab only within its existing authorization, or stage NEW profiles with eula=false and request owner action before first launch. Every server and client connection must stay inside a private network namespace. The original MTR HTTP listener on wildcard port 8889 is **not** contained by a Minecraft loopback-only server.properties; never direct-launch it on the host.
3. Build a deterministic synthetic in-world fixture: verified station, platform, rail, siding/depot, route and at least one actually moving, scheduled vehicle. Prefer public upstream registries/commands with controlled test-only world generation. A core-only Java Rail object does not count as an in-world train.
4. Export a versioned scenario manifest: exact generated seed, rail/route/station IDs only if synthetic, expected train count, mod hashes, chunk/camera reference and fixture creation commands; verify train presence independently from a stable API/log plus in-game observation as available. No real server map or private coordinates.
5. Export S0 same rails zero running trains, S1 one, S2 several and S3 dense (if feasible); run stable restarts and count reloads. Only claim scenarios actually observed. Capture full Fabric tick samples or reproducible tick query with honest limitations, whole-process time-aligned RSS/PSS, GC and MSPT on matched original-MTR/no-MTR controls; at least three independent repeat runs for comparative claims. Note empty-world tick query cannot attribute overhead.
6. Hand the frozen fixture location + manifest/hash to UI lane. Do not edit it afterward. If there is no reliable programmatic generator, write an exact manual-build-and-export procedure and reproducibility blocker. Never fabricate a PASS.

W0 exit: one actual moving original-MTR in isolated Fabric lab and sufficient evidence to establish reproducibility; otherwise explicit BLOCKED, with the narrow reason and logs. Real multi-train FPS requires UI lane and is not your claim.

## W2 | GoldRail-only playable QA

Only after PM G2. Produce GoldRail-only generated world with one station pair/loop, siding/depot, train and boardable platform, doors, stop/start and route, then game save/stop/restart; verify no duplicate original MTR provider. Write automated smoke assertions plus a concise manual riding script. Capture packet, persistence and lifecycle failures; do not patch the simulation to make tests pass. Give integrator fixture manifest and failure examples.

## W3 | Measured regression

Only after PM G3. Reproduce equivalent original-MTR and GoldRail scenes without shared world migration. Collect per-process independently repeated RSS/PSS, MSPT p50/p95/p99, allocation/GC and known-comparable client work; explicitly note unmatched gameplay features. Preserve raw recordings and do not assert success from a single best-case run.

## W4 | Release QA

Only after PM G4. Verify clean install, pinned dependencies, unsupported architecture error handling, corrupted synthetic save handling, restart, canary and **sandbox-only** rollback. Matrix: original saved fields, packets, addons, Iris/Sodium/shaders, server+client platforms. Mark untested cases NOT TESTED.

## Required tests and handoff

Run unit tests, Python syntax, scenario generator dry runs, actual relevant server if authorized, and git diff --check; include every exit status. Record all new world data only in ignored caches. Commit role-owned scripts/tests and handoffs/cod-fixture-<wave>.md on your branch. Include exact base SHA, final SHA, manifest hash, observed vs not-measured numbers, and stop for integration. Never merge, push or deploy.
