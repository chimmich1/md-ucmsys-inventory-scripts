import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not shutil.which("powershell.exe"), reason="requires Windows PowerShell 5.1")
@pytest.mark.parametrize("exit_code", [0, 7])
def test_native_stderr_survives_stop_and_tee(tmp_path, exit_code):
    child = tmp_path / "child with spaces.py"
    child.write_text('import sys, traceback\nprint("stdout marker", flush=True)\n'
                     'print("stderr first", file=sys.stderr, flush=True)\n'
                     'print("stderr middle", file=sys.stderr, flush=True)\n'
                     'print("stderr last", file=sys.stderr, flush=True)\n'
                     'try:\n    raise RuntimeError("traceback final marker")\n'
                     'except RuntimeError:\n    traceback.print_exc()\n'
                     f'sys.exit({exit_code})\n', encoding="utf-8")
    log = tmp_path / "native.log"
    script = tmp_path / "invoke.ps1"
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    script.write_text(
        '$ErrorActionPreference="Stop"\n'
        '$PSVersionTable.PSVersion.ToString()\n'
        f'. {quote(ROOT / "pipeline/invoke-native.ps1")}\n'
        'try {\n'
        f'  Invoke-NativeCommand -Executable {quote(sys.executable)} -Arguments @({quote(child)}) *>&1 | Tee-Object -FilePath {quote(log)}\n'
        '} catch { if ($ErrorActionPreference -ne "Stop") { exit 20 }; Write-Output $_.Exception.Message; exit 19 }\n'
        'if ($ErrorActionPreference -ne "Stop") { exit 20 }\n', encoding="utf-8")
    result = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                             "-File", str(script)], capture_output=True, text=True)
    assert result.stdout.startswith("5.1.")
    assert result.returncode == (19 if exit_code else 0), result.stdout + result.stderr
    logged = log.read_text(encoding="utf-16")
    for marker in ("stdout marker", "stderr first", "stderr middle", "stderr last",
                   "Traceback (most recent call last)", "RuntimeError: traceback final marker"):
        assert marker in result.stdout
        assert marker in logged
    if exit_code:
        assert "exit code 7" in result.stdout
