# PR-08: 1.0.0 release promotion

## Objective

Close the permanent-master roadmap and promote `1.0.0-rc5-hotfix3` to `1.0.0`
now that the clean-room Full/Validate/Daily/Validate sequence and the subsequent
class-aware, read-only verification have passed.

## Scope

1. Confirm PR-07 is merged and the working tree starts from current `main`.
2. Run the complete regression suite with the project-local Python environment.
3. Run root `Validate` against preserved migrated runtime state. Do not run Full,
   Daily, or contact either provider.
4. Change `VERSION` and the README title to `1.0.0`.
5. Consolidate the unreleased PR-01 through PR-07 notes under a dated `1.0.0`
   changelog heading without rewriting historical RC entries.
6. Update operations, roadmap, and handoff documentation with the final validation
   evidence and release status.
7. Prepare a reviewable release-promotion pull request. Tagging or publishing a
   GitHub release remains a separate explicit action after merge.

## Release evidence already established

- PR-06 clean-room Full, Validate, reuse-mode Daily, and final Validate passed in
  a separate checkout for snapshot `fd3ba17bd21cd53aecee93ec`.
- PR-07 changed offline planning and maintenance reporting; it did not broaden
  provider collection. Its 73-test suite and migrated-state read-only Validate
  passed for snapshot `02497c227cc9cc7fb008ede8`.
- Runtime `work/state` and `work/data` remain cumulative, ignored, and preserved.

## Known limitation

Fresh Celebrity acquisition can report 610 groups while returning 609 unique
groups. The collector fails closed and retains the previous validated artifact.
This is documented operational behavior; incomplete data must never be published.

## Acceptance criteria

- All tests pass on current merged `main`.
- Root Validate passes read-only against migrated state.
- `VERSION`, README, changelog, operations guide, roadmap, and handoff all identify
  `1.0.0` consistently.
- No provider calls, Full run, Daily run, runtime-state migration, tag, or release
  publication occurs in this PR.
