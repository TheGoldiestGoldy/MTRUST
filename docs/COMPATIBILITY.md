# Compatibility matrix

All statuses are initially **NOT TESTED**. A class found in a JAR is evidence of presence, not behavior parity.

| Surface | Evidence required | Status |
|---|---|---|
| Existing MTR world data and schema | Backup-free synthetic fixture round-trip, unknown fields | NOT TESTED |
| MTR blocks/items/registries | Exact IDs from beta JAR and test load | NOT TESTED |
| MTR networking and queue operations | Captured synthetic operation replay; packet envelopes | NOT TESTED |
| Trains/routes/stations/depots/lifts | Deterministic differential snapshots | NOT TESTED |
| Third-party MTR addons and content packs | Dependency metadata and isolated integration tests | NOT TESTED |
| Sodium/Iris/shader combinations | Client render and visual regression | NOT TESTED |
| Headless dedicated Fabric server | Full test-profile launch and unload | NOT TESTED |
| Java-only fallback/startup behavior | Fail closed on version mismatch; no duplicate simulators | NOT TESTED |

Exact addon versions and relevant mods are to be inventoried during the audit. Don't assert addon compatibility from mod ID alone.
