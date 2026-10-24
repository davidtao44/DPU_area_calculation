from pathlib import Path

from area_lab.domain.models import Design, Technology
from area_lab.infrastructure.designs import DESIGNS


def build_catalog(assets_dir: Path) -> tuple[list[Design], list[Technology]]:
    designs = list(DESIGNS)
    specifications = [
        ("ihp130", "IHP SG13G2", 130, 1.2, "libraries/ihp130/cells.lib"),
        ("nangate15", "Nangate FreePDK15", 15, 0.8, "libraries/nangate15/cells.lib"),
        ("nangate45", "Nangate Open Cell Library", 45, 1.1, "libraries/nangate45/cells.lib"),
    ]
    technologies = []
    for identifier, label, node, voltage, filename in specifications:
        available = filename is not None and (assets_dir / filename).is_file()
        technologies.append(
            Technology(
                id=identifier,
                label=label,
                node_nm=node,
                corner="typical",
                voltage_v=voltage,
                temperature_c=25,
                liberty_file=filename,
                available=available,
                reason=None
                if available
                else "Falta el Liberty .lib; los .db no bastan para Yosys.",
                unit_basis=(
                    "IHP SG13G2 standard-cell datasheet: Area in µm²."
                    if identifier == "ihp130"
                    else ("Nangate OCL: cell area in µm²; DOI 10.1145/2717764.2717783 for 15 nm.")
                ),
            )
        )
    return designs, technologies
