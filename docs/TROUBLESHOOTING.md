# Troubleshooting

Use `-RestartRun` only when intentionally discarding checkpoints for the same logical Full/Daily run. If an expensive stage completed, resume without `-RestartRun` so its checkpoint is honored.

Provider HTTP failures are not configuration evidence. Do not repair them by assigning adjacent voyage configurations.

If Validate reports a hash mismatch, treat the generated master as changed/corrupt and investigate; do not silently rewrite it during Validate.
