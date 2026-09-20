# State and cache

Everything under `work/` is runtime/generated and ignored by Git except `.gitkeep` placeholders.

- `work/data/`: current acquired and canonical voyage datasets.
- `work/state/`: durable registry, immutable source-survey archive, static masters and catalogs.
- `work/runs/`: restart checkpoints for mutating Full/Daily runs.
- `work/cache/`: disposable provider cache if a collector uses one.
- `work/logs/`: runtime logs.

Deleting `work/` is equivalent to returning to an unseeded installation. Full must be able to reconstruct required current state. Historical evidence is valuable operational state but is not committed source code.
