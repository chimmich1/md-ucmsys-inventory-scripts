#!/usr/bin/env python3
"""Build the Princess ship/version timeline from provider voyage bindings."""
from datetime import date
import argparse

from timeline_common import *


def ship_code(voyage):
    value = first(voyage, "shipCode", "ship", "providerShipCode", default="")
    if isinstance(value, dict):
        value = first(value, "providerId", "shipCode", "code", "id", default="")
    return str(value or "")


def voyage_id(voyage):
    return str(first(voyage, "providerId", "voyageId", "id", default=""))


def provider_ship_version(voyage):
    source = voyage.get("source") if isinstance(voyage.get("source"), dict) else {}
    value = first(source, "providerShipVersion", default=None)
    return None if value is None else str(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voyages", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--survey-start", default=str(date.today()))
    a = ap.parse_args()

    obj = load_json(a.voyages)
    voyages = obj if isinstance(obj, list) else first(obj, "voyages", "items", default=[])
    start = parse_date(a.survey_start)
    eligible = future_voyages(voyages, start)
    observations = []
    inventory = {}
    missing = []

    for voyage in eligible:
        ship = ship_code(voyage)
        version = provider_ship_version(voyage)
        record = {
            "provider": "PRINCESS",
            "voyageId": voyage_id(voyage),
            "shipCode": ship,
            "sailDate": sailing_date(voyage),
        }
        if not ship or version is None or version == "":
            record.update({
                "status": "UNRESOLVED_MISSING_PROVIDER_SHIP_VERSION",
                "physicalConfigurationId": None,
                "reason": "Canonical voyage has no Princess providerShipVersion.",
            })
            missing.append(record["voyageId"])
        else:
            record.update({
                "status": "SUCCESS",
                "physicalConfigurationId": version,
                "physicalConfigurationEvidence": {
                    "source": "canonical voyage source.providerShipVersion",
                    "providerSupplied": True,
                },
                "commercialHierarchySignature": None,
            })
            entry = inventory.setdefault(ship, {"shipCode": ship, "versions": {}})
            version_entry = entry["versions"].setdefault(version, {
                "physicalConfigurationId": version,
                "firstObservedSailingDate": record["sailDate"],
                "lastObservedSailingDate": record["sailDate"],
                "observedVoyageCount": 0,
            })
            version_entry["firstObservedSailingDate"] = min(
                version_entry["firstObservedSailingDate"], record["sailDate"]
            )
            version_entry["lastObservedSailingDate"] = max(
                version_entry["lastObservedSailingDate"], record["sailDate"]
            )
            version_entry["observedVoyageCount"] += 1
        observations.append(record)

    if missing:
        raise SystemExit(
            "Princess timeline has voyages without providerShipVersion: "
            + ", ".join(missing[:10])
        )

    serializable_inventory = {}
    for ship, entry in sorted(inventory.items()):
        serializable_inventory[ship] = {
            "shipCode": ship,
            "versions": [entry["versions"][key] for key in sorted(entry["versions"])],
        }
    result = {
        "schemaVersion": "1.1",
        "provider": "PRINCESS",
        "surveyStartDate": str(start),
        "eligibilityRule": "sailDate > surveyStartDate",
        "configurationEvidenceSource": "canonical voyage source.providerShipVersion",
        "shipVersionInventory": serializable_inventory,
        "observations": observations,
        "observedEras": observed_eras(observations),
        "transitions": transition_records(observations),
        "notes": [
            "Princess ship/version identity is supplied on each acquired voyage.",
            "No deckPlans.do page scraping or version projection is used.",
            "Observed bounds are not asserted effective dates beyond the published voyages.",
        ],
    }
    dump_json(a.out, result)
    print(
        f"Princess voyage-bound configurations: "
        f"{sum(len(x['versions']) for x in serializable_inventory.values())} "
        f"across {len(serializable_inventory)} ships"
    )


if __name__ == "__main__":
    main()
