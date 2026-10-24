import csv
import hashlib
import json
import math
import shutil
import time
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from area_lab.domain.errors import PipelineFailure
from area_lab.domain.models import Design, Technology
from area_lab.infrastructure.liberty import read_cells, summarize_netlist
from area_lab.infrastructure.process_runner import ProcessRunner
from area_lab.infrastructure.settings import Settings
from area_lab.infrastructure.validation import (
    SEED,
    validate_mapped,
    validate_rtl,
    write_vectors,
)
from area_lab.infrastructure.vhdl import analyze_sources

ARTIFACTS = (
    "report.json",
    "report.csv",
    "manifest.json",
    "design.v",
    "mapped.v",
    "mapped.json",
    "stat.json",
    "synth.ys",
    "run.log",
    "yosys.log",
    "vectors.txt",
    "stimuli.txt",
    "rtl-results.txt",
    "validation_tb.vhd",
    "validation_tb.v",
    "INT8_Mult.vhd",
    "INT8_Adder.vhd",
    "INT8_DPU.vhd",
    "INT8_16_DPU_perf_top.vhd",
    "simulation_cells.ys",
    "cells_sim.v",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GhdlYosysSynthesis:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.runner = ProcessRunner(settings.toolchain_bin, settings.command_timeout_seconds)

    def run(
        self,
        experiment_id: str,
        design: Design,
        technology: Technology,
        progress: Callable[[str], None],
    ) -> dict[str, Any]:
        started = time.monotonic()
        directory = self.settings.data_dir / "runs" / experiment_id
        directory.mkdir(parents=True, exist_ok=False)
        if not technology.liberty_file:
            raise PipelineFailure("La tecnología no tiene un Liberty disponible.")
        sources = [*design.source_files, design.wrapper_file]
        source_hashes = {}
        for source in sources:
            original = self.settings.assets_dir / source
            source_hashes[source] = sha256(original)
            destination = directory / "sources" / source
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, destination)
        liberty = self.settings.assets_dir / technology.liberty_file
        shutil.copy2(liberty, directory / "cells.lib")
        cells = read_cells(directory / "cells.lib")
        manifest = {
            "schema_version": 2,
            "experiment_id": experiment_id,
            "command_timeout_seconds": self.settings.command_timeout_seconds,
            "design": asdict(design),
            "technology": asdict(technology),
            "source_sha256": source_hashes,
            "liberty_sha256": sha256(directory / "cells.lib"),
            "tool_versions": {
                name: self.runner.version(name) for name in ("ghdl", "yosys", "iverilog")
            },
            "scope": "standard_cell_area_only",
            "mapping_policy": (
                "Yosys synth -noabc; dfflibmap; ABC default Liberty mapping; no timing target"
            ),
            "memory_policy": "ROM lowered to combinational logic; no SRAM macros",
            "functional_test": {
                "seed": SEED,
                "reference": design.reference,
                "numeric_notes": design.numeric_notes,
                "comparison": "bit-exact RTL vs mapped netlist; unknown outputs rejected",
                "stimuli": (
                    "256 directed, finite-biased LNS and raw-bit vectors; normal magnitudes 0.25..4"
                    if design.family == "logarithmic"
                    else "256 directed and deterministic raw-bit vectors"
                ),
                "clock_policy": "two rising edges per stimulus; registered wrapper included",
            },
            "excluded": ["routing", "wire_area", "placement", "floorplan", "pads", "clock_tree"],
        }
        asset_manifest = self.settings.assets_dir / "manifest.json"
        if asset_manifest.is_file():
            manifest["asset_snapshot"] = json.loads(asset_manifest.read_text())
        (directory / "manifest.json").write_text(json.dumps(manifest, indent=2))
        progress("analyzing")
        manifest["compilation"] = analyze_sources(self.runner, directory, design)
        (directory / "manifest.json").write_text(json.dumps(manifest, indent=2))
        self.runner.run(
            "ghdl",
            ["-a", "--std=08", "-fsynopsys", "-fexplicit", f"sources/{design.wrapper_file}"],
            directory,
        )
        progress("validating_rtl")
        vector_count = write_vectors(directory, design)
        validate_rtl(self.runner, directory, design)
        manifest["functional_test"]["stimuli_sha256"] = sha256(directory / "stimuli.txt")
        manifest["functional_test"]["rtl_results_sha256"] = sha256(directory / "rtl-results.txt")
        manifest["functional_test"]["vectors_sha256"] = sha256(directory / "vectors.txt")
        (directory / "manifest.json").write_text(json.dumps(manifest, indent=2))
        progress("converting")
        self.runner.run(
            "ghdl",
            ["--synth", "--std=08", "-fsynopsys", "-fexplicit", "--out=verilog", design.top],
            directory,
            output="design.v",
        )
        script = f"""read_liberty -lib cells.lib
read_verilog design.v
hierarchy -check -top {design.top}
synth -top {design.top} -flatten -noabc
dfflibmap -liberty cells.lib
abc -liberty cells.lib
delete t:$scopeinfo
clean
check -assert
write_json mapped.json
write_verilog -noattr mapped.v
tee -o stat.json stat -liberty cells.lib -json
"""
        (directory / "synth.ys").write_text(script)
        (directory / "simulation_cells.ys").write_text(
            "read_liberty -ignore_miss_func -ignore_miss_dir -ignore_miss_data_latch cells.lib\n"
            "write_verilog -noattr cells_sim.v\n"
        )
        progress("mapping")
        self.runner.run("yosys", ["-L", "yosys.log", "-s", "synth.ys"], directory)
        progress("checking")
        summary = summarize_netlist(
            json.loads((directory / "mapped.json").read_text()), cells, design.top
        )
        stat = json.loads((directory / "stat.json").read_text())
        stat_area = stat.get("design", {}).get("area")
        if stat_area is None:
            stat_area = stat.get("modules", {}).get("\\" + design.top, {}).get("area")
        if stat_area is None or not math.isclose(summary["total_area"], stat_area, abs_tol=0.00001):
            raise PipelineFailure("La suma por celdas no coincide con stat -liberty.")
        if summary["cell_counts"]["latch"] or summary["cell_counts"]["macro"]:
            raise PipelineFailure("Estas DPU registradas no deben introducir latches ni macros.")
        flip_flops = summary["cell_counts"]["flip_flop"]
        if not 0 < flip_flops <= design.declared_register_bits:
            raise PipelineFailure("El estado mapeado no corresponde al wrapper registrado.")
        if design.expected_flip_flops is not None and flip_flops != design.expected_flip_flops:
            raise PipelineFailure(
                f"{design.top} debe conservar {design.expected_flip_flops} flip-flops."
            )
        progress("validating_mapped")
        validate_mapped(self.runner, directory, design)
        progress("reporting")
        report = {
            **summary,
            "area_unit": technology.area_unit,
            "area_unit_basis": technology.unit_basis,
            "design_id": design.id,
            "numeric_format": design.numeric_format,
            "declared_register_bits": design.declared_register_bits,
            "top": design.top,
            "technology_id": technology.id,
            "technology_label": technology.label,
            "node_nm": technology.node_nm,
            "corner": technology.corner,
            "voltage_v": technology.voltage_v,
            "temperature_c": technology.temperature_c,
            "duration_seconds": round(time.monotonic() - started, 3),
            "validation": {
                "rtl": "passed",
                "mapped": "passed",
                "vectors": vector_count,
                "seed": SEED,
                "reference": design.reference,
                "numerical_accuracy": "not_assessed",
                "formal_equivalence": "not_run",
                "timing_analysis": "not_run",
            },
            "manifest": manifest,
        }
        (directory / "report.json").write_text(json.dumps(report, indent=2))
        with (directory / "report.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(
                stream, fieldnames=["name", "category", "count", "unit_area", "total_area"]
            )
            writer.writeheader()
            writer.writerows(summary["cells"])
        return report
