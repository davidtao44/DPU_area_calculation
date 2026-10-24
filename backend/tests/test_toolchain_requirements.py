import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CHECK_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_toolchain.py"


def test_missing_c_compiler_fails_before_ghdl_analysis():
    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT)],
        env={**os.environ, "PATH": ""},
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0
    assert "GHDL LLVM necesita cc" in result.stderr
    assert "build-essential" in result.stderr


@pytest.mark.integration
def test_smoke_check_compiles_links_simulates_and_synthesizes():
    if not all(shutil.which(tool) for tool in ("cc", "ghdl", "yosys", "iverilog")):
        pytest.skip("Requires the C compiler and EDA toolchain")
    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        "Toolchain OK: GHDL analysis, elaboration/link, simulation and Verilog synthesis."
        in result.stdout
    )
