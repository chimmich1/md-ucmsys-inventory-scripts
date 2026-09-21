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
complete Python tracebacks under Windows PowerShell 5.1. Stage completion/failure
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
# Offline permanent-master planning

Run `python master/audit-permanent-masters.py --state work/state --out-dir work/logs/permanent-master-pr01`
to compare saved masters using `config/ship-classes.json`. Review both report files.
Shared-field candidates are evidence-based proposals, not automatic inheritance.
Conflicts and unknowns require explicit migration decisions. Legacy saturation
does not establish completeness. Audit output must be outside state and data.
PR-01 does not migrate state or change Daily. See `PERMANENT-MASTER-ROADMAP.md`
for the remaining numbered PRs and `PERMANENT-MASTER-CONTRACT.md` for contracts.
