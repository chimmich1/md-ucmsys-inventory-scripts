import importlib.util
import json
import sys
import types
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "master"))
MODULE_PATH = ROOT / "master/providers/princess/published-deck-collector.py"
SPEC = importlib.util.spec_from_file_location("princess_collector", MODULE_PATH)
COLLECTOR = importlib.util.module_from_spec(SPEC)
sys.modules.setdefault("requests", types.SimpleNamespace(Session=None))
SPEC.loader.exec_module(COLLECTOR)
BUILDER_PATH = ROOT / "master/build-princess-published-masters.py"
BUILDER_SPEC = importlib.util.spec_from_file_location("princess_builder", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(BUILDER_SPEC)
BUILDER_SPEC.loader.exec_module(BUILDER)


def test_cabin_rows_supports_known_wrappers():
    assert COLLECTOR.cabin_rows({"cabins": [{"number": "A101"}]}) == [
        {"number": "A101"}
    ]
    assert COLLECTOR.cabin_rows({"data": {"cabins": [{"number": "B202"}]}}) == [
        {"number": "B202"}
    ]
    assert COLLECTOR.cabin_rows({"cabins": []}) == []


def test_source_contains_no_deckplans_version_scrape():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "deckPlans.do" not in source
    assert "--version" in source
    assert "PROVIDER_VOYAGE_SHIP_VERSION" in source


def test_builder_keys_catalog_by_voyage_ship_version():
    source = (ROOT / "master/build-princess-published-masters.py").read_text(
        encoding="utf-8"
    )
    assert 'source.get("providerShipVersion")' in source
    assert 'bindings[(ship, version)]' in source


def test_one_target_configuration_has_bounded_twenty_deck_requests(tmp_path, monkeypatch):
    class Response:
        status_code = 200
        ok = True
        def __init__(self, deck):
            self.deck = deck
        def json(self):
            return ({"cabins": [{"number": "E101", "deckNumber": 8}]}
                    if self.deck == "8" else {"cabins": []})

    calls = []
    class Session:
        def get(self, url, params, timeout):
            calls.append((url, dict(params), timeout))
            return Response(params["deck"])

    monkeypatch.setattr(COLLECTOR.requests, "Session", Session)
    out = tmp_path / "deck-plan.json"
    old = sys.argv
    try:
        sys.argv = [str(MODULE_PATH), "--ship", "AP", "--version", "4", "--out", str(out)]
        COLLECTOR.main()
    finally:
        sys.argv = old
    assert len(calls) == 20
    assert [call[1]["deck"] for call in calls] == [str(x) for x in range(1, 21)]
    assert json.loads(out.read_text())["decks"][0]["deckCode"] == "8"


def test_exact_deck_filter_probes_only_requested_decks(tmp_path, monkeypatch):
    class Response:
        status_code = 200
        ok = True
        def __init__(self, deck): self.deck = deck
        def json(self): return {"cabins": [{"number": f"D{self.deck}"}]}
    calls = []
    class Session:
        def get(self, url, params, timeout):
            calls.append(params["deck"])
            return Response(params["deck"])
    monkeypatch.setattr(COLLECTOR.requests, "Session", Session)
    out = tmp_path / "targeted.json"
    old = sys.argv
    try:
        sys.argv = [str(MODULE_PATH), "--ship", "AP", "--version", "4", "--out", str(out),
                    "--decks", "8,12"]
        COLLECTOR.main()
    finally:
        sys.argv = old
    assert calls == ["8", "12"]
    assert json.loads(out.read_text())["deckDiscovery"]["exactProbes"] == [8, 12]


def test_daily_catalog_preserves_historical_configuration_absent_from_current_voyages(tmp_path):
    state = tmp_path / "state"
    static = state / "static-masters"
    retired = static / "princess/OLD/1/published-deck-plan.json"
    retired.parent.mkdir(parents=True)
    retired.write_text('{"provider":"PRINCESS","shipCode":"OLD","physicalConfigurationId":"1"}')
    current = static / "princess/AP/4/published-deck-plan.json"
    current.parent.mkdir(parents=True)
    current.write_text('{"provider":"PRINCESS","shipCode":"AP","physicalConfigurationId":"4"}')
    catalog_path = static / "princess/catalog.json"
    catalog_path.write_text(json.dumps({"schemaVersion": "1.1", "configurations": [{
        "shipCode": "OLD", "configurationId": "1",
        "path": "princess/OLD/1/published-deck-plan.json",
        "sha256": hashlib.sha256(retired.read_bytes()).hexdigest(),
    }]}))
    voyages = tmp_path / "voyages.json"
    voyages.write_text(json.dumps({"voyages": [{"voyageId": "V1", "departureDate": "2027-01-01",
        "ship": {"providerId": "AP"}, "source": {"providerShipVersion": "4"}}]}))
    old = sys.argv
    try:
        sys.argv = [str(BUILDER_PATH), "--mode", "Daily", "--voyages", str(voyages),
                    "--state", str(state)]
        BUILDER.main()
    finally:
        sys.argv = old
    catalog = json.loads(catalog_path.read_text())
    assert {(x["shipCode"], x["configurationId"]) for x in catalog["configurations"]} == {
        ("AP", "4"), ("OLD", "1")}


def test_targeted_deck_merge_preserves_every_unprobed_deck():
    baseline = {"decks": [
        {"deckCode": "8", "response": {"cabins": [{"number": "E1", "old": True}]}},
        {"deckCode": "9", "response": {"cabins": [{"number": "D1"}]}},
    ]}
    targeted = {"provider": "PRINCESS", "deckDiscovery": {"exactProbes": [8]}, "decks": [
        {"deckCode": "8", "response": {"cabins": [{"number": "E1", "old": False}]}}
    ]}
    merged = BUILDER.merge_targeted_decks(baseline, targeted)
    assert [x["deckCode"] for x in merged["decks"]] == ["8", "9"]
    assert merged["decks"][0]["response"]["cabins"][0]["old"] is False
    assert merged["deckDiscovery"]["preservedDeckCodes"] == ["9"]
    assert merged["fingerprint"]
