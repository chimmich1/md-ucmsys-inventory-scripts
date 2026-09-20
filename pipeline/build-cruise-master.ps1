param(
  [ValidateSet("Full","Daily","Validate")][string]$Mode = "Daily",
  [string]$DataDir = "",
  [string]$StateDir = "",
  [string]$SurveyStart = (Get-Date -Format "yyyy-MM-dd"),
  [string]$Python = "python",
  [string]$RegistryPath = "",
  [switch]$ReuseAcquiredVoyages,
  [switch]$ResumeAtPrincessMasters,
  [switch]$SkipVoyageRefresh,
  [switch]$RestartRun
)
$ErrorActionPreference="Stop"
$PipelineDir=Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot=Split-Path -Parent $PipelineDir
if(!$DataDir){$DataDir=Join-Path $RepoRoot "work\data"}
if(!$StateDir){$StateDir=Join-Path $RepoRoot "work\state"}
if($Mode -ne "Validate"){ New-Item -ItemType Directory -Force -Path $DataDir,$StateDir | Out-Null }
$Voy=Join-Path $RepoRoot "voyages"
$Timeline=Join-Path $RepoRoot "fleet\timeline"
$RegistryTool=Join-Path $RepoRoot "fleet\registry"
$TimelineOut=Join-Path $StateDir "fleet-timeline-current"
if($RegistryPath){
  $Registry=$RegistryPath
} else {
  $Registry=Join-Path $StateDir "fleet-physical-configuration-registry-v1.2.json"
}
$VersionFile=Join-Path $RepoRoot "VERSION"
if(!(Test-Path $VersionFile)){throw "Missing VERSION file: $VersionFile"}
$PipelineVersion=(Get-Content -Raw $VersionFile).Trim()
$RunKey="$SurveyStart-$($Mode.ToLowerInvariant())-v$PipelineVersion"
$RunDir=Join-Path $StateDir "runs\$RunKey"
if($Mode -ne "Validate"){
  if($RestartRun -and (Test-Path $RunDir)){Remove-Item -Recurse -Force $RunDir}
  New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
}

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
  # Validate is deliberately read-only: no run directory, checkpoints or generated files.
  Require $Princess; Require $Celebrity; Require $Registry
  $p=Get-Content -Raw $Princess | ConvertFrom-Json
  $c=Get-Content -Raw $Celebrity | ConvertFrom-Json
  $r=Get-Content -Raw $Registry | ConvertFrom-Json
  Write-Host "Princess voyages: $(@($p.voyages).Count)"
  Write-Host "Celebrity voyages: $(@($c.voyages).Count)"
  if($r.version -ne "1.2"){throw "Expected Registry V1.2; found $($r.version)"}
  if(@($r.conflicts).Count -gt 0){throw "Registry contains physical-configuration conflicts"}
  & $Python (Join-Path $RepoRoot "master\validate-masters.py") --state $StateDir
  if($LASTEXITCODE -ne 0){throw "Static-master validation failed"}
  Write-Host "Validation complete (read-only)." -ForegroundColor Green
  exit 0
}


if($ResumeAtPrincessMasters -and $Mode -ne "Full"){
  throw "-ResumeAtPrincessMasters is valid only with -Mode Full"
}

if(!$SkipVoyageRefresh -and !$ResumeAtPrincessMasters){
  Push-Location $DataDir
  try {
    if($ReuseAcquiredVoyages){
      Require (Join-Path $DataDir "princess-products.json")
      Require (Join-Path $DataDir "princess-ports.json")
      Require (Join-Path $DataDir "princess-ships.json")
      Require (Join-Path $DataDir "princess-itineraries.json")
      Require (Join-Path $DataDir "celebrity-voyages-raw.json")
      Write-Host "`n=== Voyage acquisition ===" -ForegroundColor DarkCyan
      Write-Host "Using previously acquired provider artifacts." -ForegroundColor DarkGray
    } else {
      Step "Princess voyage acquisition" { Invoke-ChildPowerShellScript -ScriptPath (Join-Path $Voy "princess-inventory.ps1") }
      Step "Celebrity voyage acquisition" {
        Invoke-ChildPowerShellScript -ScriptPath (Join-Path $Voy "celebrity-inventory.ps1") -Arguments @("-Python",$Python)
      }
    }

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

if(!$ResumeAtPrincessMasters){
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

Step "Archive + append Celebrity evidence registry" {
  $SurveyFile = Join-Path $TimelineOut "celebrity-fleet-timeline-v1.0.json"
  Require $SurveyFile

  & $Python `
    (Join-Path $RegistryTool "archive-and-import-survey-v1.0.py") `
    --survey $SurveyFile `
    --archive-dir (Join-Path $StateDir "source-surveys\celebrity") `
    --registry $Registry `
    --registry-tool (Join-Path $RegistryTool "fleet-configuration-registry-v1.2.py")

  if($LASTEXITCODE -ne 0){
    throw "Celebrity survey archive/registry import failed with exit code $LASTEXITCODE"
  }
}

Step "Celebrity static cabin/category masters" {
  & $Python (Join-Path $RepoRoot "master\build-static-masters.py") --mode $Mode --voyages $Celebrity --registry $Registry --state $StateDir --data $DataDir --python $Python
  if($LASTEXITCODE -ne 0){throw "Celebrity static-master discovery failed"}
}
} else {
  Require $Registry
  Require (Join-Path $StateDir "static-masters\celebrity-manifest.json")
  Require (Join-Path $StateDir "static-masters\celebrity-catalog.json")
  Write-Host "`n=== Resume at Princess masters ===" -ForegroundColor DarkCyan
  Write-Host "Using completed canonical voyages and Celebrity static-master state." -ForegroundColor DarkGray
}

Step "Princess published static masters" {
  & $Python (Join-Path $RepoRoot "master\build-princess-published-masters.py") --mode $Mode --voyages $Princess --state $StateDir --python $Python
  if($LASTEXITCODE -ne 0){throw "Princess published static-master discovery failed"}
}

Step "Validate generated masters" {
  & $Python (Join-Path $RepoRoot "master\validate-masters.py") --state $StateDir
  if($LASTEXITCODE -ne 0){throw "Generated master validation failed"}
}


Step "Publish run manifest" {
  # Release ZIPs intentionally contain no .git directory. Git provenance is
  # optional metadata and must not make an otherwise valid clean-room run fail.
  $gitSha="UNKNOWN"
  if(Test-Path (Join-Path $RepoRoot ".git")){
    try {
      $candidate = (& git -C $RepoRoot rev-parse HEAD 2>$null | Select-Object -First 1)
      if($LASTEXITCODE -eq 0 -and $candidate){$gitSha=$candidate}
    } catch {
      $gitSha="UNKNOWN"
    }
  }
  $manifest=[ordered]@{
    schemaVersion="1.0"; pipelineVersion=$PipelineVersion; gitSha=$gitSha;
    mode=$Mode; surveyStartDate=$SurveyStart; generatedAtUtc=(Get-Date).ToUniversalTime().ToString("o");
    resumedAtPrincessMasters=[bool]$ResumeAtPrincessMasters;
    inputs=[ordered]@{
      princessVoyages=[ordered]@{path=$Princess;sha256=(Get-FileHash -Algorithm SHA256 $Princess).Hash.ToLowerInvariant()};
      celebrityVoyages=[ordered]@{path=$Celebrity;sha256=(Get-FileHash -Algorithm SHA256 $Celebrity).Hash.ToLowerInvariant()};
      registry=[ordered]@{path=$Registry;sha256=(Get-FileHash -Algorithm SHA256 $Registry).Hash.ToLowerInvariant()}
    }
  }
  $manifest | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $RunDir "run-manifest.json")
}


Write-Host "`nPipeline complete." -ForegroundColor Green
Write-Host "Mode:      $Mode"
Write-Host "State:     $StateDir"
Write-Host "Registry:  $Registry"
Write-Host "Run state: $RunDir"
Write-Host ""
Write-Host "Static masters: $(Join-Path $StateDir 'static-masters')"
