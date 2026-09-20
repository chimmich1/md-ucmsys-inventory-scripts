# Changelog

## 1.0.0-rc5-hotfix2

- Store Celebrity and Princess static-master catalog paths relative to `work/state/static-masters`, allowing runtime state to move between DEV and PROD locations and between Windows and Linux.
- Accept and relocate legacy absolute-path catalog entries during validation, so existing RC5 state does not require another Full collection.
- Normalize legacy Celebrity catalog entries on the next static-master stage and publish a relative Celebrity manifest catalog path.

## 1.0.0-rc5-hotfix1

- Preserve complete Python stderr/tracebacks during Celebrity static-master discovery under Windows PowerShell 5.1 instead of stopping on the first stderr line.
- Report the native Python exit code after its complete diagnostic output has been written to the console and run log.

## 1.0.0-rc5
- Advance existing unsaturated Celebrity configuration masters during Daily
  operation using the current master as baseline and cumulative validation as
  tested-voyage history.
- Preserve cumulative tested-voyage reports so saturation can span successive
  Daily runs without replaying Full-run voyages.
- Skip only saturated configurations or configurations with no newly proven,
  currently published voyage evidence.
- Stage incremental output separately and promote generated masters plus raw
  evidence only after conflict validation succeeds.
- Add `-ResumeAtCelebrityMasters` for guarded recovery/testing without repeating
  acquisition, normalization, fleet survey, or registry import.

## 1.0.0-rc4
- Replace unsafe Princess `deckPlans.do` version scraping with the voyage-specific
  `providerShipVersion` already supplied by Princess and preserved in canonical voyages.
- Build every observed Princess ship/version combination rather than one assumed current
  version per ship.
- Discover Princess cabin decks through bounded `getDeckJSON.do` probes and retain only
  non-empty structured provider responses; numeric ranges are never emitted as decks.
- Record voyage-binding date ranges, voyage counts, probe outcomes, and hashes for audit.
- Write Princess layouts atomically and reuse existing layouts during Daily operation.
- Treat Git provenance as optional when running from a release ZIP; record
  `gitSha: UNKNOWN` instead of failing when no `.git` directory exists.
- Make Celebrity GraphQL acquisition retry transient failures and validate the
  complete response before atomically replacing the last known-good raw file.
- Fail the acquisition stage after exhausted retries instead of writing a
  zero-voyage artifact and incorrectly creating a successful checkpoint.
- Restore the established 100-group Celebrity page size instead of requesting
  up to 1,000 deeply nested cruise groups in one gateway request.
- Retry and validate each Celebrity page independently, reconcile every page
  against a stable API total, and reject duplicate cruise groups or sailings
  before atomically publishing the assembled raw response.
- Replace captured, expiring Akamai/session cookies and PowerShell web transport
  with a fresh `curl_cffi` browser-impersonated session for Celebrity GraphQL.

## 1.0.0-rc3
- Restored the v1.8.1 direct JSON rooms-API design for Celebrity static masters.
- Removed all Celebrity RSC acquisition, parsing, and raw RSC storage.
- Discover type/subtype hierarchy from JSON `rooms[].options.stateroomTypes`.
- Discover advertised decks and `physicalConfigurationId` from JSON `roomNumbers.decks[].deckPlanUrl`.
- Restrict each configuration crawl to registry-proven voyages for that configuration.
- Reduce the default candidate ceiling from 20 to 5 and stop during the crawl once saturation is reached.
- Clean each generated configuration directory during Full rebuilds so stopped RC2 RSC artifacts cannot survive into RC3 output.

## 1.0.0-rc2
- Normalize Princess scenic-cruising calls split across midnight as one logical event, including both observed Princess flag-slot variants.
- Recognize an unlabeled same-day scenic segment only when it is provider-code-related and starts exactly one minute after a labeled scenic segment.
- Consume only a structurally valid next-day, departure-only sequential continuation row.
- Retain fail-closed handling for all other unknown Princess itinerary rows.
- Add `-ReuseAcquiredVoyages` so a failed normalization run can resume from acquired provider artifacts without repeating provider calls.

## 1.0.0-rc1
- Code-only, zero-seed Full/Daily/Validate release candidate.
- Pipeline version read from root VERSION.
- Removed legacy runtime-data migration fallback.
- Validate made read-only.
- Integrated Celebrity configuration-keyed static cabin/category discovery from an empty runtime baseline.
- Daily preserves existing static configuration masters and discovers newly proven configurations.
- Added safe Princess currently-published deck-plan collection without inventing voyage bindings.
- Added release/operations/data/provenance/file-reference documentation.
