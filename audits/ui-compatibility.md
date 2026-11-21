# Stage 1 UI compatibility matrix - 2026-11-19

**Target:** MTR Fabric 4.1.0-beta.2+1.21.1, exact release SHA-256 5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94.

| Surface | Evidence | Status |
|---|---|---|
| Original release identity | Hash and Fabric metadata verified; renderer bytecode inspected | **PASS: identity only** |
| Train body, bogies, doors, interiors and passengers | Relevant released classes and method sites identified; no visual comparison | **PARTIAL: static only** |
| Rails and lifts | Renderer entry points and distance helpers identified | **PARTIAL: static only** |
| Animated lights, signs, PIDS and dynamic maps | Dynamic texture and worker dispatch paths identified; no screenshot or timing capture | **PARTIAL: static only** |
| Sodium/Iris/shader combinations | Present in the local reference environment metadata; no controlled runtime or pixel comparison | **NOT TESTED** |
| Add-on APIs and binary compatibility | Class and packet surfaces inventoried; no add-on integration test | **NOT TESTED** |
| C2S/S2C packet payloads and ordering | Queue and packet record classes identified; no two-sided wire replay | **PARTIAL: signatures only** |
| GUI, driving, boarding and multiplayer | No interactive gameplay test | **NOT TESTED** |
| Save schema, unknown fields and rollback | No real or synthetic full-schema parity test | **NOT TESTED** |

## Renderer invariants

Preserve render-stage ordering, lightmaps, emissive lighting, cutout/translucent surfaces, sorted glass, texture binding, passenger skins, animations and resource reload behavior. A single shader or draw path cannot replace all existing material stages without pixel and behavior tests.

## Lifecycle and release risks

GPU buffers, dynamic textures, worker queues and model caches require explicit ownership and cleanup on resource reload. A suspected queue-overflow/generating-marker issue remains a hypothesis until reproduced. Matching the mod ID or class names does not establish add-on compatibility.

No third-party model, font, texture, shader or resource-pack assets are included in this publication. Their redistribution rights remain a separate release gate.
