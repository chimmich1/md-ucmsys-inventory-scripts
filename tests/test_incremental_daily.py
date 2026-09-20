import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "master"))
SCRIPT = ROOT / "master/build-static-masters.py"
COLLECTOR = ROOT / "master/providers/celebrity/configuration-discovery.py"
ROOT_PIPELINE = ROOT / "build-cruise-master.ps1"
PIPELINE = ROOT / "pipeline/build-cruise-master.ps1"


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def load_module():
    spec = importlib.util.spec_from_file_location("build_static_masters", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed_configuration(state, ship, configuration, saturated, voyage_ids):
    directory = state / "static-masters/celebrity" / ship / configuration
    master = directory / f"celebrity-ship-master-{ship}-v2.2.json"
    validation = directory / f"celebrity-ship-master-validation-{ship}-v2.2.json"
    write(master, {
        "provider": "CELEBRITY", "shipCode": ship,
        "targetConfiguration": configuration,
        "categoryAssignments": [], "categoryMaster": [],
        "saturation": {"saturated": saturated},
    })
    write(validation, {
        "provider": "CELEBRITY", "shipCode": ship,
        "targetConfiguration": configuration,
        "cabinDeckConflictCount": 0,
        "voyages": [{"voyageId": value, "failureCount": 0} for value in voyage_ids],
        "saturation": {"saturated": saturated},
    })
    return master, validation


def test_daily_advances_only_unsaturated_configuration_with_new_voyage():
    module = load_module()
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        state = base / "state"
        voyages = base / "voyages.json"
        registry = base / "registry.json"
        write(voyages, {"voyages": [
            {"voyageId": "V1"}, {"voyageId": "V2"},
            {"voyageId": "V3"}, {"voyageId": "V4"},
        ]})
        write(registry, {"voyages": {
            "V1": {"provider": "CELEBRITY", "configurationEvidenceState": "PROVEN_TARGET_SAILING", "shipCode": "AA", "physicalConfigurationId": "1", "voyageId": "V1"},
            "V2": {"provider": "CELEBRITY", "configurationEvidenceState": "PROVEN_TARGET_SAILING", "shipCode": "AA", "physicalConfigurationId": "1", "voyageId": "V2"},
            "V3": {"provider": "CELEBRITY", "configurationEvidenceState": "PROVEN_TARGET_SAILING", "shipCode": "BB", "physicalConfigurationId": "2", "voyageId": "V3"},
            "V4": {"provider": "CELEBRITY", "configurationEvidenceState": "PROVEN_TARGET_SAILING", "shipCode": "CC", "physicalConfigurationId": "3", "voyageId": "V4"},
        }})
        aa_master, aa_validation = seed_configuration(state, "AA", "1", False, ["V1"])
        seed_configuration(state, "BB", "2", True, ["V3"])
        seed_configuration(state, "CC", "3", False, ["V4"])
        write(state / "static-masters/celebrity-catalog.json", {"configurations": [
            {"shipCode": "BB", "configurationId": "2", "path": "D:/old-host/work/state/static-masters/celebrity/BB/2/celebrity-ship-master-BB-v2.2.json", "sha256": "legacy", "saturated": True},
            {"shipCode": "CC", "configurationId": "3", "path": "D:/old-host/work/state/static-masters/celebrity/CC/3/celebrity-ship-master-CC-v2.2.json", "sha256": "legacy", "saturated": False},
        ]})

        calls = []
        def fake_run(command):
            command = [str(value) for value in command]
            calls.append(command)
            assert command[command.index("--baseline-master") + 1] == str(aa_master)
            assert command[command.index("--previous-validation") + 1] == str(aa_validation)
            assert command[command.index("--include-voyage-ids") + 1] == "V2"
            output = Path(command[command.index("--output") + 1])
            previous = json.loads(aa_validation.read_text())
            write(output / "celebrity-ship-master-AA-v2.2.json", {
                "provider": "CELEBRITY", "shipCode": "AA",
                "targetConfiguration": "1", "categoryAssignments": [],
                "categoryMaster": [], "saturation": {"saturated": True},
            })
            write(output / "celebrity-ship-master-validation-AA-v2.2.json", {
                "provider": "CELEBRITY", "shipCode": "AA",
                "targetConfiguration": "1", "cabinDeckConflictCount": 0,
                "voyages": previous["voyages"] + [{"voyageId": "V2", "failureCount": 0}],
                "saturation": {"saturated": True},
            })
            write(output / "raw/02-V2/evidence.json", {"ok": True})

        module.run = fake_run
        old_argv = sys.argv
        try:
            sys.argv = [str(SCRIPT), "--mode", "Daily", "--voyages", str(voyages),
                        "--registry", str(registry), "--state", str(state),
                        "--data", str(base / "data")]
            module.main()
        finally:
            sys.argv = old_argv

        assert len(calls) == 1
        manifest = json.loads((state / "static-masters/celebrity-manifest.json").read_text())
        assert [x["shipCode"] for x in manifest["advanced"]] == ["AA"]
        assert manifest["skippedSaturated"] == ["BB:2"]
        assert manifest["skippedNoNewVoyages"] == ["CC:3"]
        assert manifest["catalogPath"] == "celebrity-catalog.json"
        catalog = json.loads((state / "static-masters/celebrity-catalog.json").read_text())
        assert all(not Path(item["path"]).is_absolute() for item in catalog["configurations"])
        for item in catalog["configurations"]:
            assert item["sha256"] == module.sha(state / "static-masters" / item["path"])
        assert {item["path"] for item in catalog["configurations"]} == {
            "celebrity/AA/1/celebrity-ship-master-AA-v2.2.json",
            "celebrity/BB/2/celebrity-ship-master-BB-v2.2.json",
            "celebrity/CC/3/celebrity-ship-master-CC-v2.2.json",
        }
        validation = json.loads(aa_validation.read_text())
        assert [x["voyageId"] for x in validation["voyages"]] == ["V1", "V2"]
        assert (aa_master.parent / "raw/02-V2/evidence.json").exists()


def test_collector_preserves_cumulative_voyage_history():
    source = COLLECTOR.read_text(encoding="utf-8")
    assert "previous_voyage_reports = list" in source
    assert "voyage_reports = list(previous_voyage_reports)" in source
    assert "current_voyage_reports.append(report)" in source
    assert '"currentRunTestedVoyageCount"' in source


def test_resume_at_celebrity_masters_is_forwarded_and_guarded():
    root_source = ROOT_PIPELINE.read_text(encoding="utf-8-sig")
    pipeline_source = PIPELINE.read_text(encoding="utf-8-sig")
    assert "ResumeAtCelebrityMasters" in root_source
    assert "$params.ResumeAtCelebrityMasters = $true" in root_source
    assert "Resume at Celebrity masters" in pipeline_source
    assert "!$ResumeAtCelebrityMasters" in pipeline_source


if __name__ == "__main__":
    test_daily_advances_only_unsaturated_configuration_with_new_voyage()
    test_collector_preserves_cumulative_voyage_history()
    test_resume_at_celebrity_masters_is_forwarded_and_guarded()
    print("Incremental Daily orchestration tests: PASS")
