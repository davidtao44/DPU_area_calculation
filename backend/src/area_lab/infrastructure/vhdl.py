"""Prepare and analyze the arithmetic sources in the profile's VHDL library."""

import hashlib
import re
from pathlib import Path

from area_lab.domain.errors import PipelineFailure
from area_lab.domain.models import Design
from area_lab.infrastructure.process_runner import ProcessRunner


def analyze_sources(runner: ProcessRunner, directory: Path, design: Design) -> dict:
    sources = [f"sources/{source}" for source in design.source_files]
    preparation = {"policy": design.compilation, "analyzed_files": sources}
    if design.compilation == "unique_ghdl_units":
        preparation = _unique_units(runner, directory, sources)
        sources = preparation["analyzed_files"]
    elif design.compilation != "files":
        raise PipelineFailure("Política de compilación VHDL desconocida.")
    runner.run(
        "ghdl",
        ["-a", "--std=08", "-fsynopsys", "-fexplicit", f"--work={design.library}", *sources],
        directory,
    )
    return preparation


def _unique_units(runner: ProcessRunner, directory: Path, sources: list[str]) -> dict:
    """Use GHDL's parser to split units; reuse only byte-identical duplicates.

    LLVM compiles one object per input file. FloPoCo's Posit16/32 files share
    helper entities/architectures, which otherwise create duplicate symbols.
    Original snapshots stay untouched. Conflicting definitions are a failure.
    """
    compilation = directory / "compilation"
    compilation.mkdir()
    unique = {}
    duplicates = []
    for source in sources:
        output = runner.run("ghdl", ["--chop", "--std=08", source], directory)
        filenames = re.findall(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*\.vhdl)\s+\(for ", output, re.M)
        if not filenames:
            raise PipelineFailure("GHDL --chop no identificó unidades VHDL.")
        for name in filenames:
            generated = directory / name
            content = generated.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            if name in unique:
                previous = unique[name]
                if content != (directory / previous["file"]).read_bytes():
                    raise PipelineFailure(f"Definiciones VHDL duplicadas diferentes: {name}.")
                duplicates.append(
                    {
                        "unit": name,
                        "source": source,
                        "shared_with": previous["source"],
                        "sha256": digest,
                    }
                )
                generated.unlink()
            else:
                relative = f"compilation/{name}"
                generated.rename(directory / relative)
                unique[name] = {"file": relative, "source": source, "sha256": digest}
    return {
        "policy": "unique_ghdl_units",
        "analyzed_files": [unit["file"] for unit in unique.values()],
        "units": list(unique.values()),
        "identical_duplicates": duplicates,
    }
