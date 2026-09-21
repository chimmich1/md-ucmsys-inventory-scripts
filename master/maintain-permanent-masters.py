#!/usr/bin/env python3
"""Run bounded queued maintenance for an active permanent-master snapshot."""
import argparse
import json
import sys
from pathlib import Path

from catalog_state import dump
from permanent_master_maintenance import (execute, known_sources, make_plan,
                                          refresh_snapshot, snapshot_sources,
                                          class_memberships, class_aware_summary)
from permanent_master_policy import assess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--celebrity-voyages", type=Path, required=True)
    parser.add_argument("--princess-voyages", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--retry-stalled", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    root = args.state / "static-masters/permanent-masters"
    policy = repo / "config/permanent-master-refresh-policy.json"
    assessment = assess(root, policy)
    known = known_sources(args.registry, args.princess_voyages)
    published = snapshot_sources(root)
    maintenance_state_path = root / "maintenance-state.json"
    maintenance_state = ({"schemaVersion": "1.0", "stalledWork": {}}
                         if not maintenance_state_path.exists() else
                         json.loads(maintenance_state_path.read_text(encoding="utf-8-sig")))
    if args.retry_stalled:
        maintenance_state["stalledWork"] = {}
    active_stalled = {key for key, value in maintenance_state["stalledWork"].items()
                      if value.get("snapshotId") == assessment["snapshotId"] and
                      value.get("policySha256") == assessment["policySha256"]}
    plan = make_plan(assessment, known, published, active_stalled)
    reuse_summary = class_aware_summary(
        plan, known, published, class_memberships(repo / "config/ship-classes.json"))
    execute(plan, repo, args.state, args.data, args.celebrity_voyages, args.princess_voyages,
            args.registry, args.python)
    if plan:
        assessment = refresh_snapshot(repo, args.state, policy)
        remaining = make_plan(assessment, known, snapshot_sources(root))
        remaining_keys = {key for job in remaining for key in job["workKeys"]}
        for key in sorted({key for job in plan for key in job["workKeys"]} & remaining_keys):
            maintenance_state["stalledWork"][key] = {
                "status": "DISCOVERY_STALLED", "reason": "targeted collection completed without resolving this work item",
                "retry": "--retry-stalled, changed evidence, or changed policy",
                "snapshotId": assessment["snapshotId"], "policySha256": assessment["policySha256"]}
        dump(maintenance_state_path, maintenance_state)
    report = {"schemaVersion": "1.0", "mode": "DAILY_MAINTENANCE", "jobs": plan,
              "collectorInvocationCount": len({x["provider"] for x in plan}),
              "resultingSnapshotId": assessment["snapshotId"],
              "stalledWorkCount": len(maintenance_state["stalledWork"]),
              "remainingQueueSummary": assessment["queueSummary"],
              "classAwareDiscovery": reuse_summary}
    dump(args.out, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
