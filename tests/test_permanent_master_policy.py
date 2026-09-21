import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "master"))
import permanent_master_policy as policy
import permanent_master_snapshot as snapshot

fixture_spec = importlib.util.spec_from_file_location(
    "snapshot_fixtures", ROOT / "tests/test_permanent_master_snapshot.py")
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)
POLICY = ROOT / "config/permanent-master-refresh-policy.json"


def published(tmp_path):
    state, classes = fixtures.evidence(tmp_path)
    snapshot_id, documents = snapshot.build_documents(state, classes, ROOT)
    output = tmp_path / "permanent"
    snapshot.publish(output, snapshot_id, documents)
    return state, classes, output


def group(report, provider, group_id):
    provider_record = next(p for p in report["providers"] if p["provider"] == provider)
    return next(g for g in provider_record["groups"] if g["groupId"] == group_id)


def test_complete_confirmed_celebrity_attributes_generate_no_physical_work(tmp_path):
    _, _, output = published(tmp_path)
    report = policy.assess(output, POLICY)
    edge = group(report, "CELEBRITY", "edge")
    assert edge["membership"]["status"] == "UNVERIFIED"
    assert edge["attributes"]["status"] == "COMPLETE"
    assert edge["assignments"]["status"] == "COMPLETE"
    assert edge["categoryDefinitions"]["status"] == "UNVERIFIED"
    assert all(item["provider"] != "CELEBRITY" or item["dimension"] != "attributes"
               for item in report["refreshQueue"])


def test_stalled_balcony_fields_are_not_complete_or_automatically_queued(tmp_path):
    _, _, output = published(tmp_path)
    report = policy.assess(output, POLICY)
    edge = group(report, "CELEBRITY", "edge")
    assert edge["attributeFields"]["balconyAreaInSqft"]["status"] == "DISCOVERY_STALLED"
    assert edge["attributeFields"]["balconyAreaInSqft"]["proof"] is None
    assert all(item.get("field") != "balconyAreaInSqft" for item in report["refreshQueue"])


def test_unknown_required_field_creates_targeted_ship_work(tmp_path):
    state, classes = fixtures.evidence(tmp_path)
    master = state / "static-masters/celebrity/AA/2/celebrity-ship-master-AA-v2.2.json"
    document = json.loads(master.read_text())
    document["cabins"][0]["locations"] = []
    new_hash = fixtures.write(master, document)
    catalog_path = state / "static-masters/celebrity-catalog.json"
    catalog = json.loads(catalog_path.read_text())
    next(x for x in catalog["configurations"] if x["shipCode"] == "AA" and x["configurationId"] == "2")["sha256"] = new_hash
    fixtures.write(catalog_path, catalog)
    snapshot_id, documents = snapshot.build_documents(state, classes, ROOT)
    output = tmp_path / "permanent"
    snapshot.publish(output, snapshot_id, documents)
    report = policy.assess(output, POLICY)
    items = [x for x in report["refreshQueue"] if x["provider"] == "CELEBRITY"]
    assert len(items) == 1
    assert items[0]["shipCode"] == "AA"
    assert items[0]["field"] == "zones"
    assert items[0]["action"] == "DISCOVER_MISSING_FIELD"
    assert items[0]["sourceIds"] == ["CELEBRITY/AA/1", "CELEBRITY/AA/2"]


def test_ambiguous_intra_ship_value_is_flagged_not_selected(tmp_path):
    state, classes = fixtures.evidence(tmp_path)
    master = state / "static-masters/celebrity/AA/2/celebrity-ship-master-AA-v2.2.json"
    document = json.loads(master.read_text())
    document["cabins"][0]["locations"] = ["AFT"]
    new_hash = fixtures.write(master, document)
    catalog_path = state / "static-masters/celebrity-catalog.json"
    catalog = json.loads(catalog_path.read_text())
    next(x for x in catalog["configurations"] if x["shipCode"] == "AA" and x["configurationId"] == "2")["sha256"] = new_hash
    fixtures.write(catalog_path, catalog)
    snapshot_id, documents = snapshot.build_documents(state, classes, ROOT)
    output = tmp_path / "permanent"
    snapshot.publish(output, snapshot_id, documents)
    report = policy.assess(output, POLICY)
    actions = [x["action"] for x in report["refreshQueue"] if x["provider"] == "CELEBRITY"]
    assert "RESOLVE_CONTRADICTORY_EVIDENCE" in actions
    assert group(report, "CELEBRITY", "edge")["attributes"]["status"] == "INCOMPLETE"
    assert actions.count("DISCOVER_MISSING_FIELD") == 0


def test_manual_and_factory_refresh_are_explicit_and_targeted(tmp_path):
    _, _, output = published(tmp_path)
    report = policy.assess(output, POLICY, manual_targets=["CELEBRITY/AA"],
                           factory_refresh_targets=["PRINCESS/AP"])
    explicit = [x for x in report["refreshQueue"] if x["action"] in
                {"MANUAL_VERIFY_PHYSICAL", "VERIFY_FACTORY_REFRESH"}]
    assert [(x["provider"], x["shipCode"], x["action"]) for x in explicit] == [
        ("CELEBRITY", "AA", "MANUAL_VERIFY_PHYSICAL"),
        ("PRINCESS", "AP", "VERIFY_FACTORY_REFRESH")]
    assert report["periodicSchedule"]["physical"]["status"] == "UNSCHEDULED"
