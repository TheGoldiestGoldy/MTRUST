# GoldRail assignment 22 | Client contract, visible gameplay and safe renderer improvements

Role: UI/Client Agent. Work in explicitly assigned W1, W2 or W3. Do not start until previous PM gate is approved. Isolated PollyMC root only, never the ordinary launcher configuration.

## Read first

AGENTS.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, docs/ARCHITECTURE.md, docs/ALPHA_READINESS.md, docs/COMPATIBILITY.md, docs/ALPHA_READINESS.md, audits/ui-renderer-map.md, audits/ui-compatibility.md, audits/ui-optimization-plan.md, audits/ui-alpha-lab-results.md and the versioned client/server protocol contract.

## Owned surface

Client-side Fabric adapter, rendering and controls under an agreed client/ subtree; client-facing packet compatibility tests, UI screenshots/tests and handoffs/ui-runtime-<wave>.md. No Rust simulation code, JNI ABI, service/world fixtures, server registry/packet implementation or common protocol schema edits. No unlicensed model/font/texture redistribution. A debug-only upstream-original dependency for reference tests is separate from GoldRail's shipping artifacts.

## W1 | Contract-only compatibility investigations

Use released MTR bytecode and the golden packet/operation contract to map expected server messages, client position updates, camera, door, boarding, driving and shader state. Produce independent contract fixtures and tests that can later run against GoldRail. Do NOT redesign UI, implement speculative renderer optimizations, or declare parity from static method presence. If an envelope is unknown, provide bytecode or isolated original-client evidence and mark UNKNOWN.

W1 exit: versioned client-facing contract assertions and negative cases, documented API restrictions, no claims of functional gameplay.

## W2 | GoldRail-only playable train

After PM G2, implement only the required client-facing subset: train model/animation position updates, visible car and interior, station signs if the scenario needs them, doors, boarding/camera, start/stop UI/driving controls, and actual server packet sync. Keep familiar MTR controls in behavior where verified; a prettier mockup does not count. Original MTR must be removed from GoldRail-only client profile; no duplicate renderer registrations. Validate latency/reconnect, wrong protocol versions, missing resources and camera face/away while a train moves.

Use original assets only after license and redistribution rights are documented; otherwise provide clean-room/authorized test visuals and disclose visual-parity limits. No native Rust drawing from Fabric client.

W2 exit: real client starts in isolated PollyMC, connects safely to isolated GoldRail server, visible moving/boardable/controllable train and recorded scripted manual test. If client can only render a static train, report NOT A2.

## W3 | Profiled client performance

Only after PM G3 and real captures. Use the W0 reference and A2 frozen scene with same resolution, render distance, renderer/shader versions, camera and motion states. Pick one measured bottleneck such as culling or buffer churn; implement minimally with correct interiors, transparencies, signs, moving textures, shader passes and addons. Three repeat captures before/after; show p50/p95/p99 frame times and 1%-low FPS, resource lifecycle and no visual regressions. CPU scopes are not GPU timing. Keep optimization changes separate so integrator can bisect.

## Handoff

Commit role source/tests and handoffs/ui-runtime-<wave>.md with branch/SHA, capture provenance, measured or NOT MEASURED performance, executable tests, screenshots descriptions and explicit compatibility labels. Test only sandbox profiles; never merge or publish.
