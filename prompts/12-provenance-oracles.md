# GoldRail assignment 12 | Released-bytecode behavioral oracle and compliance

Role: Coding/research specialist. Execute only the PM-assigned W0 or W4. Do not perform another lane's runtime workload or assert upstream source identity from a chronological association.

## Read first

AGENTS.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, audits/source-lock.md, audits/released-core-oracle.json, audits/stage1-server-evidence-repair.md, audits/architecture-inventory.md, docs/ARCHITECTURE.md, docs/COMPATIBILITY.md and license documentation.

## Ownership

Source/bytecode provenance evidence under audits/oracle-*.md or audits/license-*.md, new released_oracle_ or golden_* scripts/tests, independent fixtures under tests/golden/, and handoffs/cod-oracle-<wave>.md. Never change client capture, generated world fixture, Java JNI bridge, Rust engine or shared PM docs. No third-party binary/assets tracked in Git.

## W0 | Prove behavior instead of relying on a guessed source commit

1. Verify official archive hash 5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94. Current candidate MTR stonecutter commit and TSC candidates are **not** proven to build that archive; Gradle used a dynamic TSC version. Preserve uncertainty. If verifiable CI build artifacts/resolved dependency hashes appear, record primary evidence; otherwise keep source status UNRESOLVED.
2. Use the **released class bytes** as oracle. Design deterministic, versioned golden input/output data for at least one simulation operation that W1 Rust can implement. Include ordered messages, clock, seed, expected state/transitions, error behavior, serialization fields, boundary values and unknown-field handling. For any behavior not callable without a full MTR environment, mark unverified and include how to obtain it. Do not create expected data by guessing.
3. Extract and test at least one real released-code operation plus one save/reload observation when feasible. Distinguish exact bytes from field-semantic equivalence and floating-point tolerance; document repeatability and environmental requirements. Add negative tests for malformed save data and operation mismatch in synthetic scratch only; NEVER run destructive parsing on private saves.
4. Inventory registry/mod ID, packet entry points, addon dependencies and asset rights relevant to the **minimal A2**. Produce an uncertainty and rights ledger, not a false compatibility pass.
5. Freeze a draft protocol fixture format as a proposed PM contract for W1; preserve separation between Java baseline, optimized Java contender and Rust outputs. No JNI implementation in W0.

W0 exit: reproducible oracle command, golden fixture input/output, released hash guard, pass/fail evidence and explicit unknowns. If a golden operation cannot be executed, report BLOCKED and the specific dependency.

## W4 | Rights and provenance for distribution

Only after PM G4. Produce a license/attribution/asset SBOM for actual GoldRail-redistributed code, textures, fonts, embedded JARs and native deps. Confirm grant and conditions per asset/source. Remove unlicensed optional assets from release candidate or mark hard block. Audit embedded native checksum and dependency provenance; do not publish production logs, account data or real saves. No assumption that MTR's root MIT covers nested third-party components.

## Tests and handoff

Tests must run against hash-gated original released archive where called for. Include exact commands, resulting outputs, SHA, new fixture checksum, meaningful negative cases, NOT TESTED list and a short unblocked interface proposal for other agents. Commit branch, handoffs/cod-oracle-<wave>.md, stop; PM/integrator alone updates shared contract.
