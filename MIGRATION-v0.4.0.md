# v0.4.0 migration

Registry V1.2 intentionally does **not** upgrade a V1.1 registry in place because V1.1
does not contain trustworthy raw-survey content identity or observation chronology.

For the first v0.4.0 run, leave the existing V1.1 registry as an audit artifact and let
the pipeline create `work/state/fleet-physical-configuration-registry-v1.2.json` from
the current survey.

Historical evidence should later be rebuilt into V1.2 from the original survey JSON
files. Copying, renaming, or touching an already-imported raw survey is idempotent
because `sourceSurveyId` is the full SHA-256 of the raw file bytes.
