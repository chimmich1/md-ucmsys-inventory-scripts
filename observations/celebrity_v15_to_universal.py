"""Convert archived Celebrity v1.5 observations to the universal v1.1 envelope."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Iterable


def convert_record(record: dict[str, Any]) -> dict[str, Any]:
    observed = record.get("observedAtUtc") or record.get("observedAt")
    category = record.get("category") or {}
    cabin = record.get("cabin") or {}
    availability = record.get("availability") or {}
    pricing = record.get("pricing") or {}
    source = record.get("source") or {}
    return {
        "schemaVersion": "1.1",
        "provider": source.get("provider", "CELEBRITY"),
        "voyageId": record["voyageId"],
        "observedAt": observed,
        "packageCode": record.get("packageCode"),
        "sailDate": record.get("sailDate"),
        "shipCode": record.get("shipCode"),
        "configuration": record.get("configurationId"),
        "market": record.get("market", {}),
        "occupancy": record.get("occupancy", {}),
        "category": category,
        "cabin": {
            "cabinNumber": cabin.get("cabinNumber", cabin.get("number")),
            "deck": cabin.get("deck"),
            "location": cabin.get("location"),
            "providerPositionCode": cabin.get("providerPositionCode"),
            "providerPositionName": cabin.get("providerPositionName"),
            "physicalMasterRef": record.get("physicalMasterRef"),
            "assignmentMasterRef": record.get("assignmentMasterRef"),
            "raw": cabin,
        },
        "availability": {
            "status": availability.get("status", "UNKNOWN"),
            "roomsLeft": availability.get("roomsLeft"),
            "inventoryCompleteForCategory": availability.get("inventoryCompleteForCategory"),
            "partialReason": availability.get("partialReason"),
        },
        "pricing": {
            "scope": pricing.get("scope"),
            "fareCode": pricing.get("requestedFareCode", pricing.get("fareCode")),
            "currency": (record.get("market") or {}).get("currency"),
            "amount": pricing.get("amount"),
            "taxes": pricing.get("taxes"),
            "total": pricing.get("total"),
            "raw": pricing,
        },
        "source": {
            "provider": source.get("provider", "CELEBRITY"),
            "roomLocationUrl": source.get("roomLocationUrl"),
            "checkoutEndpoint": source.get("checkoutEndpoint"),
            "evidenceRef": cabin.get("sourcePath"),
        },
        "checkout": record.get("checkoutResponse"),
    }


def convert_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [convert_record(record) for record in records]


def convert_file(source: Path, destination: Path) -> None:
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError("Celebrity v1.5 observations must be a JSON array")
    converted = convert_records(data)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(converted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    convert_file(args.source, args.destination)
