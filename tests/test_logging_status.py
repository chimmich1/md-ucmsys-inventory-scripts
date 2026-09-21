import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "celebrity_discovery", ROOT / "master/providers/celebrity/configuration-discovery.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_current_failure_is_an_actionable_warning():
    lines = module.failure_summary_lines(5, 2)
    assert "  Current-run failures:      2" in lines
    assert "  Historical failures:       3" in lines
    assert any(line.startswith("WARNING: current") for line in lines)


def test_historical_failure_is_not_reported_as_current():
    lines = module.failure_summary_lines(5, 0)
    assert "  Historical failures:       5" in lines
    assert not any(line.startswith("WARNING:") for line in lines)
    assert any(line.startswith("NOTICE:") for line in lines)
