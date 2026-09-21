#!/usr/bin/env python3
"""Materialize an immutable permanent-master snapshot without provider calls."""
import argparse
from pathlib import Path

from permanent_master_snapshot import build_documents, publish


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--classes", type=Path)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    classes = args.classes or repo / "config/ship-classes.json"
    output = args.output_root or args.state / "static-masters/permanent-masters"
    snapshot_id, documents = build_documents(args.state, classes, repo)
    target = publish(output, snapshot_id, documents)
    print(f"Permanent-master snapshot: {snapshot_id}")
    print(f"Active manifest: {target / 'manifest.json'}")


if __name__ == "__main__":
    main()
