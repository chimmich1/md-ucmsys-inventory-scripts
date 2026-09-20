#!/usr/bin/env python3
"""Build or increment Celebrity configuration masters below runtime state."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def voyage_id(voyage):
    return str(voyage.get("voyageId") or voyage.get("providerId") or "")


def canonical_voyage_ids(path):
    document = load(path)
    return {
        voyage_id(voyage)
        for voyage in (document.get("voyages") or [])
        if voyage_id(voyage)
    }


def proven_configs(registry):
    result = {}
    for voyage in registry.get("voyages", {}).values():
        if (
            voyage.get("provider") != "CELEBRITY"
            or voyage.get("configurationEvidenceState") != "PROVEN_TARGET_SAILING"
        ):
            continue
        ship = voyage.get("shipCode")
        configuration = voyage.get("physicalConfigurationId")
        vid = voyage.get("voyageId")
        if ship and configuration and vid:
            result.setdefault((ship, str(configuration)), []).append(str(vid))
    return result


def run(command):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True)


def tested_voyages(validation):
    return {
        str(row.get("voyageId"))
        for row in (validation.get("voyages") or [])
        if row.get("voyageId")
    }


def relative_catalog_path(final, static_root):
    """Return a host-independent path relative to static-masters."""
    return Path(final).relative_to(Path(static_root)).as_posix()


def catalog_entry(ship, configuration, final, validation, static_root):
    return {
        "shipCode": ship,
        "configurationId": configuration,
        "path": relative_catalog_path(final, static_root),
        "sha256": sha(final),
        "saturated": bool((validation.get("saturation") or {}).get("saturated")),
    }


def promote_increment(staging, destination):
    """Promote validated generated files, then retain new raw evidence."""
    destination.mkdir(parents=True, exist_ok=True)
    for source in staging.iterdir():
        if source.name == "raw":
            raw_destination = destination / "raw"
            raw_destination.mkdir(parents=True, exist_ok=True)
            for voyage_dir in source.iterdir():
                target = raw_destination / voyage_dir.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.move(str(voyage_dir), str(target))
        elif source.is_file():
            temporary = destination / (source.name + ".promoting")
            shutil.copy2(source, temporary)
            temporary.replace(destination / source.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["Full", "Daily"], required=True)
    parser.add_argument("--voyages", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    state = Path(args.state)
    static_root = state / "static-masters"
    masters = static_root / "celebrity"
    masters.mkdir(parents=True, exist_ok=True)
    configurations = proven_configs(load(args.registry))
    available_voyages = canonical_voyage_ids(args.voyages)

    built = []
    advanced = []
    skipped_saturated = []
    skipped_no_new_voyages = []

    for (ship, configuration), registry_ids in sorted(configurations.items()):
        destination = masters / ship / configuration
        final = destination / f"celebrity-ship-master-{ship}-v2.2.json"
        validation_path = destination / f"celebrity-ship-master-validation-{ship}-v2.2.json"
        eligible_ids = sorted(set(registry_ids) & available_voyages)

        baseline = None
        previous_validation = None
        if args.mode == "Daily" and final.exists() and validation_path.exists():
            baseline = final
            previous_validation = validation_path
            validation = load(validation_path)
            if bool((validation.get("saturation") or {}).get("saturated")):
                skipped_saturated.append(f"{ship}:{configuration}")
                continue
            untested_ids = sorted(set(eligible_ids) - tested_voyages(validation))
            if not untested_ids:
                skipped_no_new_voyages.append(f"{ship}:{configuration}")
                continue
            selected_ids = untested_ids
            output = masters / ".daily-staging" / ship / configuration
            if output.exists():
                shutil.rmtree(output)
            output.mkdir(parents=True, exist_ok=True)
        else:
            output = destination
            if args.mode == "Full" and output.exists():
                shutil.rmtree(output)
            output.mkdir(parents=True, exist_ok=True)
            baseline = output / "bootstrap-empty-master.json"
            dump(
                baseline,
                {
                    "version": "bootstrap",
                    "provider": "CELEBRITY",
                    "shipCode": ship,
                    "fareProducts": [],
                    "categoryAssignments": [],
                    "categoryMaster": [],
                },
            )
            selected_ids = eligible_ids

        command = [
            args.python,
            root / "providers/celebrity/configuration-discovery.py",
            "--voyages", args.voyages,
            "--baseline-master", baseline,
            "--ship", ship,
            "--target-configuration", configuration,
            "--include-voyage-ids", ",".join(selected_ids),
            "--output", output,
        ]
        if previous_validation:
            command.extend(["--previous-validation", previous_validation])
        run(command)

        staged_final = output / f"celebrity-ship-master-{ship}-v2.2.json"
        staged_validation_path = output / f"celebrity-ship-master-validation-{ship}-v2.2.json"
        if not staged_final.exists() or not staged_validation_path.exists():
            raise SystemExit(f"missing expected generated master/validation {ship}:{configuration}")
        staged_validation = load(staged_validation_path)
        if staged_validation.get("cabinDeckConflictCount", 0):
            raise SystemExit(f"cabin/deck conflict {ship}:{configuration}")

        if previous_validation:
            promote_increment(output, destination)
            shutil.rmtree(output)
            final_validation = load(validation_path)
            advanced.append(catalog_entry(ship, configuration, final, final_validation, static_root))
        else:
            built.append(catalog_entry(ship, configuration, final, staged_validation, static_root))

    staging_root = masters / ".daily-staging"
    if staging_root.exists():
        shutil.rmtree(staging_root)

    catalog_path = state / "static-masters" / "celebrity-catalog.json"
    existing = {}
    if catalog_path.exists():
        for item in load(catalog_path).get("configurations", []):
            # Normalize catalogs produced by RC5 and earlier. Those releases
            # embedded the build machine's absolute path, which made otherwise
            # valid state impossible to relocate to DEV/PROD.
            ship = item.get("shipCode")
            configuration = str(item.get("configurationId"))
            if ship and configuration:
                expected = masters / ship / configuration / f"celebrity-ship-master-{ship}-v2.2.json"
                item["path"] = relative_catalog_path(expected, static_root)
            existing[(item.get("shipCode"), str(item.get("configurationId")))] = item
    for item in built + advanced:
        existing[(item["shipCode"], str(item["configurationId"]))] = item
    catalog = {
        "schemaVersion": "1.1",
        "provider": "CELEBRITY",
        "configurations": [existing[key] for key in sorted(existing)],
    }
    dump(catalog_path, catalog)

    manifest = {
        "schemaVersion": "1.1",
        "provider": "CELEBRITY",
        "mode": args.mode,
        "built": built,
        "advanced": advanced,
        "skippedSaturated": skipped_saturated,
        "skippedNoNewVoyages": skipped_no_new_voyages,
        # Backward-compatible aggregate for existing manifest consumers.
        "skippedExisting": skipped_saturated + skipped_no_new_voyages,
        "knownProvenConfigurationCount": len(configurations),
        "catalogPath": "celebrity-catalog.json",
    }
    dump(state / "static-masters" / "celebrity-manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
