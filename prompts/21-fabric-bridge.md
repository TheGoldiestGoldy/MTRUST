# GoldRail assignment 21 | Fabric shell, JNI bridge, release packaging

Role: Java/Fabric + native-bridge Coding Agent. Execute assigned W1, W2 or W4 only. Start from PM-frozen base and contracts. Do not begin W1 while G1 is closed.

## Read first

AGENTS.md, docs/ARCHITECTURE.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, docs/COMPATIBILITY.md, docs/RELEASE_SAFETY.md, audits/source-lock.md, audits/jni-poc-design.md, released bytecode oracle, current golden/protocol schema and latest PM gate.

## Owned surface

GoldRail Fabric/Java shell (for example fabric/), Java JNI lifecycle code and native adapter/binding crate only (for example bridge/ or crates/goldrail_ffi), its role tests and handoffs/cod-bridge-<wave>.md. Rust domain/engine and UI rendering remain owned by other agents. Do not edit their manifests or shared documentation without integrator ownership. Keep build target Fabric 1.21.1 Java 21, Linux x86_64 first.

## W1 | One-operation Java/JNI developer preview

1. Agree with PM's frozen ABI and Rust Agent API: opaque handles, explicit ownership/release, protocol major/minor, bounded input/output buffers, deterministic operation and error mapping. If interface absent, build test-only stubs behind a clearly disabled test flag and report BLOCKED for real end-to-end parity.
2. Implement a test-only Java 21 JNI harness and native adapter, not a production MTR-replacement JAR. Validate classloader/native library lifetime, pointer ownership, invalid handles, repeated initialize/close, library missing, wrong major version, truncated/oversized payload, exception-to-error translation, multiple dimensions/restarts and shutdown. Every unsafe Rust boundary needs a documented invariant and safe wrapper.
3. Batch commands; bound native calls and memory copies. No JNI per vertex/car, duplicate live engine, or mid-tick fallback to a second simulator. Preserve packet schema isolation. Compare JNI overhead to plain Java baseline for same operation, not unlike workloads.
4. Test actual Java->JNI->Rust one-operation execution with oracle fixtures once Rust lane is integrated by prompt 99. Your local tests can use stub implementations but must never be labeled integration PASS.

W1 exit: buildable bridge, lifecycle and negative tests, explicit JNI ABI contract and reproducible commands. Integrator demonstrates true Rust + Java link for G2.

## W2 | GoldRail-only Fabric mod and client/server packet wiring

Only after PM G2. Register blocks/items/entities/network IDs and addon facades for the approved A2 subset; verify ID collision strategy with original MTR and exact original archive contracts. Select only ONE simulation authority per dimension, enqueue ordered bounded messages off Minecraft threads, and send versioned snapshots without blocking main/render threads. Package standalone GoldRail Fabric test JAR and load it with **original MTR removed from the GoldRail-only profile**. Test failures for missing Rust library, version mismatch, absent renderer, network disconnect and restart without private save access. Never claim all addons/shaders work from class names alone.

W2 exit: source + build steps for a real test JAR; packet and lifecycle integration tests; explicit unsupported registration surfaces. Integrator runs the client-server and ride test.

## W4 | Deterministic test-release build

Only after PM G4. Build from clean checkout with dependency lockfiles, version/source hashes and reproducible artifact checksums. Verify the Linux .so and JAR loader, no runtime executable downloads, clear unsupported platform diagnostics, package signatures/checksums and synthetic rollback instructions. Do not redistribute nested assets with unresolved rights. Add a build manifest, SBOM inputs and explicit versions. Product Review/PM decide distribution.

## Handoff

Record pinned wave base, exact branch/SHA, protocol/ABI, script and test commands + outputs, what real JNI/Fabric run was proven (vs stub), known failures, artifact hashes and license uncertainty. Commit handoffs/cod-bridge-<wave>.md. Stop for integration; no merges/pushes/releases/production access.
