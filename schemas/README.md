# Consumer JSON Schemas

These Draft 2020-12 schemas describe the released JSON contracts that an external
cabin monitoring system may ingest. They validate stable envelopes and integrity
metadata while allowing additive provider-native fields.

- `canonical-voyages-v3.1.schema.json`
- `fleet-registry-v1.2.schema.json`
- `catalog.schema.json`
- `permanent-master-active-snapshot.schema.json`
- `permanent-master-manifest.schema.json`
- `permanent-physical-master.schema.json`
- `permanent-category-master.schema.json`
- `permanent-assignment-master.schema.json`

Validate manifest hashes before accepting a permanent-master snapshot and retain
the `sources` arrays as provenance.

- inventory-observation-v1.1.schema.json — universal voyage-scoped availability and pricing observation; dynamic data remains separate from permanent masters.
