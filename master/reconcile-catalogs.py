#!/usr/bin/env python3
"""Repair catalog metadata only, without collection or changes to evidence."""
import argparse
from pathlib import Path

from catalog_state import dump, load, reconcile_celebrity, relocate_princess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True)
    args = parser.parse_args()
    root = Path(args.state) / "static-masters"
    celebrity_path = root / "celebrity-catalog.json"
    princess_path = root / "princess/catalog.json"
    manifest_path = root / "celebrity-manifest.json"
    # Prepare every document before publishing any changes. Each replacement is
    # atomic and the command is idempotent if interrupted between replacements.
    celebrity = reconcile_celebrity(root, load(celebrity_path))
    princess = relocate_princess(root, load(princess_path))
    manifest = load(manifest_path)
    manifest["catalogPath"] = "celebrity-catalog.json"
    for path, document in ((celebrity_path, celebrity), (princess_path, princess),
                           (manifest_path, manifest)):
        dump(path, document)
    print(f"Reconciled {len(celebrity['configurations'])} Celebrity and "
          f"relocated {len(princess['configurations'])} Princess catalog entries; "
          "masters, validation reports, and raw evidence unchanged.")


if __name__ == "__main__":
    main()
