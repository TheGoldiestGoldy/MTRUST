# GoldRail Stage 1 architecture inventory | release-binary APIs plus dated source candidates

**Evidence basis:** confirmed class files and public signatures from the **official verified 4.1.0-beta.2+1.21.1 JAR**, cross-referenced with *candidate* `stonecutter@009b0ce8` and `TSC@020cf90d`. These commit refs are not established as exact build inputs. Source-relative paths below refer to those candidate checkouts; binary paths are confirmed.

| Responsibility | Candidate source-relative file path | Binary class path / observed API or call path | Scope |
|---|---|---|---|
| Fabric server bootstrap | MTR `src/main/java/org/mtr/fabric/MTRFabric.java` | `org/mtr/fabric/MTRFabric.class` (`ModInitializer`) | Keep Java/Fabric |
| Java game integration, dimension lifecycle | MTR `src/main/java/org/mtr/MTR.java` | `org/mtr/MTR.class`; `init()`, `sendMessageC2S(...)`; instantiates TSC `Main` around source line 209, calls `manualTick()` around 264, `processMessagesS2C(...)` around 285 | Keep Java; critical bridge boundary |
| Transport core entrypoint | TSC `src/main/java/org/mtr/core/Main.java` | `org/mtr/core/Main.class`; `Main(Path,int,boolean,boolean,Consumer,String...)`, `manualTick()`, `sendMessageC2S(Integer,QueueObject)`, `processMessagesS2C(int,Consumer)`, `stop()` | Possible integration seam |
| Per-dimension owner/ticking | TSC `src/main/java/org/mtr/core/simulation/Simulator.java` | `org/mtr/core/simulation/Simulator.class`; constructor, `tick()`, `save()`, `stop()`, `sendMessageC2S(QueueObject)` | High-priority profiling |
| Graph and lookup maps | TSC `src/main/java/org/mtr/core/data/Data.java` | `org/mtr/core/data/Data.class`; public stations/platforms/sidings/routes/rails; `sync()` rebuilds lookups | Profile map memory; Rust candidate after parity |
| Rails and signals | TSC `src/main/java/org/mtr/core/data/Rail.java` | `org/mtr/core/data/Rail.class`; `newRail(...)`, `tick1(Simulator)`, `tick2(long)` | Candidate compute kernel |
| Vehicle motion / schedules | TSC `src/main/java/org/mtr/core/data/Siding.java`, `Vehicle.java` | `org/mtr/core/data/Siding.class`, `Vehicle.class`; movement/simulation methods | Candidate **only after train-dense baseline** |
| Path search | TSC `src/main/java/org/mtr/core/path/SidingPathFinder.java`, `org/mtr/core/directions/DirectionsFinder.java` | `org/mtr/core/path/SidingPathFinder.class`, `org/mtr/core/directions/DirectionsFinder.class` | Candidate if profiling proves expensive |
| Persistence | TSC `src/main/java/org/mtr/core/simulation/FileLoader.java`, `org/mtr/core/serializer/{MessagePackReader,MessagePackWriter}.java` | `org/mtr/core/simulation/FileLoader.class`, MessagePack classes | Preserve Java/format until unknown-field parity |
| Operation dispatch | TSC `src/main/java/org/mtr/core/servlet/{QueueObject,MessageQueue,OperationProcessor}.java` | matching `org/mtr/core/servlet/*.class`; `OperationProcessor.process(String,SerializedDataBase,Simulator)` | Keep exact keys/ordering |
| Packet transport | MTR `src/main/java/org/mtr/packet/{CustomPacketC2S,CustomPacketS2C,PacketRequestResponseBase}.java` | `org/mtr/packet/CustomPacketC2S.class`, `CustomPacketS2C.class`; both Java records with `byte[] buffer()`; `MTR.PACKET_IDENTIFIER_C2S/S2C` | Keep Java Fabric envelope |
| Client renderer / layers | MTR `src/main/java/org/mtr/render/{MainRenderer,RenderVehicles,WorkerThread}.java` | `org/mtr/render/MainRenderer.class`; `render(...)`, `scheduleRender(...)` | **UI Agent owns later** |
| Dynamic textures | MTR `src/main/java/org/mtr/client/DynamicTextureCache.java` | `org/mtr/client/DynamicTextureCache.class`; `tick()` | Client memory/GPU risk |
| Client bootstrap | MTR `src/main/java/org/mtr/fabric/MTRFabricClient.java` | `org/mtr/fabric/MTRFabricClient.class` | Keep Java/Fabric |

## Binary-verified queue keys

`get_data`, `update_data`, `delete_data`, `list_data`, `arrivals`, `set_time`, `update_riding_entities`, `block_rails`, `press_lift`, `nearby_stations`, `nearby_depots`, `rails`, `generate_by_depot_ids`, `generate_by_depot_name`, `generate_by_lift`, `clear_by_depot_ids`, `clear_by_depot_name`, `instant_deploy_by_depot_ids`, `instant_deploy_by_depot_name`; S2C `vehicles_lifts`, `generation_status_update`.

Actual serialized payload compatibility and message ordering are **NOT TESTED**; names alone do not prove replay parity. Binary `QueueObject` holds a string key, serialized payload and typed callback. Packet envelope is a byte-array record, not evidence that third-party addon packets will decode on a replacement.

## Safety-critical persistence observation

`FileLoader` binary disassembly confirms use of `Files.newOutputStream(..., CREATE)` for MessagePack save files and `Files.deleteIfExists` on a parse-error path. There is no verified transactional temp-file-and-rename path here; **do not assume atomic writes or that unreadable files are retained**. For GoldRail, require read-only parsing, unknown-field retention tests, atomic save copy/swap, backups and rollback before any world migration. The Stage 1 synthetic rail round-trip exercises only generated fields; does not prove real-world save integrity.

## Candidate hotspots, ranked by audit priority (not measured bottlenecks)

1. **Siding/Vehicle movement and path/directions**: many active train objects and path rebuilds could allocate heavily; instrument before choosing Rust.
2. **Rail update, `Data.sync()`, vehicle-position spatial maps**: CPU/heap cost proportional to synthetic topology can be measured, but train-dense impact is unknown.
3. **Transport packet serialization / interest regions**: preserve envelope, measure bytes per player, allocations and update frequency before moving data across JNI.
4. **Persistence MessagePack**: high correctness risk, not automatically a runtime hot path.
5. **Client `RenderVehicles`, `WorkerThread`, `MainRenderer`, `DynamicTextureCache`**: renderer queues/meshes/textures and FPS need independent UI Agent profiling, not server-Rust assumptions.

**Do not move to Rust:** Fabric registrations, Minecraft entity/world/chunk access, existing mod IDs/addon facades, Fabric packet endpoints, client renderer and GPU resource management (until a separate renderer-specific decision). Do not treat an inherited simulation optimization as a user-visible FPS gain.

## Addons / compatibility inventory

- Read-only scans of a **client** and **server** mods directory (JAR metadata only, no world data): **100 client** JARs / **9** relevant entries in `the withheld local client mod-metadata inventory`, and **82 server** JARs / **6** relevant entries in `the withheld local server mod-metadata inventory`. The same verified MTR release JAR exists in both. The server includes `addonslib`, `architectury`, `fabric-api` and `lithium`; Iris/Sodium are client-side.
- These scans found no declared `mtr` dependency from the shortlisted mods and one unclassified server JAR. They do **not** establish all addons, prove loaded mod state, or establish runtime compatibility.
- `mtr.mixins.json`: one common mixin `PlayerTeleportationStateAccessor`, one client mixin `TextFieldSelectionEndAccessor`, Java 21; no API/mixin parity test yet.
- YanYang fork: reference only, reported based on MTR 4.0.5 and not compatible as a ready replacement for 1.21.1. No code adopted from it.

## What was actually tested

- Released JAR hashes and metadata: verified.
- Public class signatures: `javap` on the **installed JAR** (JDK21).
- Embedded `org.mtr.core.Main --help`: launched successfully with local Java 21 (no server/network).
- Generated topology `S0=0`, `T1=64`, `T2=512` rails: synthetic MessagePack save/reload matches counts (see raw metrics).
- **NOT TESTED:** active train/route movement, client FPS, Minecraft MSPT, addon game load, player interest packets, real world schema/unknown fields, shader rendering or original-JAR-from-source reproducible build.
