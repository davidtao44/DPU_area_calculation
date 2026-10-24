import math
import re
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from area_lab.domain.errors import PipelineFailure


@dataclass(frozen=True)
class CellDefinition:
    name: str
    area: Decimal
    category: str


def _remove_comments(text: str) -> str:
    # Preserve quoted strings: comment markers inside functions are not comments.
    pattern = r'"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\n]*'
    return re.sub(pattern, lambda m: m[0] if m[0].startswith('"') else " ", text)


def _block_end(text: str, opening: int) -> int:
    depth = 1
    quoted = False
    escaped = False
    for index in range(opening + 1, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise PipelineFailure("Liberty contiene un bloque sin cerrar.")


def read_cells(path: Path) -> dict[str, CellDefinition]:
    """Read cell areas and semantic ff/latch groups, not naming heuristics."""
    text = _remove_comments(path.read_text())
    cells = {}
    pattern = r'\bcell\s*\(\s*(?:"([^"\n]+)"|([^\s)]+))\s*\)\s*\{'
    for match in re.finditer(pattern, text):
        name = match[1] or match[2]
        block = text[match.end() : _block_end(text, match.end() - 1)]
        area_match = re.search(r"\barea\s*:\s*([+\-\d.eE]+)\s*;", block)
        if area_match is None:
            raise PipelineFailure(f"Celda {name} sin campo area.")
        area = Decimal(area_match[1])
        if not area.is_finite() or area < 0 or not math.isfinite(float(area)):
            raise PipelineFailure(f"Área inválida para {name}.")
        if re.search(r"\b(?:ff|ff_bank)\s*\(", block):
            category = "flip_flop"
        elif re.search(r"\b(?:latch|latch_bank)\s*\(", block):
            category = "latch"
        elif re.search(r"\bmemory\s*\(", block):
            category = "macro"
        else:
            category = "combinational"
        if name in cells:
            raise PipelineFailure(f"Celda duplicada en Liberty: {name}.")
        cells[name] = CellDefinition(name, area, category)
    if not cells:
        raise PipelineFailure("La biblioteca no contiene celdas.")
    return cells


def summarize_netlist(
    netlist: dict[str, Any], cells: dict[str, CellDefinition], top: str
) -> dict[str, Any]:
    modules = netlist.get("modules", {})
    if top not in modules:
        raise PipelineFailure("No se encontró el top en la netlist mapeada.")
    module = modules[top]
    if module.get("memories"):
        raise PipelineFailure("Quedan memorias sin mapear.")
    counts = Counter(cell["type"] for cell in module.get("cells", {}).values())
    unknown = sorted(set(counts) - set(cells))
    if unknown:
        raise PipelineFailure("Celdas sin mapear o sin área: " + ", ".join(unknown))
    if not counts:
        raise PipelineFailure("La síntesis produjo un diseño vacío.")
    categories = {name: Decimal(0) for name in ("combinational", "flip_flop", "latch", "macro")}
    category_counts = dict.fromkeys(categories, 0)
    rows = []
    for name, count in sorted(counts.items()):
        definition = cells[name]
        subtotal = definition.area * count
        categories[definition.category] += subtotal
        category_counts[definition.category] += count
        rows.append(
            {
                "name": name,
                "category": definition.category,
                "count": count,
                "unit_area": float(definition.area),
                "total_area": float(subtotal),
            }
        )
    return {
        "total_area": float(sum(categories.values(), Decimal(0))),
        "combinational_area": float(categories["combinational"]),
        "sequential_area": float(categories["flip_flop"] + categories["latch"]),
        "flip_flop_area": float(categories["flip_flop"]),
        "latch_area": float(categories["latch"]),
        "macro_area": float(categories["macro"]),
        "total_cells": sum(counts.values()),
        "cell_counts": category_counts,
        "cells": rows,
    }
