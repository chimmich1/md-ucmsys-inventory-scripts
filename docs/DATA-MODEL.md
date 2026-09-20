# Data model

Static and dynamic facts are intentionally separated.

**Cabin master:** provider, ship/configuration, cabin number, provider-returned deck and physical attributes.

**Category master:** provider commercial category/type/subtype taxonomy observed for a configuration.

**Cabin-category assignment:** explicit provider evidence connecting a cabin to a category within a physical configuration.

**Observation:** voyage/search-context/timestamp availability and price evidence. Price is an observation, never a static cabin attribute.

Provider raw codes are preserved. Canonical normalization is additive. Category code, subtype code, position code and physical configuration ID are separate namespaces even when strings happen to match.
