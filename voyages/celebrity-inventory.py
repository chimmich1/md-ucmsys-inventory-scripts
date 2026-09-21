#!/usr/bin/env python3
"""Acquire Celebrity cruise-search GraphQL data with a fresh browser-like session."""
import argparse
import json
import os
import time
from pathlib import Path

from curl_cffi import requests


BASE = "https://www.celebritycruises.com"
GRAPH_URL = BASE + "/cruises/graph"
PAGE_SIZE = 100
MAX_ATTEMPTS = 4
BACKOFF = (5, 15, 30)

QUERY = r"""
query cruiseSearch_CruisesRiver($filters: String, $sort: CruiseSearchSort, $pagination: CruiseSearchPagination) {
  cruiseSearch(filters: $filters, sort: $sort, pagination: $pagination) {
    results {
      cruises {
        id
        productViewLink
        masterSailing {
          itinerary {
            name code voyageType
            days { number type ports { activity arrivalTime departureTime port { code name region } } }
            departurePort { code name region }
            destination { code name }
            portSequence sailingNights totalNights type
            ship { code name }
          }
        }
        sailings {
          id
          itinerary {
            name code voyageType
            days { number type ports { activity arrivalTime departureTime port { code name region } } }
            departurePort { code name region }
            destination { code name }
            portSequence sailingNights totalNights type
            ship { code name }
          }
          sailDate startDate endDate bookingLink
        }
      }
      total
    }
  }
}
"""


def compact_error(value):
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        return repr(value)


def fetch_page(session, page_number, skip):
    payload = {
        "operationName": "cruiseSearch_CruisesRiver",
        "variables": {
            "filters": "voyageType:OCEAN",
            "sort": {"by": "RECOMMENDED"},
            "pagination": {"count": PAGE_SIZE, "skip": skip},
        },
        "query": QUERY,
    }
    headers = {
        "accept": "application/json",
        "apollographql-client-name": "cel-NextGen-Cruise-Search",
        "apollographql-query-name": "cruiseSearch_CruisesRiver",
        "brand": "C",
        "country": "CAN",
        "countryalpha2code": "CA",
        "currency": "CAD",
        "language": "en",
        "office": "MIA",
        "origin": BASE,
        "referer": BASE + "/ca/cruises?country=CAN",
        "skip_authentication": "true",
    }
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.post(
                GRAPH_URL, headers=headers, json=payload, timeout=90
            )
            if response.status_code != 200:
                excerpt = (response.text or "")[:500].replace("\r", " ").replace("\n", " ")
                raise RuntimeError(f"HTTP {response.status_code}; body={excerpt!r}")
            document = response.json()
            errors = document.get("errors") if isinstance(document, dict) else None
            if errors:
                raise RuntimeError("GraphQL errors: " + compact_error(errors))
            results = (((document or {}).get("data") or {}).get("cruiseSearch") or {}).get("results")
            if not isinstance(results, dict):
                raise RuntimeError("response is missing data.cruiseSearch.results")
            cruises = results.get("cruises")
            total = results.get("total")
            if not isinstance(cruises, list) or not cruises:
                raise RuntimeError(f"empty cruise page; total={total!r}")
            if not isinstance(total, int) or total <= 0:
                raise RuntimeError(f"invalid API total: {total!r}")
            sailing_count = sum(
                len(item.get("sailings") or []) for item in cruises if isinstance(item, dict)
            )
            if sailing_count <= 0:
                raise RuntimeError("page contains no individual sailings")
            return cruises, total
        except Exception as exc:
            last_error = str(exc) or repr(exc)
            if attempt < MAX_ATTEMPTS:
                delay = BACKOFF[attempt - 1]
                print(
                    f"WARNING: Celebrity page {page_number} (skip={skip}) attempt "
                    f"{attempt}/{MAX_ATTEMPTS} failed: {last_error}. "
                    f"Retrying in {delay} seconds.",
                    flush=True,
                )
                time.sleep(delay)
    raise RuntimeError(
        f"Celebrity acquisition failed on page {page_number} (skip={skip}) "
        f"after {MAX_ATTEMPTS} attempts; the previous raw file was preserved. "
        f"Last error: {last_error}"
    )


def merge_unique_groups(existing, additions):
    """Append groups while preserving the first occurrence of each provider ID."""
    seen = {str(item.get("id") or "") for item in existing}
    for item in additions:
        group_id = str(item.get("id") or "")
        if group_id and group_id not in seen:
            existing.append(item)
            seen.add(group_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="celebrity-voyages-raw.json")
    args = parser.parse_args()

    session = requests.Session(impersonate="chrome")
    # Establish fresh edge/session cookies. No captured Akamai or browser session
    # tokens are stored in source.
    try:
        session.get(BASE + "/ca/cruises?country=CAN", timeout=45)
    except Exception as exc:
        print(f"WARNING: Celebrity session bootstrap failed: {exc}", flush=True)

    all_cruises = []
    short_pages = []
    expected_total = None
    skip = 0
    page_number = 0
    while expected_total is None or len(all_cruises) < expected_total:
        page_number += 1
        try:
            cruises, reported_total = fetch_page(session, page_number, skip)
        except RuntimeError as exc:
            if short_pages and "empty cruise page" in str(exc):
                # A short non-terminal page can leave one group outside the
                # provider's fixed-offset window. Probe just after that short
                # page and merge only previously unseen group IDs.
                for short_skip, short_count in short_pages:
                    recovery_skip = short_skip + short_count
                    recovered, recovery_total = fetch_page(
                        session, page_number, recovery_skip
                    )
                    if recovery_total != expected_total:
                        raise
                    merge_unique_groups(all_cruises, recovered)
                    if len(all_cruises) >= expected_total:
                        break
                if len(all_cruises) >= expected_total:
                    break
            raise
        if expected_total is None:
            expected_total = reported_total
        elif reported_total != expected_total:
            raise RuntimeError(
                f"Celebrity GraphQL total changed during pagination: "
                f"expected={expected_total} page={page_number} reported={reported_total}"
            )
        all_cruises.extend(cruises)
        print(
            f"Celebrity page {page_number}: groups={len(cruises)}, "
            f"accumulated={len(all_cruises)}/{expected_total}",
            flush=True,
        )
        if len(cruises) < PAGE_SIZE and skip + PAGE_SIZE < expected_total:
            short_pages.append((skip, len(cruises)))
        skip += PAGE_SIZE

    if len(all_cruises) != expected_total:
        raise RuntimeError(
            f"Celebrity GraphQL pagination count mismatch: "
            f"accumulated={len(all_cruises)} API total={expected_total}"
        )
    group_ids = [str(item.get("id") or "") for item in all_cruises]
    if not all(group_ids) or len(set(group_ids)) != len(group_ids):
        raise RuntimeError("Celebrity GraphQL pagination produced missing/duplicate cruise-group IDs")
    sailings = [
        sailing
        for group in all_cruises
        for sailing in (group.get("sailings") or [])
    ]
    sailing_ids = [str(item.get("id") or "") for item in sailings]
    if not all(sailing_ids) or len(set(sailing_ids)) != len(sailing_ids):
        raise RuntimeError("Celebrity GraphQL pagination produced missing/duplicate sailing IDs")

    document = {
        "data": {
            "cruiseSearch": {
                "results": {"cruises": all_cruises, "total": expected_total}
            }
        }
    }
    target = Path(args.out).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".partial")
    temporary.write_text(
        json.dumps(document, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    os.replace(temporary, target)

    print(f"Cruise groups: {len(all_cruises)}")
    print(f"Individual sailings: {len(sailings)}")
    print(f"API total: {expected_total}")
    print(f"Saved: {target.name}")
    print("\nCelebrity acquisition complete.")
    print(f"  {target.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(str(exc) or repr(exc))
