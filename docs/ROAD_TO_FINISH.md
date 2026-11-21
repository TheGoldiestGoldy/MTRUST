# GoldRail | Road to first playable alpha and release

Status snapshot: 2026-11-21. Planning base: ui/stage1-alpha-lab@d29eaa4. This is a proposed dispatch plan, not authorization to skip a gate.

## Product definition and current evidence

Target: Minecraft 1.21.1, Fabric, Java 21, Linux x86_64 first. GoldRail is a Fabric/Java mod with an optional Rust native engine. A standalone Rust binary is not a Fabric mod. Preserve verified original MTR 4.1.0-beta.2 behavior and existing world data; do not claim compatibility that has not been demonstrated.

- A0: original MTR in an entirely separate PollyMC and Fabric sandbox. Original MTR and control servers booted and saved synthetic flat worlds. The independent PollyMC JVM entered Minecraft/render loading. No visually verified train ride, actual train-dense server data, or real frame traces.
- G1: CLOSED after independent Stage 1 FAIL. Better synthetic Java-core timing exists, but real moving-train MSPT/RSS/FPS attribution and semantic golden fixtures are missing. Exact source-to-release/TSC lock remains unresolved.
- A1: Rust/JNI developer preview, NOT STARTED. It is not playable.
- A2: one playable line with stations, depot/siding, a moving/boardable train, doors, controls, packets and restartable test data using a GoldRail-only test JAR, NOT STARTED.
- A3: objectively faster and/or lower-memory alpha on matched runs, NOT STARTED.
- G5: release-grade package and rollback, NOT STARTED.

The verified original release SHA-256 is 5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94. Official binary identity is known; binary-source equivalence is not. See audits/source-lock.md and docs/ALPHA_READINESS.md.

## Dependency road map

~~~text
W0  Original reference fixture + released oracle + client capture preparation
       -> independent review -> PM G1
W1  Rust protocol/engine + Java/JNI bridge + client packet contract
       -> integration and differential replay -> independent review -> PM G2 (A1)
W2  Fabric replacement shell + Rust service/persistence + client UI/runtime
    + isolated gameplay QA
       -> one integration agent builds and runs GoldRail-only lab
       -> independent review -> PM G3 (A2, first playable alpha)
W3  Profiled server improvements + renderer improvements + compatibility matrix
       -> integration, matched A/B measurements -> review -> PM G4 (A3)
W4  Reproducible packaging, legal notices, rollback, supported-platform matrix
       -> final integration/test agent -> independent review -> PM G5
       -> optional canary and separately approved production deployment
~~~

The stages and gate decisions are sequential. Independent subtasks **within** a stage may run simultaneously. G1/G2/G3/G4/G5 are actual stop gates, not decoration. A lower-scope mock/demo can be shipped as a developer preview, but must not be called A2.

## Wave 0: establish real reference evidence (dispatch now)

Parallel lane F, Coding: prompts/10-reference-fixture.md. Build a replayable actual original-MTR rail, platform, route, depot/siding and moving train in newly generated isolated worlds. Start with one train; expand to several and dense train scenarios only if safe. Collect independently verified train counts and whole-server measurements against a controlled no-MTR case. Owns synthetic server fixture scripts and world generation only.

Parallel lane P, Coding/research: prompts/12-provenance-oracles.md. Lock and document released bytecode behavior (operation, packet and saved payloads), provenance and rights; no claims about unproven upstream source. Owns oracle/contract tests and compliance evidence, not fixture generation.

Parallel lane U, UI: prompts/11-client-baseline.md. Validate PollyMC-only lab, capture producer and 0-train baseline now; coordinate read-only access to lane F's completed immutable moving-train fixture before actual train-dense captures. Owns capture and client metrics only. Do not start two concurrent game runs using the same profile.

Integration: prompts/99-integrator.md in W0 mode, only after all available lanes report and the fixture is frozen. Independent review: prompts/90-product-review.md. PM adjudicates G1. A partial/blocked result does not authorize W1.

## Wave 1: bounded Rust proof of concept (dispatch only after G1 approval)

Before branching, PM freezes a versioned protocol schema, golden fixture format and golden input/output examples from W0. If these are still missing, do not start concurrent coding.

- Rust lane: prompts/20-rust-core.md, owns crates and deterministic state transitions without Minecraft-specific APIs.
- Bridge lane: prompts/21-fabric-bridge.md, owns Java JNI boundary, Rust ABI adapter and bounded lifecycle, but not Rust simulation logic.
- UI/contract lane: prompts/22-client-runtime.md in contract-only mode, owns packet/UI compatibility assertions and client evidence, not production renderer edits.
- Integrator: prompts/99-integrator.md in W1 mode. Verify real JNI launch, replay parity, invalid inputs, crashes, shutdown/restart, Java-only baseline comparisons. Product Review and PM decide G2. Reject if the supposedly faster Rust path only moves memory outside the heap or silently changes behavior.

## Wave 2: first playable replacement (dispatch only after G2 approval)

Freeze mod IDs/registries, bridge versions, save schema, packet contracts and an isolated fixture interface. Never place original MTR and GoldRail together in one running profile unless an approved test explicitly needs it without conflicting registration.

- Rust lane (same prompt 20, W2 mode): implement the minimal timetable/rail/service/vehicle/persistence subset with bytecode-oracle tests; preserve unrecognized test fields or fail closed.
- Fabric bridge lane (same prompt 21, W2 mode): build GoldRail-only Fabric JAR with compatible registrations, network events and one authoritative simulator; disable unsafe mixed-engine fallback.
- UI lane (same prompt 22, W2 mode): wire actual controls, rendering and train movement for the accepted subset; no cosmetic redesign or premature FPS optimization.
- QA lane (prompt 10, W2 mode): generate new GoldRail-only world, gameplay cases and proof of restart; no writes to production saves.
- Integrator: prompt 99 W2 mode. Must personally compile the exact combined tree and drive a visual/client-server smoke with the one train line. Review + PM G3 decide whether it is A2.

## Wave 3: verify optimization (dispatch after A2 and G3)

No optimizing based solely on static suspicion. Rank candidates from actual profiles and freeze a common A/B benchmark scene.

- Server/Rust lane (prompt 20, W3 mode): improve identified allocation, topology, route or memory hot spots and measure RSS/PSS/MSPT independently from heap.
- UI lane (prompt 22, W3 mode): implement one safe renderer improvement at a time and test camera face/away, shader on/off, transparencies, interiors and addons.
- QA lane (prompt 10, W3 mode): independent matched baseline and GoldRail three-run distributions, cold/warm, no cherry-picked best case.
- Integrator + Review + PM G4: prove regression-free improvement in one or more declared metrics. No invented percentage target.

## Wave 4: supportable test release (after G4)

- Bridge/packaging lane (prompt 21, W4 mode): deterministic release build, native loader diagnostics, JAR/native checksums, no runtime downloads, supported-platform matrix and dependencies.
- Provenance lane (prompt 12, W4 mode): license audit, attribution, redistributable assets policy, SBOM and provenance gaps disclosed.
- QA lane (prompt 10, W4 mode): independent clean-install/canary/rollback, corruption recovery, backups, addon and shader compatibility matrix with NOT TESTED where appropriate.
- Integrator + independent Product Review + PM G5: reproduce clean build and tests, publish only from approved artifacts. Production remains a separate explicit owner decision.

## Mandatory G1-G5 exit criteria

| Gate | Exact evidence required | Cannot substitute |
| --- | --- | --- |
| G1 | Actual reference moving-train lab, reproducible server + client real measurements, release behavioral oracle, clear source uncertainty and Java alternative considered | Empty-world tick query, count-only rail core tests, source candidate hash |
| G2 | Compiled Rust/JNI developer preview; deterministic input/output golden differential; safe ABI, ownership, version mismatch, restart and failure tests; Rust vs Java baseline | Rust-only toy crate or untested JNI code |
| G3 / A2 | GoldRail-only Fabric JAR and isolated PollyMC/client; live moving/boardable train, controls, doors, packet, save/reload, repeatable launcher and rollback; reviewer + PM signoff | Original MTR sandbox or visual mockup |
| G4 / A3 | Same workloads and settings, multi-run p50/p95/p99 + RSS/PSS/MSPT and FPS/frame-time comparisons, regressions checked | Unmatched runs, heap-only comparisons |
| G5 | Reproducible checksummed package, rights documented, supported matrix, safety/backup/rollback drill, independent signoff | A successful local compile |

## Operational finish-line checklist

- [ ] W0 reference: one real active MTR train, multi-train scene, matched controls and genuine client frame traces.
- [ ] W0 independent review and PM G1 APPROVED.
- [ ] W1 Rust engine + JNI bridge + golden parity integrated and PM G2 APPROVED.
- [ ] W2 test-only GoldRail-only replacement, one actual ride and save/restart confirmed, PM G3 APPROVED (A2).
- [ ] W3 matched server/client performance improvements and PM G4 APPROVED (A3).
- [ ] W4 reproducible package, supported compatibility and rollback, PM G5 APPROVED.
- [ ] Optional separate canary authorization and explicit production approval. Never automatic.

Dispatch and branch rules: docs/PARALLEL_AGENT_PROTOCOL.md. Agent-specific tasks: prompts/10-*, 11-*, 12-*, 20-*, 21-*, 22-*, 90-*, 99-*. The integration agent runs after each wave, not at the same time as writers. This document supersedes the old single-agent dispatch cadence **only for independent work within a stage** and never supersedes stop gates or safety rules.


**Pinned PM planning base:** pm/parallel-road-to-finish@18f4c2838577a1ff701ae870b59b5a339d21ee18. W0 workers have not yet delivered branches; this plan is not evidence that W0 has started. G1 remains CLOSED.
