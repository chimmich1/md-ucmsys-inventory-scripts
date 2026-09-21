#!/usr/bin/env python3
"""Atomically activate a verified existing permanent-master snapshot."""
import argparse
from pathlib import Path

from permanent_master_snapshot import activate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    activate(args.state / "static-masters/permanent-masters", args.snapshot)
    print(f"Active permanent-master snapshot: {args.snapshot}")


if __name__ == "__main__":
    main()
