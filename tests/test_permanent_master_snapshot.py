import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "master"))
import permanent_master_snapshot as snapshot


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(tmp_path):
    state = tmp_path / "state"
    static = state / "static-masters"
    classes = tmp_path / "classes.json"
    write(classes, {"schemaVersion": "1.0", "unmappedPolicy": "SHIP_ONLY", "classes": [
        {"provider": "CELEBRITY", "classId": "edge", "shipCodes": ["AA", "BB"]}]})
    celebrity = []
    for ship, config, zone, code in (("AA", "1", "MID", "C1"), ("AA", "2", "MID", "C2"),
                                      ("BB", "1", "FORWARD", "C1")):
        relative = f"celebrity/{ship}/{config}/celebrity-ship-master-{ship}-v2.2.json"
        path = static / relative
        digest = write(path, {"provider": "CELEBRITY", "shipCode": ship,
            "targetConfiguration": config,
            "cabins": [{"cabinNumber": "101", "deck": {"number": 10, "name": "TEN"},
                        "locations": [zone]}],
            "categoryMaster": [{"classCode": "C", "className": "Cabin", "subtypeCode": "S",
                                "subtypeName": "Standard"}],
            "categoryAssignments": [{"cabinNumber": "101", "classCode": "C",
                                     "subtypeCode": "S", "categoryCode": code}]})
        celebrity.append({"shipCode": ship, "configurationId": config, "path": relative,
                          "sha256": digest, "saturated": True})
    write(static / "celebrity-catalog.json", {"configurations": celebrity})
    princess_path = static / "princess/AP/4/published-deck-plan.json"
    digest = write(princess_path, {"provider": "PRINCESS", "shipCode": "AP",
        "physicalConfigurationId": "4", "decks": [{"deckCode": "8", "response": {"cabins": [{
            "number": "E101", "deckNumber": 8, "deckName": "Emerald", "zoneName": "Forward",
            "areaInSqft": 200, "balconyAreaInSqft": 0, "numberOfBerths": 2,
            "wheelchairAccessible": False, "categoryCode": "OZ", "metaCode": "O",
            "subMetaCode": "F", "category": {"name": "Obstructed", "meta": {"name": "Oceanview"}}
        }]}}]})
    write(static / "princess/catalog.json", {"configurations": [{"shipCode": "AP",
        "configurationId": "4", "path": "princess/AP/4/published-deck-plan.json",
        "sha256": digest, "voyageBindingProven": True}]})
    return state, classes


def test_snapshot_is_deterministic_and_keeps_three_namespaces_separate(tmp_path):
    state, classes = evidence(tmp_path)
    first_id, first = snapshot.build_documents(state, classes, ROOT)
    second_id, second = snapshot.build_documents(state, classes, ROOT)
    assert (first_id, first) == (second_id, second)
    assert len(first) == 7  # three masters per provider plus manifest
    physical = first["celebrity-physical.json"]
    assignments = first["celebrity-assignments.json"]
    assert physical["kind"] == "PHYSICAL_CABIN_MASTER"
    assert len(assignments["revisions"]) == 2
    assert sorted(len(r["sourceIds"]) for r in assignments["revisions"]) == [1, 2]
    group = physical["groups"][0]
    assert group["conflicts"] == []  # the zone difference is a ship exception, not an intra-ship conflict
    ships = {s["shipCode"]: s for s in group["shipFields"]}
    assert ships["AA"]["cabins"][0]["fields"]["zones"]["value"] == ["MID"]
    assert ships["BB"]["cabins"][0]["fields"]["zones"]["value"] == ["FORWARD"]
    assert {m["shipCode"] for m in group["shipMembership"]} == {"AA", "BB"}
    assert all(v["status"] == "UNVERIFIED" for v in physical["coverage"].values())


def test_interrupted_activation_keeps_old_pointer_and_restart_recovers(tmp_path):
    state, classes = evidence(tmp_path)
    snapshot_id, documents = snapshot.build_documents(state, classes, ROOT)
    output = tmp_path / "permanent"
    write(output / "active-snapshot.json", {"schemaVersion": "1.0", "snapshotId": "old",
                                             "manifestPath": "snapshots/old/manifest.json"})
    def interrupt(_):
        raise RuntimeError("simulated interruption")
    with pytest.raises(RuntimeError, match="interruption"):
        snapshot.publish(output, snapshot_id, documents, before_activate=interrupt)
    assert json.loads((output / "active-snapshot.json").read_text())["snapshotId"] == "old"
    snapshot.publish(output, snapshot_id, documents)
    assert snapshot.validate_active(output)["snapshotId"] == snapshot_id


def test_tampered_snapshot_fails_closed(tmp_path):
    state, classes = evidence(tmp_path)
    snapshot_id, documents = snapshot.build_documents(state, classes, ROOT)
    output = tmp_path / "permanent"
    final = snapshot.publish(output, snapshot_id, documents)
    path = final / "celebrity-physical.json"
    document = json.loads(path.read_text())
    document["groups"] = []
    write(path, document)
    with pytest.raises(ValueError, match="hash mismatch"):
        snapshot.validate_active(output)


def test_legacy_validation_has_no_permanent_snapshot_requirement(tmp_path):
    assert snapshot.validate_active(tmp_path / "absent") is None


def test_active_pointer_cannot_escape_snapshot_root(tmp_path):
    output = tmp_path / "permanent"
    write(output / "active-snapshot.json", {"schemaVersion": "1.0", "snapshotId": "bad",
                                             "manifestPath": "../outside/manifest.json"})
    with pytest.raises(ValueError, match="escapes"):
        snapshot.validate_active(output)


def test_verified_prior_snapshot_can_be_reactivated_for_rollback(tmp_path):
    state, classes = evidence(tmp_path)
    first_id, first_documents = snapshot.build_documents(state, classes, ROOT)
    output = tmp_path / "permanent"
    snapshot.publish(output, first_id, first_documents)

    master = state / "static-masters/celebrity/AA/2/celebrity-ship-master-AA-v2.2.json"
    document = json.loads(master.read_text())
    document["categoryAssignments"][0]["categoryCode"] = "C3"
    new_hash = write(master, document)
    catalog_path = state / "static-masters/celebrity-catalog.json"
    catalog = json.loads(catalog_path.read_text())
    next(x for x in catalog["configurations"] if x["shipCode"] == "AA" and x["configurationId"] == "2")["sha256"] = new_hash
    write(catalog_path, catalog)
    second_id, second_documents = snapshot.build_documents(state, classes, ROOT)
    assert second_id != first_id
    assert (second_documents["celebrity-physical.json"]["revisionId"] ==
            first_documents["celebrity-physical.json"]["revisionId"])
    assert (second_documents["celebrity-categories.json"]["revisionId"] ==
            first_documents["celebrity-categories.json"]["revisionId"])
    assert (second_documents["celebrity-assignments.json"]["revisionId"] !=
            first_documents["celebrity-assignments.json"]["revisionId"])
    snapshot.publish(output, second_id, second_documents)
    assert snapshot.validate_active(output)["snapshotId"] == second_id

    snapshot.activate(output, first_id)
    assert snapshot.validate_active(output)["snapshotId"] == first_id
