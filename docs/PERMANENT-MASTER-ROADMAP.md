# Permanent master collector: release roadmap

## Resume here

Approved direction: build durable class templates and ship exceptions from the
collected data, then maintain them through targeted discovery. Routine voyages
must not trigger repeated discovery of established physical cabin facts.

Current work: **PR-03, transactional permanent-master snapshots**.
Branch: `feat/pr03-transactional-master-snapshots`. Draft GitHub PR 4:
https://github.com/chimmich1/md-ucmsys-inventory-scripts/pull/4. PR-02 merged as
GitHub PR 3; PR-01 merged as GitHub PR 2. PR sequence numbers below are stable
roadmap IDs, not GitHub issue numbers. Each PR depends on the preceding merged PR
unless explicitly noted.

PR-01 implementation is ready for review: proposed contracts are documented in
`PERMANENT-MASTER-CONTRACT.md`; serialization and active snapshot publication
remain PR-03 work. The offline audit and regression tests are implemented.
PR-03 implementation is ready for review. Next action after merge: PR-04 defines
independent completeness and targeted-refresh policy. Do not call providers or
switch legacy collectors/readers as part of PR-03.

PR-03 verification: 55 tests pass. The saved evidence deterministically produced
snapshot `2f9195b160259a2fd5c34edd` twice under ignored `work/logs`, outside runtime
state: six provider/master documents plus a manifest. Compact physical documents
use class defaults and ship exceptions (Celebrity 9.8 MB; Princess 29.5 MB).
No provider calls, legacy catalog edits, or cumulative state writes were made.

Verification: 44 tests passed; read-only Validate passed for 32 Celebrity and
30 Princess configurations. Two audits produced identical report hashes.
Report: `work/logs/permanent-master-pr01/migration-audit.json` and `.md` (ignored).
Audit covered 62 masters/32 ships, six supplied classes and eight ship-only groups;
59,789 shared-field candidates and 2,097 variant fields. Inputs were hash-checked
before/after the audit; runtime state/data were not modified.

## Agreed design

1. **Physical Cabin master:** class-level cabin/deck/zone and physical-attribute
   defaults, confirmed ship membership, and field-level ship exceptions. Keep
   unknown values unknown. A cabin on one sister ship is not automatically a
   cabin on every sister ship. Physical changes create explicit revisions.
2. **Category/subcategory master:** reusable commercial definitions, versioned
   independently of physical layouts. Preserve meaningful code/definition
   differences; display spelling differences are not automatically new products.
3. **Cabin-category assignment master:** reusable assignment templates with
   ship-specific applicability and revisions. A commercial reassignment does not
   rebuild the physical master. Dates remain unknown unless supported by evidence.
4. **Evidence:** minimal source path/hash and verification time for published
   master revisions. Existing raw evidence is preserved in migration. The new
   permanent master does not require a voyage-to-cabin observation graph.
5. **Completion:** track membership, physical attributes, definitions, and
   assignments separately. Distinguish verified complete, incomplete, and
   discovery stalled. No-growth sampling alone does not prove completeness.
6. **Maintenance:** use saved masters in Daily. Collect for new ships, unknown
   cabins/categories, contradictory evidence, changed commercial assignments,
   physical changes, or an explicitly scheduled verification. Avoid blanket
   class-wide or voyage-wide recollection.

Use only local collected data for the analysis/migration work. The user supplied
the class groupings; do not perform internet research or provider calls to fill
gaps. Unmapped ships remain ship-specific until explicitly classified.

## Numbered PR sequence

| PR | Scope | Required acceptance | Status |
|---|---|---|---|
| **PR-01** | Persist this roadmap; define physical/category/assignment schema contracts; encode the supplied ship classes; implement offline migration audit with shared values, ship exceptions, unknowns, conflicts, and coverage gaps. | Synthetic regression tests; deterministic report against local masters; verify source hashes and no runtime input writes; existing Validate still passes. No collector behavior changes. | Merged (GitHub PR 2) |
| **PR-02** | Operational logging and provenance: fix PowerShell Git SHA early-pipeline termination; automatic timestamped run logs; replace progress bars with request counters; stage timing, retries, failure summaries, and current-vs-historical warnings. | PowerShell 5.1 tests for SHA capture, full stderr, progress reaching logs, failure exit codes, and read-only Validate. Test without live collection. | Merged (GitHub PR 3) |
| **PR-03** | Materialize the new three-master structure from existing evidence; class defaults plus confirmed membership/field overrides; explicit revision/applicability records; independent physical/commercial identities; transactional snapshot publication, restart and rollback support. | Old/new confirmed facts reconcile; exceptions and unknowns retained; no destructive migration; interrupted publish leaves a consistent active snapshot; new and legacy readers validate. | Ready for review |
| **PR-04** | Completion and refresh policy: independent coverage states, evidence-backed completeness checks, stalled discovery, manual refresh, periodic verification policy, and targeted discovery queue. | Unknown balcony size does not cause endless discovery; stalled is not complete; unchanged completed ships queue no physical calls; ambiguous evidence remains flagged. | Planned |
| **PR-05** | Integrate both providers into maintenance-mode Daily and bootstrap Full. Use shared templates without assuming unobserved cabin membership; enrich missing facts; process only queued work; commercial changes update commercial masters independently. | Mocked request-count tests prove zero cabin discovery on unchanged completed masters and bounded requests for targeted changes. Resume/failure tests preserve cumulative state. | Planned |
| **PR-06** | Release acceptance, operator commands, backup/restore and upgrade instructions, updated handoff, and final version promotion. Validate migrated state and monitored Daily; separately run clean-room Full/Validate/Daily/Validate. | Tests and both installation paths pass; request savings and unresolved gaps documented; no 1.0.0 claim until acceptance evidence exists. | Planned |

Tests and documentation accompany every PR; PR-06 is not a reason to defer
regression coverage. PR-02 is logically independent of the new schemas, but keep
its code separate from PR-01 for review. Do not merge PRs automatically.

## Collected-data findings that constrain the implementation

Analysis covered 32 Celebrity configurations/15 ships and 30 Princess
configurations/17 ships. Class comparisons used the user-supplied groupings.

- Sphere Sun/Star have identical cabin/deck/zone maps for 2,157 cabins, but 68
  cabin numbers differ in berth count. Sharing must be per field, not per whole row.
- Royal-class overlapping cabin/deck/zone assignments agree; physical attributes
  and cabin membership do have exceptions. Regal E123 records 236 square feet;
  the other five collected Royal-class ships record 303.
- Princess Grand-class maps have deck/zone exceptions; L201 is Lido deck 14 on
  Grand and deck 15 on Caribbean. Coral/Island differ in three cabin zones.
- Celebrity Edge-class has 137 cabin numbers with differing observed zones;
  Solstice-class has 62. Common deck mappings agree in those class comparisons.
- Princess retains area, berth count, accessibility, and bath type. All saved
  balcony dimension/area fields are zero: treat them as unknown, not measured zero.
- Celebrity physical masters do not contain per-cabin area or balcony dimensions.
  Sampled raw responses include generic category size ranges, not verified
  per-cabin measurements. Never substitute a category range for a cabin measurement.
- Category assignments change without deck changes: Grand E101 is OZ in version
  4 and OV in version 5; Ascent 11116 is C1 in configuration 2362 and C2 in 2425.
- Existing legacy saturation flags are not proof that every physical attribute
  or every cabin has been observed.

These findings describe the collected records, not independently verified physical
truth or proof of change dates. Differences can also reflect source corrections
or incomplete coverage. Never silently choose a conflicting value as fact.

## Runtime and session boundaries

- Preserve `work/state` and `work/data`. Do not run Full on this installation,
  delete old masters, or migrate published state during PR-01.
- Local analysis artifacts are under `work/logs` and must remain ignored by Git.
- The last completed Daily was `2026-09-20-daily-v1.0.0-rc5-hotfix3`: 2,023 Princess
  voyages; 1,896 Celebrity voyages; 32 Celebrity and 30 Princess masters validated.
  It advanced 16 Celebrity configurations, with 11 now legacy-saturated. Registry:
  1,341 observations, 697 voyages, 693 proven, 4 unproven, zero conflicts, 4 surveys.
- That run's Git SHA was UNKNOWN. Read-only reproduction identified the cause:
  `git rev-parse HEAD | Select-Object -First 1` produced the correct SHA but exit
  code -1 under PowerShell 5.1. The fix belongs to PR-02; it is not implemented yet.
- Python available for local checks:
  `C:/Users/MichelDuron/AppData/Local/Programs/Python/Python314/python.exe`.
- Before ending each implementation session, update this file's status, next
  action, branch/PR link, test results, and any unresolved decisions. Commit those
  updates with the work so a new session can resume without chat history.
