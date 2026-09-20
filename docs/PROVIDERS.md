# Providers

## Celebrity

Voyages are acquired from sailing-specific GraphQL data. Physical configuration evidence is surveyed from target sailings. Static discovery uses room-selection endpoints and provider-returned deck/deckPlanUrl/cabin/category evidence. `curl_cffi` Chrome impersonation is required by the current provider edge behavior.

## Princess

Voyages and canonical normalization are production stages. Princess supplies a ship
version on each acquired voyage; normalization preserves it as
`source.providerShipVersion`. Static-master collection is keyed by that voyage-specific
ship/version evidence. The collector probes a bounded deck-number range but retains a
deck only when `getDeckJSON.do` returns structured cabin data for the exact ship/version
request. A numeric candidate is never treated as evidence by itself.
