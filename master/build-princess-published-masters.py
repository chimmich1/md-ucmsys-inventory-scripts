#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from catalog_state import dump


def voyage_version(voyage):
    source = voyage.get("source") or {}
    value = source.get("providerShipVersion")
    return "" if value is None else str(value).strip()


def ship_code(voyage):
    ship = voyage.get("ship") or {}
    return str(ship.get("providerId") or voyage.get("shipCode") or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["Full", "Daily"], required=True)
    ap.add_argument("--voyages", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()

    document = json.loads(Path(a.voyages).read_text(encoding="utf-8-sig"))
    voyages = document.get("voyages", [])
    bindings = defaultdict(list)
    missing = []
    for voyage in voyages:
        ship = ship_code(voyage)
        version = voyage_version(voyage)
        if not ship or not version:
            missing.append(str(voyage.get("voyageId") or "UNKNOWN"))
            continue
        bindings[(ship, version)].append(voyage)
    if missing:
        preview = ", ".join(missing[:10])
        raise SystemExit(f"Princess voyages missing provider ship/version binding: {preview}")
    if not bindings:
        raise SystemExit("no Princess voyage ship/version bindings found")

    root = Path(__file__).resolve().parent
    base = Path(a.state) / "static-masters" / "princess"
    base.mkdir(parents=True, exist_ok=True)
    catalog = []
    built = 0
    reused = 0

    for ship, version in sorted(bindings):
        evidence = bindings[(ship, version)]
        final = base / ship / version / "published-deck-plan.json"
        if a.mode == "Daily" and final.exists():
            reused += 1
        else:
            final.parent.mkdir(parents=True, exist_ok=True)
            temporary = final.with_suffix(".json.partial")
            subprocess.run(
                [
                    a.python,
                    str(root / "providers/princess/published-deck-collector.py"),
                    "--ship", ship,
                    "--version", version,
                    "--out", str(temporary),
                ],
                check=True,
            )
            temporary.replace(final)
            built += 1

        dates = sorted(
            str(v.get("departureDate")) for v in evidence if v.get("departureDate")
        )
        catalog.append(
            {
                "shipCode": ship,
                "configurationId": version,
                "voyageBindingProven": True,
                "firstObservedSailingDate": dates[0] if dates else None,
                "lastObservedSailingDate": dates[-1] if dates else None,
                "boundVoyageCount": len(evidence),
                "path": final.relative_to(Path(a.state) / "static-masters").as_posix(),
                "sha256": hashlib.sha256(final.read_bytes()).hexdigest(),
            }
        )

    dump(
        base / "catalog.json",
        {
            "schemaVersion": "1.1",
            "scope": "provider-voyage-bound Princess ship configurations",
            "configurations": catalog,
        },
    )
    print(
        json.dumps(
            {
                "princessVoyageBoundConfigurations": len(catalog),
                "built": built,
                "reused": reused,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
