# Cruise-master project handoff

## Active next steps

PR-01 merged as GitHub PR 2. PR-02 is implemented on
`fix/pr02-operational-logging`: automatic timestamped root logs, complete failure
logs and exit codes, safe Git SHA capture, stage timing, Princess request counters,
and current-versus-historical Celebrity failure labels. All 49 tests pass under
Python 3.14/Windows PowerShell 5.1; read-only Validate passes all 62 masters and
writes only its selected ignored log. No provider calls were made. After PR-02
review/merge, continue PR-03 transactional three-master materialization.

The approved permanent-master redesign is tracked in
[PERMANENT-MASTER-ROADMAP.md](PERMANENT-MASTER-ROADMAP.md). It defines six numbered
PRs, acceptance checks, data constraints, and the exact next action. Start there
in a new session. PR-01 is the schema and offline migration audit; production
collection remains RC5-hotfix3 until later integration PRs.

After the stabilization described below, the first monitored Daily completed:
2,023 Princess voyages, 1,896 Celebrity voyages, 16 Celebrity configurations
advanced, 11 legacy-saturated masters, all 32 Celebrity and 30 Princess masters
validated. Four registry voyages remain unproven and zero conflicts were recorded.
The earlier Daily's UNKNOWN Git SHA was corrected in PR-02; its historical manifest
is not rewritten. The verification and inventory sections below record the earlier
stabilization baseline.

## Current source

- Stabilization release: `1.0.0-rc5-hotfix3`.
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

No live Full/Daily provider collection is part of this stabilization. Before 1.0.0,
run the documented Full/Validate/Daily/Validate release acceptance sequence in a
separate empty checkout. The preserved main state must not be used for that test.
Multi-file master promotion is still not one atomic filesystem transaction;
reconciliation addresses a completed promotion followed by interrupted catalog
publication, not arbitrary corruption or every possible partial-file promotion.
