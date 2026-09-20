# Troubleshooting

Use `-RestartRun` only when intentionally discarding checkpoints for the same logical Full/Daily run. If an expensive stage completed, resume without `-RestartRun` so its checkpoint is honored.

Provider HTTP failures are not configuration evidence. Do not repair them by assigning adjacent voyage configurations.

If Validate reports a hash mismatch, treat the generated master as changed/corrupt and investigate; do not silently rewrite it during Validate.

An RC5 increment can also leave a stale Celebrity catalog when its master and
validation report were fully promoted but catalog publication was interrupted.
For that known case, use `python .\master\reconcile-catalogs.py --state .\work\state`
and rerun Validate. This checks the local published pair and repairs metadata only.
Do not use Full or erase runtime state as a catalog repair. See OPERATIONS.md.
