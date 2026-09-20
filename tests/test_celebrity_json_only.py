import importlib.util
import sys
import types
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "master" / "providers" / "celebrity" / "configuration-discovery.py"
ACQUISITION = Path(__file__).parents[1] / "voyages" / "celebrity-inventory.ps1"
ACQUISITION_PY = Path(__file__).parents[1] / "voyages" / "celebrity-inventory.py"


def load_collector():
    fake = types.ModuleType("curl_cffi")
    fake.requests = None
    sys.modules.setdefault("curl_cffi", fake)
    spec = importlib.util.spec_from_file_location("celebrity_configuration_discovery", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CelebrityJsonOnlyTests(unittest.TestCase):
    def test_source_has_no_rsc_path(self):
        self.assertNotIn("rsc", SCRIPT.read_text(encoding="utf-8").lower())

    def test_hierarchy_and_configuration_come_from_rooms_json(self):
        module = load_collector()
        data = {
            "rooms": [{
                "room": {
                    "stateroomType": {"code": "INTERIOR"},
                    "stateroomSubtype": {"code": "IS"},
                },
                "options": {"stateroomTypes": [{
                    "code": "INTERIOR",
                    "name": "Inside",
                    "stateroomSubtypes": [{
                        "code": "IS", "name": "Inside", "categoryCode": "I2"
                    }],
                }]},
                "roomNumbers": {
                    "decks": [{
                        "code": "07", "number": 7, "selected": True,
                        "deckPlanUrl": "/svg/svg_c_XC_2451/IDP-DECK07.svg",
                    }],
                    "categories": [],
                },
            }]
        }
        hierarchy = module.hierarchy_from_rooms_json(data)
        decks = module.advertised_decks_from_room_numbers(data["rooms"][0]["roomNumbers"])
        self.assertEqual(("INTERIOR", "IS"), module.returned_selector(data))
        self.assertEqual("I2", hierarchy[0]["leadCategoryCode"])
        self.assertEqual("2451", module.layout_version_from_url(decks[0]["deckPlanUrl"]))

    def test_acquisition_is_fail_closed_and_atomic(self):
        wrapper = ACQUISITION.read_text(encoding="utf-8-sig")
        source = ACQUISITION_PY.read_text(encoding="utf-8")
        self.assertIn('$ErrorActionPreference = "Stop"', wrapper)
        self.assertIn('celebrity-inventory.py', wrapper)
        self.assertIn("MAX_ATTEMPTS = 4", source)
        self.assertIn("PAGE_SIZE = 100", source)
        self.assertNotIn('"count": 1000', source)
        self.assertIn("pagination count mismatch", source)
        self.assertIn("duplicate cruise-group IDs", source)
        self.assertIn("duplicate sailing IDs", source)
        self.assertIn('requests.Session(impersonate="chrome")', source)
        self.assertNotIn("AKA_A2", source)
        self.assertNotIn("ak_bmsc", source)
        self.assertIn('temporary = target.with_name(target.name + ".partial")', source)
        self.assertLess(
            source.index("pagination count mismatch"),
            source.index("temporary.write_text"),
        )
        self.assertLess(
            source.index("temporary.write_text"),
            source.index("os.replace(temporary, target)"),
        )


if __name__ == "__main__":
    unittest.main()
