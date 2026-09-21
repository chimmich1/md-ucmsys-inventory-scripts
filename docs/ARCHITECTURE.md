# Architecture

The system separates provider acquisition, canonical voyage normalization, configuration evidence, static ship masters, and later high-frequency availability/pricing observations.

## Transactional permanent-master snapshots

PR-03 adds an offline materializer under `master/materialize-permanent-masters.py`.
It derives six independent revision documents from verified legacy catalog inputs.
A manifest binds their hashes. Publication writes and verifies a staging directory,
renames the complete directory to its immutable snapshot ID, then atomically writes
one active pointer. An interruption before the pointer leaves the prior snapshot
active; rerunning verifies the promoted directory and completes activation.
Legacy catalogs and readers remain valid when no active pointer exists.

PR-04 derives completion and refresh work without changing the immutable snapshot.
The evaluator binds its output to the active snapshot ID and policy hash. It builds
effective physical values from class defaults plus ship exceptions, checks required
fields only for confirmed membership, flags ambiguous observations, and compares
source membership with independent assignment revisions. Optional unavailable
measurements are stalled outside the automatic queue. Operator and factory-refresh
targets are explicit inputs; periodic work remains unscheduled until evidence has
a supported verification date.

PR-05 makes Daily queue-driven. It derives locally known configurations from the
Celebrity registry and Princess voyage-bound versions, compares them with snapshot
sources, adds new configurations, and groups assessment items by exact source ID.
One builder invocation per affected provider receives an explicit configuration
filter. Successful collection is materialized as a new transactional snapshot;
failure leaves the active pointer unchanged. Work still present after the resulting
snapshot is recorded in `maintenance-state.json` as stalled and is suppressed for
that snapshot/policy combination. Changed evidence or policy, or explicit retry,
re-enables it.

Evidence hashes are namespace-specific. Assignment-only evidence changes the
assignment revision and overall snapshot manifest, while unchanged physical and
category documents keep their revision identities. The full legacy-master file hash
continues to be validated during materialization but is not a physical revision ID.

## Evidence rules

- Future-only configuration discovery: `sailDate > surveyStartDate`; a voyage departing today is excluded.
- Never infer a deck from a cabin number.
- A physical configuration ID and a commercial offer/category signature are different namespaces.
- A later no-inventory/provider-error observation does not erase earlier exact-sailing proof.
- Conflicting exact-sailing configuration evidence fails closed.
- Celebrity sailing-specific GraphQL itinerary data is authoritative for the voyage pipeline; the legacy itinerary crawler is diagnostic only.
- Static masters are keyed by provider + ship + physical configuration and are not rediscovered every Daily run.
- Runtime provider responses and generated masters live under `work/` and are never source artifacts.

Celebrity static discovery uses only the JSON room-selection API and its deck-plan layout token. Princess configuration identity comes from the ship version attached to each provider voyage. Princess deck content is retained only from non-empty structured `getDeckJSON.do` responses for that exact ship/version.

During Daily operation, existing Celebrity configurations are not treated as a
binary cache hit. Saturated masters are skipped; unsaturated masters use their
current combined master as baseline and their cumulative validation as the
tested-voyage exclusion set. Only newly proven, currently published voyages are
eligible for the next bounded increment.

Catalogs use paths relative to `state/static-masters`. Legacy absolute paths are
mapped to local provider/ship/configuration files; validation never follows an old
workspace. Celebrity catalog metadata is reconciled from all published master and
validation pairs before Daily collection and after each completed configuration.
Atomic catalog replacement plus restart reconciliation closes the completed
promotion/catalog-publication gap. Validate stays read-only; offline metadata
repair is a separate command. Multi-file master promotion is not a single atomic
transaction, and inconsistent published pairs must be investigated.
