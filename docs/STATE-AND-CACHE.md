# State and cache

Everything under `work/` is runtime/generated and ignored by Git except `.gitkeep` placeholders.

- `work/data/`: current acquired and canonical voyage datasets.
- `work/state/`: durable registry, immutable source-survey archive, static masters and catalogs.
- `work/state/runs/`: current restart checkpoints for mutating Full/Daily runs.
- `work/runs/`: legacy/reserved runtime directory; not the current checkpoint location.
- `work/cache/`: disposable provider cache if a collector uses one.
- `work/logs/`: runtime logs.

Preserve `work/data` and `work/state` when upgrading or relocating this installation.
Historical evidence cannot be reconstructed by collecting only currently published
voyages. Full acceptance belongs in a separate empty checkout; never use it to
repair cumulative state. Catalog relocation/reconciliation is described in OPERATIONS.md.
