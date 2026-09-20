import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "master"))
import catalog_state
from test_incremental_daily import load_module, seed_configuration, write


def seed_state(state):
    root = state / "static-masters"
    final, validation = seed_configuration(state, "AT", "2362", False, ["V1"])
    write(root / "celebrity-catalog.json", {"configurations": [{
        "shipCode": "AT", "configurationId": "2362", "path": str(final.resolve()),
        "sha256": catalog_state.sha(final), "saturated": False}]})
    write(root / "celebrity-manifest.json", {"catalogPath": str(root / "celebrity-catalog.json")})
    princess = root / "princess/AP/4/published-deck-plan.json"
    write(princess, {"shipCode": "AP", "physicalConfigurationId": "4",
                    "voyageBindingProven": True, "decks": [{"deckCode": "1",
                    "cabinCount": 1, "response": {"cabins": [{"number": "101"}]}}]})
    write(root / "princess/catalog.json", {"configurations": [{
        "shipCode": "AP", "configurationId": "4", "path": str(princess.resolve()),
        "sha256": catalog_state.sha(princess), "voyageBindingProven": True}]})
    return final, validation


def validate(state):
    return subprocess.run([sys.executable, str(ROOT / "master/validate-masters.py"),
                           "--state", str(state)], capture_output=True, text=True)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("style", ["native", "windows", "posix", "relative", "relative_windows", "unc"])
@pytest.mark.parametrize("provider", ["celebrity", "princess"])
def test_relocated_validation_is_local_and_read_only(tmp_path, style, provider):
    original = tmp_path / "old/state"
    seed_state(original)
    moved = tmp_path / "new/state"
    shutil.copytree(original, moved)
    root = moved / "static-masters"
    for catalog in (root / "celebrity-catalog.json", root / "princess/catalog.json"):
        document = catalog_state.load(catalog)
        entry = document["configurations"][0]
        relative = Path(entry["path"]).relative_to(original / "static-masters").as_posix()
        if style == "windows":
            entry["path"] = "Z:\\retired\\work\\state\\static-masters\\" + relative.replace("/", "\\")
        elif style == "posix":
            entry["path"] = "/retired/work/state/static-masters/" + relative
        elif style == "relative":
            entry["path"] = relative
        elif style == "relative_windows":
            entry["path"] = relative.replace("/", "\\")
        elif style == "unc":
            entry["path"] = "\\\\retired\\share\\" + relative.replace("/", "\\")
        write(catalog, document)
    before = snapshot(moved)
    assert validate(moved).returncode == 0
    assert snapshot(moved) == before
    # The old tree still exists and matches its catalog. Validation must detect
    # a damaged LOCAL copy instead of passing against that old tree.
    local = root / ("celebrity/AT/2362/celebrity-ship-master-AT-v2.2.json" if provider == "celebrity"
                    else "princess/AP/4/published-deck-plan.json")
    local.write_text("{}", encoding="utf-8")
    result = validate(moved)
    assert result.returncode != 0
    assert "hash mismatch" in result.stderr
    local.unlink()
    result = validate(moved)
    assert result.returncode != 0
    assert "missing" in result.stderr


def test_catalog_only_repair_preserves_evidence_and_is_idempotent(tmp_path):
    state = tmp_path / "state"
    seed_state(state)
    root = state / "static-masters"
    catalog = catalog_state.load(root / "celebrity-catalog.json")
    catalog["configurations"][0].update(sha256="stale", saturated=True)
    write(root / "celebrity-catalog.json", catalog)
    before = snapshot(state)
    command = [sys.executable, str(ROOT / "master/reconcile-catalogs.py"), "--state", str(state)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    after = snapshot(state)
    changed = {path for path in before if before[path] != after[path]}
    assert changed == {"static-masters/celebrity-catalog.json",
                       "static-masters/princess/catalog.json", "static-masters/celebrity-manifest.json"}
    assert validate(state).returncode == 0
    subprocess.run(command, check=True, capture_output=True, text=True)
    assert snapshot(state) == after


@pytest.mark.parametrize("saturated", [False, True])
def test_interrupted_increment_recovered_when_restart_skips(tmp_path, monkeypatch, saturated):
    module = load_module()
    state = tmp_path / "state"
    final, validation = seed_state(state)
    # Retired catalog entry must also be reconciled despite not being in registry.
    retired, retired_validation = seed_configuration(state, "ZZ", "9", True, ["OLD"])
    root = state / "static-masters"
    catalog = catalog_state.load(root / "celebrity-catalog.json")
    catalog["configurations"].append({"shipCode": "ZZ", "configurationId": "9",
                                    "path": "old", "sha256": "stale", "saturated": False})
    write(root / "celebrity-catalog.json", catalog)
    voyages, registry = tmp_path / "voyages.json", tmp_path / "registry.json"
    write(voyages, {"voyages": [{"voyageId": "V1"}, {"voyageId": "V2"}]})
    write(registry, {"voyages": {vid: {"provider": "CELEBRITY", "shipCode": "AT",
          "physicalConfigurationId": "2362", "configurationEvidenceState": "PROVEN_TARGET_SAILING",
          "voyageId": vid} for vid in ("V1", "V2")}})
    monkeypatch.setattr(sys, "argv", [str(ROOT / "master/build-static-masters.py"),
        "--mode", "Daily", "--voyages", str(voyages), "--registry", str(registry),
        "--state", str(state), "--data", str(tmp_path)])
    def fake_collect(command):
        output = Path(command[command.index("--output") + 1])
        master = catalog_state.load(final)
        report = catalog_state.load(validation)
        master["saturation"]["saturated"] = saturated
        master["newEvidence"] = "V2"
        report["saturation"]["saturated"] = saturated
        report["voyages"].append({"voyageId": "V2", "failureCount": 0})
        write(output / final.name, master)
        write(output / validation.name, report)
        write(output / "raw/02-V2/evidence.json", {"voyageId": "V2"})
    monkeypatch.setattr(module, "run", fake_collect)
    real_dump = module.dump
    def interrupt_catalog(path, document):
        if Path(path).name == "celebrity-catalog.json" and "newEvidence" in catalog_state.load(final):
            raise RuntimeError("simulated interruption after promotion")
        real_dump(path, document)
    monkeypatch.setattr(module, "dump", interrupt_catalog)
    with pytest.raises(RuntimeError, match="simulated interruption"):
        module.main()
    assert validate(state).returncode != 0
    evidence_before = snapshot(final.parent)
    monkeypatch.setattr(module, "dump", real_dump)
    monkeypatch.setattr(module, "run", lambda command: pytest.fail("restart must not collect tested voyages"))
    module.main()
    assert snapshot(final.parent) == evidence_before
    assert validate(state).returncode == 0
    entries = catalog_state.load(root / "celebrity-catalog.json")["configurations"]
    assert entries[0]["sha256"] == catalog_state.sha(final)
    assert entries[0]["saturated"] is saturated
    assert entries[1]["sha256"] == catalog_state.sha(retired)
    assert entries[1]["saturated"] is True


def test_atomic_catalog_write_keeps_published_copy_on_failure(tmp_path, monkeypatch):
    target = tmp_path / "catalog.json"
    write(target, {"old": True})
    before = target.read_bytes()
    def fail_replace(self, destination):
        raise OSError("interrupted replacement")
    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError):
        catalog_state.dump(target, {"new": True})
    assert target.read_bytes() == before
    assert list(tmp_path.iterdir()) == [target]


@pytest.mark.parametrize("problem", ["missing", "conflict", "identity", "saturation"])
def test_reconciliation_rejects_incomplete_or_conflicting_evidence(tmp_path, problem):
    final, validation = seed_state(tmp_path)
    report = catalog_state.load(validation)
    if problem == "missing":
        validation.unlink()
    else:
        if problem == "conflict":
            report["cabinDeckConflictCount"] = 1
        elif problem == "identity":
            report["shipCode"] = "OTHER"
        else:
            report["saturation"]["saturated"] = True
        write(validation, report)
    root = tmp_path / "static-masters"
    with pytest.raises((ValueError, FileNotFoundError)):
        catalog_state.reconcile_celebrity(root, catalog_state.load(root / "celebrity-catalog.json"))


def test_princess_daily_publishes_relative_paths_without_collection(tmp_path, monkeypatch):
    seed_state(tmp_path)
    script = ROOT / "master/build-princess-published-masters.py"
    spec = importlib.util.spec_from_file_location("princess_builder", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    voyages = tmp_path / "voyages.json"
    write(voyages, {"voyages": [{"voyageId": "P1", "shipCode": "AP",
                               "source": {"providerShipVersion": "4"}}]})
    monkeypatch.setattr(sys, "argv", [str(script), "--mode", "Daily", "--voyages", str(voyages),
                                    "--state", str(tmp_path)])
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("must reuse published layout"))
    module.main()
    catalog = catalog_state.load(tmp_path / "static-masters/princess/catalog.json")
    assert catalog["configurations"][0]["path"] == "princess/AP/4/published-deck-plan.json"
