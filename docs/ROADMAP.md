# Roadmap and mandatory gates

All work is sequential, not three agents running at once. Each stage runs Coding -> UI -> Product Review -> PM gate. No automatic merge.

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

Read `docs/DISPATCH.md`. Start only `prompts/01-coding-audit.md`. UI waits for the Coding file/class map; Product Review waits for both audits.
