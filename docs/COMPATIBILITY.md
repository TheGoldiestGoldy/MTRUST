# GoldRail compatibility matrix | Stage 1 evidence

**Legend:** PASS means a *specific narrow check* passed, PARTIAL means limited evidence but no parity claim, NOT TESTED means no integration result. Audit target: MTR Fabric 4.1.0-beta.2+1.21.1, verified SHA-256 in `audits/source-lock.md`. No production world read/written.

| Surface | Stage 1 evidence / exact qualification | Status |
|---|---|---|
| Original MTR JAR identity | SHA-256 locally; official Modrinth SHA-1 and size; `fabric.mod.json`; beta class signatures | **PASS (binary ID only)** |
| Synthetic MessagePack rail persistence | Generated rail topologies 0, 64 and 512; `Simulator.stop()` then fresh `Simulator` load counted same rails, in temporary scratch directories | **PARTIAL (rail count only)** |
| Existing real MTR worlds/schema/unknown fields | Never opened personal/production saves. No unknown-field conservation, future schema or rollback tests | **NOT TESTED** |
| Blocks, items, registry namespace | `mtr` and Fabric bootstrap class present; exact registries not enumerated or loaded in a game instance | **PARTIAL (presence only)** |
| Queue and packet protocol | `OperationProcessor` operation constants; `QueueObject` key+payload; C2S/S2C `byte[]` records inspected with JDK21 `javap` | **PARTIAL (surface only)** |
| Real packet encode/decode parity | No two-sided Fabric replay, codecs, dimensions or version negotiation run | **NOT TESTED** |
| Routes, depots, stations, lifts, moving trains | Classes confirmed in installed JAR; benchmark topology intentionally has zero active vehicles/players | **NOT TESTED** |
| Standalone embedded TSC | Released JAR `org.mtr.core.Main --help` returned code 0; standalone synthetic tick/save/reload works on Java 21 | **PASS (headless core only)** |
| Headless Fabric Minecraft server | No isolated Fabric server boot performed; live server untouched | **NOT TESTED** |
| Client GUI and rendering | `MainRenderer`, `RenderVehicles`, `WorkerThread`, `DynamicTextureCache` confirmed; no game client instrumentation | **PARTIAL (class presence only)** |
| Iris/Sodium/shader combinations | Client metadata: Iris `1.8.14-beta.1+mc1.21.1`, Sodium `0.8.13+mc1.21.1`, Sodium Extra `0.9.5+mc1.21.1`; no visual or FPS comparison | **NOT TESTED** |
| MTR-related addons | Read-only metadata scans: 100 client JARs and 82 server JARs. Both have `addonslib` `1.21.1-1.14`, `architectury` `13.0.11`, and the verified same MTR JAR; no addon load/parity tests | **NOT TESTED** |
| Existing content packs/resource licenses | No content packs copied or integration checked; license scope unclear | **NOT TESTED** |
| Startup fallback/native ABI | No Rust implementation exists; fail-closed protocol is Stage 2 design only | **NOT TESTED** |

A bounded local metadata inventory was performed, but per-installation mod lists are intentionally withheld from the public repository. Metadata alone does not establish loaded mod state, runtime dependencies or compatibility; absence of a declared dependency is not evidence of independence. JNI/future engine swaps may break binary APIs even if `modid=mtr` is retained.

**Stage 1 risk:** the official `FileLoader` binary directly writes MessagePack output and can delete unreadable files on a parse-error path. Never test save migrations against anything except dedicated synthetic data. Regression suite must include malformed/unknown fields, rollback and interruptions before considering writing GoldRail world data.

## UI Agent Stage 1 renderer-specific supplement | 2026-11-19

The UI branch audit supplements (does not supersede) the general matrix above. The exact released MTR 4.1.0-beta.2+1.21.1 binary was read-only hashed and JDK21 bytecode-inspected across **15 renderer/model classes**, with **16/16 selected structural references found**. **PASS only for static identification and expected method/reference existence; no client benchmark or gameplay pass.** Full matrix, renderer map and risk ranking: audits/ui-compatibility.md, audits/ui-renderer-map.md, audits/ui-performance.md and audits/ui-optimization-plan.md.

| UI surface | Evidence at Stage 1 | Runtime status |
|---|---|---|
| Train body, doors, bogies, interiors, passenger riding | Candidate model path + released class/method sites, not rendered | **NOT TESTED** |
| Fabric world-render hook, rail renderer, dynamic textures | Release MainRenderer -> RenderVehicles/RenderRails and DynamicTextureCache symbols confirmed | **PARTIAL: bytecode only** |
| OBJ/MTL + Blockbench/model resource packs | Candidate loader/parser/cache; no real pack loaded in test environment | **NOT TESTED** |
| Iris 1.8.14-beta.1, Sodium 0.8.13, Sodium Extra 0.9.5 | Read-only client metadata and shader enable flag | **NOT TESTED** |
| Shader brightness, translucent windows, emissive lights, signs | Render stages known, no pixel capture or GPU timestamps | **NOT TESTED** |
| AddonsLib 1.21.1-1.14, Architectury 13.0.11, other mods | Dependency metadata only, no Fabric load or API calls | **NOT TESTED** |
| Original wire packets, client vehicle data, GUI/controls | Classes/data interfaces inventoried, no client/server replay | **NOT TESTED** |

**Important:** Candidate source stonecutter@009b0ce8 is **not proven the exact published build**. The beta has existing cached GPU meshes, so repeated full OBJ parsing every frame must not be claimed. Class-local lack of frustum references does not prove downstream culling absence. Five controlled synthetic frame scenarios in metrics/ui-baseline.csv remain **NOT MEASURED**; previous Coding Agent topology-only tick results have **no client FPS information**. No production changes.
