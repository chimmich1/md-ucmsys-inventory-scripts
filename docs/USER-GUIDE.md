# Universal Cruise Master Collector 1.0.0 — user guide

This guide describes the released collector, its PowerShell entry point, offline
maintenance tools, runtime directories, and the JSON files that downstream users
can safely consume.

Machine-readable Draft 2020-12 schemas are in `schemas/`; see
`schemas/README.md` before implementing an importer.

## 1. What the system produces

The collector acquires and normalizes Princess Cruises and Celebrity Cruises
voyages, records source evidence, builds provider-specific cabin/category masters,
and publishes an immutable permanent-master snapshot. It keeps raw evidence and
historical configurations so a later Daily run can target only changed or missing
work.

The repository contains code and documentation only. Collected data is intentionally
ignored by Git and normally lives under `work/data` and `work/state`.

There are three useful distinctions:

1. `work/data` contains canonical voyages and provider acquisition artifacts.
2. `work/state` contains cumulative evidence, registry, legacy masters, catalogs,
   checkpoints, and published snapshots.
3. `work/logs` contains timestamped operational logs and operator-selected reports.

Do not delete, reset, rebuild, or copy only part of `work/data` or `work/state`.
They are cumulative state, not disposable fixtures.

## 2. Installation

Use Python 3.14 or a compatible supported Python, Windows PowerShell 5.1 or later,
and network access for `Full` and normal `Daily` acquisition. A project-local
virtual environment avoids user-profile package visibility issues:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pytest
```

Use the same interpreter for the root pipeline with `-Python`:

```powershell
\.build-cruise-master.ps1 -Mode Validate `
  -Python (Resolve-Path .\.venv\Scripts\python.exe)
```

The actual command has no leading dot before the path:

```powershell
.\build-cruise-master.ps1 -Mode Validate `
  -Python (Resolve-Path .\.venv\Scripts\python.exe)
```

## 3. Root command

Always use `build-cruise-master.ps1` for operational runs. It creates a timestamped
log, prefixes every emitted line with an ISO 8601 local timestamp and UTC offset,
copies complete child stdout/stderr to the console and log, and returns the child
exit code after the log is drained.

```powershell
.\build-cruise-master.ps1 -Mode <Full|Daily|Validate> [options]
```

Root options:

| Option | Default | Meaning |
|---|---|---|
| `-Mode` | `Daily` | `Full` bootstraps an empty installation; `Daily` refreshes explicit queued work; `Validate` is read-only. |
| `-DataDir <path>` | `work/data` | Canonical voyages and provider acquisition artifacts. |
| `-StateDir <path>` | `work/state` | Registry, masters, catalogs, checkpoints, and permanent snapshots. |
| `-SurveyStart <yyyy-MM-dd>` | Today | Start date used by the fleet survey and run key. |
| `-Python <path>` | `python` | Python executable passed to every Python stage. |
| `-RegistryPath <path>` | `StateDir/fleet-physical-configuration-registry-v1.2.json` | Alternate Registry V1.2 location. |
| `-ReuseAcquiredVoyages` | Off | Reuse existing provider acquisition artifacts; skips provider voyage acquisition but still normalizes and runs downstream stages. |
| `-ResumeAtCelebrityMasters` | Off | `Daily` resume switch; skips acquisition, normalization, survey, and registry import and starts at Celebrity masters. |
| `-ResumeAtPrincessMasters` | Off | `Full` resume switch after completed Celebrity masters; starts at Princess masters. |
| `-SkipVoyageRefresh` | Off | Skip voyage acquisition. Existing canonical files must already exist. |
| `-RestartRun` | Off | Delete checkpoints for the current date/mode/version run key and rerun stages. Use only when intentionally restarting. |
| `-LogPath <path>` | `work/logs/<mode>-v<version>-<timestamp>.log` | Explicit operational log path. |

Examples:

```powershell
# Fresh empty installation only
.\build-cruise-master.ps1 -Mode Full -Python .\.venv\Scripts\python.exe

# Normal incremental maintenance
.\build-cruise-master.ps1 -Mode Daily -Python .\.venv\Scripts\python.exe

# Read-only integrity check
.\build-cruise-master.ps1 -Mode Validate -Python .\.venv\Scripts\python.exe

# Continue after acquisition completed but a later Full stage failed
.\build-cruise-master.ps1 -Mode Full -ReuseAcquiredVoyages `
  -Python .\.venv\Scripts\python.exe

# Continue a Full run after Celebrity masters completed
.\build-cruise-master.ps1 -Mode Full -ResumeAtPrincessMasters `
  -Python .\.venv\Scripts\python.exe

# Continue a Daily run at Celebrity masters
.\build-cruise-master.ps1 -Mode Daily -ResumeAtCelebrityMasters `
  -Python .\.venv\Scripts\python.exe
```

Never use `Full` against an existing cumulative installation. Use `Daily` for
maintenance. `Validate` does not create checkpoints or repair files.

## 4. Catalog repair and relocation

After moving a working copy or after an interrupted Celebrity increment, repair
catalog metadata before Validate:

```powershell
.\.venv\Scripts\python.exe master/reconcile-catalogs.py `
  --state work/state
.\build-cruise-master.ps1 -Mode Validate `
  -Python .\.venv\Scripts\python.exe
```

The repair is offline. It updates catalog paths, SHA-256 values, and saturation
from published masters and validation files. New catalog paths are forward-slash
paths relative to `work/state/static-masters`. Legacy absolute paths remain
accepted when they resolve inside the selected state tree. Missing or conflicting
evidence fails closed.

## 5. Offline permanent-master tools

These tools do not contact providers. Write reports under `work/logs`, never under
`work/data` or the active snapshot directory.

### Audit existing evidence

```powershell
.\.venv\Scripts\python.exe master/audit-permanent-masters.py `
  --state work/state `
  --classes config/ship-classes.json `
  --out-dir work/logs/permanent-master-audit
```

Produces deterministic JSON/Markdown analysis of shared fields, conflicts,
unknowns, classes, category definitions, and assignment differences.

### Materialize or verify a permanent snapshot

```powershell
.\.venv\Scripts\python.exe master/materialize-permanent-masters.py `
  --state work/state
.\.venv\Scripts\python.exe master/activate-permanent-master-snapshot.py `
  --state work/state --snapshot <snapshotId>
```

Materialization publishes a complete immutable directory before changing the
active pointer. Activation verifies the selected manifest first. These commands
are migration/administrative operations; do not use them casually on production
state.

### Assess completion and queue work

```powershell
.\.venv\Scripts\python.exe master/assess-permanent-masters.py `
  --snapshot-root work/state/static-masters/permanent-masters `
  --out work/logs/permanent-master-assessment.json
```

Options:

| Option | Meaning |
|---|---|
| `--snapshot-root <path>` | Permanent-master root containing `active-snapshot.json`. Required. |
| `--policy <path>` | Refresh policy; defaults to `config/permanent-master-refresh-policy.json`. |
| `--out <path>` | Assessment JSON destination. Required. |
| `--manual-target PROVIDER/SHIP` | Add an explicit physical verification target; repeatable. |
| `--factory-refresh-target PROVIDER/SHIP` | Add a factory-refresh physical target; repeatable. |

Unknown required fields and contradictions become targeted queue items. Stalled
fields remain stalled and are not automatically requeued.

### Plan class-aware reuse

```powershell
.\.venv\Scripts\python.exe master/plan-class-aware-discovery.py `
  --snapshot-root work/state/static-masters/permanent-masters `
  --classes config/ship-classes.json `
  --assessment work/logs/permanent-master-assessment.json `
  --out work/logs/class-aware-discovery-plan.json
```

The assessment must match the active snapshot ID. The report identifies
`TARGET_QUEUED` and `SKIP_REUSED_EVIDENCE` by provider, class, ship, source, and
namespace. Unmapped ships use `ship:<code>` groups. Class membership never creates
an unobserved cabin.

### Preview or execute Daily maintenance

Preview jobs without provider calls:

```powershell
.\.venv\Scripts\python.exe master/plan-permanent-maintenance.py `
  --snapshot-root work/state/static-masters/permanent-masters `
  --registry work/state/fleet-physical-configuration-registry-v1.2.json `
  --princess-voyages work/data/cruise-voyages-princess-v3.1.json `
  --out work/logs/permanent-master-plan.json
```

The pipeline normally invokes maintenance automatically. Direct execution accepts
the same source paths plus provider-specific voyage paths, `--state`, `--data`,
`--celebrity-voyages`, `--princess-voyages`, `--registry`, `--python`, `--out`,
and optional `--retry-stalled`. Use `--retry-stalled` only after changed evidence,
policy, or an explicit operator decision.

## 6. Final JSON outputs

### Canonical voyage files — `work/data`

| File | Use | Main shape |
|---|---|---|
| `cruise-voyages-princess-v3.1.json` | Normalized Princess voyages used by masters and consumers. | `{schemaVersion, generatedAt, voyages[]}` |
| `cruise-voyages-celebrity-v3.1.json` | Normalized Celebrity voyages. | `{schemaVersion, generatedAt, voyages[]}` |
| `celebrity-voyages-raw.json` | Validated raw Celebrity acquisition artifact. | Provider response/evidence; retain for recovery and audit. |
| `princess-products.json`, `princess-ports.json`, `princess-ships.json`, `princess-itineraries.json` | Provider acquisition inputs and normalized supporting data. | Provider-specific JSON; not permanent-master contracts. |
| `celebrity-port-country.json` | Celebrity port/country enrichment. | Enrichment map used during normalization. |

Consumers should use the canonical V3.1 files for voyage-level work. Raw and
supporting files are evidence or pipeline inputs and may change on acquisition.

### Registry and surveys — `work/state`

| File | Use | Main shape |
|---|---|---|
| `fleet-physical-configuration-registry-v1.2.json` | Durable proof linking voyages to physical configurations. | `{version, kind, surveys[], observations[], voyages{}, conflicts[], statistics}` |
| `fleet-timeline-current/celebrity-fleet-timeline-v1.0.json` | Current Celebrity survey result before registry import. | Survey document with observations and provenance. |
| `fleet-timeline-current/princess-fleet-timeline-preflight-v1.0.json` | Princess configuration-era preflight. | Voyage/version-derived configuration evidence. |
| `source-surveys/celebrity/sha256-*.json` | Immutable archived survey evidence. | Content-addressed survey JSON. |

The registry is the evidence index. A registry saturation flag is not, by itself,
proof that every cabin or physical field is complete.

### Legacy provider masters — `work/state/static-masters`

Each Celebrity configuration is under `celebrity/<ship>/<configuration>/`; Princess
configuration files are under the Princess catalog paths. These remain usable for
legacy consumers and are preserved during permanent-master migration.

Typical provider files are:

- `celebrity-cabin-master-<ship>-v2.2.json`: cabin/deck/physical records.
- `celebrity-category-master-<ship>-v2.2.json`: category and subcategory definitions.
- `celebrity-cabin-category-assignments-<ship>-v2.2.json`: cabin-to-category assignments.
- `celebrity-ship-master-<ship>-v2.2.json`: combined provider master document.
- `celebrity-ship-master-validation-<ship>-v2.2.json`: validation, conflicts,
  failures, voyage evidence, and saturation status.
- `celebrity-configuration-saturation-voyage-report-v2.2.json`: tested-voyage
  history and saturation evidence.
- `raw/`: original provider responses; retain them as evidence.

The combined ship master has fields such as `provider`, `shipCode`,
`targetConfiguration`, `configurations`, `cabins`, `categoryAssignments`,
`categoryMaster`, and `saturation`. The standalone cabin/category/assignment files
are arrays or provider-native structures; inspect their version and provenance
fields before building a consumer.

### Catalogs

| File | Use |
|---|---|
| `static-masters/celebrity-catalog.json` | Celebrity configuration identity, relative master path, SHA-256, validation path, and saturation metadata. |
| `static-masters/princess/catalog.json` | Princess voyage-bound configuration identities and master paths. |
| `static-masters/celebrity-manifest.json` | Celebrity manifest and catalog reference. |

Catalogs are indexes, not cabin data. Resolve the catalog path, verify its hash,
then read the referenced master and validation files.

### Permanent-master snapshot — authoritative new model

The active pointer is:

```text
work/state/static-masters/permanent-masters/active-snapshot.json
```

It contains `schemaVersion`, `snapshotId`, and `manifestPath`. Resolve the manifest
under `permanent-masters/snapshots/<snapshotId>/` and verify all listed hashes.
The manifest contains `files`, `contentSha256`, and the snapshot publication
metadata.

Each complete snapshot contains six consumer-facing documents:

| File | Meaning | Main fields |
|---|---|---|
| `celebrity-physical.json` | Celebrity cabin/deck/zone/physical master with class defaults and explicit ship membership/exceptions. | `provider`, `revisionId`, `sources`, `coverage`, `groups` |
| `princess-physical.json` | Princess physical cabin master. | Same physical contract, with Princess source/configuration evidence. |
| `celebrity-categories.json` | Celebrity category/subcategory definitions independent of physical layout. | `provider`, `revisionId`, `sources`, `coverage`, `definitions` |
| `princess-categories.json` | Princess category definitions. | Same category contract. |
| `celebrity-assignments.json` | Celebrity cabin-category assignment revisions and applicability. | `provider`, `revisionId`, `sources`, `coverage`, `revisions` |
| `princess-assignments.json` | Princess assignment revisions and applicability. | Same assignment contract. |

`coverage` records completion status and scoped proof. `sources` records evidence
paths/hashes. `revisionId` is namespace-specific: a commercial assignment change
does not silently rewrite the physical revision. Unknown values remain unknown;
zero measurements are not treated as measured values.

The consumer schemas are:

| Schema | Validates |
|---|---|
| `schemas/canonical-voyages-v3.1.schema.json` | Both canonical voyage files. |
| `schemas/fleet-registry-v1.2.schema.json` | The V1.2 physical-configuration registry. |
| `schemas/catalog.schema.json` | Both provider catalogs. |
| `schemas/permanent-master-active-snapshot.schema.json` | The active snapshot pointer. |
| `schemas/permanent-master-manifest.schema.json` | A published snapshot manifest. |
| `schemas/permanent-physical-master.schema.json` | Both physical snapshot documents. |
| `schemas/permanent-category-master.schema.json` | Both category snapshot documents. |
| `schemas/permanent-assignment-master.schema.json` | Both assignment snapshot documents. |

The schemas validate stable envelopes and integrity metadata while allowing
provider-native records to gain additive fields. An importer should reject an
unknown schema version, verify manifest SHA-256 values, retain `sources` as
provenance, and treat absent or unknown measurements as unknown rather than zero.

### Run and maintenance reports

Every Full/Daily run creates `work/state/runs/<run-key>/` with:

- `run-manifest.json`: pipeline version, Git SHA, mode, survey date, timestamps,
  and SHA-256 hashes of canonical input files.
- stage checkpoint markers (`*.complete`, `*.started`, `*.failed`) used for resume.
- `permanent-master-maintenance.json` in Daily: jobs, resulting snapshot, stalled
  count, remaining queue summary, and `classAwareDiscovery` reuse decisions.

The root wrapper writes the complete timestamped console log to `work/logs`. Logs
are the right place to measure request cadence, retries, stage duration, and failure
context. Do not use PowerShell `Write-Progress` output as an operational record.

## 7. Safe consumption rules

- Read canonical voyages for voyage-level schedules and prices.
- Read permanent snapshot documents for current static cabin/category/assignment
  masters.
- Use legacy provider files only when a consumer still requires their native schema.
- Keep `raw/`, surveys, validation reports, and catalogs as provenance; do not edit
  them by hand.
- Do not infer a cabin's membership on a sister ship solely from its class.
- Treat pricing and availability as dynamic sailing observations, separate from
  static physical/category/assignment masters.
- If validation fails, preserve the active snapshot and investigate the evidence;
  never delete state to make validation pass.

## 8. Troubleshooting

If `python` is not found, pass the full interpreter path with `-Python`. If pytest
cannot access the user-profile temporary directory, run it with the project venv
and `--basetemp .pytest-tmp`.

If a run stops after acquisition, use `-ReuseAcquiredVoyages`. If it stops after
Celebrity masters during Full, use `-ResumeAtPrincessMasters`. If it stops during
Daily Celebrity work, use `-ResumeAtCelebrityMasters`. For catalog path/hash
problems, run `reconcile-catalogs.py` and then read-only Validate. Never repair
catalogs inside Validate and never run Full against migrated state.

For a fresh Celebrity pagination mismatch, the collector is intentionally fail
closed. Preserve the previous validated artifact, retain the complete stderr/log,
and retry only after the source response is complete and internally consistent.

## Dynamic inventory observations

PR-09 introduces the universal observation envelope in schemas/inventory-observation-v1.1.schema.json. Archived Celebrity v1.5 records can be converted with observations/celebrity_v15_to_universal.py; observations retain availability, pricing, checkout evidence, provenance, and partial-deck status separately from permanent masters.
