# md-ucmsys-inventory-scripts

Universal Cruise Monitoring System — provider inventory, voyage normalization,
fleet physical-configuration evidence, and master-data pipeline.

## Repository layout

- `build-cruise-master.ps1` — stable root entry point.
- `pipeline/` — orchestration.
- `voyages/` — Princess/Celebrity acquisition and canonical normalization.
- `fleet/timeline/` — physical-configuration survey/timeline tooling.
- `fleet/registry/` — durable configuration evidence registry tooling.
- `diagnostics/legacy/` — historical/diagnostic tools, never production pipeline.
- `work/` — generated runtime data/state; intentionally excluded from Git.
- `tests/` — deterministic fixtures and expected results.
- `docs/architecture/` — architecture decisions and documentation.

## v0.3.1 Celebrity change

Celebrity `cruiseSearch_CruisesRiver` GraphQL now supplies both voyage discovery and
each individual `sailings[].itinerary`. Full and Daily no longer invoke the
itinerary-page/RSC crawler. The old v5.2 crawler is retained only under
`diagnostics/legacy/`.

## Clean first run

From the repository root:

```powershell
.\build-cruise-master.ps1 -Mode Full -RestartRun
```

With no path overrides, generated data goes to `work\data` and pipeline state goes to
`work\state`.

Validation:

```powershell
.\build-cruise-master.ps1 -Mode Validate
```

Daily:

```powershell
.\build-cruise-master.ps1 -Mode Daily
```

You may still override `-DataDir`, `-StateDir`, `-RegistryPath`, `-SurveyStart`, and
`-Python`.

## Current hardening items

- Registry V1.2 content-addressed provenance/idempotency is not yet integrated.
- Per-stage checkpoint identity still needs relevant-input fingerprints; v0.3.1
  namespaces checkpoints by pipeline version so older v0.2/v0.3.0 markers cannot
  suppress this implementation.
- Static cabin/category discovery remains a separate later integration stage.
