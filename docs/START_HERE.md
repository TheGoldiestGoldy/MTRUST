# GoldRail W0 deployment sheet

**Current authorization: W0 evidence completion only. G1 is FAIL/CLOSED.** Do not begin Rust/JNI implementation or call the current reference lab a GoldRail alpha.

## Pinned base

Use pm/parallel-road-to-finish at commit:

18f4c2838577a1ff701ae870b59b5a339d21ee18

The PM must verify the branch still points to this exact SHA before dispatch. Each worker creates a separate worktree from that commit. The PM supplies the assigned project root through GOLDRAIL_ROOT; do not hard-code machine paths.

## Parallel workers

### Lane F - original-MTR railway fixture (Coding)

Use prompts/10-reference-fixture.md. Create only new isolated test data. Produce a genuine route, platform, siding/depot and at least one moving original-MTR train. Verify achieved counts independently. Do not accept a new EULA or start a server unless the exact test profile and launch have separate authorization. No production access.

### Lane P - released bytecode oracle and provenance (Coding/research)

Use prompts/12-provenance-oracles.md. Treat the exact published JAR as the reference until its source/dependency mapping is proven. Build golden inputs and outputs for operations and serialization. Do not claim a source commit is byte-identical without proof.

### Lane U - client capture (UI)

Use prompts/11-client-baseline.md. Use a separate PollyMC profile only. Establish a valid S0 baseline first. Do not launch a second game session using the same profile. Wait for Lane F's immutable fixture manifest before train-loaded capture. If the PM has not supplied a reviewed isolated runner, stop and report BLOCKED. Never copy account credentials or tokens.

## Integration and review

Only after the three W0 handoffs, PM may authorize prompts/99-integrator.md on a new integrate/w0 worktree. The integrator verifies exact branch tips, tests the combined evidence and stops. Then PM may dispatch prompts/90-product-review.md on a separate review/w0-g1 branch. Product Review does not implement fixes or approve the gate.

## Later waves

Prompts 20-22 are future W1/W2 work only. They are not current authorization. W1 requires an explicit PM G1 PASS; later waves require their own frozen base SHA and gate approval.
