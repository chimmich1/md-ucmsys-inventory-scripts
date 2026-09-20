import importlib.util
import json
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "master/providers/princess/published-deck-collector.py"
SPEC = importlib.util.spec_from_file_location("princess_collector", MODULE_PATH)
COLLECTOR = importlib.util.module_from_spec(SPEC)
sys.modules.setdefault("requests", types.SimpleNamespace(Session=None))
SPEC.loader.exec_module(COLLECTOR)


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
