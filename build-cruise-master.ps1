[CmdletBinding()]
param(
  [ValidateSet("Full","Daily","Validate")][string]$Mode = "Daily",
  [string]$DataDir = "",
  [string]$StateDir = "",
  [string]$SurveyStart = (Get-Date -Format "yyyy-MM-dd"),
  [string]$Python = "python",
  [string]$RegistryPath = "",
  [switch]$ReuseAcquiredVoyages,
  [switch]$ResumeAtCelebrityMasters,
  [switch]$ResumeAtPrincessMasters,
  [switch]$SkipVoyageRefresh,
  [switch]$RestartRun,
  [string]$LogPath = ""
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

if ($ReuseAcquiredVoyages) {
    $params.ReuseAcquiredVoyages = $true
}

if ($ResumeAtPrincessMasters) {
    $params.ResumeAtPrincessMasters = $true
}

if ($ResumeAtCelebrityMasters) {
    $params.ResumeAtCelebrityMasters = $true
}

if ($RestartRun) {
    $params.RestartRun = $true
}

$logs = Join-Path $PSScriptRoot "work\logs"
if (!$LogPath) {
    $stamp = [DateTimeOffset]::Now.ToString("yyyyMMdd-HHmmss")
    $LogPath = Join-Path $logs "$($Mode.ToLowerInvariant())-v$((Get-Content -Raw (Join-Path $PSScriptRoot 'VERSION')).Trim())-$stamp.log"
}
$logParent = Split-Path -Parent $LogPath
New-Item -ItemType Directory -Force -Path $logParent | Out-Null
Write-Host "[$([DateTimeOffset]::Now.ToString('o'))] Run log: $LogPath"

$childArguments = @("-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $script,
    "-Mode", $Mode, "-SurveyStart", $SurveyStart, "-Python", $Python)
foreach ($name in @("DataDir", "StateDir", "RegistryPath")) {
    if ($params.ContainsKey($name)) { $childArguments += @("-$name", [string]$params[$name]) }
}
foreach ($name in @("SkipVoyageRefresh", "ReuseAcquiredVoyages", "ResumeAtPrincessMasters",
                     "ResumeAtCelebrityMasters", "RestartRun")) {
    if ($params.ContainsKey($name) -and $params[$name]) { $childArguments += "-$name" }
}

$savedPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = "Continue"
    & powershell.exe @childArguments 2>&1 |
        ForEach-Object {
            foreach ($line in ($_.ToString() -split "`r?`n")) {
                "[$([DateTimeOffset]::Now.ToString('o'))] $line"
            }
        } |
        Tee-Object -FilePath $LogPath
    $pipelineExitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $savedPreference
}
if ($pipelineExitCode -ne 0) {
    throw "Pipeline failed with exit code $pipelineExitCode. Complete output: $LogPath"
}
