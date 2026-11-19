# Exact sequence; budget context across ChatGPT chats

**Do not launch 3 parallel long-running agents.** In this ChatGPT setup the PM cannot create subagents, new projects, or inspect account usage quota; the user manually starts role chats. Separate chats should share a project and GitHub repository (sanitized files only), not megabytes of copied context. Open no new agent until prerequisites are met.

| Sequence | Stage | Chat | Prompt | Gate |
|---|---|---|---|---|
| 1 | 1 | Coding | `prompts/01-coding-audit.md` | deliver evidence |
| 2 | 1 | UI | `prompts/03-ui-audit.md` | inspect renderer after coding file map |
| 3 | 1 | Product Review | `prompts/02-review-baseline.md` | PM decides G1 |
| 4 | 2 | Coding | `prompts/04-coding-rust-poc.md` | parity |
| 5 | 2 | UI | `prompts/06-ui-protocol.md` | stable client schema |
| 6 | 2 | Product Review | `prompts/05-review-poc.md` | PM decides G2 |
| 7 | 3 | Coding | `prompts/07-coding-fabric.md` | integrated JAR |
| 8 | 3 | UI | `prompts/08-ui-compat.md` | UI parity |
| 9 | 3 | Product Review | `prompts/09-review-compat.md` | PM decides G3 |
| 10 | 4 | Coding | `prompts/10-coding-perf.md` | memory profiling |
| 11 | 4 | UI | `prompts/11-ui-render-opt.md` | client FPS |
| 12 | 4 | Product Review | `prompts/12-review-performance.md` | PM decides G4 |
| 13 | 5 | Coding | `prompts/13-coding-release.md` | binary release |
| 14 | 5 | UI | `prompts/14-ui-release.md` | final UX |
| 15 | 5 | Product Review | `prompts/15-review-release.md` | PM decides G5 |

Each role can continue in its existing ChatGPT thread until its context becomes unwieldy. Then start a fresh chat with `PROJECT_INSTRUCTIONS.md` and latest handoff, avoiding unnecessary resending of entire outputs. Suggested initial dispatch = coding Stage 1 ONLY, then UI and Review on actual evidence. Limit expensive model effort to architecture, difficult debugging and independent gate review; use lower-effort chat for straightforward docs and small edits. Don't claim knowledge of current client quotas.

**Prompt availability:** Only `01-coding-audit.md`, `02-review-baseline.md`, and `03-ui-audit.md` have been authored. Later-stage prompt paths in this sequence are planned, not yet present. Author and review them before dispatch.
