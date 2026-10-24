import sys

import pytest

from area_lab.domain.errors import PipelineFailure
from area_lab.infrastructure.process_runner import ProcessRunner


def test_timeout_keeps_tool_diagnostics_in_run_log(tmp_path):
    runner = ProcessRunner(None, timeout=1)
    with pytest.raises(PipelineFailure, match="excedió el tiempo máximo") as failure:
        runner.run(
            sys.executable,
            [
                "-u",
                "-c",
                "import sys, time; print('tool diagnostic before timeout'); "
                "print('tool stderr before timeout', file=sys.stderr); time.sleep(20)",
            ],
            tmp_path,
        )
    log = (tmp_path / "run.log").read_text()
    assert "tool diagnostic before timeout" in log
    assert "[timeout=1s; process group terminated]" in log
    assert "tool diagnostic before timeout" in str(failure.value)
    assert "tool stderr before timeout" in str(failure.value)
    assert "1 s" in str(failure.value)
    assert "run.log" in str(failure.value)


def test_nonzero_exit_shows_bounded_tail_and_keeps_full_log(tmp_path):
    runner = ProcessRunner(None, timeout=5)
    with pytest.raises(PipelineFailure) as failure:
        runner.run(
            sys.executable,
            [
                "-c",
                "import sys; print('first diagnostic'); "
                "print('intermediate diagnostic\\n' * 10000); "
                "print('final diagnostic'); sys.exit(2)",
            ],
            tmp_path,
        )
    message = str(failure.value)
    assert "final diagnostic" in message
    assert "first diagnostic" not in message
    assert "código 2" in message
    assert len(message) < 9000
    assert "first diagnostic" in (tmp_path / "run.log").read_text()


def test_redirected_stdout_stays_separate_from_diagnostics(tmp_path):
    runner = ProcessRunner(None, timeout=5)
    content = runner.run(
        sys.executable,
        ["-c", "import sys; print('module example; endmodule'); print('warning', file=sys.stderr)"],
        tmp_path,
        output="design.v",
    )
    assert content == (tmp_path / "design.v").read_text() == "module example; endmodule\n"
    assert "warning" in (tmp_path / "run.log").read_text()


def test_silent_failure_does_not_show_previous_command_output(tmp_path):
    runner = ProcessRunner(None, timeout=5)
    runner.run(sys.executable, ["-c", "print('previous command diagnostic')"], tmp_path)
    with pytest.raises(PipelineFailure) as failure:
        runner.run(sys.executable, ["-c", "raise SystemExit(1)"], tmp_path)
    assert "previous command diagnostic" not in str(failure.value)
