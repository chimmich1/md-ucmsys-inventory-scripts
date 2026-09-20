"""Include historical hyphenated, script-style regressions in pytest runs."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("filename", ["test-registry-v1.2.py", "test-registry-v1.2-chronology.py"])
def test_registry_script(filename):
    result = subprocess.run([sys.executable, str(Path(__file__).with_name(filename))],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
