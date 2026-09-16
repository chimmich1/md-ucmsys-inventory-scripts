[CmdletBinding()]
param(
  [ValidateSet("Full","Daily","Validate")][string]$Mode = "Daily",
  [string]$DataDir = "",
  [string]$StateDir = "",
  [string]$SurveyStart = (Get-Date -Format "yyyy-MM-dd"),
  [string]$Python = "python",
  [string]$RegistryPath = "",
  [switch]$SkipVoyageRefresh,
  [switch]$RestartRun
)
$ErrorActionPreference="Stop"
$script=Join-Path $PSScriptRoot "pipeline\build-cruise-master.ps1"
$params = @{
    Mode        = $Mode
    SurveyStart = $SurveyStart
    Python      = $Python
}

if ($DataDir) {
    $params.DataDir = $DataDir
}

if ($StateDir) {
    $params.StateDir = $StateDir
}

if ($RegistryPath) {
    $params.RegistryPath = $RegistryPath
}

if ($SkipVoyageRefresh) {
    $params.SkipVoyageRefresh = $true
}

if ($RestartRun) {
    $params.RestartRun = $true
}

& $script @params
