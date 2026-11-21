# GoldRail alpha readiness

This document distinguishes the original-MTR reference lab from an actual GoldRail replacement.

| Milestone | What it means | Verified status |
|---|---|---|
| A0 reference sandbox | Original MTR in isolated Fabric 1.21.1 server/client profiles | **PARTIAL**: two isolated servers (MTR and control) booted and saved generated flat worlds. A separate PollyMC client initialized Minecraft/Fabric/MTR and renderer resources. No in-world train gameplay or client frame capture is verified. |
| A1 engine developer preview | Narrow Rust/JNI operation with released-bytecode golden replay | **NOT STARTED**. G1 is CLOSED. |
| A2 first playable GoldRail alpha | GoldRail-only Fabric test JAR with one working line, platform, depot/siding and a moving, boardable train | **NOT STARTED**. |
| A3 optimized alpha | Same workload with repeatably lower total RSS/PSS or MSPT and/or client frame time | **NOT STARTED**. |

## A2 acceptance

- A standalone GoldRail Fabric 1.21.1 test JAR runs on Java 21 with original MTR removed from the isolated GoldRail profile.
- One deterministic generated line, platform, route, siding/depot and visibly moving train work.
- Client joins, sees the train, boards/rides it, operates doors and controls, and receives correct position updates.
- Supported synthetic state survives stop/restart without corrupting data. Unknown or unsupported fields fail safely; no production saves are used.
- A repeatable isolated startup/test/rollback procedure and exact artifact/fixture hashes are recorded.
- Independent Product Review and explicit PM G3 approval are recorded.

A build or static test alone is not A2. A static train model is not a moving train. A reference MTR client is not GoldRail.

## Current blockers

1. No deterministic, independently verified moving-train Fabric fixture.
2. No matched original-MTR train-loaded server MSPT/RSS/PSS measurements.
3. No valid client frame-time, GPU-time or 1%-low capture.
4. Exact MTR source and embedded TSC dependency provenance remains unresolved; released-bytecode oracle work is partial.
5. Save unknown-field, packet, addon, shader and visual parity remain untested.
6. No Rust/JNI implementation or Java-optimized counterfactual exists.

EULA acceptance and runtime launches apply only to individually authorized, isolated test profiles. Never copy production worlds, launcher credentials or private data into a test profile.
