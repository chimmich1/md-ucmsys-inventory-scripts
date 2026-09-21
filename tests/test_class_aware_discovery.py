import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "master/plan-class-aware-discovery.py"
sys.path.insert(0, str(ROOT / "master"))
spec = importlib.util.spec_from_file_location("class_aware_plan", SCRIPT)
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_plan_fixture(tmp_path, monkeypatch, refresh_queue=None, assessment_snapshot="snap1"):
    state = tmp_path / "state"
    snapshot = state / "snapshots" / "snap1"
    manifest = {"snapshotId": "snap1"}
    monkeypatch.setattr(planner, "validate_active", lambda path: manifest)
    write(snapshot / "celebrity-physical.json", {"groups": [{
        "groupId": "edge-template",
        "shipMembership": [{"shipCode": "AA", "configurationEvidence": ["CELEBRITY/AA/1"]}],
    }]})
    write(snapshot / "celebrity-assignments.json", {"revisions": [{
        "sourceIds": ["CELEBRITY/AA/1"],
    }]})
    write(snapshot / "princess-physical.json", {"groups": []})
    write(snapshot / "princess-assignments.json", {"revisions": []})
    classes = tmp_path / "classes.json"
    write(classes, {"schemaVersion": "1.0", "unmappedPolicy": "SHIP_ONLY", "classes": [
        {"provider": "CELEBRITY", "classId": "edge", "shipCodes": ["AA"]}]})
    assessment = tmp_path / "assessment.json"
    write(assessment, {"snapshotId": assessment_snapshot, "refreshQueue": refresh_queue or []})
    return state, classes, assessment


def test_class_plan_skips_reused_physical_and_assignment_evidence(tmp_path, monkeypatch):
    state, classes, assessment = make_plan_fixture(tmp_path, monkeypatch)
    result = planner.plan(state, classes, assessment)

    assert result["providerCallsPlanned"] == 0
    assert result["providerCallsSkipped"] == 3
    assert result["rows"][0]["classId"] == "edge"
    assert result["rows"][0]["physical"]["action"] == "SKIP_REUSED_EVIDENCE"
    assert result["rows"][0]["assignments"]["knownSourceCount"] == 1


def test_class_plan_targets_only_queued_namespace(tmp_path, monkeypatch):
    queue = [{"provider": "CELEBRITY", "shipCode": "AA", "dimension": "attributes"}]
    state, classes, assessment = make_plan_fixture(tmp_path, monkeypatch, queue)
    result = planner.plan(state, classes, assessment)

    assert result["providerCallsPlanned"] == 1
    assert result["rows"][0]["physical"]["action"] == "TARGET_QUEUED"
    assert result["rows"][0]["assignments"]["action"] == "SKIP_REUSED_EVIDENCE"


def test_class_plan_rejects_stale_assessment(tmp_path, monkeypatch):
    state, classes, assessment = make_plan_fixture(
        tmp_path, monkeypatch, assessment_snapshot="older-snapshot"
    )

    try:
        planner.plan(state, classes, assessment)
    except ValueError as exc:
        assert "assessment snapshot does not match" in str(exc)
    else:
        raise AssertionError("stale assessment was accepted")
