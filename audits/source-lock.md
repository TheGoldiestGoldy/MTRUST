# Source lock | Stage 1 initial observations, not yet complete

**Status: PARTIAL / source commit unresolved.** The following observations came from a read-only inspection of the installed artifact on 2026-11-19. Never infer source correspondence from an upstream master branch.

- Artifact filename: `MTR-fabric-4.1.0-beta.2+1.21.1.jar`
- SHA-256: `5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94`
- Length: `111620655` bytes; ZIP entries: `10921`
- `fabric.mod.json`: ID `mtr`, version `4.1.0-beta.2`, Minecraft dependency `1.21.1`
- `META-INF/MANIFEST.MF`: `Stonecutter-Node-Project: 1.21.1-fabric`; mappings `intermediary`
- Embedded core evidence: `org/mtr/core/Main.class`, `org/mtr/core/simulation/Simulator.class`, `org/mtr/core/servlet/QueueObject.class`
- Nested JAR declarations: Elementa 743, Kotlin Stdlib 2.4.20-Beta1, UniversalCraft 1.21 Fabric 497. **Check separate third-party licenses.**

Official source candidates, **not yet proven to correspond to the binary**:
- https://github.com/Minecraft-Transit-Railway/Minecraft-Transit-Railway
- https://github.com/Minecraft-Transit-Railway/Transport-Simulation-Core
- https://modrinth.com/mod/minecraft-transit-railway/version/FABRIC-4.1.0-beta.2%2B1.21.1

## Agent-owned next evidence

1. Locate upstream release build tag/commit and exact Fabric build parameters.
2. Determine which TSC dependency version and Git commit was embedded; compare signatures or compile reproducible release JAR.
3. Verify the artifact checksum against an official release if published; otherwise document distribution provenance as unresolved.
4. Verify MTR MIT license and **each** library, asset, font, model and shader's rights.
5. Record exact commits, tag IDs, Gradle dependency coordinates, hashes, and proof in this document. Avoid claiming tag equivalence without independent evidence.
