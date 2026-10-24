import json
import math
import shutil
from uuid import uuid4

import pytest

from area_lab.infrastructure.catalog import build_catalog
from area_lab.infrastructure.designs import DESIGNS
from area_lab.infrastructure.settings import Settings
from area_lab.infrastructure.synthesis import GhdlYosysSynthesis


@pytest.mark.integration
@pytest.mark.parametrize("technology_id", ["ihp130", "nangate15", "nangate45"])
@pytest.mark.parametrize("design_id", [design.id for design in DESIGNS])
def test_actual_pipeline_reports_only_fully_mapped_validated_cells(
    tmp_path, technology_id, design_id
):
    if not all(shutil.which(tool) for tool in ("ghdl", "yosys", "iverilog", "vvp")):
        pytest.skip("Requires GHDL, Yosys, iverilog and vvp")
    settings = Settings(data_dir=tmp_path)
    designs, technologies = build_catalog(settings.assets_dir)
    design = next(item for item in designs if item.id == design_id)
    technology = next(item for item in technologies if item.id == technology_id)
    identifier = str(uuid4())
    report = GhdlYosysSynthesis(settings).run(identifier, design, technology, lambda _: None)
    assert report["total_area"] > 0
    assert report["validation"]["rtl"] == report["validation"]["mapped"] == "passed"
    assert report["validation"]["vectors"] == 256
    assert 0 < report["cell_counts"]["flip_flop"] <= design.declared_register_bits
    if design.expected_flip_flops is not None:
        assert report["cell_counts"]["flip_flop"] == design.expected_flip_flops
    assert report["cell_counts"]["latch"] == report["cell_counts"]["macro"] == 0
    assert math.isclose(report["total_area"], sum(cell["total_area"] for cell in report["cells"]))
    assert report["manifest"]["technology"]["id"] == technology_id
    assert report["design_id"] == design_id
    assert report["validation"]["reference"] == design.reference
    directory = tmp_path / "runs" / identifier
    assert json.loads((directory / "report.json").read_text())["total_area"] == report["total_area"]
    assert (directory / "report.csv").read_text().startswith("name,category,count")
    assert (directory / "mapped.v").stat().st_size > 0
    assert (directory / "sources" / design.wrapper_file).is_file()
    assert "Executing script file `synth.ys'" in (directory / "yosys.log").read_text()
    assert report["manifest"]["command_timeout_seconds"] == settings.command_timeout_seconds
