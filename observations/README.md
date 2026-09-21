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


For JSON-only full-ship jobs, deck_codes_from_master.py extracts the known deck selector values from the active published physical master. The collector should query those values through the provider's JSON request envelope and fail closed if any requested deck is not returned.

celebrity_json_inventory.py contains the JSON-only deck enumeration core. It places the requested deck in ooms[0].room.deckCode, queries every deck supplied by the physical master, retains raw JSON evidence, and fails closed when a requested deck is absent. Transport wiring remains explicit and provider-only.

category_pricing.py normalizes the provider's category pricing and cabin membership from each oomNumbers response while preserving the native pricing object.

Successful JSON observations can be written with publish, which replaces the destination atomically through a same-directory temporary file.
