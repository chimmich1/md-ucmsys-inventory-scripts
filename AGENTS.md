# Project instructions

- Active development plan: read `docs/PERMANENT-MASTER-ROADMAP.md` first and
  continue the numbered PR sequence. Update its status and next action before
  handoff. Local-only analysis/migration must not contact providers.
- Permanent-master publication promotes and verifies a complete immutable snapshot
  before atomically changing its active pointer. Preserve legacy catalogs during
  migration; absence of an active snapshot must remain valid until integration.
- Do not treat legacy saturation, no-growth sampling, or a file timestamp as a
  completeness proof. Stalled fields stay outside automatic refresh unless an
  operator, factory refresh, or changed evidence/policy explicitly requeues them.
- Daily permanent-master maintenance must process explicit source/configuration jobs
  only. Preserve the active snapshot on collection failure and retain historical
  catalog entries. No-progress work is stalled after one attempt for that snapshot
  and policy; never bypass this by restoring broad voyage-wide cabin discovery.
- Class-aware discovery plans must match the active snapshot assessment. Reuse
  completed namespace evidence, retain ship-only fallback for unmapped ships, and
  never infer unobserved cabin membership from a sister ship.
- Read README.md, VERSION, CHANGELOG.md, docs/PROJECT-HANDOFF.md, and relevant
  documentation before changes. Inspect Git status and history; preserve user edits.
- `work/state` and `work/data` are required cumulative runtime state, not disposable
  fixtures. Do not delete, reset, rebuild, or run Full against them without explicit
  user authorization. Keep runtime data ignored by Git. Use synthetic temporary
  directories for tests and a separate empty checkout for release acceptance.
- Validate must remain read-only, with no provider calls or checkpoint writes.
  For catalog recovery use `master/reconcile-catalogs.py --state work/state`, then
  Validate. Do not silently repair catalogs within Validate.
- Catalog paths for both providers are relative to `state/static-masters` with
  forward slashes. Legacy absolute paths must resolve within the selected local
  state, even if the old workspace is still accessible.
- Reconcile all existing Celebrity catalog entries from published masters and
  validation reports, including skipped and no-longer-current configurations.
  Preserve complete tested-voyage history and raw evidence across Daily increments.
  Fail closed for inconsistent published evidence; never infer cabin decks or
  physical configurations from unrelated sailings.
- Publish catalog JSON atomically. Preserve full native stderr under Windows
  PowerShell 5.1 before failing on a nonzero exit code; use pipeline/invoke-native.ps1.
- Invoke the root script for operational runs so output is automatically copied to
  a timestamped `work/logs` file. Do not reintroduce `Write-Progress`; progress and
  request summaries must be durable log lines.
- Preserve the root logger's ISO 8601 local-time prefix, including its UTC offset, on every emitted line. New logging
  paths must provide equivalent timestamps so request and stage slowness is auditable.
- Run `python -m pytest tests -q` after behavioral changes. It includes both legacy
  registry script regressions. Run the root pipeline's Validate on migrated state
  when available, and report skipped checks or limitations accurately.
- Keep VERSION, README, CHANGELOG, operations documentation, and PROJECT-HANDOFF
  aligned with the implemented behavior. Do not promote 1.0.0 without the documented
  clean-room Full/Validate/Daily/Validate acceptance sequence.
