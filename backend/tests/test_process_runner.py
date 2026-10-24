import sys

import pytest

from area_lab.domain.errors import PipelineFailure
from area_lab.infrastructure.process_runner import ProcessRunner


def test_timeout_keeps_tool_diagnostics_in_run_log(tmp_path):
    runner = ProcessRunner(None, timeout=1)
    with pytest.raises(PipelineFailure, match="excedió el tiempo máximo"):
        runner.run(
            sys.executable,
            ["-u", "-c", "import time; print('tool diagnostic before timeout'); time.sleep(20)"],
            tmp_path,
        )
    log = (tmp_path / "run.log").read_text()
    assert "tool diagnostic before timeout" in log
    assert "[timeout=1s; process group terminated]" in log
