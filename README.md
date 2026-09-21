# Universal Cruise Master Collector — 1.0.0-rc5-hotfix3

Code-only collector. Git intentionally contains **no collected cruise data**.
An existing working copy can contain required cumulative runtime state in ignored
`work/data` and `work/state`; preserve both directories when upgrading.

Every root command writes the same complete output shown in the console to a
timestamped file under `work/logs`. Use `-LogPath <path>` for a specific name.
Princess collection reports durable request counts rather than a progress display.

## Existing installations and relocated runtime state

Do not run Full on the migrated cumulative state. To repair catalog metadata and
validate it without provider calls or changes to collected evidence:

```powershell
python .\master\reconcile-catalogs.py --state .\work\state
.\build-cruise-master.ps1 -Mode Validate
```

Catalog paths are relative to `work/state/static-masters`. Legacy absolute paths
resolve inside the selected state tree, never against an old workspace. Daily
reconciles all Celebrity entries before collection and after completed increments,
including configurations skipped because they are saturated or already tested.

## Fresh empty installation only (PowerShell)

```powershell
python -m pip install -r requirements.txt
.\build-cruise-master.ps1 -Mode Full
.\build-cruise-master.ps1 -Mode Validate
.\build-cruise-master.ps1 -Mode Daily
.\build-cruise-master.ps1 -Mode Validate
```

`Full` starts with an empty `work/`. `Daily` discovers newly proven Celebrity configurations and incrementally advances existing unsaturated configurations using only newly proven, previously untested voyages. Saturated configurations are preserved without provider calls. `Validate` is read-only.

Celebrity physical configurations are proven from sailing-specific room-selection JSON. Princess physical configurations are keyed by the provider ship version attached to each acquired voyage; no current-page version is projected onto unrelated sailings.

See `docs/OPERATIONS.md`, `docs/ARCHITECTURE.md`, and `docs/FILE-REFERENCE.md`.

For development, install `pytest` and run `python -m pytest tests -q`. The suite
includes the historical registry scripts; Windows stderr integration tests require
Windows PowerShell 5.1. See `docs/PROJECT-HANDOFF.md` for the stabilization status.

The approved permanent-master redesign and numbered PR sequence are in
[docs/PERMANENT-MASTER-ROADMAP.md](docs/PERMANENT-MASTER-ROADMAP.md).
# Offline permanent-master audit (PR-01)

The [implementation roadmap](docs/PERMANENT-MASTER-ROADMAP.md) records the six
numbered PRs. The [proposed contracts](docs/PERMANENT-MASTER-CONTRACT.md) describe
the future physical, category, and assignment masters. Current collector formats
remain unchanged.

```powershell
python master/audit-permanent-masters.py --state work/state --out-dir work/logs/permanent-master-pr01
```

This reads the collected masters, verifies their catalog hashes, and writes JSON
and Markdown reports. It makes no provider calls and publishes no masters.

To materialize an immutable proposed snapshot from the same local evidence:

```powershell
python master/materialize-permanent-masters.py --state work/state
```

The command writes physical, category, and assignment documents for each provider,
verifies and promotes their complete snapshot directory, then atomically switches
`static-masters/permanent-masters/active-snapshot.json`. Legacy catalogs remain
present and authoritative during this migration stage.
