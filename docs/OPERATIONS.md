# Operations

## Starting from zero

A clean Git clone needs Python, PowerShell, Internet access, and dependencies in `requirements.txt`. Do not copy any old `work/` directory, registry, survey, voyage JSON, cabin master, or cache into the clone.

Run `Full` once. It acquires voyages, normalizes them, surveys physical configurations, archives immutable runtime evidence, builds Registry V1.2, discovers static masters where evidence permits, and validates generated masters.

Run `Daily` thereafter. Existing Celebrity provider+ship+configuration masters are preserved; only newly proven configurations are candidates for static discovery. Provider voyage data and survey evidence are refreshed.

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

RC4 must not be promoted to 1.0.0 until this sequence succeeds from a virgin clone.
