param(
  [string]$Dir="."
)

$ErrorActionPreference="Stop"
$Dir=[IO.Path]::GetFullPath($Dir)

function Require-File($f){
  $p=Join-Path $Dir $f
  if(!(Test-Path $p)){throw "Missing required Celebrity source file: $p. Run .\\celebrity-inventory.ps1 first."}
  return $p
}
function J($f){Get-Content -Raw (Require-File $f)|ConvertFrom-Json}

$celebrity=J "celebrity-voyages-raw.json"

# Celebrity-only region -> ISO country/territory mapping.
$regionCountry=@{
  "Alaska"="US";"Florida"="US";"New Jersey"="US";"Maine"="US";"Louisiana"="US"
  "British Columbia"="CA";"Newfoundland"="CA"
  "Italy"="IT";"Japan"="JP";"Norway"="NO";"Spain"="ES";"Greece"="GR";"Peru"="PE"
  "New Zealand"="NZ";"Indonesia"="ID";"Vietnam"="VN";"Mexico"="MX";"France"="FR"
  "Montenegro"="ME";"Iceland"="IS";"Chile"="CL";"South Korea"="KR";"Australia"="AU"
  "Vanuatu"="VU";"Thailand"="TH";"Dominican Republic"="DO";"BVI"="VG";"Dominica"="DM"
  "Bahamas"="BS";"St. Vincent"="VC";"Brazil"="BR";"Argentina"="AR";"Jamaica"="JM"
  "Denmark"="DK";"Turkey"="TR";"Bermuda"="BM";"Ecuador"="EC";"Guatemala"="GT"
  "Costa Rica"="CR";"Canary Islands"="ES";"Falkland Island"="FK";"Malaysia"="MY"
  "Fiji"="FJ";"Taiwan"="TW";"Scotland"="GB";"England"="GB";"Northern Ireland"="GB"
  "Galapagos"="EC";"Isabela Island"="EC";"Floreana Island"="EC";"Santa Cruz Island"="EC"
  "San Cristobal Island"="EC";"Fernandina Island"="EC";"Santiago Island"="EC"
  "St. Maarten"="SX";"St. Thomas"="VI";"Antigua"="AG";"Aruba"="AW";"Bonaire"="BQ"
  "Curacao"="CW";"Grand Cayman"="KY";"Puerto Rico"="PR";"Barbados"="BB"
  "St. Lucia"="LC";"St. Kitts"="KN";"Grenada"="GD";"Belize"="BZ";"Panama"="PA"
  "Colombia"="CO";"Uruguay"="UY";"Portugal"="PT";"Croatia"="HR";"Malta"="MT"
  "Cyprus"="CY";"Slovenia"="SI";"Estonia"="EE";"Latvia"="LV";"Lithuania"="LT"
  "Germany"="DE";"Belgium"="BE";"Netherlands"="NL";"Sweden"="SE";"Finland"="FI"
  "Singapore"="SG";"Philippines"="PH";"Hong Kong"="HK";"French Polynesia"="PF"
  "South Africa"="ZA";"Egypt"="EG";"Morocco"="MA";"UAE"="AE";"United Arab Emirates"="AE"
  "Israel"="IL"
  "Corsica"="FR";"Samoa"="WS";"Oregon"="US";"Massachusetts"="US";"Washington"="US"
  "California"="US";"Hawaii"="US";"(Zeebrugge)"="BE";"Sardinia"="IT";"Crete"="GR"
  "Coquimbo"="CL";"Sicily"="IT";"Martinique"="MQ";"Turks & Caicos"="TC"
  "United Kingdom"="GB";"Ireland"="IE";"China"="CN";"Greenland"="GL";"Loyalty Island"="NC"
  "New Caledonia"="NC";"Scotland "="GB";"Azores"="PT";"American Samoa"="AS";"Tahiti"="PF"
  "Honduras"="HN";"Antarctica"="AQ";"St Kitts & Nevis"="KN";"Nova Scotia"="CA"
  "Quebec"="CA";"Nb (Bay Of Fundy)"="CA";"PEI"="CA"
}

# Celebrity-specific overrides where region is absent/ambiguous.
$codeCountry=@{
  "PTY"="PA";"SLB"="US";"GRB"="EC";"PUN"="EC";"SPL"="EC";"DAP"="EC";"DRH"="EC"
  "EBI"="EC";"SLV"="EC";"BAR"="EC";"NSY"="EC";"INV"="GB";"ISP"="US";"ENC"="US"
  "BGP"="GL";"XIP"="US";"MAE"="CL";"GES"="AQ";"DBS"="NZ";"DKY"="NZ";"LEL"="VU"
  "AJA"="FR";"APH"="AQ";"APW"="WS";"AST"="US";"BOS"="US";"BRU"="BE"
  "CAG"="IT";"CHQ"="GR";"COW"="CL";"CTA"="IT";"FDF"="MQ";"GDT"="TC"
  "GIB"="GI";"GWY"="IE";"HER"="GR";"HKG"="HK";"HNL"="US";"ITO"="US"
  "JJU"="GL";"KOA"="US";"LAX"="US";"LIF"="NC";"NOU"="NC";"NWF"="GB"
  "OPO"="PT";"ORK"="IE";"PDB"="AQ";"PDL"="PT";"PPG"="AS";"PPT"="PF"
  "RAB"="EC";"RTB"="HN";"SCD"="AQ";"SEA"="US";"SFO"="US";"SKB"="KN"
  "YHZ"="CA";"YQB"="CA";"YQY"="CA";"YSJ"="CA";"YYG"="CA"
}

# Celebrity records that are not geographic ports and intentionally have no country.
$countrylessCodes=@{
  "CRU"=$true  # generic Cruising
  "DLG"=$true  # MISSING PORT CONTENT
  "ECL"=$true  # Solar Eclipse (Cruising)
  "PSA"=$true  # MISSING PORT CONTENT
  "SPO"=$true  # MISSING PORT CONTENT
  "XID"=$true  # International Dateline
}

$result=@{}
$unresolved=@{}

foreach($g in $celebrity.data.cruiseSearch.results.cruises){
  foreach($sailing in @($g.sailings)){
    $m=$sailing.itinerary
    foreach($d in @($m.days)){
      foreach($x in @($d.ports)){
      $p=$x.port
      if(!$p.code -or $result.ContainsKey([string]$p.code)){continue}

      $code=[string]$p.code
      $region=if($null -eq $p.region){$null}else{([string]$p.region).Trim()}
      $cc=$null

      # Prefer a Celebrity code override because a region can be broader than the actual territory
      # (for example HKG is Hong Kong even when Celebrity reports region=China).
      if($codeCountry.ContainsKey($code)){$cc=$codeCountry[$code]}
      elseif($region -and $regionCountry.ContainsKey($region)){$cc=$regionCountry[$region]}

      if($cc){
        $result[$code]=$cc
      }elseif(!$countrylessCodes.ContainsKey($code)){
        $unresolved[$code]=[pscustomobject]@{name=$p.name;region=$p.region}
      }
      }
    }
  }
}

$ordered=[ordered]@{}
$result.GetEnumerator()|Sort-Object Name|ForEach-Object{$ordered[$_.Name]=$_.Value}

$out=Join-Path $Dir "celebrity-port-country.json"
$ordered|ConvertTo-Json|Set-Content $out -Encoding UTF8

Write-Host "$($ordered.Count) Celebrity port countries -> $out"
if($unresolved.Count){
  Write-Host "$($unresolved.Count) unresolved port codes:" -ForegroundColor Yellow
  $unresolved.GetEnumerator()|Sort-Object Name|ForEach-Object{
    Write-Host ("  {0}  {1}  [{2}]" -f $_.Name,$_.Value.name,$_.Value.region)
  }
}
