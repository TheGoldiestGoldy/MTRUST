# GoldRail | Project Manager Gate G1 Decision | 2026-11-19

**Decision: G1 REJECTED / CLOSED** following independent Product Review **FAIL** at `review/stage1-gate@e92a5372cddb0605943f4be48dbe80a7b4c4d5e7`.

This is a **gate decision**, not a judgment that Stage 1's static research was wasted. The released binary identity, API inventory, 10 passing helper tests, 16 static renderer probes and synthetic Java-core rail-count checks are useful and reproducible. They cannot justify the proposed Stage 2 Rust/JNI rewrite or promise a memory/FPS win.

## Independent PM checks

- Re-ran `python3 -m unittest discover -s tests -v` on review tip: **10/10 PASS**.
- `git diff --check pm/stage1-review-dispatch..review/stage1-gate`: PASS.
- Recomputed baseline medians/p95/p99 from `metrics/stage1-raw.json` with nearest rank: S0 **0.011685/0.029911/0.033664 ms**, T1 **0.043479/0.138011/0.173964**, T2 **0.260449/0.382223/0.471665**; these are **Java-only standalone synthetic rails**, not MSPT or moving train frame times.
- `metrics/ui-baseline.csv` has five entries with `status=NOT MEASURED`.
- Verified from code that `scripts/benchmark_tsc.py` polls `/proc` from `WARMED` until process exit, while `scripts/CoreSyntheticBenchmark.java` saves/reloads and sleeps 350ms after the measured ticks. Thus memory samples mix tick/save/reload/idle phases and should **not** be used as tick steady-state RSS/PSS.
- Verified that the Java harness resets simulated clock to `System.currentTimeMillis()-1000` before every measured invocation, not a continuous, seeded train timetable. This is insufficient for real-world performance conclusions.
- Agent 3's independent review `audits/stage1-product-review.md` and 14-item `audits/stage1-defects.md` are substantially supported. Suspected texture stuck-marker remains a hypothesis; CREATE-only file overwrite is an API-level hazard, **not a verified production data loss event**.

## Blockers to reopening G1

1. **GR-G1-01:** Controlled isolated original-MTR server with moving trains and representative rail/routes/stations: S0-S4, N>=3 runs, real MSPT/p95/p99, Java heap, allocation/GC, native/NMT, RSS/PSS, control with MTR absent where technically comparable. Distinguish core allocation from Minecraft and off-heap. Preserve exact scene/seed/input equivalence.
2. **GR-G1-02:** Controlled isolated original-MTR client 0/1/several/dense moving trains and matching rail geometry, shaders on/off, off-screen camera rotation, Distant Horizons and chunk load separated; capture real frame distribution, 1% low, CPU render-thread, GPU time/draws and VRAM with repeated samples.
3. **GR-G1-03:** Establish released-core build/source provenance or define the exact *released bytecode* as canonical behavioral oracle with golden replay and serialization tests, explicitly acknowledging incomplete source provenance.
4. Fix benchmark time semantics and memory phase tags **GR-G1-04/05** and frame capture input validation **GR-G1-12** before relying on new measurements. Keep original recordings unchanged for historical audit; never overwrite them without provenance.

## Conditional deferrals

For a future strictly **read-only, isolated, never-deployed** Stage 2 POC, full production save migrations, addon ABI/game-load parity, shader visual parity and redistribution license clearances may be scheduled at later gates **only if their risks remain tracked and no write-capable replacement is built**. Such deferral does not make compatibility PASS and is not approval for a runnable replacement JAR.

## Authorized next work and sequence

**Next Coding assignment (Stage 1 remediation, NOT Stage 2):** `prompts/01b-coding-baseline-remediation.md`. Work in a new `cod/stage1-evidence-repair` branch based on this PM decision branch, without merging or touching production. Fix the synthetic benchmark measurement defects, investigate official release provenance and work toward an isolated active-train Fabric baseline. Handoff with measurements or explicitly document blockers.

**Then:** UI evidence capture/validation remediation on its own branch (PM to dispatch after Coding handoff). **Then:** independent Product Review of the corrected evidence; **then:** PM can reconsider G1. Do not run multiple long agents at once.

No G1 waiver or Stage 2 development is approved. This decision predates the curated public GitHub snapshot; publication does not reopen G1 or authorize Stage 2.
