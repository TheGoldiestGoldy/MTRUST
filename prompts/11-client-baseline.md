# GoldRail assignment 11 | Isolated PollyMC baseline and frame evidence

Role: UI performance specialist. Assigned wave: **W0 only**. Base commit and branch pinned by PM. Coordinate with fixture owner before running game workloads.

## Read first

AGENTS.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, docs/ALPHA_READINESS.md, docs/BENCHMARKS.md, audits/ui-alpha-lab-results.md, audits/ui-performance.md, audits/ui-renderer-map.md, audits/ui-compatibility.md, audits/source-lock.md. Inspect scripts/ui_frame_stats.py, scripts/prepare_pollymc_client.py and the PM-supplied reviewed private-network runner (not part of this public snapshot).

## Facts to respect

The actual launcher is PollyMC-Continued, not Prism. The *independent* PollyMC root previously reached Minecraft render/resource loading with the verified original MTR 4.1.0-beta.2 on Java21/Fabric1.21.1. No real menu/in-world train proof, paired connection, whole-frame traces or frame percentiles have been captured. Do not claim otherwise. Existing ordinary PollyMC profiles, accounts, shaders, saves and installed mods are out of bounds.

## Ownership

Client trace acquisition scripts and tests (new ui_capture_ files), metrics/ui-a0-*.csv or machine-independent summarized CSV, audits/ui-w0-client-evidence.md and handoffs/ui-baseline-w0.md. You may adjust scripts/ui_frame_stats.py only with new negative tests. No modification of server fixture generator, protocol, original renderer or shared docs. Put large raw data, screenshots and sensitive logs in ignored .audit-cache/agents/w0-ui.

## Assignment

1. Verify actual isolated PollyMC launcher/game files and capture hash from source-lock. If the lab uses an installed launcher executable, it must always pass the independent --dir root; never use the regular PollyMC wrapper. Confirm menu/in-world rendering visually if possible, and record truthfully when only logs show startup.
2. Select an actual trustworthy whole-frame timing producer, verify its units and monotonic timestamps by a known live sample; do NOT pass CPU render-thread timing, GPU event duration or FPS-average values as whole-frame timestamps. Preserve version, resolution, driver and capture method metadata.
3. Complete S0 original MTR and no-MTR reference profile baseline **without** claiming train-density results. Do not start an untrusted Internet-facing HTTP server or let an unisolated client reach the synthetic offline-mode test world.
4. Wait for the fixture agent's immutable manifest and evidence of real trains. Then, in the same network namespace and controlled settings, measure S1 (one moving train), S2 (several), S3 (dense), facing/away, shaders off/on where present. Three independent runs per valid comparison with 30s warmup and >=120s whole-frame trace; lock client resolution, settings, camera and renderer version. If shader assets or client access are missing, mark blocked instead of copying settings/tokens from production.
5. Analyze traces with scripts/ui_frame_stats.py. Report actual frame time median/p95/p99 and 1% low with raw metadata, CPU vs GPU ambiguity, variability and failure modes. If capture producer timestamps are incompatible, repair acquisition and re-verify before claiming numbers.
6. Propose top renderer bottlenecks only where measured and establish an untouched reference for later W3 tests. Do not redesign UI or modify renderer in W0.

## Acceptance and stopping

Pass: isolated client joined a generated MTR scene; real, metadata-backed whole-frame captures analyzed and independently repeatable. If user sign-in or specific safe connectivity is blocked, document precise owner-only step and tests that DID pass. Scripts syntax/unit tests and git diff --check required. Commit only owned files, write handoffs/ui-baseline-w0.md with actual branch/SHA and test results, stop for integrator + independent Product Review. **Do not begin W1 or make FPS improvement claims.**
