#!/usr/bin/env python3
"""Offline, non-publishing audit for the permanent-master migration."""
import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from catalog_state import dump, resolve_catalog_path

PHYSICAL_FIELDS = (
    "deckNumber", "deckName", "zones", "areaInSqft", "balconyAreaInSqft",
    "balconyWidth", "balconyLength", "numberOfBerths", "wheelchairAccessible",
    "bathType", "familySuite",
)
DIMENSIONS = {"areaInSqft", "balconyAreaInSqft", "balconyWidth", "balconyLength"}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def normalize(field, value):
    if value is None or value == "" or value == []:
        return None
    if field in DIMENSIONS:
        return value if type(value) in (int, float) and value > 0 else None
    if field == "deckNumber":
        return int(value)
    if field == "zones":
        return sorted({str(v).strip().upper() for v in value if v}) or None
    if isinstance(value, str):
        return value.strip().upper() or None
    return value


def load_classes(path):
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if document.get("schemaVersion") != "1.0" or document.get("unmappedPolicy") != "SHIP_ONLY":
        raise ValueError("expected class configuration 1.0 with SHIP_ONLY fallback")
    index = {}
    for group in document["classes"]:
        if group["provider"] not in ("CELEBRITY", "PRINCESS") or not group["classId"]:
            raise ValueError("invalid class provider or identifier")
        for ship in group["shipCodes"]:
            key = (group["provider"], ship)
            if key in index:
                raise ValueError(f"duplicate class membership: {key}")
            index[key] = group["classId"]
    return index


def extract(provider, document):
    """Retain physical facts and commercial facts in independent namespaces."""
    cabins, definitions, assignments = [], {}, defaultdict(set)
    if provider == "CELEBRITY":
        for row in document["cabins"]:
            deck = row.get("deck") or {}
            attrs = {"deckNumber": deck.get("number"), "deckName": deck.get("name"),
                     "zones": row.get("locations")}
            cabins.append((str(row["cabinNumber"]), attrs))
        for row in document["categoryMaster"]:
            key = canonical([row["classCode"], row["subtypeCode"]])
            # leadCategoryCode and candidateCategories are observations of offers,
            # not the stable definition of a type/subtype.
            value = {k: row.get(k) for k in ("classCode", "className", "subtypeCode", "subtypeName")}
            definitions.setdefault(key, {})[fingerprint(value)] = value
        for row in document["categoryAssignments"]:
            assignments[str(row["cabinNumber"])].add(
                (row["classCode"], row["subtypeCode"], row["categoryCode"]))
    else:
        for deck in document["decks"]:
            response = deck["response"]
            rows = response.get("cabins")
            if not isinstance(rows, list):
                rows = (response.get("data") or {}).get("cabins")
            if not isinstance(rows, list) or not rows:
                raise ValueError("Princess deck contains no structured cabin rows")
            for row in rows:
                cabin = str(row["number"])
                returned_deck = row.get("deck") or {}
                attrs = {field: row.get(field) for field in PHYSICAL_FIELDS}
                attrs["deckNumber"] = row.get("deckNumber", returned_deck.get("number"))
                attrs["deckName"] = row.get("deckName", returned_deck.get("name"))
                if normalize("deckNumber", attrs["deckNumber"]) != int(deck["deckCode"]):
                    raise ValueError(f"Princess returned/probed deck mismatch: {cabin}")
                zone = row.get("zoneName") or (row.get("zone") or {}).get("name")
                attrs["zones"] = [zone] if zone else None
                cabins.append((cabin, attrs))
                category = row.get("category") or {}
                code = row["categoryCode"]
                value = {"categoryCode": code, "categoryName": category.get("name"),
                         "classCode": row.get("metaCode"), "subtypeCode": row.get("subMetaCode"),
                         "className": (category.get("meta") or {}).get("name")}
                definitions.setdefault(code, {})[fingerprint(value)] = value
                assignments[cabin].add((row.get("metaCode"), row.get("subMetaCode"), code))
    physical = defaultdict(lambda: defaultdict(set))
    for cabin, attrs in cabins:
        for field in PHYSICAL_FIELDS:
            physical[cabin][field].add(canonical(normalize(field, attrs.get(field))))
    return physical, definitions, assignments


def audit(state, classes_path):
    static = state / "static-masters"
    inputs = {classes_path: hashlib.sha256(classes_path.read_bytes()).hexdigest()}
    classes = load_classes(classes_path)
    sources = []
    grouped = defaultdict(list)

    def read(path):
        data = path.read_bytes()
        inputs[path] = hashlib.sha256(data).hexdigest()
        return json.loads(data.decode("utf-8-sig"))

    for provider, relative in (("CELEBRITY", "celebrity-catalog.json"), ("PRINCESS", "princess/catalog.json")):
        catalog = read(static / relative)
        seen = set()
        for item in catalog["configurations"]:
            ship, config = item["shipCode"], str(item["configurationId"])
            if (ship, config) in seen:
                raise ValueError(f"duplicate catalog identity: {provider}/{ship}/{config}")
            seen.add((ship, config))
            filename = f"celebrity-ship-master-{ship}-v2.2.json" if provider == "CELEBRITY" else "published-deck-plan.json"
            path = resolve_catalog_path(static, item["path"], provider.lower(), ship, config, filename)
            if not path.resolve().is_relative_to(static.resolve()):
                raise ValueError("master path escapes selected static state")
            document = read(path)
            if inputs[path] != item["sha256"]:
                raise ValueError(f"catalog hash mismatch: {path}")
            actual_config = document.get("targetConfiguration") if provider == "CELEBRITY" else document.get("physicalConfigurationId")
            if document.get("provider") != provider or document.get("shipCode") != ship or str(actual_config) != config:
                raise ValueError(f"master identity mismatch: {path}")
            source_id = f"{provider}/{ship}/{config}"
            physical, definitions, assignments = extract(provider, document)
            physical_payload = {cabin: {field: sorted(values) for field, values in sorted(fields.items())}
                                for cabin, fields in sorted(physical.items())}
            definition_payload = {key: {digest: value for digest, value in sorted(variants.items())}
                                  for key, variants in sorted(definitions.items())}
            assignment_payload = {cabin: sorted(values) for cabin, values in sorted(assignments.items())}
            class_id = classes.get((provider, ship))
            missing = {field: sum(values[field] == {"null"} for values in physical.values()) for field in PHYSICAL_FIELDS}
            sources.append({"sourceId": source_id, "path": path.relative_to(static).as_posix(),
                            "sha256": inputs[path], "provider": provider, "shipCode": ship,
                            "configurationId": config, "classId": class_id,
                            "physicalEvidenceSha256": fingerprint(physical_payload),
                            "categoryEvidenceSha256": fingerprint(definition_payload),
                            "assignmentEvidenceSha256": fingerprint(assignment_payload),
                            "observedCabins": len(physical), "unknownFields": missing,
                            "legacySaturated": item.get("saturated"),
                            "membershipCompleteness": "UNVERIFIED"})
            grouped[(provider, class_id or f"ship:{ship}")].append({
                "sourceId": source_id, "ship": ship, "config": config,
                "physical": physical, "definitions": definitions, "assignments": assignments})

    groups = []
    for (provider, group_id), records in sorted(grouped.items()):
        records.sort(key=lambda record: record["sourceId"])
        facts = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        ship_facts = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))
        membership = defaultdict(set)
        definition_variants = defaultdict(lambda: defaultdict(set))
        definition_values = {}
        assignment_maps = defaultdict(list)
        for record in records:
            source_id = record["sourceId"]
            membership[record["ship"]].update(record["physical"])
            for cabin, fields in record["physical"].items():
                for field, values in fields.items():
                    for value in values:
                        facts[cabin][field][value].add(source_id)
                        ship_facts[record["ship"]][cabin][field][value].add(source_id)
            for key, variants in record["definitions"].items():
                for digest, value in variants.items():
                    definition_values[digest] = value
                    definition_variants[key][digest].add(source_id)
            mapping = {c: sorted(values) for c, values in sorted(record["assignments"].items())}
            assignment_maps[fingerprint(mapping)].append(source_id)

        shared, variants, ship_only = [], [], 0
        for cabin, fields in sorted(facts.items()):
            for field, values in sorted(fields.items()):
                known = {v: ids for v, ids in values.items() if v != "null"}
                if len(known) == 1:
                    value, ids = next(iter(known.items()))
                    ships = {sid.split("/")[1] for sid in ids}
                    if len(ships) > 1:
                        shared.append({"cabinNumber": cabin, "field": field,
                                       "value": json.loads(value), "sourceIds": sorted(ids),
                                       "unknownSourceIds": sorted(values.get("null", []))})
                    else:
                        ship_only += 1
                elif len(known) > 1:
                    variants.append({"cabinNumber": cabin, "field": field,
                                     "unknownSourceIds": sorted(values.get("null", [])),
                                     "variants": [{"value": json.loads(v), "sourceIds": sorted(ids)}
                                                  for v, ids in sorted(known.items())]})

        version_differences = []
        for a, b in itertools.combinations(records, 2):
            if a["ship"] != b["ship"]:
                continue
            ma, mb = a["assignments"], b["assignments"]
            common = ma.keys() & mb.keys()
            changed = sorted(c for c in common if ma[c] != mb[c])
            version_differences.append({"sourceA": a["sourceId"], "sourceB": b["sourceId"],
                "commonCabins": len(common), "differentAssignmentSets": len(changed),
                "disjointAssignmentSets": sum(ma[c].isdisjoint(mb[c]) for c in changed),
                "examples": [{"cabinNumber": c, "a": sorted(ma[c]), "b": sorted(mb[c])} for c in changed[:5]]})
        groups.append({"provider": provider, "groupId": group_id,
            "scope": "SHIP_ONLY" if group_id.startswith("ship:") else "CLASS",
            "confirmedShipMembership": {ship: sorted(cabins) for ship, cabins in sorted(membership.items())},
            "sourceMembership": [{"sourceId": record["sourceId"],
                                  "cabinNumbers": sorted(record["physical"])} for record in records],
            "shipFieldObservations": [{"shipCode": ship, "cabins": [
                {"cabinNumber": cabin, "fields": [{"field": field, "values": [
                    {"value": json.loads(value), "sourceIds": sorted(ids)}
                    for value, ids in sorted(values.items())]}
                    for field, values in sorted(fields.items())]}
                for cabin, fields in sorted(cabins.items())]}
                for ship, cabins in sorted(ship_facts.items())],
            "observedCabinUnion": len(facts), "proposedSharedFields": shared,
            "shipOnlyFieldCount": ship_only, "fieldsRequiringVariants": variants,
            "variantCountsByField": dict(sorted(Counter(v["field"] for v in variants).items())),
            "categoryDefinitions": [{"key": key, "variants": [
                {"definition": definition_values[digest], "sourceIds": sorted(ids)}
                for digest, ids in sorted(values.items())]} for key, values in sorted(definition_variants.items())],
            "identicalAssignmentMapGroups": [sorted(ids) for ids in assignment_maps.values() if len(ids) > 1],
            "assignmentRevisions": [{"assignmentFingerprint": digest,
                                     "sourceIds": sorted(assignment_maps[digest]),
                                     "assignments": [{"cabinNumber": cabin, "categoryIdentities": values}
                                                     for cabin, values in sorted(next(
                                                         {c: sorted(v) for c, v in sorted(r["assignments"].items())}
                                                         for r in records if r["sourceId"] in assignment_maps[digest]).items())]}
                                    for digest in sorted(assignment_maps)],
            "assignmentVersionDifferences": version_differences})

    # Detect concurrent edits during the read. Audit never writes these inputs.
    for path, digest in inputs.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"input changed during audit: {path}")
    return {"schemaVersion": "1.0", "kind": "PERMANENT_MASTER_MIGRATION_AUDIT",
        "publishesMasters": False, "classConfigurationSha256": inputs[classes_path],
        "summary": {"sourceMasters": len(sources), "ships": len({(s['provider'], s['shipCode']) for s in sources}),
                    "classGroups": sum(g["scope"] == "CLASS" for g in groups),
                    "unmappedShipGroups": sum(g["scope"] == "SHIP_ONLY" for g in groups),
                    "proposedSharedFields": sum(len(g["proposedSharedFields"]) for g in groups),
                    "variantFields": sum(len(g["fieldsRequiringVariants"]) for g in groups)},
        "limitations": ["Membership is observed, not verified complete; legacy saturation is not completeness.",
                         "Shared values apply only to source-confirmed ship/cabin fields; unknowns remain unknown.",
                         "Variants span ships and collected configurations; no chronology or physical change is inferred.",
                         "Zero dimensions are unknown; category ranges are not cabin measurements.",
                         "No provider calls, prices, or production master changes are part of this audit."],
        "sources": sorted(sources, key=lambda s: s["sourceId"]), "groups": groups}


def markdown(report):
    lines = ["# Permanent-master migration audit", "", "Offline proposal only; existing masters are unchanged.", "",
             "| Group | Ships | Observed cabin union | Shared field candidates | Variant fields |",
             "|---|---:|---:|---:|---:|"]
    for group in report["groups"]:
        lines.append(f"| {group['provider']}/{group['groupId']} | {len(group['confirmedShipMembership'])} | "
                     f"{group['observedCabinUnion']} | {len(group['proposedSharedFields'])} | {len(group['fieldsRequiringVariants'])} |")
    lines.extend(["", "## Limits", ""] + [f"- {x}" for x in report["limitations"]])
    lines.extend(["", "Detailed JSON contains confirmed membership, source hashes, field variants, category definitions, and assignment comparisons.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--classes", type=Path, default=Path(__file__).resolve().parents[1] / "config/ship-classes.json")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    # Keep output separate from all operational state/data, even through symlinks.
    operational = (args.state.resolve(), args.state.parent.resolve() / "data")
    output = args.out_dir.resolve()
    if any(output == root or output.is_relative_to(root) for root in operational):
        parser.error("audit output must be outside runtime state and data")
    report = audit(args.state, args.classes)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    dump(args.out_dir / "migration-audit.json", report)
    (args.out_dir / "migration-audit.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Report: {args.out_dir / 'migration-audit.md'}")


if __name__ == "__main__":
    main()
