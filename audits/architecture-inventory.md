# Stage 1 architecture inventory | binary class presence only

Inspection source: exact installed 4.1.0-beta.2 Fabric JAR. These are names inside the ZIP, **not** confirmed Java source paths, public APIs, code paths or benchmark hotspots.

| Concern | Confirmed class path in JAR | What still needs inspection |
|---|---|---|
| Core entry point | `org/mtr/core/Main.class` | message API & tick startup |
| Per-dimension simulation | `org/mtr/core/simulation/Simulator.class` | ownership, event loop, mutability |
| Disk I/O | `org/mtr/core/simulation/FileLoader.class` | format, atomic writes, unknown fields |
| Message queue | `org/mtr/core/servlet/QueueObject.class` | operation names and order |
| Vehicles | `org/mtr/core/data/Vehicle.class` | update hotspots and heap allocations |
| Rail path search | `org/mtr/core/path/SidingPathFinder.class` | path-cache misses and algorithmic costs |
| Client draw scheduling | `org/mtr/render/MainRenderer.class` | mesh reuse and draw-call costs |
| Client texture handling | `org/mtr/client/DynamicTextureCache.class` | GPU uploads and allocations |
| C2S packet | `org/mtr/packet/CustomPacketC2S.class` | envelope and version compatibility |
| S2C packet | `org/mtr/packet/CustomPacketS2C.class` | packet parity and batching |
| Fabric entrypoint | `org/mtr/fabric/MTRFabric.class` | registry/load behavior |
| Fabric client entrypoint | `org/mtr/fabric/MTRFabricClient.class` | client hooks, compatibility |

ZIP entry counts (directory prefixes, not all Java classes): `org/mtr/core/` 302; `org/mtr/packet/` 56; `org/mtr/render/` 60; `org/mtr/client/` 18; `assets/mtr/` 4436.

## Boundaries to preserve

Retain Java/Fabric shell for IDs, blocks, packet endpoints, client renderer, addon APIs. Only benchmark and port the stateful simulation operations when Java-vs-Rust parity is demonstrated. Compare optimized Java before assuming JNI is faster. A 111 MB distribution JAR says nothing directly about live heap or GPU memory.

## Agent-owned inventory completion

Find exact matching source files, call graphs, method signatures, mixins, queue operation names, data versioning, APIs exposed to addons, build and TSC version, and rendering code path. Mark missing source as unresolved. Don't assert current master = installed beta.
