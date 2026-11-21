# Verified agent handoffs

This is a public summary of local handoff commits. These local refs are not automatically the same as remote GitHub branches; see docs/PUBLICATION_NOTES.md.

| Role | Local branch tip | Verified delivery | Gate/status |
|---|---|---|---|
| Coding Stage 1 audit | cod/stage1-audit@1d7091d069860e407bde9883025fd97fa8334327 | Exact release artifact inventory, architecture/source candidates, synthetic Java-core harness and initial tests. | Audit only; source mapping unresolved. |
| UI Stage 1 audit | ui/stage1-audit@df0e8b3bcf4a3e89da3a8f7b5c4e2df80727d47e | Read-only renderer map, compatibility risks, 15 classes and 16/16 static probes; 10/10 helper tests. | No real FPS or GPU capture. |
| Independent Product Review | review/stage1-gate@e92a5372cddb0605943f4be48dbe80a7b4c4d5e7 | Replayed helper tests and challenged source mapping, memory sampling, clock semantics, save safety and UI evidence. | **G1 FAIL**. |
| PM G1 decision | pm/g1-decision@a404975b50885194165c8c980fdb21571ae961e6 | Accepted review blockers and authorized evidence remediation only. | **G1 CLOSED**. |
| Coding evidence repair | cod/stage1-evidence-repair@1cf7419da2ea598f74d0f04f7ba62d496e31b876 | Phase-tagged Java-core harness, deterministic internal clock, 9 JVM runs and 360 internal calls per synthetic topology; 29/29 helper tests. | Zero trains/players; not Fabric MSPT. |
| PM alpha readiness | pm/alpha-readiness-dispatch@911030ea034066fa1b27046379b845f07346cde4 | Defined A0/A1/A2/A3 and dispatched isolated UI reference-lab work. | G1 remains closed. |
| UI A0 reference lab | ui/stage1-alpha-lab@d29eaa45218d4461a5175a9c98b5ef7a1fad3700 | Isolated original-MTR and no-MTR servers booted; separate PollyMC client reached game/render initialization; frame-capture validator repaired. | No moving train, joined gameplay or FPS capture. |
| PM finish-line plan | pm/parallel-road-to-finish@18f4c2838577a1ff701ae870b59b5a339d21ee18 | W0-W4 roadmap, parallel-agent protocol, deployment sheet and future gated prompts. | Documentation only; W0 workers not yet delivered. |

## Latest verification - 2026-11-21

- Full local Python suite: **39/39 PASS**.
- Git whitespace check across the planning branch: **PASS**.
- Sanitized public snapshot test copy: **39/39 PASS** after removing the embedded fixture-seed constant and machine-specific launcher defaults.
- No Rust build, JNI build, GoldRail Fabric build, moving-train benchmark or real client frame capture was run.
- No valid train-loaded server MSPT/RSS comparison or client FPS/1%-low result exists.

## Required handoff format

Every new handoff records role/wave/date, exact base and tip SHA, owned files, reproduction commands, tests and exit codes, measured results or NOT MEASURED, compatibility limits, privacy/license review, blockers and next owner. A report is not a gate approval.
