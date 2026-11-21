# Stage 1 decision note | minimal Rust JNI proof-of-concept design (NO Stage 2 code)

**Status:** design only; no Rust JNI implementation, new Fabric JAR, native binary, source replacement, world migration or server deployment authorized in Stage 1.

## Problem boundary

Minecraft + Fabric requires a JVM shell. The released beta already contains a standalone TSC that accepts bounded `QueueObject` requests and ticks per dimension. A Rust engine may eventually replace one *authoritative* TSC simulation owner per dimension, not the Minecraft registries/client renderer. Native RSS adds to heap; avoiding Java allocations may or may not reduce *total* memory.

## Proposed first narrow experiment (subject to PM G1)

- Java 21 Fabric façade owns mod registration, existing block/item IDs, `mtr` packet record types, renderer, addon APIs and startup lifecycle.
- Test-profile Rust library `libgoldrail_ffi.so` is packaged with checksums and versioned JNI exports. No download at runtime.
- Versioned protocol `major.minor` negotiates startup. A mismatched major version must fail startup; do not enable a half-active Rust simulator.
- JNI calls are **batched per tick/dimension**, never per model vertex or entity substep. Suggested functions `createEngine(configBytes, protocolVersion) -> handle`, `submitBatch(handle, orderedCommandBytes)`, `tick(handle, clockMillis) -> snapshotBytes`, `drainEvents(handle) -> eventBytes`, `closeEngine(handle)`. These are *proposed*, not existing APIs.
- Java thread enqueues C2S requests into bounded queue with stable ordering and sequence numbers. Rust runs on a single owner thread per dimension. S2C callbacks return on the correct Minecraft server thread. Native code does not touch Minecraft objects or JNIEnv after crossing an invalid thread boundary.
- Rust state IDs and snapshots preserve MTR IDs, dimensions, ordering, packet operation keys, unknown fields and serialization semantics. Java retains the network envelope until wire-level differential tests pass.
- Start with a **tiny deterministic subset**: create/lookup synthetic rails, single step, serialize snapshot and compare with Java TSC on identical recorded synthetic operations, independent clock and seeded RNG. Test null/invalid handles, bounds, buffer ownership, unwinds/panics, concurrency and restart failure.
- Require measurements vs *two* controls: shipped Java TSC and reasonably optimized Java implementation, under same input/topology. Report heap, **native allocation and total RSS/PSS**, JNI boundary cost, TSC step latency and client outcomes separately. Only promote if memory or CPU gain beats variance and compatibility passes.
- Keep saves read-only in first POC. No live-world files are ever used; synthetic round-trip and unknown-field tests must precede write support. Verify atomic temp+fsync+rename semantics and backups before migration.
- No automatic fail-open fallback mid-tick: choose Java or Rust engine at startup, restart on failures using backed-up safe state. Shadow comparator can replay clones but must never mutate production.

## Stop/go gates

**G1 remains closed:** exact source-to-binary map and runtime TSC coordinate unproven, active-train S1-S4 reference loads not generated, Fabric MSPT/FPS and JNI-vs-Java performance unmeasured, addon tests absent. Product Review and PM must approve evidence before starting any Stage 2 implementation.

## Reference-only alternate code

YanYang community fork reportedly builds on MTR 4.0.5; its 1.21.x mapping support is not a verified replacement for MTR 4.1.0-beta.2+1.21.1. No fork code included. License and asset provenance would require their own review even for isolated reuse.
