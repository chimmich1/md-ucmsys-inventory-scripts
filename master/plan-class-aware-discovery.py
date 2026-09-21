#!/usr/bin/env python3
"""Plan class-aware static discovery from a permanent snapshot, without provider calls."""
import argparse
import hashlib
import json
from pathlib import Path

from catalog_state import dump
from permanent_master_snapshot import validate_active


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def class_index(path):
    document = load(path)
    if document.get("schemaVersion") != "1.0" or document.get("unmappedPolicy") != "SHIP_ONLY":
        raise ValueError("unsupported ship class configuration")
    result = {}
    for group in document.get("classes", []):
        provider, class_id = group.get("provider"), group.get("classId")
        for ship in group.get("shipCodes", []):
            key = (provider, ship)
            if key in result:
                raise ValueError(f"duplicate class membership: {key}")
            result[key] = class_id
    return result


def plan(snapshot_root, classes_path, assessment_path):
    manifest = validate_active(snapshot_root)
    if not manifest:
        raise ValueError("no active permanent-master snapshot")
    files = Path(snapshot_root) / "snapshots" / manifest["snapshotId"]
    classes = class_index(classes_path)
    assessment = load(assessment_path)
    queued = {(item.get("provider"), item.get("shipCode"), item.get("dimension"))
              for item in assessment.get("refreshQueue", [])}
    rows = []
    for provider in ("CELEBRITY", "PRINCESS"):
        physical = load(files / f"{provider.lower()}-physical.json")
        assignments = load(files / f"{provider.lower()}-assignments.json")
        assignment_sources = {source for revision in assignments.get("revisions", [])
                              for source in revision.get("sourceIds", [])}
        for group in physical.get("groups", []):
            for membership in group.get("shipMembership", []):
                ship = membership["shipCode"]
                class_id = classes.get((provider, ship))
                physical_queued = (provider, ship, "attributes") in queued
                assignment_queued = (provider, ship, "assignments") in queued
                source_ids = membership.get("configurationEvidence", [])
                rows.append({
                    "provider": provider, "classId": class_id or f"ship:{ship}",
                    "shipCode": ship, "groupId": group["groupId"],
                    "sourceIds": source_ids,
                    "physical": {"action": "TARGET_QUEUED" if physical_queued else "SKIP_REUSED_EVIDENCE",
                                  "reason": "missing-field-or-conflict queue" if physical_queued
                                            else "class/ship evidence has no queued physical work"},
                    "assignments": {"action": "TARGET_QUEUED" if assignment_queued else "SKIP_REUSED_EVIDENCE",
                                    "reason": "assignment gap queue" if assignment_queued
                                              else "assignment revision covers known source configurations",
                                    "knownSourceCount": sum(source in assignment_sources for source in source_ids)},
                    "categoryDefinitions": {"action": "SKIP_REUSED_EVIDENCE",
                                             "reason": "definitions are retained independently of physical discovery"},
                })
    rows.sort(key=lambda row: (row["provider"], row["classId"], row["shipCode"], row["groupId"]))
    counts = {}
    for namespace in ("physical", "assignments", "categoryDefinitions"):
        counts[namespace] = {action: sum(row[namespace]["action"] == action for row in rows)
                             for action in sorted({row[namespace]["action"] for row in rows})}
    return {"schemaVersion": "1.0", "kind": "CLASS_AWARE_DISCOVERY_PLAN",
            "snapshotId": manifest["snapshotId"],
            "classesSha256": hashlib.sha256(Path(classes_path).read_bytes()).hexdigest(),
            "assessmentSnapshotId": assessment.get("snapshotId"),
            "rows": rows, "rowCount": len(rows), "counts": counts,
            "providerCallsPlanned": sum(v.get("TARGET_QUEUED", 0) for v in counts.values()),
            "providerCallsSkipped": sum(v.get("SKIP_REUSED_EVIDENCE", 0) for v in counts.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--classes", type=Path, default=Path(__file__).resolve().parents[1] / "config/ship-classes.json")
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = plan(args.snapshot_root, args.classes, args.assessment)
    dump(args.out, report)
    print(json.dumps({k: report[k] for k in ("rowCount", "providerCallsPlanned", "providerCallsSkipped", "counts")}, indent=2))
    print(f"Plan: {args.out}")


if __name__ == "__main__":
    main()
