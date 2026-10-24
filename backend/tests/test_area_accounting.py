from decimal import Decimal

import pytest

from area_lab.domain.errors import PipelineFailure
from area_lab.infrastructure.liberty import CellDefinition, read_cells, summarize_netlist


def test_semantic_classification_and_exact_area(tmp_path):
    path = tmp_path / "cells.lib"
    path.write_text("""library(example) {
      /* A misleading name must not decide sequential classification. */
      cell(DFF_named_but_logic) { area: 0.1; pin(Y) { function: "A"; } }
      cell(state_without_ff_name) { area: 0.3; ff(IQ,IQN) { next_state: D; } }
      cell(held) { area: 0.2; latch(IQ,IQN) { data_in: D; } }
    }""")
    cells = read_cells(path)
    netlist = {
        "modules": {
            "top": {
                "cells": {
                    "a": {"type": "DFF_named_but_logic"},
                    "b": {"type": "state_without_ff_name"},
                    "c": {"type": "held"},
                }
            }
        }
    }
    result = summarize_netlist(netlist, cells, "top")
    assert result["total_area"] == 0.6
    assert result["combinational_area"] == 0.1
    assert result["sequential_area"] == 0.5
    assert result["cell_counts"]["flip_flop"] == 1
    assert result["cell_counts"]["latch"] == 1


@pytest.mark.parametrize("cell_type", ["$mul", "$scopeinfo", "missing_macro"])
def test_unresolved_cells_invalidate_report(cell_type):
    netlist = {"modules": {"top": {"cells": {"x": {"type": cell_type}}}}}
    with pytest.raises(PipelineFailure, match="sin mapear"):
        summarize_netlist(
            netlist, {"known": CellDefinition("known", Decimal("1"), "combinational")}, "top"
        )


@pytest.mark.parametrize("area", ["-1", "1e999999"])
def test_invalid_area_cannot_be_reported(tmp_path, area):
    path = tmp_path / "invalid.lib"
    path.write_text(f"library(l) {{ cell(x) {{ area: {area}; }} }}")
    with pytest.raises(PipelineFailure):
        read_cells(path)
