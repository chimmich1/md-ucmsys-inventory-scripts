# PR-09 dynamic inventory observations plan

## Problem

The 1.0.0 release publishes canonical voyages and permanent physical,
category, and assignment masters. It does not yet publish the high-frequency
availability and pricing observations required by the universal inventory.
The archived Celebrity cabin adapter v1.5 proves the provider chain from a
sailing through room selection, a specific cabin, checkout, and price.

## Scope

PR-09 recovers that proven Celebrity capability into the current repository
without changing permanent-master semantics or copying the large archived
runtime output into Git. It will:

1. Define a provider-neutral observation envelope and Draft 2020-12 schema for
   voyage, market, occupancy, cabin availability, category pricing, checkout
   evidence, and source provenance.
2. Add an offline importer/compatibility path for the archived Celebrity v1.5
   observation and validation formats, preserving the original fields and
   evidence while producing the universal observation contract.
3. Add a current Celebrity observation collector using the proven
   `type-and-subtype`, `room-location`, and checkout calls. It must be explicit
   about selected-deck versus complete-category coverage and must fail closed
   when provider evidence is incomplete.
4. Store observations separately from permanent masters, keyed by voyage and
   observation time, with atomic output and validation. Dynamic observations
   must never promote or rewrite static master snapshots.
5. Add synthetic/offline regression tests for schema validation, archived
   conversion, exact-cabin versus category-sample pricing, partial deck
   inventory, checkout errors, and atomic failure behavior.
6. Update the user/operator documentation to state the daily universal-inventory
   contract and its current provider coverage. Princess dynamic acquisition is
   explicitly the next bounded provider PR; this PR must not pretend static
   Princess data is live availability or pricing.

## Acceptance

- Existing 1.0.0 tests and read-only Validate pass unchanged.
- A captured Celebrity fixture converts deterministically to the universal
  schema and retains checkout/price provenance and partial-inventory status.
- No live provider calls are used by tests or migration.
- A failed observation write leaves the prior observation file intact.
- Daily integration is opt-in/explicit until both provider adapters satisfy the
  same contract; static master publication remains independent.
- Output includes local ISO-8601 timestamps with UTC offsets for operation logs,
  and UTC observation timestamps where provider evidence requires them.

## Non-goals

PR-09 does not infer cabin membership from sister ships, merge dynamic data into
permanent physical masters, or implement the Princess cabin/pricing adapter.
Pricing/availability remains observation data and is never treated as static
cabin fact.
## Existing universal model input

The archive `D:\dev\github\_archives\universal-cruise-cabin-model-v1.1`
contains the canonical physical-cabin model, provider mapping matrix, migration
notes, and representative Celebrity/Princess examples. Its key boundary is
preserved: physical cabin, accommodation, service tier, commercial category, and
cabin-category assignment belong to static configuration masters; availability,
rooms-left, fare selectors, promotions, taxes, and prices belong to the separate
voyage/fare observation layer. PR-09 will use that v1.1 vocabulary and its
provenance/resolution rules when linking dynamic observations to static masters.
It will not copy the archive wholesale or duplicate its static-master schema. All dynamic acquisition in this sequence is JSON/API-only: no browser automation, DOM scraping, or rendered-page scraping. The production target is complete ship-wide availability with associated category pricing; exact-cabin checkout evidence remains additional provenance where the JSON API supplies it.
The archived mapping also records that Celebrity exact-cabin physical facts are
currently less resolved than Princess facts; unknowns must remain unknown.


