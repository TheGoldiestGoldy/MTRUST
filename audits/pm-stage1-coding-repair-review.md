# GoldRail | PM check of Stage 1 Coding Evidence Repair | 2026-11-19

**Branch reviewed:** `cod/stage1-evidence-repair@1cf7419da2ea598f74d0f04f7ba62d496e31b876`, clean worktree before PM branch. **Disposition:** accept completed *evidence tooling and fixture provisioning* as a partial Stage 1 Coding handoff; **G1 remains CLOSED** and no Rust work is authorized.

## Reproduced / inspected

- `python3 -m unittest discover -s tests -v`: **29/29 PASS**. 19 new tests include negative checks for phase/time, fixture destination and JAR mismatches. `git diff --check pm/g1-decision..cod/stage1-evidence-repair`: PASS.
- Raw `the withheld raw V2 phase-level process trace`: 9 runs, three each of 0/64/512 static rails, **360 internal-tick samples per scenario**, each 30 seconds wall-time warmup, **120,000 ms virtual clock advance per run**, count-only reloads match original generated rail counts. Independently recomputed p50/p95/p99 (ms): S0 0.018990/0.042504/0.072684; T1 0.027014/0.043602/0.060104; T2 0.134271/0.215008/0.302726.
- V2 emits JVM phase markers, attempts phase-scoped `/proc` memory readings, records NMT and preserves original V1 evidence. V2 directly invokes the original release's private `Simulator.tick(long)` **via reflection**, not the full Fabric tick or any train service. The virtual clock advances 1000ms per call while nominal calls are paced every 50ms: **do not equate this with normal game tick or real-time train-service workloads**. Phase-tagged RSS/PSS is *whole Java process*, not the MTR core's own attributable native bytes.
- Published-JAR oracle fingerprints nine released classes, but is **not** a proven source build pin or differential vehicle/packet/save behavioral replay.
- Ignored `.audit-cache/isolated-fabric/stage1-v1` contains two staged profiles with official Fabric launcher and pinned Fabric API; one also contains verified MTR release. Both `eula.txt` values are **false**; neither has a generated world; no actual moving-train game was measured. EULA-gated loader startup alone is not a playable baseline.
- Bounded tracked-file scan located no committed JAR/world data, and Git remains local only. This cannot establish that everything on the workstation is private or unchanged, so do not overclaim.

## Outstanding high-value tasks

- **GR-G1-01 BLOCKER**: actual operating generated MTR routes/sidings/vehicles in a separate test server, original MTR vs control, real Fabric MSPT/RSS and 3+ repeats.
- **GR-G1-02 BLOCKER**: independently measured original-MTR client frame times, shader and camera controls, GPU vs CPU attribution. Frame capture parser still accepts invalid capture timestamps.
- **GR-G1-03**: provenance unresolved; published-JAR bytecode strategy is sensible but class fingerprints do not replace semantic golden replay.
- Native Java heap / process RSS improvements or a Rust speedup have **never** been demonstrated. Active-train/rider/addon/packet/production world parity NOT TESTED.

**PM action:** sequentially dispatch UI Agent Stage 1 evidence/sandbox assignment via `prompts/03b-ui-alpha-lab.md` from PM branch `pm/alpha-readiness-dispatch`. Only after that, dispatch targeted Coding fixture completion if needed, then independent Product Review and explicit G1 decision. Alpha criteria: `docs/ALPHA_READINESS.md`.

This memo is an evidence review, **not a PR, merged release, approval for EULA acceptance or permission to access production**.
