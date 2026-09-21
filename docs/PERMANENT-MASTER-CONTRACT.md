# Permanent master contracts (proposed v2)

Status: PR-01 design contract. Production continues to use the RC5 formats.
The offline audit proposes sharing; it does not publish or select these records.
PR-03 must implement and validate serialization against this contract before any
reader switches formats. All paths are relative to `work/state/static-masters`.

## Common revision envelope

Each master has `schemaVersion: "2.0"`, `kind`, `provider`, `revisionId`,
`contentSha256`, `sources`, and `coverage`. Revision IDs are immutable.
Content hashes exclude the hash field itself and use canonical sorted-key JSON.
Sources contain a relative `path`, SHA-256, and nullable `verifiedAt` timestamp.
Do not invent verification dates from filesystem modification dates.
Coverage is recorded separately for membership, attributes, category definitions,
and assignments: `UNVERIFIED`, `INCOMPLETE`, `DISCOVERY_STALLED`, or `COMPLETE`.
COMPLETE requires an explicit evidence reference and validation rule; a legacy
saturation flag alone is insufficient. Unknown measurements are null, never zero.

## Physical master: PHYSICAL_CABIN_MASTER

Identity is provider/class (or provider/ship for unmapped ships), independent of
commercial configuration IDs. Store:

- `classDefaults`: cabin number, field, value, supporting source references.
- `shipMembership`: ship, physical revision, confirmed cabin numbers, evidence.
- `shipFields`: ship, cabin, field, explicit value or null, evidence references.
- `conflicts`: competing observations that cannot yet be selected reliably.
- `applicability`: ship and known configuration references; effective dates may
  be null. Configuration references do not themselves create physical revisions.

Fields include deck number/name, zones, cabin area, balcony area/width/length,
berths, accessibility, bath type, and family-suite flag. A default is only usable
for a confirmed ship/cabin/field. Missing ship evidence is unknown, not permission
to inherit the default. Explicit null overrides a default. Field-level exceptions
take precedence; unresolved conflicting values cannot become a selected value.
Units for cabin and balcony area are square feet; dimension units must be stated
before publishing non-null widths/lengths. Preserve observed membership by source
configuration when deciding applicability; a historical union is not a current
configuration's complete membership.

## Category master: CATEGORY_DEFINITION_MASTER

Definitions retain provider codes, category/subcategory hierarchy, display names,
and source references. Reuse identical definitions across ships; preserve variant
definitions with their applicability. Pricing, availability, lead categories, and
candidate offers are not physical facts. Spelling variants remain reviewable;
PR-01 does not silently normalize them into one commercial product.

## Assignment master: CABIN_CATEGORY_ASSIGNMENT_MASTER

Templates map cabin numbers to observed category identities. Store independent
assignment revisions and ship/configuration applicability, referencing category
revisions and confirmed physical membership. Multiple observed assignments remain
sets until evidence identifies valid applicability. An assignment change creates
no physical revision unless physical facts also change. Partial observations must
not remove unobserved cabins or assignments. Effective dates remain null unless
supported by evidence.

## Publication and audit boundary

PR-03 will publish an immutable snapshot containing compatible revisions of all
three masters and then atomically switch its active pointer. Readers must never
mix snapshots. Restart must recover an interrupted publication without discarding
prior state. Existing catalogs and raw evidence remain available during migration.

PR-03 implements this as six documents, one physical/category/assignment set per
provider. The manifest binds their canonical hashes and `active-snapshot.json`
selects one manifest. It promotes and verifies the immutable directory before the
pointer update. The initial migrated coverage states are all `UNVERIFIED`, and
legacy catalogs remain authoritative until the later collector-integration PRs.

Completion assessments are derived and do not mutate an immutable snapshot.
COMPLETE requires a scoped proof. Physical completeness covers required fields for
confirmed membership and does not establish membership completeness. Stalled fields
have no proof and no automatic retry; their record names the manual or policy-change
condition. Category definitions remain unverified without an independent closed set.
Assignments may be complete for each observed source configuration even while
membership remains unverified.

PR-01's `migration-audit.json` is a separate report, schema version 1.0. It contains
source identities/hashes, observed ship membership, field-sharing candidates,
conflicting field values, category variants, and assignment comparisons. Its
`publishesMasters` value is always false. It intentionally makes no completeness
or effective-date claims. Source hashes are checked before and after analysis.
