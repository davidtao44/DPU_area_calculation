import re
import shutil
from dataclasses import replace

import pytest

from area_lab.domain.errors import PipelineFailure
from area_lab.infrastructure.designs import DESIGNS
from area_lab.infrastructure.process_runner import ProcessRunner
from area_lab.infrastructure.settings import Settings
from area_lab.infrastructure.vhdl import analyze_sources

SHARED = """library ieee;
use ieee.std_logic_1164.all;
entity shared_helper is port(x:in std_logic; y:out std_logic); end;
architecture rtl of shared_helper is begin y <= not x; end;
"""


def test_posit16_metadata_matches_the_instantiated_operator():
    design = next(item for item in DESIGNS if item.id == "posit16")
    source = (Settings().assets_dir / design.source_files[-1]).read_text()
    operator_es = re.search(r"component PositMult_16_(\d+)_", source).group(1)
    assert re.search(r"es=(\d+)", design.label).group(1) == operator_es


def write_fixture(directory):
    sources = directory / "sources/rtl/duplicate"
    sources.mkdir(parents=True)
    for name in ("first", "second"):
        (sources / f"{name}.vhd").write_text(
            SHARED
            + f"""
library ieee;
use ieee.std_logic_1164.all;
entity {name} is port(x:in std_logic; y:out std_logic); end;
architecture rtl of {name} is begin dut: entity work.shared_helper port map(x,y); end;
"""
        )
    (sources / "top.vhd").write_text("""library ieee;
use ieee.std_logic_1164.all;
entity duplicate_top is end;
architecture test of duplicate_top is signal a,b:std_logic; begin
  one:entity work.first port map('0',a);
  two:entity work.second port map('1',b);
end;
""")
    return replace(
        DESIGNS[0],
        library="duplicate_lib",
        compilation="unique_ghdl_units",
        source_files=tuple(f"rtl/duplicate/{name}.vhd" for name in ("first", "second", "top")),
    )


@pytest.mark.integration
def test_identical_helpers_link_once_without_changing_original_sources(tmp_path):
    if not shutil.which("ghdl"):
        pytest.skip("Requires GHDL LLVM")
    design = write_fixture(tmp_path)
    originals = {p: p.read_bytes() for p in (tmp_path / "sources").rglob("*.vhd")}
    runner = ProcessRunner(None, timeout=15)
    analyze_sources(runner, tmp_path, design)
    runner.run("ghdl", ["-e", "--std=08", "--work=duplicate_lib", "duplicate_top"], tmp_path)
    assert all(p.read_bytes() == original for p, original in originals.items())


@pytest.mark.integration
def test_conflicting_helpers_are_rejected_before_linking(tmp_path):
    if not shutil.which("ghdl"):
        pytest.skip("Requires GHDL")
    design = write_fixture(tmp_path)
    source = tmp_path / "sources/rtl/duplicate/second.vhd"
    source.write_text(source.read_text().replace("y <= not x", "y <= x"))
    with pytest.raises(PipelineFailure, match="duplicadas diferentes"):
        analyze_sources(ProcessRunner(None, timeout=15), tmp_path, design)
