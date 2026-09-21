#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from catalog_state import dump, load, relocate_princess


def voyage_version(voyage):
    source = voyage.get("source") or {}
    value = source.get("providerShipVersion")
    return "" if value is None else str(value).strip()


def ship_code(voyage):
    ship = voyage.get("ship") or {}
    return str(ship.get("providerId") or voyage.get("shipCode") or "").strip()


def merge_targeted_decks(baseline, targeted):
    """Replace probed decks while preserving every unprobed published deck."""
    merged = dict(targeted)
    decks = {str(deck["deckCode"]): deck for deck in baseline.get("decks", [])}
    decks.update({str(deck["deckCode"]): deck for deck in targeted.get("decks", [])})
    merged["decks"] = [decks[key] for key in sorted(decks, key=lambda value: int(value))]
    discovery = dict(targeted.get("deckDiscovery") or {})
    targeted_codes = {str(deck["deckCode"]) for deck in targeted.get("decks", [])}
    discovery["preservedDeckCodes"] = sorted(
        (str(deck["deckCode"]) for deck in baseline.get("decks", [])
         if str(deck["deckCode"]) not in targeted_codes), key=int)
    merged["deckDiscovery"] = discovery
    merged["fingerprint"] = hashlib.sha256(
        json.dumps(merged["decks"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["Full", "Daily"], required=True)
    ap.add_argument("--voyages", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--configuration-filter", default="",
                    help="comma-separated SHIP/CONFIG targets; selected existing targets are recollected")
    ap.add_argument("--deck-targets", default="{}",
                    help="JSON mapping SHIP/CONFIG to exact deck numbers; absent targets use the bounded full scan")
    a = ap.parse_args()
    targets = {tuple(value.split("/", 1)) for value in a.configuration_filter.split(",") if value}
    deck_targets = json.loads(a.deck_targets)

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
    catalog_path = base / "catalog.json"
    existing_catalog = (relocate_princess(Path(a.state) / "static-masters", load(catalog_path))
                        if catalog_path.exists() else {"configurations": []})
    catalog = {(item["shipCode"], str(item["configurationId"])): item
               for item in existing_catalog.get("configurations", [])}
    built = 0
    reused = 0

    for ship, version in sorted(bindings):
        evidence = bindings[(ship, version)]
        final = base / ship / version / "published-deck-plan.json"
        if a.mode == "Daily" and final.exists() and (not targets or (ship, version) not in targets):
            reused += 1
        else:
            final.parent.mkdir(parents=True, exist_ok=True)
            temporary = final.with_suffix(".json.partial")
            baseline = json.loads(final.read_text(encoding="utf-8-sig")) if final.exists() else None
            command = [
                    a.python,
                    str(root / "providers/princess/published-deck-collector.py"),
                    "--ship", ship,
                    "--version", version,
                    "--out", str(temporary),
                ]
            selected_decks = deck_targets.get(f"{ship}/{version}")
            if selected_decks:
                command.extend(["--decks", ",".join(map(str, selected_decks))])
            subprocess.run(command, check=True)
            if selected_decks and baseline is not None:
                dump(temporary, merge_targeted_decks(
                    baseline, json.loads(temporary.read_text(encoding="utf-8-sig"))))
            temporary.replace(final)
            built += 1

        dates = sorted(
            str(v.get("departureDate")) for v in evidence if v.get("departureDate")
        )
        catalog[(ship, version)] = {
                "shipCode": ship,
                "configurationId": version,
                "voyageBindingProven": True,
                "firstObservedSailingDate": dates[0] if dates else None,
                "lastObservedSailingDate": dates[-1] if dates else None,
                "boundVoyageCount": len(evidence),
                "path": final.relative_to(Path(a.state) / "static-masters").as_posix(),
                "sha256": hashlib.sha256(final.read_bytes()).hexdigest(),
            }

    dump(
        catalog_path,
        {
            "schemaVersion": "1.1",
            "scope": "provider-voyage-bound Princess ship configurations",
            "configurations": [catalog[key] for key in sorted(catalog)],
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
