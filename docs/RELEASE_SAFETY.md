# Release and production safety

1. Do not stop, change, profile aggressively, or replace files on the live Minecraft server without a separate explicit authorization.
2. No use of personal world files, private seeds, IPs or user data in public commits, bug reports, fixtures, CI artifacts or logs.
3. Build and benchmark in a physically distinct project directory with generated synthetic worlds only.
4. Never mutate original save files. Any future migration requires dry-run, versioned backups, atomic writes and demonstrated rollback on copies.
5. A Rust engine and Java engine must never both mutate the same live world. Engine selection occurs at startup; no mid-tick fallback.
6. Package native Linux x86_64 library only after integrity/provenance verification; do not download arbitrary binaries at mod launch.
7. License-audit all reused MIT Java code, shaders, assets, dependencies and mods individually. MTR MIT does not automatically license every bundled model/library.
8. All code changes on feature branches. No merge, deployment or release until Product Review and PM signoff. Production requires separate explicit approval after canary.
