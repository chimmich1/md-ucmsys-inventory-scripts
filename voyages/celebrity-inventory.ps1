param(
  [string]$Python = "python",
  [string]$Out = ".\celebrity-voyages-raw.json"
)

$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "celebrity-inventory.py"
if (!(Test-Path $script)) { throw "Missing Celebrity acquisition script: $script" }

& $Python $script --out $Out
if ($LASTEXITCODE -ne 0) {
  throw "Celebrity Python acquisition failed (exit code $LASTEXITCODE)"
}
