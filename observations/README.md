# Celebrity dynamic observation collector

`celebrity-cabin-collector-v1.5.ps1` is the recovered provider collector for the
Celebrity room-selection → specific-cabin → checkout chain. It writes the
archived-compatible hierarchy, observations, validation report, and raw RSC
captures to the caller-selected output directory. It does not modify permanent
masters or `work/state`.

The collector requires Python 3 with `curl_cffi` and makes direct JSON/RSC API calls. It does not launch a browser, execute JavaScript, parse a DOM, or scrape rendered pages.
Use it only as an explicit observation job after selecting a voyage and output
folder. Tests use the converter and synthetic fixtures instead of contacting the
provider.


Use -RequireCompleteInventory for production jobs that must fail closed when any advertised deck was not returned by the provider API. Do not publish that run as a complete ship observation when the switch fails.

