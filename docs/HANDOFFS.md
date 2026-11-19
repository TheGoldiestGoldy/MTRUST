# Agent handoffs

Each agent appends a dated, one-page handoff. A review gate has not passed until independent Product Review challenges the evidence and PM explicitly approves it.

## Required template

**Role / stage / date:**

**Branch and commit:** exact local commit SHA and, once remote configured, PR URL. Distinguish unpushed from published.

**Files changed:** paths and purpose.

**Evidence and reproduction:** commands; synthetic fixture provenance; exact upstream JAR hash; inputs, expected and observed outputs.

**Tests:** tests run; numerical results/log references; any tests skipped and why.

**Performance:** measured heap/native/RSS/PSS/MSPT/client FPS including scenarios, counts and methods; or **not measured**.

**Compatibility:** PASS/PARTIAL/FAIL/NOT TESTED for world saves, packets, rendering, required addons.

**Known risks and blockers:** specific, documented; include source mapping uncertainty and licensing.

**Next role / gate:** explicit owner and exact prompt; do not automatically dispatch.

## PM status

2026-11-19: sanitized project scaffold published to the MTRUST GitHub repository. Coding Stage 1 remains in progress on a separate branch; no performance results or gate approvals yet.
