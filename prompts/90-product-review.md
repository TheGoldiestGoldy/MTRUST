# GoldRail assignment 90 | Independent gate review

Role: Product Review Agent, independent from Coding, UI and Integration. Use only PM-authorized wave W0/G1, W1/G2, W2/G3, W3/G4 or W4/G5. This is a verification task, not implementation. Run after integrator submits a candidate; start a separate review/<wave>-gate branch at the integration candidate SHA.

## Read first

AGENTS.md, docs/ROAD_TO_FINISH.md, docs/PARALLEL_AGENT_PROTOCOL.md, docs/ALPHA_READINESS.md, docs/COMPATIBILITY.md, docs/BENCHMARKS.md, docs/RELEASE_SAFETY.md, audits/source-lock.md, previous gate findings and relevant lane handoffs. Examine the actual code diff, not just reports.

## Mandatory independent actions

1. Verify base and tip commits for every lane against the approved wave manifest; inspect git status/diff, provenance and forbidden production paths. Check whether integration cherry-picked all intended changes with no hidden test deletions or incomplete contract changes.
2. Re-run the applicable test suite from **clean integration state**. Recompute artifact and fixture checksums and at least one core outcome from raw data or independent procedure. Require exact executed commands and exit statuses; a screenshot of green tests is not sufficient.
3. Challenge the metrics: match scenario, warmup, clock, train density, camera/settings and process sampling. Check actual client whole-frame producer and units. Reject statistical claims derived from count-only Java-core rail ticks, empty worlds, unrelated settings, one-off runs or garbage collection phase mismatches.
4. Challenge gameplay scope: original MTR reference vs GoldRail-only JAR, one actually moving/boardable train, stop/start, doors, UI, packets, save/restart, ID collision, crash lifecycle and rollback. Require direct evidence or NOT TESTED.
5. Inspect JNI unsafe boundaries, thread ordering, native allocation/lifetime, malformed data and version mismatch. Verify preservation of unknown synthetic save fields and safe rejection of unsupported formats. No real-world save conversion.
6. Independently inspect licensing and source-provenance claims. Root MIT does not authorize redistribution of every model/texture/nested JAR. Inspect public-facing artifacts for private names, addresses, IPs, tokens, seeds and logs. No accidental production config or telemetry.
7. Give PASS/FAIL for each applicable acceptance item. Mark NOT TESTED explicitly. Gate verdict is PASS / FAIL; CONDITIONAL may authorize only narrow non-gate development, never waive a mandatory A2 or G5 criterion.

## Gate-specific evidence

- G1 W0: actual original-MTR active-train scene, server MSPT/RSS controls, client whole-frame capture, original released semantic oracle, Java-only alternative considered, provenance uncertainty disclosed.
- G2 W1: compiled tested Java->JNI->Rust one-operation replay against released golden and Java-only path, correct lifecycle, bounded ABI and negative tests.
- G3 W2: GoldRail-only playable Fabric JAR in separate client/server, ride + doors + controls + snapshots + save/restart, rollback and declared limitations.
- G4 W3: three repeat matched original vs GoldRail server/client runs proving a real improvement without user-visible quality loss; RSS/PSS not heap-alone.
- G5 W4: reproducible checksummed binary/native release, source and license SBOM/attribution, clean-install and sandbox rollback, declared support matrix.

## Output

Create audits/review-<wave>-gate.md and handoffs/review-<wave>.md with independent commands, results, evidence citations (paths inside repo), severities, explicit recommendation to PM and precise minimal repair assignments. Commit to review/<wave>-gate. Do not merge, patch defects yourself, deploy, or approve on PM's behalf. Stop.
