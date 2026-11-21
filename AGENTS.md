# GoldRail agent contract

Target: Minecraft 1.21.1, Fabric, Java 21, Linux x86_64. Preserve validated MTR 4.1.0-beta.2 behavior and existing data. GoldRail is a Fabric/Java mod; Rust is optional and not a standalone Fabric mod.

The public project repository is MTRUST. The local development history and public GitHub history may not share a Git root or tracking remote. **Inspect the current branch, exact base SHA, worktree status and remote refs before any change. Never assume local refs are already published.** The current PM planning base is pm/parallel-road-to-finish at 18f4c2838577a1ff701ae870b59b5a339d21ee18.

## Rules

- Work only on the role-owned branch prefix and files. Use a separate Git worktree for each concurrent agent.
- Never commit directly to main, force-push, overwrite another agent's branch, or merge without explicit PM authorization.
- The role prompt defines the only authorized task. G1-G5 are sequential stop gates.
- Current authorization is W0 reference evidence only. G1 is rejected/closed. No Rust/JNI implementation or playable replacement is authorized.
- Do not access or modify production worlds, servers, installed mods, account data, ordinary launcher profiles, or private saves.
- Use only newly generated synthetic fixtures. Keep seeds and all generated worlds in ignored local scratch; never commit them.
- Do not publish machine addresses, private paths, credentials, user identifiers, logs, world data, seeds, or third-party binaries/assets.
- Record exact branch/SHA, files, commands, exit codes, measured values or NOT MEASURED, compatibility limits, risks and next owner.
- Never claim a test, build, benchmark, launch or review occurred without its actual output.
- Respect upstream and third-party licenses. No project license has been selected; do not assume reuse rights.
- Stop after the assigned handoff. Integrator, Product Review and PM have separate ownership.

## Ownership

Coding: cod/* only. UI: ui/* only. Product Review: review/* only. Integrator: integrate/* only. PM owns roadmap, shared contracts and dispatch. Shared documents are changed only through PM/integrator review.
