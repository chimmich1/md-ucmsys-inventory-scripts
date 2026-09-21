# File reference

| Path | Purpose | Runtime writes? |
|---|---|---|
| `build-cruise-master.ps1` | Stable root entry point; forwards parameters to pipeline. | No |
| `pipeline/build-cruise-master.ps1` | Full/Daily orchestration and read-only Validate entry. | Full/Daily only |
| `voyages/princess-inventory.ps1` | Princess voyage acquisition. | `work/data` |
| `voyages/celebrity-inventory.ps1` | Celebrity GraphQL voyage acquisition. | `work/data` |
| `voyages/celebrity-inventory.py` | Fresh browser-impersonated, paginated Celebrity transport with atomic validated publishing. | `work/data` |
| `voyages/build-celebrity-port-country.ps1` | Celebrity port/country enrichment. | `work/data` |
| `voyages/cruise-voyage-normalizer-v3.1.ps1` | Provider-to-canonical voyage normalization. | `work/data` |
| `fleet/timeline/celebrity-fleet-timeline-v1.0.py` | Future target-sailing physical configuration survey. | `work/state` |
| `fleet/timeline/princess-fleet-timeline-preflight-v1.0.py` | Builds Princess configuration eras from provider versions attached to canonical voyages. | `work/state` |
| `fleet/registry/archive-and-import-survey-v1.0.py` | Content-addresses survey and appends Registry V1.2. | `work/state` |
| `fleet/registry/fleet-configuration-registry-v1.2.py` | Durable evidence registry. | `work/state` |
| `master/build-static-masters.py` | Builds missing Celebrity masters, advances unsaturated configurations, and reconciles all catalog entries. | `work/state/static-masters` |
| `master/catalog_state.py` | Local catalog path resolution, atomic JSON publishing, and metadata reconciliation. | Caller-selected catalogs |
| `master/reconcile-catalogs.py` | Offline catalog recovery and relocation without collection. | Two catalogs and Celebrity manifest only |
| `master/materialize-permanent-masters.py` | Builds and transactionally activates an immutable proposed permanent-master snapshot from local evidence. | `static-masters/permanent-masters` |
| `master/activate-permanent-master-snapshot.py` | Verifies and atomically activates an existing snapshot for rollback. | Permanent-master active pointer |
| `master/assess-permanent-masters.py` | Evaluates independent completion dimensions and writes a targeted offline refresh queue. | Caller-selected report |
| `master/permanent_master_policy.py` | Applies required/stalled fields, proofs, conflicts, assignments, and explicit refresh triggers. | None (pure assessment) |
| `master/maintain-permanent-masters.py` | Executes grouped Daily queue jobs, republishes changed snapshots, and records no-progress work. | Legacy target masters, permanent snapshot, maintenance report/state |
| `master/plan-permanent-maintenance.py` | Previews exact Daily jobs without provider calls or state changes. | Caller-selected plan report |
| `master/plan-class-aware-discovery.py` | Audits class/ship evidence reuse and queued namespaces against a matching active-snapshot assessment. | Caller-selected plan report |
| `master/permanent_master_maintenance.py` | Pure planning plus bounded provider-builder orchestration. | Through explicitly invoked builders |
| `config/permanent-master-refresh-policy.json` | Required fields, stalled fields, allowed triggers, and periodic verification intervals. | Policy input |
| `master/permanent_master_snapshot.py` | Deterministic snapshot construction, publication, restart recovery, and validation. | Caller-selected snapshot root |
| `pipeline/invoke-native.ps1` | Preserves complete native stderr before checking exit codes. | No |
| `master/providers/celebrity/configuration-discovery.py` | Configuration-aware Celebrity cabin/category saturation collector. | Caller-selected runtime directory |
| `master/build-princess-published-masters.py` | Enumerates voyage-bound Princess ship/version configurations. | `work/state/static-masters` |
| `master/providers/princess/published-deck-collector.py` | Collects provider-confirmed Princess deck JSON for one exact ship/version. | Caller-selected runtime file |
| `master/validate-masters.py` | Hash/integrity validation; no writes. | No |
| `master/universal/*.py` | Universal Cabin Model adapters retained for provider-neutral transformation work. | Caller-selected output |
| `diagnostics/legacy/*` | Diagnostics only; never Full/Daily. | Not by pipeline |
| `tests/*` | Deterministic registry, provider, catalog recovery/relocation, and Windows stderr regressions; production snapshots must not be fixtures. | Temporary test dirs only |
| `requirements.txt` | Python runtime dependencies. | No |
| `VERSION` | Pipeline/release version. | No |
| `docs/USER-GUIDE.md` | Complete installation, operation, option, output, schema, and troubleshooting guide. | No |
| `schemas/` | Draft 2020-12 consumer schemas for canonical voyages, registry, catalogs, snapshot metadata, and permanent masters. | No |
