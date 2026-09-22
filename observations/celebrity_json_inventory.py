"""Celebrity JSON-only full-deck availability collector.

This module performs direct provider API requests. It never launches a browser or
parses rendered pages. Network execution is deliberately kept behind ``collect``
so tests can validate request construction offline.
"""
from __future__ import annotations
import argparse, json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from .category_pricing import category_pricing

@dataclass(frozen=True)
class Job:
    package_code: str
    sail_date: str
    country: str = "CAN"
    currency: str = "CAD"
    adults: int = 2
    children: int = 0


def request_payload(job: Job, type_code: str, subtype_code: str, deck_code: str) -> dict[str, Any]:
    return {
        "countryCode": job.country, "packageId": job.package_code,
        "sailDate": job.sail_date, "currencyCode": job.currency,
        "language": "en", "platform": "web", "options": True,
        "roomNumbers": True,
        "rooms": [{"adultCount": job.adults, "childCount": job.children,
                    "stateroomTypeCode": type_code, "stateroomSubtypeCode": subtype_code,
                    "accessible": False, "selectionFallbackStrategy": "RECOMMENDATION",
                    "editMode": True, "reset": False, "taxesAndFeesBundled": True,
                    "room": {"deckCode": str(deck_code).zfill(2)}}],
    }


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values(): yield from _walk(child)
    elif isinstance(value, list):
        for child in value: yield from _walk(child)


def room_numbers(response: Any) -> dict[str, Any] | None:
    for node in _walk(response):
        candidate = node.get("roomNumbers")
        if isinstance(candidate, dict) and isinstance(candidate.get("decks"), list):
            return candidate
    return None


def request_json(payload: dict[str, Any], *, endpoint: str = "https://www.celebritycruises.com/checkout/api/v1/rooms", timeout: int = 60) -> dict[str, Any]:
    """Execute one direct JSON API request using curl_cffi browser TLS impersonation.

    This is HTTP transport only: it does not launch a browser or parse HTML.
    """
    try:
        from curl_cffi import requests
    except ImportError as exc:
        raise RuntimeError("curl_cffi is required for Celebrity JSON transport") from exc
    response = requests.post(endpoint, json=payload, timeout=timeout, impersonate="chrome")
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError("Celebrity JSON endpoint returned a non-object response")
    return data

def collect(job: Job, selectors: list[tuple[str, str]], decks: list[str], request: Callable[[dict[str, Any]], Any]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    expected = {str(deck).zfill(2) for deck in decks}
    for type_code, subtype_code in selectors:
        for deck_code in sorted(expected, key=int):
            payload = request(request_payload(job, type_code, subtype_code, deck_code))
            inventory = room_numbers(payload)
            if inventory is None:
                raise RuntimeError(f"No roomNumbers JSON for {type_code}/{subtype_code}/deck {deck_code}")
            returned = {str(item.get("code", item.get("number"))).zfill(2) for item in inventory.get("decks", []) if item.get("code", item.get("number")) is not None}
            if deck_code not in returned:
                raise RuntimeError(f"Requested deck {deck_code} absent from provider response for {type_code}/{subtype_code}")
            observations.append({"selector": {"typeCode": type_code, "subtypeCode": subtype_code}, "requestedDeckCode": deck_code, "roomNumbers": inventory, "categoryPricing": category_pricing(inventory), "raw": payload})
    return observations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", type=Path, required=True, help="JSON job with packageCode, sailDate, selectors, decks")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit("Live execution is intentionally not wired to a browser; use the provider JSON transport adapter.")

if __name__ == "__main__": main()


def publish(path: Path, observations: list[dict[str, Any]]) -> None:
    """Atomically publish a complete observation array."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(observations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


