# Operations

## Preserve an existing installation

`work/data` and `work/state` are cumulative operational state, even though Git
ignores them. Back up and copy both when relocating an installation. Do not run
Full, clear state, or rebuild masters to repair catalog metadata. The empty-clone
procedure below is a separate release acceptance exercise.

In RC5-hotfix3, both provider catalogs store forward-slash paths relative to
`work/state/static-masters`. Validation maps legacy Windows/POSIX absolute paths
to the selected local tree, even if the old workspace still exists. Missing local
masters fail validation; the old location is never a fallback.

After relocation or an interrupted Celebrity increment, repair metadata offline:

```powershell
python .\master\reconcile-catalogs.py --state .\work\state
.\build-cruise-master.ps1 -Mode Validate
```

The repair updates only the two catalogs and Celebrity manifest catalog reference.
It makes no provider calls and preserves masters, cumulative validation reports,
raw evidence, registry, canonical voyages, and checkpoints. It refreshes every
Celebrity entry's relative path, SHA-256, and saturation from the published master
and validation pair. Missing files, identity mismatches, cabin/deck conflicts, or
inconsistent saturation stop repair. Princess paths are relocated only after
their existing hashes match local files. Each JSON replacement is atomic and
rerunning the command is safe if it is interrupted between documents.

Daily performs the same Celebrity reconciliation before collection and after
each completed configuration. Thus an increment promoted before a crash is
recatalogued on restart even if its voyages are already tested or it is saturated.
This repairs a completed promotion/catalog gap; it is not a rollback mechanism
for arbitrary damage or a partially promoted, inconsistent master/report pair.
Investigate such inconsistencies rather than deleting cumulative state.

All root pipeline runs automatically create a timestamped log under `work/logs`.
The path is printed before work starts. `-LogPath` selects a stable destination:

```powershell
.\build-cruise-master.ps1 -Mode Validate -LogPath .\work\logs\validate.log
```

The wrapper runs the pipeline in a child PowerShell process, drains stdout and
stderr to both console and file, and only then returns the exit code. This keeps
complete Python tracebacks under Windows PowerShell 5.1. Every emitted line is
prefixed with an ISO 8601 local timestamp including its UTC offset for duration and slowdown analysis. Stage completion/failure
includes elapsed seconds. Princess itinerary acquisition logs every 25th request
and a final matched/fallback/failure summary; it does not use `Write-Progress`.
Celebrity discovery separately labels failures added by the current run and older
failures retained as evidence. A historical notice alone does not mean the current
run's provider calls failed.

## Starting from zero

A clean Git clone needs Python, PowerShell, Internet access, and dependencies in `requirements.txt`. Do not copy any old `work/` directory, registry, survey, voyage JSON, cabin master, or cache into the clone.

Run `Full` once. It acquires voyages, normalizes them, surveys physical configurations, archives immutable runtime evidence, builds Registry V1.2, discovers static masters where evidence permits, and validates generated masters.

Run `Daily` thereafter. Existing unsaturated Celebrity masters advance using newly
proven, previously untested published voyages; saturated configurations are
skipped. Provider voyage data and survey evidence are refreshed.

Run `Validate` at any time after Full. Validate does not create directories, checkpoints, manifests, or other state.

If acquisition succeeded but a later stage failed, install the corrected source
over the same working copy and resume without calling the voyage providers again:

```powershell
.\build-cruise-master.ps1 -Mode Full -ReuseAcquiredVoyages
```

This requires the previously acquired provider artifacts in `work/data`; it
still reruns enrichment, canonical normalization, and all downstream stages.

If an RC3 run completed Celebrity masters and failed specifically at
`Princess published static masters`, install RC4 over that working copy and
resume without repeating either provider acquisition or Celebrity collection:

```powershell
.\build-cruise-master.ps1 -Mode Full -ResumeAtPrincessMasters
```

The switch fails unless both canonical voyage files and the completed Celebrity
catalog and manifest are present. It then builds Princess masters, validates all
generated masters, and publishes the run manifest.

To resume a completed acquisition/survey run specifically at incremental
Celebrity masters, preserving canonical data and the current registry:

```powershell
.\build-cruise-master.ps1 -Mode Daily -ResumeAtCelebrityMasters
```

The resume switch skips acquisition, normalization, fleet survey, and registry
import. Existing checkpoints for this date, mode, and VERSION are honored. A
version change creates a different run key, so explicitly use the resume switch
to avoid repeating acquisition. `-RestartRun` clears that run's checkpoints and
should be used only when intentionally rerunning completed stages. Catalog-only
repair does not need it and does not contact providers.

## Developer verification

```powershell
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest tests -q
.\build-cruise-master.ps1 -Mode Validate
```

Tests use synthetic temporary state. The pytest suite also runs the two legacy
registry scripts. PowerShell stderr tests execute Windows PowerShell 5.1 and
check complete tracebacks in console output and Tee-Object logs. They are skipped
on systems without `powershell.exe`. Use the pipeline's `-Python` parameter for
an explicit interpreter path when `python` is unavailable in the current shell.

## Clean-room release acceptance

```powershell
git clone <repository> md-ucmsys-inventory-scripts-clean-test
cd md-ucmsys-inventory-scripts-clean-test
python -m pip install -r requirements.txt
.\build-cruise-master.ps1 -Mode Full
.\build-cruise-master.ps1 -Mode Validate
.\build-cruise-master.ps1 -Mode Daily
.\build-cruise-master.ps1 -Mode Validate
```

RC5 must not be promoted to 1.0.0 until this sequence succeeds from a virgin clone.
## Offline permanent-master planning

Run `python master/audit-permanent-masters.py --state work/state --out-dir work/logs/permanent-master-pr01`
to compare saved masters using `config/ship-classes.json`. Review both report files.
Shared-field candidates are evidence-based proposals, not automatic inheritance.
Conflicts and unknowns require explicit migration decisions. Legacy saturation
does not establish completeness. Audit output must be outside state and data.
PR-01 does not migrate state or change Daily. See `PERMANENT-MASTER-ROADMAP.md`
for the remaining numbered PRs and `PERMANENT-MASTER-CONTRACT.md` for contracts.

## Materialize a permanent-master snapshot

Back up cumulative state before an intentional migration, then run:

```powershell
python .\master\materialize-permanent-masters.py --state .\work\state
.\build-cruise-master.ps1 -Mode Validate
```

The materializer makes no provider calls and does not modify legacy catalogs,
masters, raw evidence, registry, voyages, or checkpoints. It verifies every input
catalog hash before deriving the snapshot. Complete immutable files are promoted
before the active pointer changes. Rerunning is deterministic and safely completes
an interruption between promotion and activation. Coverage remains unverified;
legacy collectors continue using their existing catalogs in PR-03.

To roll back the proposed snapshot pointer to a previously published immutable
snapshot, use its manifest `snapshotId`:

```powershell
python .\master\activate-permanent-master-snapshot.py --state .\work\state --snapshot <snapshotId>
```

Activation verifies every document and manifest hash before changing the pointer.

## Assess completion and targeted refresh work

Assessment is offline and does not alter the active snapshot:

```powershell
python .\master\assess-permanent-masters.py `
  --snapshot-root .\work\state\static-masters\permanent-masters `
  --out .\work\logs\permanent-master-assessment.json
```

The report separates membership, required attributes, definitions, and assignments.
Review every `INCOMPLETE` and contradiction item. `DISCOVERY_STALLED` is not complete
and is not automatically queued. It is retried only after policy/evidence changes or
an explicit operator trigger:

```powershell
python .\master\assess-permanent-masters.py `
  --snapshot-root .\work\state\static-masters\permanent-masters `
  --manual-target CELEBRITY/EG `
  --factory-refresh-target PRINCESS/SU `
  --out .\work\logs\permanent-master-assessment.json
```

Periodic intervals are policy values, not inferred change dates. Migrated evidence
has no supported `verifiedAt`, so its schedule is `UNSCHEDULED`; operators must not
invent dates from file timestamps. PR-04 emits work but does not call providers.

## Daily maintenance integration

Daily materializes an active snapshot from local legacy masters if necessary, then
runs `maintain-permanent-masters.py`. It compares locally known configurations with
snapshot sources and processes only the targeted queue. Existing Princess work
probes only known affected decks; a new configuration is bounded to decks 1–20.
Celebrity work is restricted to selected
configurations and uses new voyages first; verification without new voyages uses at
most one eligible prior voyage. Historical Princess configurations remain catalogued
even when absent from the current voyage feed.

Preview exact jobs without provider calls or state changes:

```powershell
python .\master\plan-permanent-maintenance.py `
  --snapshot-root .\work\state\static-masters\permanent-masters `
  --registry .\work\state\fleet-physical-configuration-registry-v1.2.json `
  --princess-voyages .\work\data\cruise-voyages-princess-v3.1.json `
  --out .\work\logs\permanent-master-plan.json
```

If targeted collection fails, the active snapshot remains unchanged and the stage
checkpoint is not written. Resume the same Daily after correcting the failure. If a
successful collection does not resolve a work item, it is recorded in
`static-masters/permanent-masters/maintenance-state.json` and is not called again
for the same snapshot and policy. To retry all stalled items deliberately:

```powershell
python .\master\maintain-permanent-masters.py <normal arguments> --retry-stalled
```

The pipeline supplies the normal arguments automatically. Use the direct command
only for diagnosis or an explicit retry. Full still performs bootstrap collection,
then publishes and assesses the permanent snapshot.
