# Data model

Static and dynamic facts are intentionally separated.

**Cabin master:** provider, ship/configuration, cabin number, provider-returned deck and physical attributes.

**Category master:** provider commercial category/type/subtype taxonomy observed for a configuration.

**Cabin-category assignment:** explicit provider evidence connecting a cabin to a category within a physical configuration.

**Observation:** voyage/search-context/timestamp availability and price evidence. Price is an observation, never a static cabin attribute.

Provider raw codes are preserved. Canonical normalization is additive. Category code, subtype code, position code and physical configuration ID are separate namespaces even when strings happen to match.

## Proposed permanent-master snapshot

`static-masters/permanent-masters/active-snapshot.json` identifies one immutable
snapshot. Its manifest hashes six documents: physical, category definitions, and
cabin-category assignments for Celebrity and Princess. Physical documents store
class defaults only when multiple ships support the same field, confirmed cabin
membership per source configuration, and compact ship-field exceptions. Unknowns
remain unknown; zero dimensions do not become measurements. Commercial definitions
and assignments have independent revision identities and applicability sources.

Coverage remains `UNVERIFIED` after migration. The snapshot does not infer dates,
completeness, or physical changes from configuration IDs. Legacy catalogs remain
authoritative until later roadmap integration. See `PERMANENT-MASTER-CONTRACT.md`.
