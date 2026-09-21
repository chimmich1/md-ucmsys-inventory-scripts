# Cruise-master project handoff

## Active next steps`r`n`r`nPR-09 is the active next step: recover the archived Celebrity v1.5 dynamic availability/pricing adapter into a provider-neutral observation contract. The plan is committed in [PR-09-DYNAMIC-OBSERVATIONS-PLAN.md](PR-09-DYNAMIC-OBSERVATIONS-PLAN.md). The archived source remains outside the repository under `D:\dev\github\_archives\celebrity-cabin-adapter-v1.5`; do not modify or copy its 47 MB output into Git. First inspect and adapt the script, then add schemas, synthetic tests, and documentation. Princess dynamic cabin/pricing acquisition is a later bounded provider PR.`r`n`r`n## Current source

- Stabilization release promoted to `1.0.0` by PR-08; the RC5 history remains in
  the changelog for provenance.
- Starting Git baseline: `776cbfe` (portable RC5 incremental pipeline), clean
  `main` working tree before this stabilization work.
- Source and migrated runtime state are now in the main checkout. The separate
  `md-ucmsys-inventory-scripts-1.0-rc1-test` folder is not the authoritative target
  for validation or further source changes.

## Incident and correction

An interrupted RC5 increment promoted Celebrity masters and cumulative validation
reports before publishing celebrity-catalog.json. A restart skipped already-tested
configurations, leaving stale hashes (observed for AT/2362). The migrated catalog
had already received the manual hash repair, but both catalogs still contained
absolute paths into the old test workspace.

Daily now reconciles every catalog entry from the local published master/report
pair before provider collection, including configurations absent from the current
registry and configurations skipped as saturated or fully tested. Completed
configurations missing from the catalog are recovered from registry identities.
Each completed configuration triggers atomic catalog publication. Restarting
after promotion but before publication repairs metadata without replaying tested
voyages. Missing or conflicting published evidence fails closed.

Both provider catalogs publish forward-slash paths relative to
`work/state/static-masters`. Legacy Windows, UNC, and POSIX absolute paths map to
local provider/ship/configuration files regardless of whether the old tree exists.
Validation never falls back to that old tree. Relative Windows separators are
accepted too. Validate remains read-only and requires the Celebrity catalog.

`master/reconcile-catalogs.py --state work/state` performs offline recovery:
Celebrity paths/hashes/saturation, Princess path relocation with existing hash
verification, and the Celebrity manifest's catalog reference. It changes no
masters, reports, raw evidence, registry, voyages, or checkpoints. Each document
replacement is atomic; the whole multi-document operation is safely repeatable.

`pipeline/invoke-native.ps1` preserves all native stderr before checking exit codes,
including Python tracebacks under Windows PowerShell 5.1 and Tee-Object. The
pipeline stages, child PowerShell calls, and Celebrity acquisition wrapper use it.

## Verification

- Python 3.14.3, pytest 9.1.1, Windows PowerShell 5.1.
- `python -m pytest tests -q`: **34 passed**, no skipped tests on this Windows host.
- Coverage includes both providers after relocation, old paths still accessible,
  Windows/POSIX/UNC and relative separators, interrupted increments followed by
  saturated or already-tested skips, retired entries, atomic catalog write failure,
  incomplete/conflicting evidence, offline repair idempotency, and complete native
  traceback capture. Both historical registry scripts run through pytest.
- Catalog-only migration completed: 32 Celebrity entries reconciled and 30
  Princess entries relocated to relative paths.
- Root `build-cruise-master.ps1 -Mode Validate` passed using the explicit Python
  3.14 executable: 2,023 Princess voyages, 1,908 Celebrity voyages, 32 Celebrity
  configurations, and 30 Princess configurations.
- SHA-256 audit of **66,692 runtime files** found changes only in
  `static-masters/celebrity-catalog.json`, `static-masters/princess/catalog.json`,
  and `static-masters/celebrity-manifest.json` under `work/state`. No runtime files
  were added or removed. All other file contents were unchanged. A separate
  file-size/mtime inventory confirmed Validate made no runtime writes.
- The ignored audit baseline and local verification script are in `work/logs`
  (`rc5-stabilization-before.json` and `rc5-stabilization-audit.py`). They are local
  verification artifacts, not production fixtures or source files.
- Full and Daily were not run against real runtime state; no provider calls were
  made. `git diff --check` passed.

## Migrated runtime inventory

- Canonical files and provider artifacts are present in `work/data`.
- Celebrity catalog: 32 configurations, 5 saturated and 27 unsaturated.
- Princess catalog: 30 voyage-bound configurations.
- Registry V1.2: 1,007 observations, 561 voyages, 559 proven, 2 unproven,
  0 conflicts, 3 archived surveys.
- Runtime state occupies approximately 13.1 GB. It is intentionally ignored by Git
  and must be preserved independently of source control.

## Operational boundaries and remaining acceptance

Do not run Full or delete/rebuild `work/state` or `work/data` in this installation.
Use catalog-only repair and Validate for relocation/recovery. If continuing an
interrupted collection, use `-Mode Daily -ResumeAtCelebrityMasters`; version changes
create a new checkpoint key, so do not assume old-version checkpoints will apply.
Do not add `-RestartRun` unless intentionally discarding current-run checkpoints.

PR-06 acceptance used a separate clean checkout. Full completed with 32 Celebrity
and 30 Princess configurations; reuse-mode Daily and final Validate passed against
snapshot `fd3ba17bd21cd53aecee93ec`. A fresh Celebrity acquisition can still fail
closed at the pagination boundary when the provider reports 610 groups but returns
609 unique groups; the previous valid raw artifact is preserved and must not be
silently replaced by incomplete data.

PR-07 implementation is the active change. Read
`docs/PR-07-CLASS-AWARE-DISCOVERY-PLAN.md` before modifying collector behavior.
Multi-file master promotion is still not one atomic filesystem transaction;
reconciliation addresses a completed promotion followed by interrupted catalog
publication, not arbitrary corruption or every possible partial-file promotion.


