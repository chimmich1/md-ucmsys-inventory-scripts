param(
    [string]$InputFile = ".\celebrity-voyages-raw.json",
    [string]$OutputFile = ".\celebrity-itineraries-page.json",
    [string]$CheckpointFile = ".\celebrity-itineraries-page-checkpoint.json",
    [string]$FailureFile = ".\celebrity-itineraries-page-failures.json",
    [int]$Limit = 0,
    [int]$DelayMs = 750,
    [int]$MaxRetries = 3,
    [int]$DeferredRetryPasses = 1,
    [int]$DeferredRetryDelayMs = 5000,
    [switch]$NoResume,
    [switch]$Incremental,
    [string]$VoyageId = "",
    [ValidateSet("au","ca","gb","us")]
    [string]$Market = "ca"
)

$ErrorActionPreference = "Stop"

function Save-JsonAtomic {
    param(
        [Parameter(Mandatory=$true)]$Object,
        [Parameter(Mandatory=$true)][string]$Path
    )

    $tmp = "$Path.tmp"
    ConvertTo-Json -InputObject $Object -Depth 100 | Set-Content $tmp -Encoding UTF8
    Move-Item -Force $tmp $Path
}

function Get-NextFlightText {
    param([Parameter(Mandatory=$true)][string]$Html)

    $matches = [regex]::Matches(
        $Html,
        'self\.__next_f\.push\(\[1,"(?<payload>(?:\\.|[^"\\])*)"\]\)',
        [System.Text.RegularExpressions.RegexOptions]::Singleline
    )

    if ($matches.Count -eq 0) {
        return $null
    }

    $sb = New-Object System.Text.StringBuilder
    foreach ($m in $matches) {
        $encoded = '"' + $m.Groups["payload"].Value + '"'
        try {
            $decoded = $encoded | ConvertFrom-Json
            [void]$sb.Append($decoded)
            [void]$sb.Append("`n")
        }
        catch {
            [void]$sb.Append($m.Groups["payload"].Value)
            [void]$sb.Append("`n")
        }
    }

    return $sb.ToString()
}

function Get-BalancedJsonObject {
    param(
        [Parameter(Mandatory=$true)][string]$Text,
        [Parameter(Mandatory=$true)][int]$StartIndex
    )

    $i = $StartIndex
    while ($i -lt $Text.Length -and [char]::IsWhiteSpace($Text[$i])) { $i++ }
    if ($i -ge $Text.Length -or $Text[$i] -ne '{') {
        return $null
    }

    $depth = 0
    $inString = $false
    $escape = $false

    for ($j = $i; $j -lt $Text.Length; $j++) {
        $c = $Text[$j]

        if ($inString) {
            if ($escape) {
                $escape = $false
                continue
            }
            if ($c -eq [char]92) {
                $escape = $true
                continue
            }
            if ($c -eq '"') {
                $inString = $false
            }
            continue
        }

        if ($c -eq '"') {
            $inString = $true
            continue
        }

        if ($c -eq '{') {
            $depth++
            continue
        }

        if ($c -eq '}') {
            $depth--
            if ($depth -eq 0) {
                return $Text.Substring($i, $j - $i + 1)
            }
        }
    }

    return $null
}

function Get-StructuredItinerary {
    param(
        [Parameter(Mandatory=$true)][string]$FlightText,
        [Parameter(Mandatory=$true)][string]$ExpectedPackageCode
    )

    # The public itinerary page embeds the authoritative PDP object in the RSC as:
    #   "itinerary":{"packageCode":"EG11K166", ... }
    # Search specifically for packageCode immediately inside itinerary so we do not
    # accidentally pick up the Schema.org itinerary ItemList earlier in the flight.
    $escapedCode = [regex]::Escape($ExpectedPackageCode)
    $pattern = '"itinerary"\s*:\s*\{\s*"packageCode"\s*:\s*"' + $escapedCode + '"'
    $m = [regex]::Match($FlightText, $pattern)

    if (-not $m.Success) {
        return $null
    }

    $colonIndex = $FlightText.IndexOf(':', $m.Index)
    if ($colonIndex -lt 0) {
        return $null
    }

    $objectStart = $FlightText.IndexOf('{', $colonIndex)
    if ($objectStart -lt 0) {
        return $null
    }

    $json = Get-BalancedJsonObject -Text $FlightText -StartIndex $objectStart
    if ([string]::IsNullOrWhiteSpace($json)) {
        return $null
    }

    return ($json | ConvertFrom-Json)
}

function Get-CountryForMarket {
    param([Parameter(Mandatory=$true)][string]$Market)

    switch ($Market) {
        "au" { return "AUS" }
        "ca" { return "CAN" }
        "gb" { return "GBR" }
        "us" { return "USA" }
        default { return "CAN" }
    }
}

function Get-OfficialItineraryUrl {
    param(
        [Parameter(Mandatory=$true)]$Group,
        [Parameter(Mandatory=$true)]$Sailing,
        [Parameter(Mandatory=$true)][string]$Market
    )

    $groupId = [string]$Group.id
    $packageCode = [string]$Sailing.itinerary.code
    $sailDate = [string]$Sailing.sailDate
    $productViewLink = [string]$Group.productViewLink
    $masterCode = [string]$Group.masterSailing.itinerary.code

    if ([string]::IsNullOrWhiteSpace($productViewLink)) {
        throw "Group $groupId has no productViewLink."
    }

    $pathOnly = ($productViewLink -split '\?', 2)[0].TrimStart('/')

    if (-not [string]::IsNullOrWhiteSpace($masterCode) -and $pathOnly.EndsWith($masterCode)) {
        $pathOnly = $pathOnly.Substring(0, $pathOnly.Length - $masterCode.Length) + $packageCode
    }
    elseif ($pathOnly -match '-[A-Z0-9]+$') {
        $pathOnly = $pathOnly -replace '-[A-Z0-9]+$', "-$packageCode"
    }
    else {
        throw "Cannot safely replace package code in productViewLink path: $pathOnly"
    }

    $country = Get-CountryForMarket -Market $Market
    $query = "country=$country&groupId=$([uri]::EscapeDataString($groupId))&packageCode=$([uri]::EscapeDataString($packageCode))&sailDate=$([uri]::EscapeDataString($sailDate))"

    if ($Market -eq "us") {
        return "https://www.celebritycruises.com/$pathOnly`?$query"
    }

    return "https://www.celebritycruises.com/$Market/$pathOnly`?$query"
}

function Get-ItineraryPage {
    param(
        [Parameter(Mandatory=$true)]$Group,
        [Parameter(Mandatory=$true)]$Sailing,
        [Parameter(Mandatory=$true)][string]$Market
    )

    $packageCode = [string]$Sailing.itinerary.code
    $sailDate = [string]$Sailing.sailDate
    $url = Get-OfficialItineraryUrl -Group $Group -Sailing $Sailing -Market $Market

    $headers = @{
        "Accept" = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        "Accept-Language" = "en-CA,en;q=0.9"
        "Cache-Control" = "no-cache"
        "Pragma" = "no-cache"
        "Upgrade-Insecure-Requests" = "1"
    }

    $response = Invoke-WebRequest `
        -Uri $url `
        -Method Get `
        -Headers $headers `
        -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"

    $flight = Get-NextFlightText -Html ([string]$response.Content)
    if ([string]::IsNullOrWhiteSpace($flight)) {
        throw "No Next.js RSC flight data found."
    }

    $itinerary = Get-StructuredItinerary -FlightText $flight -ExpectedPackageCode $packageCode
    if (-not $itinerary) {
        throw "Structured itinerary object not found in RSC."
    }

    # Strong sailing identity checks. Never accept a master/group itinerary for a variant.
    if ([string]$itinerary.packageCode -ne $packageCode) {
        throw "Package code mismatch: requested=$packageCode returned=$($itinerary.packageCode)"
    }

    if ([string]$itinerary.sailDate -ne $sailDate) {
        throw "Sail date mismatch: requested=$sailDate returned=$($itinerary.sailDate)"
    }

    if ([string]$itinerary.groupId -ne [string]$Group.id) {
        throw "Group ID mismatch: requested=$($Group.id) returned=$($itinerary.groupId)"
    }

    if (-not $itinerary.chapters -or @($itinerary.chapters).Count -eq 0) {
        throw "Structured itinerary contains no chapters."
    }

    return [pscustomobject]@{
        requestUrl = $url
        httpStatus = [int]$response.StatusCode
        itinerary  = $itinerary
    }
}

if (-not (Test-Path $InputFile)) {
    throw "Input file not found: $InputFile"
}

Write-Host "Loading $InputFile ..."
$raw = Get-Content $InputFile -Raw | ConvertFrom-Json
$groups = @($raw.data.cruiseSearch.results.cruises)

$targets = New-Object System.Collections.Generic.List[object]
$seen = @{}

foreach ($g in $groups) {
    foreach ($s in @($g.sailings)) {
        $candidateVoyageId = [string]$s.id
        if ([string]::IsNullOrWhiteSpace($candidateVoyageId)) { continue }
        if ($seen.ContainsKey($candidateVoyageId)) { continue }
        $seen[$candidateVoyageId] = $true

        $targets.Add([pscustomobject]@{
            voyageId = $candidateVoyageId
            group     = $g
            sailing   = $s
        })
    }
}

$targets = @($targets | Sort-Object { [string]$_.sailing.sailDate }, { [string]$_.voyageId })

if (-not [string]::IsNullOrWhiteSpace($VoyageId)) {
    $targets = @($targets | Where-Object { $_.voyageId -eq $VoyageId })
    if ($targets.Count -eq 0) {
        throw "VoyageId not found in $InputFile`: $VoyageId"
    }
}

if ($Limit -gt 0) {
    $targets = @($targets | Select-Object -First $Limit)
}

Write-Host "Celebrity sailings selected: $($targets.Count)"

$results = New-Object System.Collections.Generic.List[object]
$failures = New-Object System.Collections.Generic.List[object]
$successByIdentity = @{}

function Get-SailingIdentity {
    param(
        [string]$VoyageId,
        [string]$GroupId,
        [string]$PackageCode,
        [string]$SailDate
    )
    return "$VoyageId|$GroupId|$PackageCode|$SailDate"
}

function Add-CachedResult {
    param($Record)
    if (-not $Record) { return }
    $id = Get-SailingIdentity `
        -VoyageId ([string]$Record.voyageId) `
        -GroupId ([string]$Record.groupId) `
        -PackageCode ([string]$Record.packageCode) `
        -SailDate ([string]$Record.sailDate)
    if ($successByIdentity.ContainsKey($id)) { return }
    $successByIdentity[$id] = $true
    $results.Add($Record)
}

# Resume an interrupted crawl first. In Incremental mode also seed from the durable
# final output, so a normal daily run does not re-fetch thousands of unchanged pages.
if (-not $NoResume -and (Test-Path $CheckpointFile)) {
    try {
        $checkpoint = Get-Content $CheckpointFile -Raw | ConvertFrom-Json
        foreach ($r in @($checkpoint.results)) { Add-CachedResult $r }
        Write-Host "Resume cache: $($results.Count) successful sailing(s) from checkpoint."
    }
    catch {
        Write-Warning "Could not load checkpoint: $($_.Exception.Message)"
    }
}

if ($Incremental -and (Test-Path $OutputFile)) {
    try {
        $existingOutput = Get-Content $OutputFile -Raw | ConvertFrom-Json
        foreach ($r in @($existingOutput.itineraries)) { Add-CachedResult $r }
        Write-Host "Incremental cache after final output merge: $($results.Count) successful sailing(s)."
    }
    catch {
        Write-Warning "Could not load existing itinerary output: $($_.Exception.Message)"
    }
}

$processedThisRun = 0
$successThisRun = 0
$failedFirstPass = 0
$recoveredDeferred = 0
$index = 0

# Keep the target objects for first-pass failures so they can be retried after the
# main crawl. This deliberately separates a transient provider/CDN response from
# a genuinely persistent itinerary-page failure.
$pendingFailures = New-Object System.Collections.Generic.List[object]

function Invoke-SailingTarget {
    param(
        [Parameter(Mandatory=$true)]$Target,
        [Parameter(Mandatory=$true)][int]$Retries,
        [Parameter(Mandatory=$true)][string]$Phase
    )

    $g = $Target.group
    $s = $Target.sailing
    $packageCode = [string]$s.itinerary.code
    $sailDate = [string]$s.sailDate
    $shipCode = [string]$g.masterSailing.itinerary.ship.code
    if ([string]::IsNullOrWhiteSpace($shipCode)) {
        $shipCode = ([string]$Target.voyageId -split '[0-9]', 2)[0]
    }

    $lastError = $null

    for ($attempt = 1; $attempt -le $Retries; $attempt++) {
        try {
            $page = Get-ItineraryPage -Group $g -Sailing $s -Market $Market
            $it = $page.itinerary

            $record = [pscustomobject]@{
                voyageId    = [string]$Target.voyageId
                groupId     = [string]$g.id
                packageCode = $packageCode
                sailDate    = $sailDate
                shipCode    = [string]$it.ship.code
                fetchedAt   = (Get-Date).ToString("o")
                httpStatus  = $page.httpStatus
                requestUrl  = $page.requestUrl
                source      = "CELEBRITY_ITINERARY_PAGE"
                itinerary   = $it
            }

            return [pscustomobject]@{
                ok          = $true
                record      = $record
                error       = $null
                packageCode = $packageCode
                sailDate    = $sailDate
                shipCode    = $shipCode
            }
        }
        catch {
            $lastError = $_.Exception.Message
            Write-Warning "  $Phase attempt $attempt/$Retries`: $lastError"
            if ($attempt -lt $Retries) {
                Start-Sleep -Milliseconds ([Math]::Max(1000, $DelayMs * $attempt))
            }
        }
    }

    return [pscustomobject]@{
        ok          = $false
        record      = $null
        error       = $lastError
        packageCode = $packageCode
        sailDate    = $sailDate
        shipCode    = $shipCode
    }
}

foreach ($t in $targets) {
    $index++

    $s = $t.sailing
    $g = $t.group
    $packageCode = [string]$s.itinerary.code
    $sailDate = [string]$s.sailDate
    $identity = Get-SailingIdentity -VoyageId ([string]$t.voyageId) -GroupId ([string]$g.id) -PackageCode $packageCode -SailDate $sailDate
    if ($successByIdentity.ContainsKey($identity)) {
        continue
    }
    $shipCode = [string]$g.masterSailing.itinerary.ship.code
    if ([string]::IsNullOrWhiteSpace($shipCode)) {
        $shipCode = ([string]$t.voyageId -split '[0-9]', 2)[0]
    }

    Write-Host "[$index/$($targets.Count)] $sailDate $shipCode $packageCode"

    $processedThisRun++
    $attemptResult = Invoke-SailingTarget -Target $t -Retries $MaxRetries -Phase "first-pass"

    if ($attemptResult.ok) {
        $results.Add($attemptResult.record)
        $successByIdentity[$identity] = $true
        $successThisRun++
        Write-Host "  OK: $($attemptResult.record.itinerary.name) | chapters=$(@($attemptResult.record.itinerary.chapters).Count)"
    }
    else {
        $failedFirstPass++
        $pendingFailures.Add([pscustomobject]@{
            target      = $t
            voyageId    = [string]$t.voyageId
            groupId     = [string]$g.id
            packageCode = $attemptResult.packageCode
            sailDate    = $attemptResult.sailDate
            shipCode    = $attemptResult.shipCode
            failedAt    = (Get-Date).ToString("o")
            error       = $attemptResult.error
        })
        Write-Warning "  FAILED FIRST PASS: $($attemptResult.error)"
    }

    # Checkpoint persistent state after every first-pass sailing. At this point the
    # pending list contains unresolved failures only; recovered deferred failures
    # are handled below before final serialization.
    $checkpointFailures = @($pendingFailures.ToArray() | ForEach-Object {
        [pscustomobject]@{
            voyageId    = $_.voyageId
            groupId     = $_.groupId
            packageCode = $_.packageCode
            sailDate    = $_.sailDate
            shipCode    = $_.shipCode
            failedAt    = $_.failedAt
            error       = $_.error
        }
    })

    $checkpointObject = [pscustomobject]@{
        provider  = "CELEBRITY"
        source    = "ITINERARY_PAGE"
        updatedAt = (Get-Date).ToString("o")
        results   = $results.ToArray()
        failures  = $checkpointFailures
    }
    Save-JsonAtomic -Object $checkpointObject -Path $CheckpointFile

    if ($DelayMs -gt 0) {
        Start-Sleep -Milliseconds $DelayMs
    }
}

# Deferred retry pass(es): retry only the small set that failed after their normal
# immediate retries. This lets transient CDN/provider conditions clear while the
# rest of the inventory finishes, without slowing every successful request.
if ($DeferredRetryPasses -gt 0 -and $pendingFailures.Count -gt 0) {
    for ($pass = 1; $pass -le $DeferredRetryPasses -and $pendingFailures.Count -gt 0; $pass++) {
        Write-Host ""
        Write-Host "Deferred retry pass $pass/$DeferredRetryPasses`: $($pendingFailures.Count) sailing(s) pending."

        $retrySet = @($pendingFailures.ToArray())
        $nextPending = New-Object System.Collections.Generic.List[object]
        $retryIndex = 0

        foreach ($pending in $retrySet) {
            $retryIndex++
            $t = $pending.target

            $retryIdentity = Get-SailingIdentity -VoyageId ([string]$t.voyageId) -GroupId ([string]$t.group.id) -PackageCode ([string]$t.sailing.itinerary.code) -SailDate ([string]$t.sailing.sailDate)
            if ($successByIdentity.ContainsKey($retryIdentity)) {
                continue
            }

            if ($DeferredRetryDelayMs -gt 0) {
                Start-Sleep -Milliseconds $DeferredRetryDelayMs
            }

            Write-Host "[deferred $retryIndex/$($retrySet.Count)] $($pending.sailDate) $($pending.shipCode) $($pending.packageCode)"
            $retryResult = Invoke-SailingTarget -Target $t -Retries $MaxRetries -Phase "deferred-pass-$pass"

            if ($retryResult.ok) {
                $results.Add($retryResult.record)
                $successByIdentity[$retryIdentity] = $true
                $successThisRun++
                $recoveredDeferred++
                Write-Host "  RECOVERED: $($retryResult.record.itinerary.name) | chapters=$(@($retryResult.record.itinerary.chapters).Count)"
            }
            else {
                $nextPending.Add([pscustomobject]@{
                    target      = $t
                    voyageId    = [string]$t.voyageId
                    groupId     = [string]$t.group.id
                    packageCode = $retryResult.packageCode
                    sailDate    = $retryResult.sailDate
                    shipCode    = $retryResult.shipCode
                    failedAt    = (Get-Date).ToString("o")
                    error       = $retryResult.error
                })
                Write-Warning "  STILL FAILED: $($retryResult.error)"
            }

            $checkpointFailures = @($nextPending.ToArray() | ForEach-Object {
                [pscustomobject]@{
                    voyageId    = $_.voyageId
                    groupId     = $_.groupId
                    packageCode = $_.packageCode
                    sailDate    = $_.sailDate
                    shipCode    = $_.shipCode
                    failedAt    = $_.failedAt
                    error       = $_.error
                }
            })

            $checkpointObject = [pscustomobject]@{
                provider  = "CELEBRITY"
                source    = "ITINERARY_PAGE"
                updatedAt = (Get-Date).ToString("o")
                results   = $results.ToArray()
                failures  = $checkpointFailures
            }
            Save-JsonAtomic -Object $checkpointObject -Path $CheckpointFile
        }

        $pendingFailures = $nextPending
    }
}

$failures = New-Object System.Collections.Generic.List[object]
foreach ($pending in @($pendingFailures.ToArray())) {
    $failures.Add([pscustomobject]@{
        voyageId    = $pending.voyageId
        groupId     = $pending.groupId
        packageCode = $pending.packageCode
        sailDate    = $pending.sailDate
        shipCode    = $pending.shipCode
        failedAt    = $pending.failedAt
        error       = $pending.error
    })
}

$currentIdentitySet = @{}
foreach ($t in $targets) {
    $currentIdentitySet[(Get-SailingIdentity -VoyageId ([string]$t.voyageId) -GroupId ([string]$t.group.id) -PackageCode ([string]$t.sailing.itinerary.code) -SailDate ([string]$t.sailing.sailDate))] = $true
}
$activeResults = @($results.ToArray() | Where-Object {
    $rid = Get-SailingIdentity -VoyageId ([string]$_.voyageId) -GroupId ([string]$_.groupId) -PackageCode ([string]$_.packageCode) -SailDate ([string]$_.sailDate)
    $currentIdentitySet.ContainsKey($rid)
})
$sortedResults = @($activeResults | Sort-Object sailDate, voyageId)
$sortedFailures = @($failures.ToArray() | Sort-Object sailDate, voyageId)

$outputObject = [pscustomobject]@{
    provider    = "CELEBRITY"
    source      = "ITINERARY_PAGE"
    generatedAt = (Get-Date).ToString("o")
    count       = $sortedResults.Count
    itineraries = $sortedResults
}

Save-JsonAtomic -Object $outputObject -Path $OutputFile
Save-JsonAtomic -Object $sortedFailures -Path $FailureFile

$checkpointObject = [pscustomobject]@{
    provider  = "CELEBRITY"
    source    = "ITINERARY_PAGE"
    updatedAt = (Get-Date).ToString("o")
    results   = $sortedResults
    failures  = $sortedFailures
}
Save-JsonAtomic -Object $checkpointObject -Path $CheckpointFile

Write-Host ""
Write-Host "Celebrity itinerary-page crawl complete."
Write-Host "  Output:     $OutputFile"
Write-Host "  Successful: $($sortedResults.Count)"
Write-Host "  Failures:   $($sortedFailures.Count)"
Write-Host "  This run:   processed=$processedThisRun success=$successThisRun firstPassFailed=$failedFirstPass recoveredDeferred=$recoveredDeferred persistentFailed=$($sortedFailures.Count)"
Write-Host "  Reused:     $($sortedResults.Count - $successThisRun) unchanged cached itinerary(s)"
Write-Host ""
Write-Host "Recommended validation run:"
Write-Host "  .\celebrity-itineraries-v5.2.ps1 -Limit 50 -DelayMs 1000 -NoResume"
