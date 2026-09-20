# Universal Cruise Master Collector — 1.0.0-rc4

Code-only collector. The repository intentionally contains **no collected cruise data**. A fresh clone bootstraps its runtime state from provider sources.

## Quick start (PowerShell)

```powershell
python -m pip install -r requirements.txt
.\build-cruise-master.ps1 -Mode Full
.\build-cruise-master.ps1 -Mode Validate
.\build-cruise-master.ps1 -Mode Daily
.\build-cruise-master.ps1 -Mode Validate
```

`Full` starts with an empty `work/`. `Daily` reuses only locally generated state and discovers new Celebrity physical configurations as they become proven. `Validate` is read-only.

Celebrity physical configurations are proven from sailing-specific room-selection JSON. Princess physical configurations are keyed by the provider ship version attached to each acquired voyage; no current-page version is projected onto unrelated sailings.

See `docs/OPERATIONS.md`, `docs/ARCHITECTURE.md`, and `docs/FILE-REFERENCE.md`.
