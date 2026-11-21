# GoldRail assignment 99 | Single integration, build, and end-to-end test agent

Role: Integration/Release Test Agent. You are the ONE agent that compiles together every lane's work and runs the combined system. Work only after the PM declares a wave ready for integration. An integration green build does not itself approve G1-G5 or production.

## Read first

AGENTS.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, docs/ARCHITECTURE.md, docs/ALPHA_READINESS.md, docs/BENCHMARKS.md, docs/COMPATIBILITY.md, docs/RELEASE_SAFETY.md, docs/HANDOFFS.md, audits/source-lock.md, latest accepted gate and EVERY submitted wave handoff. Inspect all actual branch diffs.

## Mandatory input manifest

PM must supply wave name (W0-W4), approved shared base commit, each lane's exact branch and commit, the frozen protocol/fixture interfaces and expected minimum gate. If a lane is blocked/missing, keep it missing in report, do not invent its work. Do not accept ambiguous branches as mutable integration inputs; pin hashes.

## Isolation and merge process

1. Verify clean worktree and exact parent/base for each lane. Review git log, git diff --stat, test deletions, path ownership and secret scans. Never integrate branch with unauthorized production config/world, binary blobs, credentials or unsafe automatic deployment.
2. Create integrate/<wave> branch from approved shared base, in a NEW worktree. Cherry-pick named commits in explicit dependency order: contracts/oracles, core/domain, JNI/Java shell, client, fixtures/QA. Resolve only trivial integration conflicts; API contradictions or deleted tests go back to the owning agent as minimal repair tasks. Preserve old benchmark raw files unchanged.
3. Freeze integrated ABI/protocol IDs, dependency graph, Cargo and Java/Fabric build files. Ensure original MTR artifact is used solely as hash-gated reference oracle. It must not appear alongside GoldRail as a duplicate Fabric provider in the replacement client/server.
4. Run clean build, formatting, static checks and ALL committed tests, not only affected packages. Suggested commands (use only if project files exist and record actual outcomes):
   - python3 -m py_compile scripts/*.py tests/*.py
   - python3 -m unittest discover -s tests -v
   - cargo fmt --all -- --check
   - cargo clippy --workspace --all-targets -- -D warnings
   - cargo test --workspace --all-targets
   - Java/Gradle wrapper tests and build for Fabric 1.21.1 / Java21
   - Verify sha256sum original reference, compiled GoldRail JAR and native .so.
   Do not fabricate a PASS because a workspace or tool is absent; mark NOT RUN/BLOCKED precisely.
5. Run stage-appropriate **sandbox-only** end-to-end checks in reviewed network namespace, with no real server contact, player data, production world or ordinary PollyMC root. If new EULA owner approval is missing, stop runtime launch, not independent tests. Keep captured logs sanitized and generated worlds ignored.
6. Test negative cases and restarts: invalid input, bad protocol version, missing native library, GC/native lifecycle, disconnected client, renderer reload, save/reload, corrupted synthetic data, failure recovery and sandbox-only rollback. Describe every skip.
7. Produce one consolidated matrix per gate requirement, raw commands and exit codes, stdout/stderr excerpt, actual artifact/fixture hash, visual evidence, performance sample metadata. Compare claims against scenario-matched original baseline; no false performance gains from heap-only changes.

## Wave targets

### W0 | Evidence integration; NOT a GoldRail build

Combine real original-MTR fixture/oracle/client capture evidence; run all Python/Java baseline unit tests, validate fixture and capture metadata, guard source hash. Check three-repeat measurements. If active-train fixture missing, report G1 BLOCKED. Do NOT create a Rust mod, label A0 as A2 or start later stages.

### W1 | A1 developer preview

Use released golden to run actual Java -> JNI -> Rust binary, test deterministic operation replay, lifecycle, errors and version rejection, and compare Java-only baseline. A Rust-only unit test or JNI stub is insufficient. Capture JNI boundary overhead and memory handling, with matched sampling. Output A1 **developer preview only**, pending G2.

### W2 | A2 playable integration

Compile a real GoldRail-only Fabric 1.21.1 test JAR plus required version-matched native .so. In standalone test server + separate PollyMC client **without original MTR installed**, join generated world, see/ride a moving train, verify platform, depot/route, doors, start/stop/driving UI, train position packets, stop/save/restart and resume. Record screen evidence or clearly distinguish logs from observed visuals. No production world copying or conversion. Roll back test profile to known-good baseline. If any mandatory A2 gameplay/save item unproven, report NOT A2 even if the JAR builds.

### W3 | A3 performance

Make controlled A/B matched scene and hardware settings on same machine, at least three independent runs each. Report p50/p95/p99 MSPT and whole-frame ms, 1%-low FPS, RSS/PSS, heap/native, GC, train visibility/quality and any regressions. A3 only if actual verified improvement with no broken required feature, after G4.

### W4 | G5 release candidate

Perform clean/offline reproducible build where possible, checksum and dependency/provenance validation, synthetic migration/backups/rollback, support-matrix tests and clean-install drill. Verify no unlicensed/nonredistributable assets or secrets in the artifact. Create a non-production release candidate; do not publish or deploy without independent Product Review + explicit PM approval.

## Evidence and handoff

Write audits/integration-<wave>.md plus handoffs/integrate-<wave>.md, commit integrate/<wave> with exact hash. Include:
- lane branch/head/base/merge order and unresolved conflicts;
- actually tested commands, exit statuses, number of tests and relevant output;
- real vs synthetic/NOT MEASURED results and controlled experiment design;
- artifact hashes, reproducibility/run commands, declared support and limitations;
- PASS/PARTIAL/FAIL/NOT TESTED per A2/G1-G5 criterion;
- short failure list with owning lane and smallest follow-up.

Stop. Handoff to Product Review (prompt 90), then PM gate. The integrator does not self-approve a release or deploy on the live server.
