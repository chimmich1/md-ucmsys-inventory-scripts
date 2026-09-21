import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "master"))
import permanent_master_maintenance as maintenance


def assessment(items=()):
    return {"refreshQueue": list(items)}


def item(provider, ship, source, action="DISCOVER_MISSING_FIELD", field="zones"):
    return {"provider": provider, "shipCode": ship, "sourceIds": [source],
            "action": action, "dimension": "attributes", "field": field,
            "deckNumbers": [8], "reason": "synthetic targeted gap"}


def test_unchanged_complete_snapshot_plans_and_executes_zero_collectors(tmp_path):
    published = {"CELEBRITY/AA/1", "PRINCESS/AP/4"}
    plan = maintenance.make_plan(assessment(), published, published)
    calls = []
    commands = maintenance.execute(plan, ROOT, tmp_path / "state", tmp_path / "data",
        tmp_path / "celebrity.json", tmp_path / "princess.json", tmp_path / "registry.json",
        runner=lambda *args, **kwargs: calls.append((args, kwargs)))
    assert plan == []
    assert commands == []
    assert calls == []
    summary = maintenance.class_aware_summary(plan, published, published,
        {("CELEBRITY", "AA"): "edge", ("PRINCESS", "AP"): "grand"})
    assert summary["targetedSourceCount"] == 0
    assert summary["skippedSourceCount"] == 2
    assert summary["byClass"]["edge"] == {"targeted": 0, "skipped": 1}


def test_targeted_items_are_grouped_into_one_bounded_builder_per_provider(tmp_path):
    items = [
        item("CELEBRITY", "AA", "CELEBRITY/AA/1", field="zones"),
        item("CELEBRITY", "AA", "CELEBRITY/AA/1", action="RESOLVE_CONTRADICTORY_EVIDENCE", field="deckName"),
        item("PRINCESS", "AP", "PRINCESS/AP/4", field="areaInSqft"),
    ]
    published = {"CELEBRITY/AA/1", "PRINCESS/AP/4"}
    plan = maintenance.make_plan(assessment(items), published, published)
    calls = []
    commands = maintenance.execute(plan, ROOT, tmp_path / "state", tmp_path / "data",
        tmp_path / "celebrity.json", tmp_path / "princess.json", tmp_path / "registry.json",
        python="python", runner=lambda command, check: calls.append((command, check)))
    assert len(plan) == 2
    assert len(commands) == len(calls) == 2
    celebrity = next(c for c in commands if "build-static-masters.py" in str(c[1]))
    princess = next(c for c in commands if "build-princess-published-masters.py" in str(c[1]))
    assert celebrity[celebrity.index("--configuration-filter") + 1] == "AA/1"
    assert princess[princess.index("--configuration-filter") + 1] == "AP/4"
    assert princess[princess.index("--deck-targets") + 1] == '{"AP/4":[8]}'
    summary = maintenance.class_aware_summary(plan, published, published,
        {("CELEBRITY", "AA"): "edge", ("PRINCESS", "AP"): "grand"})
    assert summary["targetedSourceCount"] == 2
    assert summary["skippedSourceCount"] == 0


def test_new_configuration_bootstraps_all_dimensions_once():
    plan = maintenance.make_plan(assessment(), {"CELEBRITY/AA/1", "CELEBRITY/AA/2"},
                                 {"CELEBRITY/AA/1"})
    assert len(plan) == 1
    assert plan[0]["configurationId"] == "2"
    assert plan[0]["actions"] == ["BOOTSTRAP_CONFIGURATION"]
    assert plan[0]["dimensions"] == ["assignments", "attributes", "categoryDefinitions", "membership"]


def test_unchanged_failed_work_is_stalled_until_explicit_retry_or_new_snapshot():
    target = item("PRINCESS", "AP", "PRINCESS/AP/4", field="areaInSqft")
    initial = maintenance.make_plan(assessment([target]), {"PRINCESS/AP/4"}, {"PRINCESS/AP/4"})
    key = initial[0]["workKeys"][0]
    assert maintenance.make_plan(assessment([target]), {"PRINCESS/AP/4"}, {"PRINCESS/AP/4"}, {key}) == []
    assert maintenance.make_plan(assessment([target]), {"PRINCESS/AP/4"}, {"PRINCESS/AP/4"})


def test_pipeline_uses_maintenance_daily_and_bootstrap_full():
    source = (ROOT / "pipeline/build-cruise-master.ps1").read_text(encoding="utf-8-sig")
    assert 'if($Mode -eq "Daily")' in source
    assert "maintain-permanent-masters.py" in source
    assert "Bootstrap permanent masters from local evidence" in source
    assert "Publish permanent master snapshot" in source


def test_collector_failure_does_not_change_active_snapshot(tmp_path):
    state = tmp_path / "state"
    active = state / "static-masters/permanent-masters/active-snapshot.json"
    active.parent.mkdir(parents=True)
    active.write_bytes(b'{"snapshotId":"preserved"}')
    plan = maintenance.make_plan(assessment([
        item("PRINCESS", "AP", "PRINCESS/AP/4", field="areaInSqft")]),
        {"PRINCESS/AP/4"}, {"PRINCESS/AP/4"})
    def fail(command, check):
        raise subprocess.CalledProcessError(9, command)
    try:
        maintenance.execute(plan, ROOT, state, tmp_path / "data", tmp_path / "celebrity.json",
                            tmp_path / "princess.json", tmp_path / "registry.json", runner=fail)
    except subprocess.CalledProcessError as exc:
        assert exc.returncode == 9
    else:
        raise AssertionError("collector failure was not propagated")
    assert active.read_bytes() == b'{"snapshotId":"preserved"}'
