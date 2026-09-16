param(
  [ValidateSet("PRINCESS","CELEBRITY")][string]$Provider,
  [switch]$SkipFetch,
  [string]$Dir="."
)

$ErrorActionPreference = "Stop"
$Dir = [IO.Path]::GetFullPath($Dir)

function File([string[]]$names) {
  foreach ($n in $names) {
    $p = Join-Path $Dir $n
    if (Test-Path $p) { return $p }
  }
  throw "Missing required file: $($names -join ' or ')"
}

function J([string[]]$names) {
  Get-Content -Raw (File $names) | ConvertFrom-Json
}

function D($s) {
  if (!$s) { return $null }
  $v = [string]$s
  if ($v -match '^\d{8}$') {
    return "$($v.Substring(0,4))-$($v.Substring(4,2))-$($v.Substring(6,2))"
  }
  return $v.Substring(0,10)
}

function T($s) {
  if (!$s) { return $null }
  $v = [string]$s
  if ($v -match '^\d{2}:\d{2}:\d{2}$') { return $v }
  if ($v -match '^\d{2}:\d{2}$') { return "$v`:00" }
  try { return ([datetime]::Parse($v)).ToString("HH:mm:ss") } catch { return $v }
}

function Port($id, $name, $country, $region = $null) {
  [pscustomobject]@{
    providerId  = $id
    name        = $name
    countryCode = $country
    region      = $region
  }
}

function DateRangeInclusive([string]$startDate, [string]$endDate) {
  $start = [datetime](D $startDate)
  $end   = [datetime](D $endDate)
  if ($end -lt $start) { throw "Invalid date range: $startDate -> $endDate" }
  for ($d = $start; $d -le $end; $d = $d.AddDays(1)) {
    $d.ToString("yyyy-MM-dd")
  }
}

function New-CelebrityEvent($chapter, [string]$date, [hashtable]$countryByCode) {
  $startDate = D $chapter.startDate
  $endDate   = D $chapter.endDate
  $isFirst   = ($date -eq $startDate)
  $isLast    = ($date -eq $endDate)
  $code      = [string]$chapter.code
  $type      = [string]$chapter.type
  $activity  = [string]$chapter.activity

  $canonicalType =
    if ($code -eq "XID") { "DATE_LINE" }
    elseif ($type -eq "SHIP" -and $activity -eq "CRUISING") { "SEA" }
    elseif ($type -eq "LOCATION" -and $activity -eq "CRUISING") { "SCENIC_CRUISING" }
    elseif ($type -eq "LOCATION") { "PORT" }
    elseif ($type -eq "TOUR" -and $activity -eq "TOURING") { "LAND_TOUR" }
    else { "UNKNOWN" }

  $arrival = if ($isFirst) { T $chapter.arrivalTime } else { $null }
  $depart  = if ($isLast)  { T $chapter.departureTime } else { $null }

  $port = $null
  $tour = $null
  $visitType = $null

  if ($canonicalType -eq "PORT" -or $canonicalType -eq "SCENIC_CRUISING") {
    $country = if ($countryByCode.ContainsKey($code)) { $countryByCode[$code] } else { $null }
    $port = Port $code $chapter.name $country
  }

  if ($canonicalType -eq "PORT") {
    $visitType = switch ($activity) {
      "EMBARK"   { "EMBARK" }
      "DEBARK"   { "DEBARK" }
      "TENDERED" { "TENDERED" }
      "DOCKED"   { "DOCKED" }
      default     { $null }
    }
  }

  if ($canonicalType -eq "LAND_TOUR") {
    $tour = [pscustomobject]@{
      providerId = $code
      name       = $chapter.name
    }
  }

  [pscustomobject]@{
    type          = $canonicalType
    port          = $port
    tour          = $tour
    visitType     = $visitType
    arrivalTime   = $arrival
    departureTime = $depart
  }
}

if (!$SkipFetch) {
  & (Join-Path $Dir $(if ($Provider -eq "PRINCESS") { "princess-inventory.ps1" } else { "celebrity-inventory.ps1" }))
}

if ($Provider -eq "PRINCESS") {
  $products = J @("princess-products.json")
  $ports    = J @("princess-ports.json")
  $ships    = J @("princess-ships.json")
  $its      = J @("princess-itineraries.json")

  $pm = @{}
  $ports.ports | ForEach-Object { if ($_.id) { $pm[[string]$_.id] = $_ } }

  $sm = @{}
  $ships.ships | ForEach-Object { if ($_.id) { $sm[[string]$_.id] = $_ } }

  $im = @{}
  $its.cruises | ForEach-Object { if ($_.id) { $im[[string]$_.id] = $_ } }

  $voyages = @(foreach ($product in $products.products) {
    foreach ($c in $product.cruises) {
      $v = $c.voyage
      $start = D $v.sailDate
      $end = D $c.endDate
      $days = $null

      if ($im.ContainsKey([string]$v.id)) {
        $ip = $im[[string]$v.id]
        $eventsByDate = @{}
        $unknownPrincessEvents = 0

        foreach ($x in @($ip.itineraries)) {
          $date = D $x.arrivalDt
          if (!$date) {
            throw "Princess itinerary row has no arrivalDt: voyage=$($v.id) id=$($x.id)"
          }

          if ([datetime]$date -lt [datetime]$start -or [datetime]$date -gt [datetime]$end) {
            throw "Princess itinerary date outside voyage range: voyage=$($v.id) date=$date range=$start..$end"
          }

          $code = $null
          if ($x.id) {
            # Princess itinerary IDs append sequence suffixes. Match the
            # longest known provider location-code prefix.
            $code = $pm.Keys |
              Where-Object { ([string]$x.id).StartsWith([string]$_, [StringComparison]::OrdinalIgnoreCase) } |
              Sort-Object { $_.Length } -Descending |
              Select-Object -First 1
          }

          $pp = if ($code) { $pm[[string]$code] } else { $null }

          # IDL is a synthetic Princess location for crossing the International
          # Date Line. Some rows lack resFlag1=CD, so provider code is the more
          # reliable discriminator. Never normalize IDL as a physical PORT.
          $type =
            if ([string]$code -eq "IDL") { "DATE_LINE" }
            elseif (!$x.id) { "SEA" }
            elseif ($x.resFlag1 -eq "CD") { "DATE_LINE" }
            elseif ($x.resFlag1 -eq "SE" -or $x.resDesc1 -eq "SCENIC CRUISING" -or ($pp -and $pp.name -match "Scenic Cruising")) { "SCENIC_CRUISING" }
            elseif ($pp) { "PORT" }
            else { "UNKNOWN" }

          if ($type -eq "UNKNOWN") { $unknownPrincessEvents++ }

          # DATE_LINE is an operational event, not a port. Keep its location
          # object null, matching Celebrity XID normalization.
          $po = if (($type -eq "PORT" -or $type -eq "SCENIC_CRUISING") -and $pp) {
            Port $pp.id $pp.name $pp.countryId
          } else {
            $null
          }

          $visitType = $null
          if ($type -eq "PORT" -and $x.resFlag1 -eq "TR") { $visitType = "TENDERED" }

          $event = [pscustomobject]@{
            type          = $type
            port          = $po
            visitType     = $visitType
            arrivalTime   = T $x.arrivalTime
            departureTime = T $x.departTime
          }

          if (!$eventsByDate.ContainsKey($date)) {
            $eventsByDate[$date] = New-Object System.Collections.ArrayList
          }
          [void]$eventsByDate[$date].Add($event)
        }

        if ($unknownPrincessEvents -gt 0) {
          throw "Princess normalization produced $unknownPrincessEvents UNKNOWN event(s) for voyage $($v.id)."
        }

        # Canonical itinerary is date-centric. Princess dayIn is provider
        # sequencing metadata and can diverge from real calendar dates around
        # International Date Line crossings. Derive canonical day from the
        # explicit provider date instead. Multiple same-date provider rows are
        # represented as one MULTI day with ordered events[].
        $days = @(foreach ($date in @($eventsByDate.Keys | Sort-Object)) {
          $dayNumber = ([datetime]$date - [datetime]$start).Days + 1
          $events = @($eventsByDate[$date])

          if ($events.Count -eq 1) {
            $e = $events[0]
            [pscustomobject]@{
              day           = $dayNumber
              date          = $date
              type          = $e.type
              port          = $e.port
              visitType     = $e.visitType
              arrivalTime   = $e.arrivalTime
              departureTime = $e.departureTime
            }
          }
          else {
            [pscustomobject]@{
              day    = $dayNumber
              date   = $date
              type   = "MULTI"
              events = $events
            }
          }
        })
      }

      [pscustomobject]@{
        cruiseLine     = "PRINCESS"
        voyageId       = [string]$v.id
        ship            = [pscustomobject]@{
          providerId = $v.ship.id
          name       = $sm[[string]$v.ship.id].name
        }
        departureDate   = $start
        endDate         = $end
        durationNights  = ([datetime]$end - [datetime]$start).Days
        itineraryName   = $product.name
        itinerary       = $days
        source          = [pscustomobject]@{
          provider              = "PRINCESS"
          providerItineraryCode = $c.productCode
          providerShipVersion   = $v.ship.version
        }
      }
    }
  })
}
else {
  # Celebrity cruiseSearch GraphQL is the authoritative source for both the
  # complete sailing set and each sailing's own structured itinerary.
  $doc = J @("celebrity-voyages-raw.json")

  $cc = @{}
  $ccFile = File @("celebrity-port-country.json")
  (Get-Content -Raw $ccFile | ConvertFrom-Json).psobject.Properties |
    ForEach-Object { $cc[$_.Name] = $_.Value }

  function New-CelebrityGraphQlEvent($providerDay, $providerPort, [hashtable]$countryByCode) {
    $code = [string]$providerPort.port.code
    $name = [string]$providerPort.port.name
    $region = $providerPort.port.region
    $activity = [string]$providerPort.activity
    $dayType = [string]$providerDay.type

    $canonicalType =
      if ($code -eq "XID") { "DATE_LINE" }
      elseif ($dayType -eq "TOUR" -or $activity -eq "TOURING") { "LAND_TOUR" }
      elseif ($activity -eq "CRUISING" -and ($code -eq "ASE" -or $code -eq "CRU" -or !$code)) { "SEA" }
      elseif ($activity -eq "CRUISING") { "SCENIC_CRUISING" }
      else { "PORT" }

    $port = $null
    $tour = $null
    $visitType = $null

    if ($canonicalType -eq "PORT" -or $canonicalType -eq "SCENIC_CRUISING") {
      $country = if ($countryByCode.ContainsKey($code)) { $countryByCode[$code] } else { $null }
      $port = Port $code $name $country $region
    }
    if ($canonicalType -eq "LAND_TOUR") {
      $tour = [pscustomobject]@{ providerId=$code; name=$name }
    }
    if ($canonicalType -eq "PORT") {
      $visitType = switch ($activity) {
        "EMBARK"   { "EMBARK" }
        "DEBARK"   { "DEBARK" }
        "TENDERED" { "TENDERED" }
        "DOCKED"   { "DOCKED" }
        default     { $null }
      }
    }

    [pscustomobject]@{
      type          = $canonicalType
      port          = $port
      tour          = $tour
      visitType     = $visitType
      arrivalTime   = T $providerPort.arrivalTime
      departureTime = T $providerPort.departureTime
      providerDayType = $dayType
      providerActivity = $activity
      providerPortCode = $code
    }
  }

  $seen = New-Object 'System.Collections.Generic.HashSet[string]'
  $unknownEventCount = 0

  $voyages = @(foreach ($g in $doc.data.cruiseSearch.results.cruises) {
    foreach ($sailing in @($g.sailings)) {
      $voyageId = [string]$sailing.id
      if (!$voyageId) { throw "Celebrity sailing has no voyage id." }
      if (!$seen.Add($voyageId)) { throw "Duplicate Celebrity voyageId: $voyageId" }

      $it = $sailing.itinerary
      if (!$it) { throw "Celebrity sailing has no sailing-specific itinerary: $voyageId" }
      if (!@($it.days).Count) { throw "Celebrity sailing itinerary has no days: $voyageId" }

      $packageCode = [string]$it.code
      if (!$packageCode) { throw "Celebrity sailing itinerary has no package code: $voyageId" }

      $start = D $sailing.startDate
      $sailDate = D $sailing.sailDate
      $end = D $sailing.endDate
      if (!$start) { $start = $sailDate }
      if (!$end) { throw "Celebrity sailing has no endDate: $voyageId" }

      # GraphQL day.number is the provider's package-day ordinal. Multiple
      # provider rows/events sharing an ordinal are retained as canonical MULTI.
      # This preserves Date Line and PORT_TOUR structures instead of flattening
      # them into the old itinerary-page presentation model.
      $byNumber = @{}
      foreach ($pd in @($it.days)) {
        $n = [int]$pd.number
        if ($n -lt 1) { throw "Celebrity invalid itinerary day number: voyage=$voyageId number=$n" }
        if (!$byNumber.ContainsKey($n)) { $byNumber[$n] = New-Object System.Collections.ArrayList }

        $ports = @($pd.ports)
        if (!$ports.Count) {
          # Keep an explicit provider sea day even if no synthetic ASE port is supplied.
          if ([string]$pd.type -eq "CRUISING") {
            $synthetic=[pscustomobject]@{
              activity="CRUISING"; arrivalTime=$null; departureTime=$null
              port=[pscustomobject]@{code="ASE";name="Cruising";region=$null}
            }
            [void]$byNumber[$n].Add((New-CelebrityGraphQlEvent $pd $synthetic $cc))
          } else {
            throw "Celebrity itinerary day has no ports: voyage=$voyageId day=$n type=$($pd.type)"
          }
        } else {
          foreach ($pp in $ports) {
            $event = New-CelebrityGraphQlEvent $pd $pp $cc
            if ($event.type -eq "UNKNOWN") { $unknownEventCount++ }
            [void]$byNumber[$n].Add($event)
          }
        }
      }

      $days = @(foreach ($n in @($byNumber.Keys | Sort-Object {[int]$_})) {
        $date = ([datetime]$start).AddDays(([int]$n)-1).ToString("yyyy-MM-dd")
        $events = @($byNumber[$n])
        if ($events.Count -eq 1) {
          $e=$events[0]
          [pscustomobject]@{
            day=$n; date=$date; type=$e.type; port=$e.port; tour=$e.tour
            visitType=$e.visitType; arrivalTime=$e.arrivalTime; departureTime=$e.departureTime
          }
        } else {
          [pscustomobject]@{ day=$n; date=$date; type="MULTI"; events=$events }
        }
      })

      [pscustomobject]@{
        cruiseLine="CELEBRITY"
        voyageId=$voyageId
        ship=[pscustomobject]@{
          providerId=[string]$it.ship.code
          name=[string]$it.ship.name
        }
        departureDate=$start
        sailDate=$sailDate
        endDate=$end
        durationNights=([datetime]$end-[datetime]$start).Days
        itineraryName=[string]$it.name
        itinerary=$days
        source=[pscustomobject]@{
          provider="CELEBRITY"
          providerItineraryCode=$packageCode
          providerGroupId=[string]$g.id
          providerProductType=[string]$it.type
          providerVoyageType=[string]$it.voyageType
          sailingNights=$it.sailingNights
          totalNights=$it.totalNights
          bookingLink=$sailing.bookingLink
          itinerarySource="CRUISE_SEARCH_GRAPHQL_SAILING"
        }
      }
    }
  })

  if ($unknownEventCount -gt 0) {
    throw "Celebrity normalization produced $unknownEventCount UNKNOWN event(s). Refusing to write canonical output."
  }
  $expected = @($doc.data.cruiseSearch.results.cruises | ForEach-Object { $_.sailings }).Count
  if ($voyages.Count -ne $expected) {
    throw "Celebrity count mismatch after normalization: voyages=$($voyages.Count) discovered=$expected"
  }
}

$out = Join-Path $Dir ("cruise-voyages-" + $Provider.ToLower() + "-v3.1.json")

[pscustomobject]@{
  schemaVersion = 3
  generatedAt   = (Get-Date).ToUniversalTime().ToString("o")
  voyages       = $voyages
} | ConvertTo-Json -Depth 30 -Compress | Set-Content $out -Encoding UTF8

Write-Host "$($voyages.Count) voyages -> $out"
