# GoldRail reference architecture (Architecture Decision Record 0001)

## Product and technical boundaries
Minecraft and Fabric are JVM systems. A native Rust shared library cannot itself be loaded as a stand-alone Fabric mod. GoldRail ships a Fabric/Java JAR that registers blocks, items, entities, key binds, networking, hooks, and addon APIs. Native Rust is an optional, versioned computation engine accessed through a carefully defined bridge. The JS/Angular dashboard and UI may be reused only with appropriate licensing and parity checks.

MTR v4 already has a standalone Java 21 Transport Simulation Core (TSC). Its `Simulator` instances own per-dimension stations, platforms, rails, routes, depots, vehicles, lifts, messages, and persistence. They communicate through `QueueObject` operation names; integration uses `Main.sendMessageC2S` and `Main.processMessagesS2C`. The existing core has its own tick scheduling and a REST system-map API. We must inspect the exact tagged versions rather than assume master branch interfaces equal the beta release.

## Proposed deployment
```
Minecraft Fabric server (Java 21)
  | GoldRail Fabric shell: packets, block/item registrations, addon facades
  | RustBridge (JNI; bounded calls per tick/dimension, explicit version)
  +----> goldrail_ffi   [shared library; Linux x86_64 alpha]
             | goldrail_protocol  [canonical operation DTO + snapshot schema]
             | goldrail_engine    [deterministic simulated state; no MC classes]
             | goldrail_domain    [rails, stations, routes, vehicles, lifts]
             | goldrail_persist   [compatible save reader/writer; atomic saves]
             + goldrail_metrics   [sampling, performance counters]
Client Fabric/JVM renderer (initially upstream-compatible)
  | GoldRail UI and train renderer profiling/culling/mesh reuse
  + retained addon/content-pack compatibility, packet format and models
```

## Why JNI
Compared with an out-of-process Rust daemon, JNI avoids duplicated Java ↔ native service persistence, two live simulations, background daemon lifecycle and network IPC latency. It does **not** make total memory disappear. Benchmark JNI against a sidecar on representative loads before finalizing; if bindings are too fragile a verified sidecar can be reconsidered by PM. JNI boundary should exchange batched versioned commands and compact snapshots, not a call for each vertex or train-car update. Use direct buffers or bounded serialized batches only if profiling confirms benefit. No unsound `unsafe`; document safety and threading invariant at every unsafe boundary.

## Core contracts
- **Single owner:** one authoritative simulator per dimension. During parity tests a shadow simulator may process cloned replay events but may never issue real-world mutations.
- **Deterministic replay:** given a canonical state, ordered operations, clock ticks, and seeded RNG, Rust outputs equivalent snapshots to reference Java within documented tolerances. Do not assume floating-point bit-exact matching if formats differ.
- **Version:** `bridge_protocol_major.minor`; negotiate early; fail closed for incompatible major version; no silent partial compatibility.
- **Threading:** Java game callbacks enqueue bounded, ordered messages; Rust sim runs on one owner thread per dimension unless benchmark-proven parallelism is safe. Rendering and networking thread never block on expensive path search.
- **Data:** parse the exact MTR save format, preserve unknown fields where feasible, write atomically to temp file, fsync as required, rename, and keep versioned backups. Canonicalize only when parity tests allow. No automatic irreversible migration.
- **Network:** preserve the MTR client/server packet envelope and operation behavior when documented by tests. Do not assume vanilla clients connect without client mod.
- **Compatibility:** add-on mod IDs, mixins, API class names, content packs and scripts have independent constraints; document PASS/PARTIAL/FAIL per addon.
- **Fallback:** no fail-open switch mid-tick to a duplicate simulator. Choose engine at startup, and recover by stopping server and restoring known-good JAR/data backup.
- **Native packaging:** package Linux x86_64 `.so` in JAR only after verifying build provenance and checksums; provide explicit diagnostics on unsupported architectures. No executable downloads at mod runtime.

## Performance architecture
Server: arrays/ID-indexed structures where measured; compact rail topology, reuse buffers, incremental path caches, bounded per-player spatial interest maps, avoid hot-loop allocations, avoid huge collections of boxed objects. JNI batching must not re-serialize the entire world each tick.
Client: cache preprocessed OBJ meshes, reuse GPU resources, frustum + chunk/rail visibility culling, dynamic LOD for far trains, avoid reupload and texture churn, render-state batching when safe and compatible with Sodium/Iris. Never hide nearby trains or alter high-detail content as a shortcut. Benchmark GPU and CPU render-thread costs independently.

## Rollout
1. Original upstream baseline in isolated test copy.
2. Rust engine selected only by feature flag in test environment; initial shadow replay and differential tests.
3. Full replacement JAR in test profile with upstream MTR removed; check blocks, IDs, schemas, addon dependency and packet compatibility.
4. Canary on separate server copy with rollback script.
5. Production only after PM explicit approval and Product Review signoff.

## Architecture decisions still open after audit
- Exact MTR/tag/commit and TSC embedded artifact for 1.21.1 beta.
- Source of server RAM attribution; potential native/non-heap allocations.
- Whether `modid=mtr` is legally/technically appropriate for addon compatibility (inspect metadata and dependency semantics).
- Whether JNI is beneficial vs optimized Java or other implementation after baseline.
- Client renderer code and shader / addon conflicts.
