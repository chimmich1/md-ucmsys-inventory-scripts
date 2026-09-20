#!/usr/bin/env python3
"""Collect one voyage-proven Princess ship/version cabin layout.

Deck numbers are probed, not inferred: a deck is retained only when Princess's
getDeckJSON endpoint returns a structured response containing cabins.
"""
import argparse
import hashlib
import json
from pathlib import Path

import requests

BASE = "https://www.princess.com"


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def cabin_rows(obj):
    if isinstance(obj, dict):
        rows = obj.get("cabins")
        if isinstance(rows, list):
            return rows
        data = obj.get("data")
        if isinstance(data, dict) and isinstance(data.get("cabins"), list):
            return data["cabins"]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ship", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deck-min", type=int, default=1)
    ap.add_argument("--deck-max", type=int, default=20)
    a = ap.parse_args()
    if a.deck_min < 0 or a.deck_max < a.deck_min or a.deck_max > 99:
        raise SystemExit("invalid bounded deck-probe range")

    session = requests.Session()
    rows = []
    probe_audit = []
    fatal_probes = []
    response_fingerprints = {}
    for number in range(a.deck_min, a.deck_max + 1):
        deck = str(number)
        response = session.get(
            BASE + "/getDeckJSON.do",
            params={"shipCode": a.ship, "version": a.version, "deck": deck},
            timeout=45,
        )
        audit = {"deckProbe": deck, "httpStatus": response.status_code}
        if not response.ok:
            audit["outcome"] = "HTTP_NOT_OK"
            probe_audit.append(audit)
            if response.status_code not in (400, 404):
                fatal_probes.append(f"deck {deck}: HTTP {response.status_code}")
            continue
        try:
            obj = response.json()
        except ValueError:
            audit["outcome"] = "NON_JSON"
            probe_audit.append(audit)
            continue
        cabins = cabin_rows(obj)
        if not cabins:
            audit["outcome"] = "NO_CABINS"
            probe_audit.append(audit)
            continue
        response_fingerprint = hashlib.sha256(
            json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        earlier_deck = response_fingerprints.get(response_fingerprint)
        if earlier_deck is not None:
            raise SystemExit(
                f"Princess returned the same non-empty deck JSON for probes "
                f"{earlier_deck} and {deck} on {a.ship} version {a.version}; "
                "refusing ambiguous deck assignment"
            )
        response_fingerprints[response_fingerprint] = deck
        audit.update({"outcome": "PROVIDER_CONFIRMED", "cabinCount": len(cabins)})
        probe_audit.append(audit)
        rows.append({"deckCode": deck, "response": obj, "cabinCount": len(cabins)})

    if fatal_probes:
        raise SystemExit(
            f"provider deck probes failed for {a.ship} version {a.version}: "
            + "; ".join(fatal_probes)
        )
    if not rows:
        raise SystemExit(
            f"no provider-confirmed cabin decks for {a.ship} version {a.version} "
            f"after bounded getDeckJSON probes {a.deck_min}..{a.deck_max}"
        )

    payload = {
        "schemaVersion": "1.1",
        "provider": "PRINCESS",
        "shipCode": a.ship,
        "physicalConfigurationId": str(a.version),
        "bindingScope": "PROVIDER_VOYAGE_SHIP_VERSION",
        "voyageBindingProven": True,
        "deckDiscovery": {
            "method": "BOUNDED_PROVIDER_JSON_PROBES",
            "range": {"minimum": a.deck_min, "maximum": a.deck_max},
            "acceptanceRule": "structured getDeckJSON response containing one or more cabins",
            "probes": probe_audit,
        },
        "decks": rows,
    }
    payload["fingerprint"] = hashlib.sha256(
        json.dumps(payload["decks"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    dump(a.out, payload)
    print(
        f"{a.ship}: version={a.version}, provider-confirmed decks={len(rows)}, "
        f"cabins={sum(x['cabinCount'] for x in rows)}"
    )


if __name__ == "__main__":
    main()
