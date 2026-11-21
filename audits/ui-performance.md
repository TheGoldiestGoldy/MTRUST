# Stage 1 UI performance evidence - 2026-11-19

**Status: static renderer audit only. Client FPS, frame-time percentiles, GPU time, per-frame draw counts, VRAM, allocations per second and train-loaded UI memory are NOT MEASURED. No performance improvement is claimed.**

Target release: MTR Fabric 4.1.0-beta.2+1.21.1, SHA-256 5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94. The read-only JDK 21 bytecode audit inspected 15 renderer/model classes and passed 16/16 selected structural probes. Static references are not runtime timings.

## Verified static observations

- RenderVehicles contains two distance-helper references and one java.util.Random constructor site.
- The scanned RenderVehicles class contains no local frustum token. This does not prove that downstream Minecraft/backend culling is absent.
- NewOptimizedModel contains one vertex-buffer draw-method reference and one upload-method reference. These are call sites, not calls per frame.
- DynamicTextureCache dispatch and worker queue APIs are present in the released bytecode.
- Existing model buffers and render-stage grouping already exist. A duplicate cache or broad renderer rewrite is not justified without profiling.

## Hypotheses, not confirmed causes

1. Train visibility and off-screen car transforms may cause avoidable CPU/GPU work.
2. Per-car and per-passenger temporary objects may create allocation pressure.
3. Mesh submission, uniforms and state changes may dominate some scenes, but static call sites cannot quantify draw count or GPU cost.
4. Rail geometry work may scale with infrastructure even when no train is visible.
5. Dynamic texture queue drops or resource reloads may create stale state; the suspected stuck-marker consequence is not reproduced.
6. Iris/Sodium shader paths, chunk loading and distant-horizon work are competing explanations that require controlled A/B tests.

## Required client experiment - not yet run

Use the same isolated world topology and quality settings for S0 (zero trains), S1 (one train), S2 (several moving trains) and S3 (dense moving trains). Hold camera, resolution, model resources and renderer versions constant. Capture front-facing and off-screen views, then shader OFF/ON. Use at least three independent repetitions, a 30-second warmup and a 120-second capture. Record whole-frame durations, CPU render-thread scopes, GPU timestamps, draw submissions, VRAM and process memory separately.

A valid client result must report p50/p95/p99 frame time and a stated 1%-low FPS method. CPU/GPU utilization percentages are not GPU frame-time measurements. No current client frame capture exists; metrics/ui-baseline-v2.csv explicitly records NOT MEASURED.

Machine hardware, display settings, private shader-pack names and local launcher configuration are intentionally not published.
