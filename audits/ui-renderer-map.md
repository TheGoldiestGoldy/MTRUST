# GoldRail Stage 1 UI renderer map | 2026-11-19

**Target:** Minecraft 1.21.1 Fabric, MTR **4.1.0-beta.2+1.21.1**. Exact installed client JAR SHA-256 **5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94**, rechecked read-only. Bytecode was inspected using JDK 21 javap -c -p. The reproducible script scripts/ui_binary_audit.py records 15 class inventories and **16/16 structural checks** in audits/ui-binary-evidence.json.

**Evidence convention:** **VERIFIED-BINARY** = released class signatures/bytecode; **CANDIDATE-SOURCE** = time-constrained checkout stonecutter@009b0ce8316b8b1adfaebad22ed5ffe2ee80b81b; **INFERRED** = plausible cost/behavior not profiled. Matching signatures do NOT establish exact build-to-source mapping. Minecraft intermediary names are obfuscated (net.minecraft.class_*).

## Renderer / model / resource call map

| Stage | Candidate source path and lines | Binary-verified evidence / behavior |
|---|---|---|
| World-render registration | org/mtr/MTRClient.java:382; EventRegistryClient.registerWorldRenderEvent(MainRenderer::render) | **CANDIDATE-SOURCE** for event hook; no runtime hook trace |
| Frame entry | org/mtr/render/MainRenderer.java:136-205 | **VERIFIED-BINARY:** calls RenderVehicles.render, RenderRails.render, RenderPassengers.render, DynamicTextureCache.tick; candidate also simulates client vehicle/lift state, handles riding and ticks arrivals |
| Trains/cars | org/mtr/render/RenderVehicles.java:48-340 | **VERIFIED-BINARY:** calls CullingHelper.getDistanceFromCamera; contains java.util.Random constructor and net.minecraft.class_745 (RemotePlayer in source) allocation *sites*; candidate loops known vehicles, interpolates cars/bogies, evaluates distance, sounds/door/riding/passengers |
| Train resources | org/mtr/resource/{VehicleResource,VehicleResourceCache}.java; org/mtr/model/BuiltVehicleModelHolder.java | **VERIFIED-BINARY:** named classes and methods present; candidate models body, doors, bogies, interiors, lights, displays using part conditions |
| Render submissions | org/mtr/render/MainRenderer.java:217-223,305-324 | **VERIFIED-BINARY:** calls NewOptimizedModel.begin and render. Candidate buckets by mesh and render stage, drains opaque/translucent and applies light/transform per instance |
| Static GPU mesh | org/mtr/model/{ModelLoaderBase,NewOptimizedModel,NewOptimizedModelGroup}.java | **VERIFIED-BINARY:** NewOptimizedModel has VertexBuffer field and intermediary method_1352 upload and method_35665 draw calls. Candidate uploads built meshes then reuses them |
| OBJ / Blockbench parsing | org/mtr/model/{ObjModelLoader,BlockbenchModelLoader}.java | **CANDIDATE-SOURCE:** parse on worker executor. ModelLoaderBase caches built meshes; CustomResourceLoader awaits parse then preloads GPU buffers on render thread |
| Rails | org/mtr/render/RenderRails.java:71-99,251-348 | **VERIFIED-BINARY:** calls CullingHelper.getDistanceFromCameraToBox; candidate distance-filters rail AABBs then builds segment callbacks |
| Lifts / occlusion | org/mtr/render/{RenderLifts,WorkerThread}.java | **VERIFIED-BINARY:** RenderLifts calls WorkerThread.scheduleLifts; candidate schedules main-thread results |
| Textures / signs | org/mtr/client/{DynamicTextureCache,RouteMapGenerator}.java, org/mtr/render/MoreRenderLayers.java | **VERIFIED-BINARY:** DynamicTextureCache calls WorkerThread.scheduleDynamicTextures and creates intermediary DynamicTexture class_1043; candidate caches texture IDs, manages delayed GL deletion |
| UI, riders, passengers | org/mtr/render/{RenderPassengers,DrivingGuiRenderer}.java; org/mtr/client/VehicleRidingMovement.java | **CANDIDATE-SOURCE:** controls, camera shifts, first/third-person passenger and riding effects; runtime parity untested |

## Existing caching (do not claim it is absent)

**CANDIDATE-SOURCE:** ModelLoaderBase.java:94-152 caches built vehicle/other models. NewOptimizedModelGroup.java:39-58 groups by texture/stage and builds static meshes. NewOptimizedModel.java:72-115 uses a VertexBuffer allocated/uploaded on model build. **VERIFIED-BINARY:** matching structures and upload/draw refs exist. **No evidence of OBJ reparsing or GPU reupload every render frame.** Cross-resource mesh deduplication, total resident geometry and resource-reload buffer disposal remain unmeasured.

**CANDIDATE-SOURCE:** BuiltVehicleModelHolder.java:44-69 evaluates PartCondition and submits selected animated doors, route/direction variants and display parts. RenderVehicles.java:125-340 handles bogies, car bodies, gangways, barriers, player/passenger visuals, door interaction, sounds, and riding. These are functional/visual parity requirements, not disposable decoration.

## Culling and far/offscreen work

**VERIFIED-BINARY:** RenderVehicles calls radial camera-distance helper; static javap scan finds **zero** frustum/Frustum/class_4604 tokens *in that class*, and no direct call from that class to WorkerThread.scheduleVehicles. The worker exposes a vehicle-occlusion API, but **CANDIDATE-SOURCE** has no matching vehicle caller. Negative static results do not rule out downstream Minecraft/backend culling. Lift worker occlusion invocation was found. Rail bounding-box *distance* check was found; that is not view-frustum rejection.

**CANDIDATE-SOURCE:** RenderVehicles.java:64-115 computes smoothed car/bogie state using streams/collect before applying each car's radial distance check. RenderVehicles.java:135-193,258-340 performs door/floor, sound and riding work outside mesh-distance guard. Thus distant/offscreen cars may cost CPU even without draws. Some work is necessary for riding/interaction; separate logic before any optimization.

## Frame scheduling / threading / texture lifetime

**CANDIDATE-SOURCE:** MainRenderer.java:100-105,169-205,217-223,305-324 clears/repopulates per-frame buckets, groups identical meshes/stages but still issues one mesh draw for each transform with matrix/color uniforms. This is NOT instanced drawing. Batch grouping reduces state changes, but real draw counts are **NOT MEASURED**.

**CANDIDATE-SOURCE:** WorkerThread.java:56-81,89-123,137-182 uses a virtual-thread executor, worker loop, two atomic occlusion inboxes and a dynamic-texture queue limited to 256 pending/8 drained per loop. DynamicTextureCache.java:105-125,290-365 scans cache + pending deletions once per frame, queues bitmap generation, registers GL textures on the client path, and uses a 10-second expiry/grace period. Candidate queue overflow drops oldest runnable without clearing its generating key marker: **source-supported suspected correctness issue**, not reproduced against beta.

**CANDIDATE-SOURCE:** CustomResourceLoader.java:108-117,188-205 reloads resource caches, waits (up to 60 s in candidate) for asynchronous OBJ/Blockbench parsing, and preloads buffers on render thread. Preserve GL thread ownership; potential cold-load stalls are not timing measurements.

## Client compatibility contracts

Retain MinecraftClientData's mirrored trains/rails, vehicle IDs and car positions, packet timing, rider camera offsets, UI/driver controls, OBJ/MTL and Blockbench, ModelProperties, PartCondition, ModelDisplayPart, emissive/translucent/interior stages, texture IDs, animations, door collision, gangways, passengers, sounds, and ResourcePack reload. Avoid culling camera-intersecting or boarded cars. Preserve Fabric MTR namespace, addon-facing APIs, shader/light uniforms and ordering compatible with Sodium/Iris. A future Rust server core does not imply a Rust client renderer.

## Reproduction

Run scripts/ui_binary_audit.py --jar /path/to/verified-MTR.jar --jdk /path/to/jdk21 --output audits/ui-binary-evidence.json. The script checks SHA-256 before disassembling 15 released classes and stores sanitized structural results. Static call sites are NOT runtime calls/frame or performance samples. Actual source commit mapping, visuals and addon parity remain **NOT TESTED**.
