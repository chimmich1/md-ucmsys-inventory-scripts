#!/usr/bin/env python3
"""Preview permanent-master Daily jobs without calling providers or changing state."""
import argparse
import json
from pathlib import Path

from catalog_state import dump
from permanent_master_maintenance import known_sources, make_plan, snapshot_sources
from permanent_master_policy import assess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--princess-voyages", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    policy = repo / "config/permanent-master-refresh-policy.json"
    assessment = assess(args.snapshot_root, policy)
    plan = make_plan(assessment, known_sources(args.registry, args.princess_voyages),
                     snapshot_sources(args.snapshot_root))
    report = {"schemaVersion": "1.0", "mode": "PLAN_ONLY", "snapshotId": assessment["snapshotId"],
              "jobs": plan, "jobCount": len(plan),
              "providerBuilderCount": len({x["provider"] for x in plan})}
    dump(args.out, report)
    print(json.dumps({"jobCount": report["jobCount"],
                      "providerBuilderCount": report["providerBuilderCount"]}, indent=2))
    print(f"Plan: {args.out}")


if __name__ == "__main__":
    main()
