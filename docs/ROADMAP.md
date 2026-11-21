# Roadmap and mandatory gates

**Gates remain sequential (G1 through G5)**. After the 2026-11-20 PM concurrency revision, independent coding, UI and provenance tasks **within** an approved wave may run in parallel in different Git worktrees. A single integrator assembles completed work, an independent Product Reviewer challenges it, and PM alone decides the next gate. See docs/ROAD_TO_FINISH.md and docs/PARALLEL_AGENT_PROTOCOL.md. No automatic merge.

| Stage | Coding goal | UI goal | Product Review gate |
|---|---|---|---|
| 1 | Pin beta binary/source; inventory architecture; reproducible synthetic baseline | Inventory renderer/UI and client bottlenecks using Coding's class map | G1: evidence, metric validity and compatibility risks accepted |
| 2 | Deterministic Rust JNI proof of concept with protocol and replay | Define stable UI/client message expectations | G2: replay parity, JNI safety, measurable case for Rust |
| 3 | Full test-profile Fabric integration with compatible packets/data/API | Preserve original controls, shaders and trains | G3: integration and compatibility PASS/PARTIAL/FAIL |
| 4 | Optimize proven server hot spots and memory | Profile/optimize culling, meshes, frame timing | G4: repeatable RAM/MSPT and FPS wins without quality loss |
| 5 | Reproducible signed/checksummed release, canary, rollback docs | End-to-end UX parity and regression report | G5: complete signoff before any production consideration |

## Release thresholds

No invented fixed performance percentage. Measure repeatable baseline first; define thresholds only after distribution and variability are known. Must preserve user-visible parity and save compatibility. Distinguish reductions in Java heap from changes in native memory and total process RSS/PSS.

## Source lock

Target is MTR 4.1.0-beta.2+1.21.1, not upstream master. Keep exact artifact SHA-256, release source tag, TSC dependency coordinates and commit refs in `audits/source-lock.md`.

## Dispatch

For the current work, use docs/ROAD_TO_FINISH.md and docs/PARALLEL_AGENT_PROTOCOL.md plus prompts/10-reference-fixture.md, 11-client-baseline.md and 12-provenance-oracles.md. The Stage 1 original audit prompts are preserved as historical dispatch. **G1 is closed** and the W1 Rust implementation cannot start until independent review and PM approve it.

## First runnable alpha milestones

See `docs/ALPHA_READINESS.md` for acceptance tests and the distinction between original-MTR reference sandbox (A0), Rust JNI developer preview (A1), first *playable GoldRail* test-only alpha (A2, target after Stage 3), and independently measured optimized alpha (A3, Stage 4). Existing G1-G5 review gates and production restrictions remain in force; there is no silent waiver for an earlier demo.
