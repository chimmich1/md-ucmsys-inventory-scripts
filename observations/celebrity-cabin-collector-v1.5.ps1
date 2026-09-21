param(
    [string]$PackageCode = "XC07E474",
    [string]$SailDate = "2027-03-07",
    [string]$GroupId = "XC07MIA-1163767524",
    [string]$Country = "CAN",
    [string]$Currency = "CAD",
    [int]$Adults = 2,
    [int]$Children = 0,
    [string]$OutputDir = ".",
    [int]$DelayMs = 300,
    [ValidateSet("ExactCabin","CategorySample")]
    [string]$PricingMode = "ExactCabin"
)

$ErrorActionPreference = "Stop"
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Transport = Join-Path $ScriptDir "celebrity-http.py"

if (!(Test-Path $Transport)) {
    throw "Missing HTTP transport helper: $Transport"
}

$Python = $null
foreach ($candidate in @("python","py")) {
    try {
        $null = & $candidate --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $Python = $candidate
            break
        }
    } catch {}
}
if (!$Python) {
    throw "Python 3 is required for this diagnostic because Celebrity/Akamai is rejecting non-browser TLS fingerprints. Install Python 3 with the 'curl_cffi' package."
}

try {
    $null = & $Python -c "import curl_cffi" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "requests missing" }
}
catch {
    throw "Python package 'curl_cffi' is required. Run: $Python -m pip install curl_cffi"
}

$Base = "https://www.celebritycruises.com"

$HeadersRsc = [ordered]@{
    "User-Agent"      = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0 Safari/537.36"
    "Accept"          = "text/x-component"
    "Accept-Language" = "en-US,en;q=0.9"
    "RSC"             = "1"
    "Referer"         = "https://www.celebritycruises.com/"
}

$HeadersJson = [ordered]@{
    "User-Agent"      = $HeadersRsc["User-Agent"]
    "Accept"          = "*/*"
    "Accept-Language" = "en-US,en;q=0.9"
    "Content-Type"    = "application/json"
    "Referer"         = "https://www.celebritycruises.com/"
    "Origin"          = "https://www.celebritycruises.com"
}

function New-QP([string]$Key, [object]$Value) {
    [pscustomobject]@{ Key=$Key; Value=$Value }
}
function Enc([object]$Value) {
    [uri]::EscapeDataString([string]$Value)
}
function Build-Query([object[]]$Pairs) {
    $parts = foreach ($pair in $Pairs) {
        if ($null -eq $pair -or [string]::IsNullOrWhiteSpace([string]$pair.Key) -or $null -eq $pair.Value) { continue }
        "$(Enc $pair.Key)=$(Enc $pair.Value)"
    }
    $parts -join "&"
}

function Invoke-CelebrityHttp(
    [ValidateSet("GET","POST")][string]$Method,
    [string]$Uri,
    [object]$Headers,
    $Body = $null
) {
    $req = [ordered]@{
        method  = $Method
        url     = $Uri
        headers = $Headers
        timeout = 60
    }
    if ($null -ne $Body) { $req.body = $Body }

    $reqJson = $req | ConvertTo-Json -Depth 30 -Compress
    $raw = $reqJson | & $Python $Transport

    if ($LASTEXITCODE -ne 0) {
        throw "Python HTTP transport failed for $Method $Uri"
    }

    $resp = $raw | ConvertFrom-Json
    if ([int]$resp.status -lt 200 -or [int]$resp.status -ge 300) {
        $preview = [string]$resp.text
        if ($preview.Length -gt 1000) { $preview = $preview.Substring(0,1000) }
        throw "HTTP $($resp.status) for $Uri`n$preview"
    }
    return $resp
}

function Get-BalancedJsonArray([string]$Text, [string]$Key) {
    $m = [regex]::Match($Text, '"' + [regex]::Escape($Key) + '"\s*:\s*\[')
    if (!$m.Success) { return $null }
    $start = $m.Index + $m.Length - 1
    $depth=0; $inString=$false; $escape=$false

    for ($i=$start; $i -lt $Text.Length; $i++) {
        $c=$Text[$i]
        if ($escape) { $escape=$false; continue }
        if ($inString -and $c -eq [char]92) { $escape=$true; continue }
        if ($c -eq '"') { $inString=!$inString; continue }
        if (!$inString) {
            if ($c -eq '[') { $depth++ }
            elseif ($c -eq ']') {
                $depth--
                if ($depth -eq 0) {
                    $json=$Text.Substring($start,$i-$start+1)
                    try { return $json | ConvertFrom-Json } catch { return $null }
                }
            }
        }
    }
    return $null
}


function Get-BalancedJsonObject([string]$Text,[string]$Key) {
    $needle='"'+$Key+'"'
    $ki=$Text.IndexOf($needle,[System.StringComparison]::OrdinalIgnoreCase)
    if ($ki -lt 0) { return $null }

    $colon=$Text.IndexOf(':',$ki+$needle.Length)
    if ($colon -lt 0) { return $null }

    $start=$Text.IndexOf('{',$colon+1)
    if ($start -lt 0) { return $null }

    $depth=0; $inString=$false; $escaped=$false
    for ($i=$start; $i -lt $Text.Length; $i++) {
        $ch=$Text[$i]
        if ($inString) {
            if ($escaped) { $escaped=$false; continue }
            if ($ch -eq '\') { $escaped=$true; continue }
            if ($ch -eq '"') { $inString=$false }
            continue
        }

        if ($ch -eq '"') { $inString=$true; continue }
        if ($ch -eq '{') { $depth++ }
        elseif ($ch -eq '}') {
            $depth--
            if ($depth -eq 0) {
                $json=$Text.Substring($start,$i-$start+1)
                try { return ($json | ConvertFrom-Json) } catch { return $null }
            }
        }
    }
    return $null
}

function Get-SelectedDeck($RoomNumbers,$Room) {
    if ($RoomNumbers -and $RoomNumbers.decks) {
        $selected=@($RoomNumbers.decks | Where-Object { $_.selected -eq $true })
        if ($selected.Count -eq 1) { return $selected[0] }

        # Fallback only to another explicit provider field: assignment.deck.
        $assignmentDeck=$null
        if ($Room -and $Room.room -and $Room.room.assignment) {
            $assignmentDeck=$Room.room.assignment.deck
        }
        if ($assignmentDeck) {
            $match=@($RoomNumbers.decks | Where-Object {
                ([string]$_.code -eq [string]$assignmentDeck.code) -or
                ($null -ne $_.number -and $null -ne $assignmentDeck.number -and
                 [int]$_.number -eq [int]$assignmentDeck.number)
            })
            if ($match.Count -eq 1) { return $match[0] }
        }
    }
    return $null
}

function Convert-ProviderDeck($Deck) {
    if ($null -eq $Deck) { return $null }
    [pscustomobject]@{
        code=[string]$Deck.code
        number=if ($null -ne $Deck.number) {[int]$Deck.number} else {$null}
        name=[string]$Deck.name
        deckPlanUrl=[string]$Deck.deckPlanUrl
        startingPrice=$Deck.startingPrice
        roomsLeft=$Deck.roomsLeft
        connecting=$Deck.connecting
        selected=$Deck.selected
    }
}

function Get-RoomNumberInventory($Content) {
    $roomNumbers=Get-BalancedJsonObject $Content "roomNumbers"
    $rooms=Get-BalancedJsonArray $Content "rooms"
    $room=$null
    if ($rooms -and @($rooms).Count -gt 0) { $room=@($rooms)[0] }

    if ($null -eq $roomNumbers) {
        return [pscustomobject]@{
            roomNumbers=$null
            room=$room
            selectedDeck=$null
            deckOptions=@()
            cabins=@()
            isComplete=$false
            partialReason="roomNumbers object not found"
        }
    }

    $deckOptions=@($roomNumbers.decks)
    $selectedDeck=Get-SelectedDeck $roomNumbers $room
    $selectedDeckCanonical=Convert-ProviderDeck $selectedDeck

    $cabins=New-Object System.Collections.ArrayList
    foreach ($category in @($roomNumbers.categories)) {
        $providerCategory=[string]$category.categoryCode
        foreach ($cabin in @($category.cabins)) {
            if ($null -eq $cabin -or [string]::IsNullOrWhiteSpace([string]$cabin.cabinNumber)) { continue }
            [void]$cabins.Add([pscustomobject]@{
                roomNumber=[string]$cabin.cabinNumber
                categoryCode=$providerCategory
                positionCode=[string]$cabin.positionCode
                deck=$selectedDeckCanonical
                categoryPricing=$category.pricing
            })
        }
    }

    # The RSC payload exposes the current deck as selected=true. categories[].cabins[]
    # belongs to that selected deck. Other decks are advertised as choices but their
    # cabin arrays are not included in this response.
    $unselected=@($deckOptions | Where-Object { $_.selected -ne $true })
    $isComplete=($unselected.Count -eq 0)
    $reason=$null
    if (!$isComplete) {
        $reason="Provider advertised additional deck choices that were not enumerated by this request."
    }

    [pscustomobject]@{
        roomNumbers=$roomNumbers
        room=$room
        selectedDeck=$selectedDeckCanonical
        deckOptions=@($deckOptions | ForEach-Object { Convert-ProviderDeck $_ })
        cabins=@($cabins)
        isComplete=$isComplete
        partialReason=$reason
    }
}

function Get-PropValue($Object,[string[]]$Names) {
    if ($null -eq $Object) { return $null }
    foreach ($name in $Names) {
        $p=$Object.PSObject.Properties[$name]
        if ($null -ne $p -and $null -ne $p.Value -and [string]$p.Value -ne "") { return $p.Value }
    }
    return $null
}


function New-DeckContext($Code=$null,$Number=$null,$Name=$null) {
    $n=$null
    if ($null -ne $Number -and [string]$Number -match '^\d+$') { $n=[int]$Number }
    [pscustomobject]@{
        code=if ($null -ne $Code -and [string]$Code -ne "") {[string]$Code} else {$null}
        number=$n
        name=if ($null -ne $Name -and [string]$Name -ne "") {[string]$Name} else {$null}
    }
}

function Get-DeckFromNode($Node,[string]$CollectionName,$InheritedDeck) {
    if ($null -eq $Node -or !($Node -is [psobject])) { return $InheritedDeck }

    # Explicit room/deck metadata first.
    $deckNumber=Get-PropValue $Node @("deckNumber")
    $deckCode=Get-PropValue $Node @("deckCode")
    $deckName=Get-PropValue $Node @("deckName")

    $deckProp=$Node.PSObject.Properties["deck"]
    if ($deckProp -and $null -ne $deckProp.Value) {
        $dv=$deckProp.Value
        if ($dv -is [string] -or $dv -is [int] -or $dv -is [long]) {
            if (!$deckNumber -and ([string]$dv -match '^\d+$')) { $deckNumber=$dv }
            if (!$deckCode) { $deckCode=[string]$dv }
        }
        elseif ($dv -is [psobject]) {
            if (!$deckCode)   { $deckCode=Get-PropValue $dv @("code","deckCode","id") }
            if (!$deckNumber) { $deckNumber=Get-PropValue $dv @("number","deckNumber") }
            if (!$deckName)   { $deckName=Get-PropValue $dv @("name","deckName","displayName") }
        }
    }

    # When traversing a known deck collection, the object itself is the deck.
    if ($CollectionName -match '^(decks?|deckOptions?)$') {
        if (!$deckCode)   { $deckCode=Get-PropValue $Node @("code","deckCode","id") }
        if (!$deckNumber) { $deckNumber=Get-PropValue $Node @("number","deckNumber") }
        if (!$deckName)   { $deckName=Get-PropValue $Node @("name","deckName","displayName") }
    }

    # A provider deck object often identifies itself by a DECK ... name.
    $selfName=Get-PropValue $Node @("name","displayName")
    if (!$deckName -and $selfName -and ([string]$selfName -match '(?i)^deck\b')) {
        $deckName=$selfName
        if (!$deckCode)   { $deckCode=Get-PropValue $Node @("code","id") }
        if (!$deckNumber) { $deckNumber=Get-PropValue $Node @("number") }
    }

    if ($deckCode -or $deckNumber -or $deckName) {
        return New-DeckContext $deckCode $deckNumber $deckName
    }
    return $InheritedDeck
}

function Get-PositionFromNode($Node,[string]$CollectionName,$InheritedCode,$InheritedName) {
    $code=$InheritedCode
    $name=$InheritedName
    if ($null -eq $Node -or !($Node -is [psobject])) {
        return [pscustomobject]@{code=$code;name=$name}
    }

    $explicitCode=Get-PropValue $Node @("positionCode","locationCode")
    $explicitName=Get-PropValue $Node @("positionName","locationName")
    if ($explicitCode) { $code=[string]$explicitCode }
    if ($explicitName) { $name=[string]$explicitName }

    foreach ($propName in @("position","location")) {
        $p=$Node.PSObject.Properties[$propName]
        if ($p -and $p.Value -is [psobject]) {
            $v=$p.Value
            $c=Get-PropValue $v @("code","positionCode","locationCode","id")
            $n=Get-PropValue $v @("name","positionName","locationName","displayName")
            if ($c) { $code=[string]$c }
            if ($n) { $name=[string]$n }
        }
    }

    if ($CollectionName -match '^(positions?|locationOptions?)$') {
        $c=Get-PropValue $Node @("code","positionCode","locationCode","id")
        $n=Get-PropValue $Node @("name","positionName","locationName","displayName")
        if ($c) { $code=[string]$c }
        if ($n) { $name=[string]$n }
    }

    [pscustomobject]@{code=$code;name=$name}
}

function Add-RoomCandidate(
    [System.Collections.ArrayList]$Found,
    [string]$RoomNumber,
    $RoomObject,
    $Deck,
    [string]$PositionCode,
    [string]$PositionName,
    [string]$Path
) {
    if ([string]::IsNullOrWhiteSpace($RoomNumber)) { return }
    [void]$Found.Add([pscustomobject]@{
        roomNumber=$RoomNumber
        room=$RoomObject
        deck=$Deck
        positionCode=$PositionCode
        positionName=$PositionName
        sourcePath=$Path
    })
}

function Walk-RoomTree(
    $Node,
    [System.Collections.ArrayList]$Found,
    $InheritedDeck=$null,
    [string]$InheritedPositionCode="",
    [string]$InheritedPositionName="",
    [string]$CollectionName="",
    [string]$Path="$"
) {
    if ($null -eq $Node) { return }

    if ($Node -is [System.Collections.IDictionary]) {
        foreach ($k in $Node.Keys) {
            Walk-RoomTree $Node[$k] $Found $InheritedDeck $InheritedPositionCode $InheritedPositionName ([string]$k) "$Path.$k"
        }
        return
    }

    if ($Node -is [System.Collections.IEnumerable] -and !($Node -is [string]) -and !($Node -is [psobject])) {
        $i=0
        foreach ($x in $Node) {
            Walk-RoomTree $x $Found $InheritedDeck $InheritedPositionCode $InheritedPositionName $CollectionName "$Path[$i]"
            $i++
        }
        return
    }

    # PowerShell arrays returned by ConvertFrom-Json are PSObjects too, so handle
    # enumerable objects before treating a node as a normal object.
    if ($Node -is [System.Collections.IEnumerable] -and !($Node -is [string]) -and
        $Node.GetType().IsArray) {
        $i=0
        foreach ($x in $Node) {
            Walk-RoomTree $x $Found $InheritedDeck $InheritedPositionCode $InheritedPositionName $CollectionName "$Path[$i]"
            $i++
        }
        return
    }

    if (!($Node -is [psobject])) { return }

    $deck=Get-DeckFromNode $Node $CollectionName $InheritedDeck
    $pos=Get-PositionFromNode $Node $CollectionName $InheritedPositionCode $InheritedPositionName

    $explicitRoom=Get-PropValue $Node @("roomNumber","stateroomNumber","cabinNumber")
    $genericRoom=$null
    if (!$explicitRoom -and $CollectionName -match '^(rooms?|cabins?|availableRooms?|staterooms?)$') {
        $genericRoom=Get-PropValue $Node @("number")
    }
    $roomNo=if ($explicitRoom) {[string]$explicitRoom} elseif ($genericRoom) {[string]$genericRoom} else {$null}

    if ($roomNo) {
        Add-RoomCandidate $Found $roomNo $Node $deck ([string]$pos.code) ([string]$pos.name) $Path
    }

    foreach ($p in $Node.PSObject.Properties) {
        Walk-RoomTree $p.Value $Found $deck ([string]$pos.code) ([string]$pos.name) $p.Name "$Path.$($p.Name)"
    }
}

function Merge-RoomCandidates([System.Collections.ArrayList]$Found) {
    $map=[ordered]@{}
    foreach ($candidate in @($Found)) {
        $key=[string]$candidate.roomNumber
        if (!$map.Contains($key)) {
            $map[$key]=$candidate
            continue
        }

        $existing=$map[$key]
        if ($null -eq $existing.deck -and $null -ne $candidate.deck) { $existing.deck=$candidate.deck }
        if ([string]::IsNullOrWhiteSpace([string]$existing.positionCode) -and
            ![string]::IsNullOrWhiteSpace([string]$candidate.positionCode)) {
            $existing.positionCode=$candidate.positionCode
        }
        if ([string]::IsNullOrWhiteSpace([string]$existing.positionName) -and
            ![string]::IsNullOrWhiteSpace([string]$candidate.positionName)) {
            $existing.positionName=$candidate.positionName
        }
        if ($existing.sourcePath -notlike "*$($candidate.sourcePath)*") {
            $existing.sourcePath="$($existing.sourcePath) | $($candidate.sourcePath)"
        }
    }
    @($map.Values)
}

function Get-NormalizedLocation([string]$Code,[string]$Name) {
    # Prefer provider text where available. Only normalize unambiguous codes.
    if (![string]::IsNullOrWhiteSpace($Name)) { return $Name }
    switch ($Code) {
        "FW" { return "FORWARD" }
        "MS" { return "MIDSHIP" }
        "AF" { return "AFT" }
        default { return $null }
    }
}

function Get-TypeSubtype {
    $pairs=@(
        (New-QP "packageCode" $PackageCode),
        (New-QP "sailDate" $SailDate),
        (New-QP "country" $Country),
        (New-QP "selectedCurrencyCode" $Currency),
        (New-QP "shipCode" $PackageCode.Substring(0,2)),
        (New-QP "cabinClassType" "INTERIOR"),
        (New-QP "roomIndex" "0"),
        (New-QP "r0a" $Adults),
        (New-QP "r0c" $Children),
        (New-QP "r0b" "n"),
        (New-QP "r0r" "n"),
        (New-QP "r0s" "n"),
        (New-QP "r0q" "n"),
        (New-QP "r0t" "n"),
        (New-QP "r0d" "INTERIOR"),
        (New-QP "r0D" "y"),
        (New-QP "rgVisited" "true"),
        (New-QP "r0C" "y")
    )
    $uri="$Base/room-selection/type-and-subtype?$(Build-Query $pairs)"
    Write-Host "GET type-and-subtype" -ForegroundColor Cyan
    Write-Host "  $uri" -ForegroundColor DarkGray
    $resp=Invoke-CelebrityHttp -Method GET -Uri $uri -Headers $HeadersRsc
    $rawPath=Join-Path $OutputDir "celebrity-type-and-subtype-rsc.txt"
    Set-Content -LiteralPath $rawPath -Value $resp.text -Encoding UTF8
    $rooms=Get-BalancedJsonArray $resp.text "rooms"
    if (!$rooms) { throw "Could not extract rooms[] from type-and-subtype RSC. Raw response: $rawPath" }
    [pscustomobject]@{Uri=$uri;Rooms=$rooms}
}

function Get-RoomLocation([string]$TypeCode,[string]$SubtypeCode,[string]$CategoryCode) {
    $pairs=@(
        (New-QP "groupId" $GroupId),
        (New-QP "packageCode" $PackageCode),
        (New-QP "sailDate" $SailDate),
        (New-QP "country" $Country),
        (New-QP "selectedCurrencyCode" $Currency),
        (New-QP "shipCode" $PackageCode.Substring(0,2)),
        (New-QP "cabinClassType" $TypeCode),
        (New-QP "category" $CategoryCode),
        (New-QP "roomIndex" "0"),
        (New-QP "r0a" $Adults),
        (New-QP "r0c" $Children),
        (New-QP "r0b" "n"),
        (New-QP "r0r" "n"),
        (New-QP "r0s" "n"),
        (New-QP "r0q" "n"),
        (New-QP "r0t" "n"),
        (New-QP "r0d" $TypeCode),
        (New-QP "r0D" "y"),
        (New-QP "rgVisited" "true"),
        (New-QP "r0C" "y"),
        (New-QP "r0e" $SubtypeCode),
        (New-QP "r0f" $CategoryCode),
        (New-QP "r0g" "BESTRATE"),
        (New-QP "r0h" "n")
    )
    $uri="$Base/room-selection/room-location?$(Build-Query $pairs)"
    $resp=Invoke-CelebrityHttp -Method GET -Uri $uri -Headers $HeadersRsc
    [pscustomobject]@{Uri=$uri;Content=$resp.text}
}

function Get-ExactCabinPrice([string]$TypeCode,[string]$SubtypeCode,[string]$CategoryCode,[string]$RoomNumber) {
    $payload=[ordered]@{
        countryCode=$Country
        packageId=$PackageCode
        sailDate=$SailDate
        currencyCode=$Currency
        rooms=@(
            [ordered]@{
                stateroomTypeCode=$TypeCode
                stateroomSubtypeCode=$SubtypeCode
                categoryCode=$CategoryCode
                fareCode="BESTRATE"
                accessible=$false
                qualifiers=[ordered]@{
                    fireFighter=$false
                    military=$false
                    police=$false
                    senior=$false
                }
                occupancy=[ordered]@{
                    adultCount=$Adults
                    childCount=$Children
                }
                roomNumber=$RoomNumber
            }
        )
    }
    $uri="$Base/checkout/api/v1/rooms/checkout"
    try {
        $resp=Invoke-CelebrityHttp -Method POST -Uri $uri -Headers $HeadersJson -Body $payload
        return ($resp.text | ConvertFrom-Json)
    } catch {
        return [pscustomobject]@{error=$_.Exception.Message}
    }
}

Write-Host ""
Write-Host "Celebrity universal inventory observation collector v1.5" -ForegroundColor Green
Write-Host "  HTTP transport: curl_cffi / Chrome TLS impersonation"
Write-Host "  Package:   $PackageCode"
Write-Host "  Sail date: $SailDate"
Write-Host "  Group:     $GroupId"
Write-Host "  Market:    $Country / $Currency"
Write-Host "  Guests:    $Adults adult(s), $Children child(ren)"
Write-Host ""

$ts=Get-TypeSubtype
$rootRooms=@($ts.Rooms)
if ($rootRooms.Count -eq 0) { throw "rooms[] was empty." }

$stateroomTypes=@($rootRooms[0].options.stateroomTypes)
if ($stateroomTypes.Count -eq 0) { throw "No stateroomTypes found." }

$hierarchy=New-Object System.Collections.ArrayList
$observations=New-Object System.Collections.ArrayList
$rawDir=Join-Path $OutputDir "celebrity-room-location-rsc"
New-Item -ItemType Directory -Force -Path $rawDir | Out-Null

foreach ($type in $stateroomTypes) {
    $typeCode=[string](Get-PropValue $type @("code","typeCode","name"))
    $typeName=[string](Get-PropValue $type @("name","displayName","code"))

    foreach ($sub in @($type.stateroomSubtypes)) {
        $subCode=[string](Get-PropValue $sub @("code","subtypeCode"))
        $subName=[string](Get-PropValue $sub @("name","displayName"))
        $leadCategory=[string](Get-PropValue $sub @("categoryCode","category"))

        $candidateCategories=New-Object System.Collections.Generic.HashSet[string]
        if ($leadCategory) { [void]$candidateCategories.Add($leadCategory) }

        foreach ($propName in @("categories","stateroomCategories","categoryOptions")) {
            $prop=$sub.PSObject.Properties[$propName]
            if ($prop -and $prop.Value) {
                foreach ($cat in @($prop.Value)) {
                    $cc=[string](Get-PropValue $cat @("code","categoryCode","id"))
                    if ($cc) { [void]$candidateCategories.Add($cc) }
                }
            }
        }

        [void]$hierarchy.Add([pscustomobject]@{
            typeCode=$typeCode
            typeName=$typeName
            subtypeCode=$subCode
            subtypeName=$subName
            leadCategoryCode=$leadCategory
            candidateCategories=@($candidateCategories)
            roomsLeft=Get-PropValue $sub @("roomsLeft")
            pricing=$sub.pricing
        })

        foreach ($catCode in @($candidateCategories)) {
            if (!$typeCode -or !$subCode -or !$catCode) { continue }

            Write-Host "ROOM-LOCATION $typeCode / $subCode / $catCode" -ForegroundColor DarkCyan
            try {
                $loc=Get-RoomLocation $typeCode $subCode $catCode
            } catch {
                Write-Warning "room-location failed for $typeCode/$subCode/$catCode : $($_.Exception.Message)"
                continue
            }

            $safe="$typeCode-$subCode-$catCode" -replace '[^A-Za-z0-9_.-]','_'
            Set-Content -LiteralPath (Join-Path $rawDir "$safe.txt") -Value $loc.Content -Encoding UTF8

            $inventory=Get-RoomNumberInventory $loc.Content
            $rooms=@($inventory.cabins)

            if ($null -eq $inventory.selectedDeck -and $rooms.Count -gt 0) {
                Write-Warning "Provider returned cabins but no explicit selected deck for $typeCode/$subCode/$catCode. Cabins will retain deck=null."
            }

            if (!$inventory.isComplete) {
                $otherDecks=@($inventory.deckOptions | Where-Object { $_.selected -ne $true } | ForEach-Object { $_.code })
                Write-Warning ("PARTIAL DECK INVENTORY {0}/{1}/{2}: selected deck={3}; additional advertised decks={4}" -f `
                    $typeCode,$subCode,$catCode,$inventory.selectedDeck.code,($otherDecks -join ","))
            }
            $samplePrice=$null
            $sampleRoomNo=$null

            foreach ($candidate in $rooms) {
                $roomNo=[string]$candidate.roomNumber
                if (!$roomNo) { continue }

                $positionCode=[string]$candidate.positionCode
                $positionName=""
                $deck=$candidate.deck

                $price=$null
                $pricingScope="EXACT_CABIN"
                $pricedUsingCabinNumber=$roomNo

                if ($PricingMode -eq "CategorySample") {
                    $pricingScope="CATEGORY_SAMPLE"
                    if ($null -eq $samplePrice) {
                        Write-Host "  PRICE category sample using room $roomNo" -ForegroundColor Gray
                        $samplePrice=Get-ExactCabinPrice $typeCode $subCode $catCode $roomNo
                        $sampleRoomNo=$roomNo
                        if ($DelayMs -gt 0) { Start-Sleep -Milliseconds $DelayMs }
                    }
                    $price=$samplePrice
                    $pricedUsingCabinNumber=$sampleRoomNo
                }
                else {
                    Write-Host "  PRICE room $roomNo" -ForegroundColor Gray
                    $price=Get-ExactCabinPrice $typeCode $subCode $catCode $roomNo
                }

                $checkoutRoom=$null
                if ($price.PSObject.Properties["rooms"] -and @($price.rooms).Count -gt 0) {
                    $checkoutRoom=@($price.rooms)[0]
                }

                [void]$observations.Add([pscustomobject]@{
                    voyageId="$PackageCode`_$SailDate"
                    observedAtUtc=(Get-Date).ToUniversalTime().ToString("o")
                    packageCode=$PackageCode
                    sailDate=$SailDate
                    shipCode=$PackageCode.Substring(0,2)
                    market=[pscustomobject]@{
                        countryCode=$Country
                        currency=$Currency
                    }
                    occupancy=[pscustomobject]@{
                        adults=$Adults
                        children=$Children
                    }
                    category=[pscustomobject]@{
                        classCode=$typeCode
                        className=$typeName
                        subtypeCode=$subCode
                        subtypeName=$subName
                        categoryCode=$catCode
                    }
                    cabin=[pscustomobject]@{
                        number=$roomNo
                        deck=$deck
                        providerPositionCode=$positionCode
                        providerPositionName=$positionName
                        location=Get-NormalizedLocation $positionCode $positionName
                        sourcePath="roomNumbers.categories[].cabins[]"
                    }
                    availability=[pscustomobject]@{
                        status="AVAILABLE"
                        source="ROOM_LOCATION"
                        inventoryCompleteForCategory=$inventory.isComplete
                        partialReason=$inventory.partialReason
                    }
                    deckInventory=[pscustomobject]@{
                        selectedDeck=$inventory.selectedDeck
                        advertisedDecks=$inventory.deckOptions
                        advertisedDeckCount=@($inventory.deckOptions).Count
                        unqueriedDeckCodes=@($inventory.deckOptions | Where-Object { $_.selected -ne $true } | ForEach-Object { $_.code })
                    }
                    pricing=[pscustomobject]@{
                        roomLocationCategoryPricing=$candidate.categoryPricing
                        scope=$pricingScope
                        requestedFareCode="BESTRATE"
                        pricedUsingCabinNumber=$pricedUsingCabinNumber
                        checkoutRoom=$checkoutRoom
                    }
                    source=[pscustomobject]@{
                        provider="CELEBRITY"
                        roomLocationUrl=$loc.Uri
                        checkoutEndpoint="$Base/checkout/api/v1/rooms/checkout"
                    }
                    checkoutResponse=$price
                })

                if ($PricingMode -eq "ExactCabin" -and $DelayMs -gt 0) { Start-Sleep -Milliseconds $DelayMs }
            }
        }
    }
}

$hierarchyOut=Join-Path $OutputDir "celebrity-cabin-hierarchy-v1.5.json"
$obsOut=Join-Path $OutputDir "celebrity-cabin-observations-v1.5.json"
$validationOut=Join-Path $OutputDir "celebrity-cabin-validation-v1.5.json"

@($hierarchy) | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $hierarchyOut -Encoding UTF8
@($observations) | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $obsOut -Encoding UTF8

$deckMissing=@($observations | Where-Object { $null -eq $_.cabin.deck }).Count
$positionMissing=@($observations | Where-Object {
    [string]::IsNullOrWhiteSpace([string]$_.cabin.providerPositionCode) -and
    [string]::IsNullOrWhiteSpace([string]$_.cabin.providerPositionName)
}).Count
$checkoutErrors=@($observations | Where-Object {
    $_.checkoutResponse -and $_.checkoutResponse.PSObject.Properties["error"]
}).Count
$partialCategoryKeys=@(
    $observations |
    Where-Object { $_.availability.inventoryCompleteForCategory -eq $false } |
    ForEach-Object {
        "{0}/{1}/{2}" -f $_.category.classCode,$_.category.subtypeCode,$_.category.categoryCode
    } |
    Sort-Object -Unique
)
$partialObservationCount=@($observations | Where-Object {
    $_.availability.inventoryCompleteForCategory -eq $false
}).Count

$validation=[pscustomobject]@{
    version="1.5"
    voyageId="$PackageCode`_$SailDate"
    pricingMode=$PricingMode
    cabinCount=$observations.Count
    missingDeckCount=$deckMissing
    missingPositionCount=$positionMissing
    checkoutErrorCount=$checkoutErrors
    uniqueCabinCount=@($observations | ForEach-Object {$_.cabin.number} | Sort-Object -Unique).Count
    partialInventoryCategoryCount=$partialCategoryKeys.Count
    partialInventoryObservationCount=$partialObservationCount
    partialInventoryCategories=$partialCategoryKeys
    generatedAtUtc=(Get-Date).ToUniversalTime().ToString("o")
}
$validation | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $validationOut -Encoding UTF8

Write-Host ""
Write-Host "Celebrity universal inventory observation collector v1.5 complete." -ForegroundColor Green
Write-Host "  Hierarchy:       $hierarchyOut"
Write-Host "  Observations:    $obsOut"
Write-Host "  Validation:      $validationOut"
Write-Host "  Raw room RSC:    $rawDir"
Write-Host "  Cabins:          $($observations.Count)"
Write-Host "  Missing deck:    $deckMissing"
Write-Host "  Missing position:$positionMissing"
Write-Host "  Checkout errors: $checkoutErrors"
Write-Host "  Partial categories:$($partialCategoryKeys.Count)"
if ($partialCategoryKeys.Count -gt 0) {
    Write-Warning "Inventory is correct for the provider-selected deck(s), but not yet complete across all advertised decks. See validation JSON."
}

if ($observations.Count -eq 0) {
    Write-Warning "No physical cabin objects were detected. Inspect the saved room-location RSC files."
}

