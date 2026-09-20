param(
  [string]$Python = "python",
  [string]$Out = ".\celebrity-voyages-raw.json"
)

$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "celebrity-inventory.py"
if (!(Test-Path $script)) { throw "Missing Celebrity acquisition script: $script" }

. (Join-Path $PSScriptRoot "..\pipeline\invoke-native.ps1")
Invoke-NativeCommand -Executable $Python -Arguments @($script, "--out", $Out)
