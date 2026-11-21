# GoldRail assignment 20 | Rust simulation, protocol, persistence, server optimization

Role: Rust Coding Agent. Execute only explicitly assigned W1, W2 or W3. Never implement a whole mod merely because Cargo compiles: Java/Fabric owns mod entrypoints. Start from the PM-pinned wave base and frozen protocol. No G1 approval means no W1.

## Read first

AGENTS.md, docs/ARCHITECTURE.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, docs/ALPHA_READINESS.md, docs/COMPATIBILITY.md, docs/BENCHMARKS.md, docs/RELEASE_SAFETY.md, audits/source-lock.md, audits/jni-poc-design.md, released-bytecode golden fixtures and latest PM gate.

## Owned surface

Rust domain, engine, protocol, persistence and engine metrics modules (for example crates/goldrail_domain, crates/goldrail_engine, crates/goldrail_protocol, crates/goldrail_persist, crates/goldrail_metrics), Rust-only tests and benchmarks, handoffs/cod-rust-<wave>.md. You may create the Rust workspace manifest under an agreed ownership lock; **do not** edit any Java Fabric shell, JNI adapter, client GUI, QA scenario generator or shared PM docs. If the workspace manifest is PM/integrator-owned, build in role-local crate workspace and hand off patch instructions instead of editing it.

## W1 | Minimal golden-driven deterministic engine

1. Read the pinned W0 released bytecode behavioral oracle. Require verified golden outputs, declared protocol major/minor and deterministic operation order. If no such contract exists, STOP with a blocking interface request; do not hallucinate expected simulation results.
2. Implement strictly bounded protocol DTOs for one measurable rail/vehicle/route operation selected by PM. Use explicit version and schema validation, stable ordering, fixed/controlled clock and deterministic seeded RNG. Separate error states from normal outputs.
3. Implement a safe, unit-testable Rust operation that reproduces released **semantic golden outputs** within specified tolerances. Include zero case, multiple messages, invalid payload, wrong version and repeat/restart tests. Never claim binary parity if only semantic fields were compared.
4. Provide a Rust-native library API usable by the JNI bridge with documented ownership, no hidden global mutable simulation, and a bounded batch size. Avoid serialization of the full world every tick; no unbounded queue or per-car native calls.
5. Include time/space complexity note and a Java-only optimization counterfactual at the same synthetic workload (measurement can be integrated later). No performance win claims without matched Java/JNI end-to-end samples.

W1 acceptance: cargo fmt, cargo clippy with warnings denied, cargo test, sanitizable/fuzzable invalid input tests, deterministic golden replay test and a real library artifact. Exact platform/toolchain and version recorded.

## W2 | Minimal playable services and test-only persistence

Only after PM G2 and frozen W2 interfaces. Implement the required route, platform, timetable, siding/depot, moving cars, doors, passenger/boarding state and stable vehicle snapshots for the **bounded A2 feature set**. Preserve ordering across ticks; test delayed/duplicate messages, shutdown/restart and replay consistency. Implement known fields of isolated synthetic MTR saves or a versioned GoldRail test save, honoring PM-approved compatibility contract. Reject unknown destructive migrations; keep unknown fields where feasible, atomic temp-write/fsync/rename, backup and corrupted-file fail-closed behavior. Never operate on private saves. Do not implement native platform-specific UI drawing.

W2 acceptance: synthetic train lifecycle golden tests, save/reload byte+semantic validation where appropriate, crash/restart tests and proof one authority owns each dimension. Integrator alone verifies actual game.

## W3 | Evidence-led server optimization

Only after PM G3 and fixed matched scenarios. Profile before changing. Select one server bottleneck with real tick/memory data; optimize with allocations, cache reuse, interest maps or topology representation only where proven. Compare Rust + JNI end-to-end to original MTR and an optimized Java contender on identical workloads; report p50/p95/p99 MSPT, RSS/PSS and GC, separately heap/native committed. Do not claim lower RAM from heap change alone, and do not trade missing trains for speed.

## Handoff

All tests and actual command outputs, changed API/ABI, performance **measured or NOT MEASURED**, assumptions, source/feature gaps, branch/final SHA. Commit handoffs/cod-rust-<wave>.md and all owned source/tests. Never integrate or deploy yourself.
