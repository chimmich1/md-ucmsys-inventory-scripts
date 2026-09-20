# Provenance

Celebrity fleet surveys are archived under runtime state by SHA-256 content identity. Registry V1.2 records the raw survey hash/byte length and distinguishes survey chronology from import chronology. Importing an older survey later cannot make it the latest survey observation.

Exact target-sailing configuration proof is durable. Unobservable/no-inventory observations are evidence about current observability, not evidence that a previously proven configuration ceased to exist.

Princess configuration identity comes from the version attached by Princess to each
acquired voyage. A Princess deck enters a master only after a non-empty structured
`getDeckJSON.do` response; bounded probe numbers that return no cabins are retained only
in the audit and are not published as decks.
