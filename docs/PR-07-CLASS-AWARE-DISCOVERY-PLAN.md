# PR-07: class-aware discovery planning

## Objective

Reduce Full and Daily source-evidence calls by reusing the permanent class
masters and querying only unknown, changed, or contradictory evidence. Existing
raw evidence and provenance remain authoritative and are never deleted by this
work.

## Planned behavior

1. Build a local discovery index from the active permanent snapshot, completion
   assessment, registry, catalogs, and source hashes.
2. Map each supplied ship to its class; unmapped ships remain ship-specific.
3. Select class anchor evidence and derive field-level defaults only where the
   collected records agree. Ship membership and exceptions remain explicit.
4. Plan physical discovery by dimension:
   - new class or ship: bounded bootstrap discovery;
   - known ship with complete membership and matching physical revision: zero
     repeated physical calls;
   - missing field, contradiction, changed configuration, or scheduled refresh:
     targeted calls only.
5. Plan category definitions independently from physical facts.
6. Reuse cabin-category assignment revisions when the source hash and
   applicability match. Query assignments only for new configurations,
   changed assignment hashes, gaps, contradictions, or scheduled verification.
7. Continue collecting pricing and availability as dynamic sailing observations;
   they do not trigger static cabin discovery.
8. Emit planned, skipped, and executed counts by provider, class, ship,
   configuration, namespace, and reason. Preserve a durable plan and evidence
   hashes so an interrupted run can resume safely.

## Safety rules

- A class default never creates unobserved cabin membership.
- A missing or zero measurement remains unknown.
- Assignment changes do not create physical revisions.
- Provider configuration IDs do not independently establish a physical change.
- Conflicting evidence fails closed and remains in the targeted queue.
- A failed collector preserves the active snapshot and prior raw evidence.
- Existing source files are retained; this PR only suppresses avoidable future
  calls.

## Implementation sequence

1. Add a deterministic discovery-index and plan schema with namespace-specific
   hashes and explicit skip reasons.
2. Add offline plan generation and audit reports against the migrated snapshot.
3. Integrate the plan into Celebrity and Princess Full bootstrap paths.
4. Integrate assignment/category reuse separately from physical discovery.
5. Add restart, failure, class-exception, new-ship, and changed-assignment tests.
6. Measure request reduction against the PR-06 clean Full baseline.

## Acceptance criteria

- Unchanged completed sister ships produce zero physical discovery calls.
- New ships remain bounded and do not inherit unobserved membership.
- Category-only changes do not rebuild physical masters.
- Assignment-only changes update assignment revisions without physical calls.
- Missing fields and contradictions produce targeted work items.
- Interrupted plans resume without losing evidence or changing the active pointer.
- Full, Daily, Validate, and the complete regression suite pass.
- Reports show request counts and skipped-call reasons for both providers.

This document is the PR-07 plan. Collector behavior changes begin only after
this plan is reviewed and merged.
