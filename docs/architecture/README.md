# Architecture notes

Runtime artifacts are separated from version-controlled source. Celebrity individual
sailing itinerary data is sourced directly from GraphQL `sailings[].itinerary`; group
`masterSailing.itinerary` is not authoritative for a specific sailing. The legacy
itinerary-page crawler is diagnostic-only.
