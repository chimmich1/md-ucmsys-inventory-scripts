#!/usr/bin/env python3
"""Assess completion and emit a targeted, offline permanent-master refresh queue."""
import argparse
import json
from pathlib import Path

from catalog_state import dump
from permanent_master_policy import assess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--policy", type=Path,
                        default=Path(__file__).resolve().parents[1] / "config/permanent-master-refresh-policy.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manual-target", action="append", default=[], metavar="PROVIDER/SHIP")
    parser.add_argument("--factory-refresh-target", action="append", default=[], metavar="PROVIDER/SHIP")
    args = parser.parse_args()
    report = assess(args.snapshot_root, args.policy, args.manual_target, args.factory_refresh_target)
    dump(args.out, report)
    print(json.dumps(report["queueSummary"], indent=2))
    print(f"Assessment: {args.out}")


if __name__ == "__main__":
    main()
