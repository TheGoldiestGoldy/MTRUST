# GoldRail | Multi-agent operating protocol

This is a coordination contract for concurrent agents on the same Linux computer. Read AGENTS.md, docs/ARCHITECTURE.md, docs/ALPHA_READINESS.md, docs/BENCHMARKS.md, docs/COMPATIBILITY.md, docs/RELEASE_SAFETY.md, docs/HANDOFFS.md and docs/ROAD_TO_FINISH.md before acting.

## Workspace resolution

The PM supplies GOLDRAIL_ROOT for the assigned development checkout. Agents must verify it with Git status and the pinned base SHA. Do not hard-code, print or publish a machine-specific absolute path.

## Shared ground rules

1. No production server, world, mod directory, player data, login/token, firewall, shared online server, or regular PollyMC application root may be modified. NEVER use real user saves as fixtures. New artificial worlds only. Keep existing baseline CSV/JSON immutable.
2. Original MTR is a reference oracle, not a GoldRail implementation. Do not claim Rust speedups without paired tests. Do not substitute a count-only rail benchmark for moving trains or an empty world for renderer load.
3. Each agent starts from the **same PM-advertised pinned wave base commit** in its own Git worktree or clone. Never run separate agents in a shared working tree: Git checkout and simultaneous writes will destroy each other's evidence.
4. Each writer uses its assigned prefix and owns exclusive files. Existing shared docs (AGENTS.md, docs/HANDOFFS.md, docs/ROADMAP.md, docs/ARCHITECTURE.md, docs/COMPATIBILITY.md, docs/RELEASE_SAFETY.md) are PM/integrator-owned. Writers put handoffs in handoffs/<role>-<wave>.md and update shared docs only through a clearly labeled integration request.
5. Use branches such as cod/w0-reference-fixture, cod/w0-oracles, ui/w0-client-baseline, cod/w1-rust-core, cod/w1-jni-bridge, ui/w1-client-contract, review/w0-g1 and integrate/w0. Never force-push, reset, cherry-pick or merge someone else's branch from a worker role.
6. Each agent gets an isolated ignored scratch directory such as .audit-cache/agents/<wave>-<lane>/ and dedicated local ports/profile. World-test launches use the reviewed network-namespace wrapper: original MTR starts a wildcard HTTP listener on port 8889 even when the Minecraft address binds to loopback. Never run it directly on a host interface.
7. Only one agent owns a particular running Minecraft scenario at a time. The fixture producer exports an immutable versioned manifest with generator command and content hashes. UI/QA consume that snapshot, not an in-progress edited world. Scheduling simultaneous Java/Rust unit tests in separate worktrees is fine.
8. No agent accepts new Minecraft EULAs for new profiles without explicit owner authorization. The prior ui-a0-v1 test profile had owner permission; that does not extend to every new directory. No credentials, tokens, proprietary assets, private seeds, full unredacted player logs or world files in tracked commits.
9. Source matching, third-party license rights, shader/addon compatibility and save-data parity are **unknown until proven**. Evidence must label PASS/PARTIAL/FAIL/NOT TESTED. Fail closed when protocol versions, ownership or saved formats do not match.
10. No merging, publishing, opening production backups, canary rollout or release unless Product Review and PM grant the relevant gate. Developers may run local offline build/unit tests in their worktrees.

## Wave branch freeze and interface handoff

PM creates one immutable base commit and dispatch manifest per wave listing branch names, assignments and explicit cross-lane contracts. Worktree example (adjust paths to actual repo):

~~~bash
cd GOLDRAIL_ROOT
git worktree add ../goldrail-w0-fixture -b cod/w0-reference-fixture <PINNED_WAVE_BASE_SHA>
git worktree add ../goldrail-w0-oracles -b cod/w0-oracles <PINNED_WAVE_BASE_SHA>
git worktree add ../goldrail-w0-ui -b ui/w0-client-baseline <PINNED_WAVE_BASE_SHA>
~~~

Only the PM/integrator creates shared interface contracts. Before W1: freeze operation DTOs, protocol version and golden fixture IDs. Before W2: freeze Fabric registry/mod ID plan, packet envelope and save fields. Agents cannot silently change another lane's public interface. Proposed interface changes require a versioned request to PM; otherwise adapt within the owned lane.

Worktree branches and hashes can be referenced locally. The repository currently has no configured remote; do not pretend a PR exists or push without permission. Git integration is cherry-pick-by-reviewed-commit, never overwriting other agents' folders.

## Deliverables for every worker

- A **committed** branch with exact SHA and a single reproducible role-local handoff in handoffs/<role>-<wave>.md.
- Own-file manifest, any API diff, actual test command and exact exit/output, independent negative tests.
- Versioned fixture or generated binary SHA-256, provenance details, success/failure logs **sanitized**, and explicit measurements vs NOT MEASURED.
- Compatibility status for snapshots, packet, Fabric, client, addons, shaders; block/owner/next action for each failure.
- Build tooling, test fixtures and reproducible invocation in tracked scripts. Large binaries, logs, screenshots, video, actual worlds and credentials remain ignored in .audit-cache. Keep original benchmarks intact.
- A red/green acceptance table that maps each user-visible behavior to observed output. No speculative completion percentage.

## Integrator-only actions

After all dispatched lanes finish or report a genuine blocker, run prompts/99-integrator.md. Integrator checks clean base, cherry-picks branch commits in dependency order, resolves ownership conflicts by asking/assigning a narrow repair rather than deleting tests, compiles full tree, runs unit/integration and isolated gameplay tests, produces hashes and an integration report. Integrator must not silently interpret a missing lane as passing. Reviewer independently challenges results; PM alone decides gates. A failed gate goes to a repair wave, not automatic release.

## Suggested concurrency budget

Default: 2-3 **writing** agents + 1 read-only researcher, avoiding simultaneous game/benchmark processes. Keep the PM and independent Product Reviewer outside implementation. This is a resource and collision precaution, not a platform claim about account limits. Assign U capture after F freezes the scene. Run only one performance capture at a time on the shared GPU/CPU.

## Reviewer decision template

Status is PASS, CONDITIONAL with explicit **non-gate** scope, or FAIL. Include exact git hash, commands independently run, warnings, missing evidence, regression risks, safety/licensing, and recommended gate decision. For A2 acceptance, CONDITIONAL does **not** mean an unspecified missing gameplay/save feature may be treated as complete.

## Immediate dispatch order

1. PM pins this plan branch after review.
2. Start W0 fixture and provenance/oracles in separate worktrees. UI can prepare a capture producer and isolated PollyMC profile simultaneously, but defers train-loaded measurements until fixture is immutable.
3. Integrator W0 combines evidence and reruns tests; Product Review W0; PM G1.
4. Start W1 only if PM G1 explicitly passes.
