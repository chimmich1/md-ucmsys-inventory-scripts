import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "master"))
spec = importlib.util.spec_from_file_location("permanent_audit", ROOT / "master/audit-permanent-masters.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture_state(tmp_path):
    state = tmp_path / "state"
    static = state / "static-masters"
    (static / "princess").mkdir(parents=True)
    (static / "princess/catalog.json").write_text('{"configurations": []}')
    classes = tmp_path / "classes.json"
    classes.write_text(json.dumps({"schemaVersion": "1.0", "unmappedPolicy": "SHIP_ONLY",
        "classes": [{"provider": "CELEBRITY", "classId": "edge", "shipCodes": ["AA", "BB", "CC"]}]}))
    entries = []
    for ship, config, zone, category in [("AA", "1", "MID", "C1"), ("AA", "2", "MID", "C2"),
                                         ("BB", "1", "FORWARD", "C1"), ("CC", "1", None, "C1"),
                                         ("ZZ", "1", "MID", "C1")]:
        relative = f"celebrity/{ship}/{config}/celebrity-ship-master-{ship}-v2.2.json"
        path = static / relative
        path.parent.mkdir(parents=True)
        document = {"provider": "CELEBRITY", "shipCode": ship, "targetConfiguration": config,
            "cabins": [{"cabinNumber": "101", "deck": {"number": 1, "name": "ONE"}, "locations": [zone] if zone else []}],
            "categoryMaster": [{"classCode": "C", "className": "Cabin", "subtypeCode": "S", "subtypeName": "Standard"}],
            "categoryAssignments": [{"cabinNumber": "101", "classCode": "C", "subtypeCode": "S", "categoryCode": category}]}
        path.write_text(json.dumps(document))
        entries.append({"shipCode": ship, "configurationId": config, "path": relative,
                        "sha256": audit.hashlib.sha256(path.read_bytes()).hexdigest(), "saturated": True})
    catalog = static / "celebrity-catalog.json"
    catalog.write_text(json.dumps({"configurations": entries}))
    return state, classes, catalog


def test_audit_preserves_conflicts_unknowns_and_commercial_changes(tmp_path):
    state, classes, _ = fixture_state(tmp_path)
    before = {p: p.read_bytes() for p in state.rglob("*") if p.is_file()}
    result = audit.audit(state, classes)
    assert result == audit.audit(state, classes)
    assert before == {p: p.read_bytes() for p in state.rglob("*") if p.is_file()}
    assert result["publishesMasters"] is False
    assert result["summary"]["unmappedShipGroups"] == 1
    group = next(g for g in result["groups"] if g["scope"] == "CLASS")
    assert {x["field"] for x in group["proposedSharedFields"]} == {"deckName", "deckNumber"}
    assert group["variantCountsByField"] == {"zones": 1}
    assert group["fieldsRequiringVariants"][0]["unknownSourceIds"] == ["CELEBRITY/CC/1"]
    assert group["assignmentVersionDifferences"][0]["differentAssignmentSets"] == 1
    assert all(s["membershipCompleteness"] == "UNVERIFIED" for s in result["sources"])
    assert all(s["unknownFields"]["areaInSqft"] == 1 for s in result["sources"])


@pytest.mark.parametrize("field,value,expected", [("areaInSqft", 0, None), ("balconyWidth", -1, None),
    ("wheelchairAccessible", False, False), ("zones", ["mid", "MID"], ["MID"]), ("areaInSqft", 236, 236)])
def test_normalize(field, value, expected):
    assert audit.normalize(field, value) == expected


def test_stale_hash_rejected(tmp_path):
    state, classes, catalog = fixture_state(tmp_path)
    document = json.loads(catalog.read_text())
    document["configurations"][0]["sha256"] = "0" * 64
    catalog.write_text(json.dumps(document))
    with pytest.raises(ValueError, match="hash mismatch"):
        audit.audit(state, classes)


def test_duplicate_class_membership_rejected(tmp_path):
    _, classes, _ = fixture_state(tmp_path)
    document = json.loads(classes.read_text())
    document["classes"].append(document["classes"][0])
    classes.write_text(json.dumps(document))
    with pytest.raises(ValueError, match="duplicate class"):
        audit.load_classes(classes)


def test_output_cannot_modify_state(tmp_path, monkeypatch):
    state, classes, _ = fixture_state(tmp_path)
    monkeypatch.setattr(sys, "argv", ["audit", "--state", str(state), "--classes", str(classes), "--out-dir", str(state / "report")])
    with pytest.raises(SystemExit):
        audit.main()
    assert not (state / "report").exists()


def test_princess_physical_and_category_fields_are_separate():
    document = {"decks": [{"deckCode": "8", "response": {"cabins": [{
        "number": "E101", "deckNumber": 8, "deckName": "Emerald", "zoneName": "Forward",
        "areaInSqft": 236, "balconyAreaInSqft": 0, "numberOfBerths": 2,
        "wheelchairAccessible": False, "categoryCode": "OZ", "metaCode": "O", "subMetaCode": "F",
        "category": {"name": "Obstructed", "meta": {"name": "Oceanview"}}
    }]}}]}
    physical, definitions, assignments = audit.extract("PRINCESS", document)
    assert physical["E101"]["areaInSqft"] == {"236"}
    assert physical["E101"]["balconyAreaInSqft"] == {"null"}
    assert physical["E101"]["wheelchairAccessible"] == {"false"}
    assert assignments["E101"] == {("O", "F", "OZ")}
    assert "OZ" in definitions
    document["decks"][0]["deckCode"] = "9"
    with pytest.raises(ValueError, match="deck mismatch"):
        audit.extract("PRINCESS", document)
