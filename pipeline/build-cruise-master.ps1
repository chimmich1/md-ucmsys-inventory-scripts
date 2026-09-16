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
$PipelineDir=Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot=Split-Path -Parent $PipelineDir
if(!$DataDir){$DataDir=Join-Path $RepoRoot "work\data"}
if(!$StateDir){$StateDir=Join-Path $RepoRoot "work\state"}
New-Item -ItemType Directory -Force -Path $DataDir,$StateDir | Out-Null
$Voy=Join-Path $RepoRoot "voyages"
$Timeline=Join-Path $RepoRoot "fleet\timeline"
$RegistryTool=Join-Path $RepoRoot "fleet\registry"
$TimelineOut=Join-Path $StateDir "fleet-timeline-current"
if($RegistryPath){
  $Registry=$RegistryPath
} else {
  $Registry=Join-Path $StateDir "fleet-physical-configuration-registry-v1.2.json"
  # Convenience migration path for the validated standalone V1.1 registry.
  $LegacyRegistry=Join-Path $DataDir "fleet-configuration-registry-v1.1\fleet-physical-configuration-registry-v1.2.json"
  if(!(Test-Path $Registry) -and (Test-Path $LegacyRegistry)){
    $Registry=$LegacyRegistry
  }
}

$PipelineVersion="0.4.0"
$RunKey="$SurveyStart-$($Mode.ToLowerInvariant())-v$PipelineVersion"
$RunDir=Join-Path $StateDir "runs\$RunKey"
if($RestartRun -and (Test-Path $RunDir)){Remove-Item -Recurse -Force $RunDir}
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

function StageKey([string]$Name){
  return (($Name.ToLowerInvariant() -replace '[^a-z0-9]+','-').Trim('-'))
}
function Step([string]$Name,[scriptblock]$Block,[switch]$Always){
  $marker=Join-Path $RunDir "$(StageKey $Name).complete"
  if(!$Always -and (Test-Path $marker)){
    Write-Host "`n=== $Name ===" -ForegroundColor DarkCyan
    Write-Host "CHECKPOINT: already completed for $RunKey; skipping." -ForegroundColor DarkGray
    return
  }
  Write-Host "`n=== $Name ===" -ForegroundColor Cyan
  $started=(Get-Date).ToUniversalTime()
  $startedMarker=Join-Path $RunDir "$(StageKey $Name).started"
  $failedMarker=Join-Path $RunDir "$(StageKey $Name).failed"
  Remove-Item -Force -ErrorAction SilentlyContinue $failedMarker
  [pscustomobject]@{
    stage=$Name; runKey=$RunKey; startedAt=$started.ToString("o")
  } | ConvertTo-Json | Set-Content -Encoding UTF8 $startedMarker
  try {
    & $Block
    [pscustomobject]@{
      stage=$Name
      runKey=$RunKey
      completedAt=(Get-Date).ToUniversalTime().ToString("o")
      elapsedSeconds=[math]::Round(((Get-Date).ToUniversalTime()-$started).TotalSeconds,3)
    } | ConvertTo-Json | Set-Content -Encoding UTF8 $marker
    Remove-Item -Force -ErrorAction SilentlyContinue $startedMarker
    Write-Host "CHECKPOINT: completed." -ForegroundColor DarkGray
  } catch {
    [pscustomobject]@{
      stage=$Name; runKey=$RunKey; failedAt=(Get-Date).ToUniversalTime().ToString("o")
      error=$_.Exception.Message
    } | ConvertTo-Json | Set-Content -Encoding UTF8 $failedMarker
    Remove-Item -Force -ErrorAction SilentlyContinue $startedMarker
    throw "$Name failed: $($_.Exception.Message)"
  }
}
function Require([string]$p){if(!(Test-Path $p)){throw "Missing required file: $p"}}

function Invoke-ChildPowerShellScript {
  param(
    [Parameter(Mandatory=$true)][string]$ScriptPath,
    [string[]]$Arguments = @()
  )
  $argList = @(
    "-NoLogo",
    "-NoProfile",
    "-ExecutionPolicy","Bypass",
    "-File",$ScriptPath
  ) + $Arguments

  & powershell.exe @argList
  $code=$LASTEXITCODE
  if($code -ne 0){throw "Child PowerShell script failed: $ScriptPath (exit code $code)"}
}


$Princess=Join-Path $DataDir "cruise-voyages-princess-v3.1.json"
$Celebrity=Join-Path $DataDir "cruise-voyages-celebrity-v3.1.json"

if($Mode -eq "Validate"){
  Step "Validate canonical inputs" -Always {
    Require $Princess; Require $Celebrity
    $p=Get-Content -Raw $Princess | ConvertFrom-Json
    $c=Get-Content -Raw $Celebrity | ConvertFrom-Json
    Write-Host "Princess voyages: $(@($p.voyages).Count)"
    Write-Host "Celebrity voyages: $(@($c.voyages).Count)"
  }
  Step "Validate registry" -Always {
    Require $Registry
    $r=Get-Content -Raw $Registry | ConvertFrom-Json
    Write-Host "Registry version: $($r.version)"
    if($r.version -ne "1.2"){throw "Expected Registry V1.2; found $($r.version)"}
    Write-Host "Observations: $(@($r.observations).Count)"
    Write-Host "Voyages: $(@($r.voyages.PSObject.Properties).Count)"
    Write-Host "Conflicts: $(@($r.conflicts).Count)"
    if(@($r.conflicts).Count -gt 0){throw "Registry contains physical-configuration conflicts"}
  }
  exit 0
}

if(!$SkipVoyageRefresh){
  Push-Location $DataDir
  try {
    Step "Princess voyage acquisition" { Invoke-ChildPowerShellScript -ScriptPath (Join-Path $Voy "princess-inventory.ps1") }
    Step "Celebrity voyage acquisition" { Invoke-ChildPowerShellScript -ScriptPath (Join-Path $Voy "celebrity-inventory.ps1") }

    # v0.3: sailing-specific itinerary data is returned in the same GraphQL
    # acquisition above. No itinerary-page/RSC crawl is part of Full or Daily.
    Step "Celebrity port-country enrichment" {
      Invoke-ChildPowerShellScript -ScriptPath (Join-Path $Voy "build-celebrity-port-country.ps1") -Arguments @("-Dir",$DataDir)
    }
    Step "Princess canonical V3.1" {
      Invoke-ChildPowerShellScript -ScriptPath (Join-Path $Voy "cruise-voyage-normalizer-v3.1.ps1") -Arguments @("-Provider","PRINCESS","-SkipFetch","-Dir",$DataDir)
    }
    Step "Celebrity canonical V3.1" {
      Invoke-ChildPowerShellScript -ScriptPath (Join-Path $Voy "cruise-voyage-normalizer-v3.1.ps1") -Arguments @("-Provider","CELEBRITY","-SkipFetch","-Dir",$DataDir)
    }
  } finally { Pop-Location }
}

Require $Princess; Require $Celebrity

Step "Fleet physical-configuration survey" {
  New-Item -ItemType Directory -Force -Path $TimelineOut | Out-Null
  & $Python (Join-Path $Timeline "celebrity-fleet-timeline-v1.0.py") `
    --voyages $Celebrity --survey-start $SurveyStart --max-probes 0 `
    --out (Join-Path $TimelineOut "celebrity-fleet-timeline-v1.0.json")
  if($LASTEXITCODE -ne 0){throw "Celebrity fleet timeline failed"}
  & $Python (Join-Path $Timeline "princess-fleet-timeline-preflight-v1.0.py") `
    --voyages $Princess --survey-start $SurveyStart `
    --out (Join-Path $TimelineOut "princess-fleet-timeline-preflight-v1.0.json")
  if($LASTEXITCODE -ne 0){throw "Princess fleet timeline preflight failed with exit code $LASTEXITCODE"}
}

Step "Append Celebrity evidence registry" {
  & $Python (Join-Path $RegistryTool "fleet-configuration-registry-v1.2.py") `
    --registry $Registry `
    --survey (Join-Path $TimelineOut "celebrity-fleet-timeline-v1.0.json")
  if($LASTEXITCODE -ne 0){throw "Registry updater failed with exit code $LASTEXITCODE"}
}

Write-Host "`nPipeline complete." -ForegroundColor Green
Write-Host "Mode:      $Mode"
Write-Host "State:     $StateDir"
Write-Host "Registry:  $Registry"
Write-Host "Run state: $RunDir"
Write-Host ""
Write-Host "NOTE: cabin-master/category-master discovery is intentionally NOT yet auto-invoked."
Write-Host "The existing Celebrity saturation crawler is not yet a fleet-generic, configuration-keyed production stage."
