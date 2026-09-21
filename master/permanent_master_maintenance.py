"""Plan and execute bounded permanent-master maintenance jobs."""
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from catalog_state import dump
from permanent_master_policy import assess
from permanent_master_snapshot import build_documents, publish, validate_active


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def known_sources(registry_path, princess_voyages_path):
    result = set()
    registry = load(registry_path)
    for voyage in registry.get("voyages", {}).values():
        if voyage.get("provider") == "CELEBRITY" and voyage.get("configurationEvidenceState") == "PROVEN_TARGET_SAILING":
            ship, config = voyage.get("shipCode"), voyage.get("physicalConfigurationId")
            if ship and config is not None:
                result.add(f"CELEBRITY/{ship}/{config}")
    for voyage in load(princess_voyages_path).get("voyages", []):
        ship_obj, source = voyage.get("ship") or {}, voyage.get("source") or {}
        ship = ship_obj.get("providerId") or voyage.get("shipCode")
        config = source.get("providerShipVersion")
        if ship and config is not None and str(config).strip():
            result.add(f"PRINCESS/{ship}/{str(config).strip()}")
    return result


def snapshot_sources(snapshot_root):
    manifest = validate_active(snapshot_root)
    directory = Path(snapshot_root) / "snapshots" / manifest["snapshotId"]
    result = set()
    for provider in ("celebrity", "princess"):
        physical = load(directory / f"{provider}-physical.json")
        result.update(source["sourceId"] for source in physical["sources"])
    return result


def work_key(source, action, dimension, field=""):
    return "|".join((source, action, dimension, field or ""))


def make_plan(assessment, known, published, stalled_keys=()):
    stalled_keys = set(stalled_keys)
    jobs = defaultdict(lambda: {"actions": set(), "dimensions": set(), "reasons": set(),
                                "workKeys": set(), "deckNumbers": set(), "fullDeckScan": False})
    for source in sorted(set(known) - set(published)):
        key = work_key(source, "BOOTSTRAP_CONFIGURATION", "all")
        if key in stalled_keys:
            continue
        jobs[source]["actions"].add("BOOTSTRAP_CONFIGURATION")
        jobs[source]["dimensions"].update(("membership", "attributes", "categoryDefinitions", "assignments"))
        jobs[source]["reasons"].add("configuration is known locally but absent from active snapshot")
        jobs[source]["workKeys"].add(key)
        jobs[source]["fullDeckScan"] = True
    for item in assessment["refreshQueue"]:
        sources = item.get("sourceIds") or [s for s in published
            if s.startswith(f"{item['provider']}/{item['shipCode']}/")]
        for source in sources:
            key = work_key(source, item["action"], item["dimension"], item.get("field", ""))
            if key in stalled_keys:
                continue
            job = jobs[source]
            job["actions"].add(item["action"])
            job["dimensions"].add(item["dimension"])
            job["reasons"].add(item["reason"])
            job["workKeys"].add(key)
            if item.get("deckNumbers"):
                job["deckNumbers"].update(item["deckNumbers"])
            else:
                job["fullDeckScan"] = True
    result = []
    for source, value in sorted(jobs.items()):
        provider, ship, configuration = source.split("/", 2)
        result.append({"sourceId": source, "provider": provider, "shipCode": ship,
                       "configurationId": configuration, "actions": sorted(value["actions"]),
                       "dimensions": sorted(value["dimensions"]), "reasons": sorted(value["reasons"]),
                       "workKeys": sorted(value["workKeys"]), "deckNumbers": sorted(value["deckNumbers"]),
                       "fullDeckScan": value["fullDeckScan"]})
    return result


def run(command, runner=subprocess.run):
    print("+", " ".join(map(str, command)), flush=True)
    runner([str(x) for x in command], check=True)


def execute(plan, repo, state, data, celebrity_voyages, princess_voyages, registry,
            python=sys.executable, runner=subprocess.run):
    by_provider = defaultdict(list)
    for job in plan:
        by_provider[job["provider"]].append(f"{job['shipCode']}/{job['configurationId']}")
    commands = []
    if by_provider["CELEBRITY"]:
        commands.append([python, repo / "master/build-static-masters.py", "--mode", "Daily",
            "--voyages", celebrity_voyages, "--registry", registry, "--state", state,
            "--data", data, "--python", python, "--configuration-filter", ",".join(by_provider["CELEBRITY"])])
    if by_provider["PRINCESS"]:
        princess_jobs = [job for job in plan if job["provider"] == "PRINCESS"]
        deck_targets = {f"{job['shipCode']}/{job['configurationId']}": job["deckNumbers"]
                        for job in princess_jobs if not job["fullDeckScan"] and job["deckNumbers"]}
        commands.append([python, repo / "master/build-princess-published-masters.py", "--mode", "Daily",
            "--voyages", princess_voyages, "--state", state, "--python", python,
            "--configuration-filter", ",".join(by_provider["PRINCESS"]),
            "--deck-targets", json.dumps(deck_targets, sort_keys=True, separators=(",", ":"))])
    for command in commands:
        run(command, runner)
    return commands


def refresh_snapshot(repo, state, policy_path):
    snapshot_root = Path(state) / "static-masters/permanent-masters"
    snapshot_id, documents = build_documents(Path(state), repo / "config/ship-classes.json", repo)
    publish(snapshot_root, snapshot_id, documents)
    return assess(snapshot_root, policy_path)
