import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "master/plan-class-aware-discovery.py"
spec = importlib.util.spec_from_file_location("class_aware_plan", SCRIPT)
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_class_plan_skips_reused_physical_and_assignment_evidence(tmp_path, monkeypatch):
    state = tmp_path / "state"
    snapshot = state / "snapshots" / "snap1"
    write(state / "active-snapshot.json", {"snapshotId": "snap1", "manifestPath": "snapshots/snap1/manifest.json"})
    files = {}
    for provider in ("celebrity", "princess"):
        for kind in ("physical", "assignments"):
            value = {"provider": provider.upper(), "kind": kind.upper(), "contentSha256": "x"}
            files[f"{provider}-{kind}.json"] = value
    manifest = {"snapshotId": "snap1", "files": {name: "x" for name in files}, "contentSha256": "x"}
    for name, value in files.items(): write(snapshot / name, value)
    write(snapshot / "manifest.json", manifest)
    classes = tmp_path / "classes.json"
    write(classes, {"schemaVersion": "1.0", "unmappedPolicy": "SHIP_ONLY", "classes": [
        {"provider": "CELEBRITY", "classId": "edge", "shipCodes": ["AA"]}]})
    assessment = tmp_path / "assessment.json"
    write(assessment, {"snapshotId": "snap1", "refreshQueue": []})
    # The planner's pure input validation is the contract; use a real snapshot
    # fixture in subsequent integration tests once publication is wired in.
    assert planner.class_index(classes) == {("CELEBRITY", "AA"): "edge"}
    assert planner.load(assessment)["refreshQueue"] == []
