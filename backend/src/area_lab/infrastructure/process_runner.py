import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

from area_lab.domain.errors import PipelineFailure


class ProcessRunner:
    """Fixed argv, no shell; isolated working directory and bounded subprocesses."""

    def __init__(self, toolchain_bin: Path | None, timeout: int) -> None:
        self.toolchain_bin = toolchain_bin
        self.timeout = timeout

    def executable(self, name: str) -> str:
        candidate = str(self.toolchain_bin / name) if self.toolchain_bin else shutil.which(name)
        if not candidate or not Path(candidate).is_file():
            raise PipelineFailure(f"Herramienta no disponible: {name}.")
        return candidate

    def run(self, name: str, args: list[str], directory: Path, output: str | None = None) -> str:
        command = [self.executable(name), *args]
        started = time.monotonic()
        with (directory / "run.log").open("a") as log:
            log.write("\n$ " + " ".join(command) + "\n")
            log.flush()
            result_path = directory / (output or ".command-output")
            with result_path.open("w") as stdout:
                process = subprocess.Popen(
                    command,
                    cwd=directory,
                    stdout=stdout,
                    stderr=log,
                    start_new_session=True,
                    env={**os.environ, "LC_ALL": "C"},
                )
                try:
                    process.wait(timeout=self.timeout)
                except subprocess.TimeoutExpired as exc:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    content = result_path.read_text(errors="replace")
                    log.write(content if output is None else f"[stdout guardado en {output}]\n")
                    log.write(f"[timeout={self.timeout}s; process group terminated]\n")
                    log.flush()
                    raise PipelineFailure(f"{name} excedió el tiempo máximo.") from exc
            content = result_path.read_text(errors="replace")
            log.write(content if output is None else f"[stdout guardado en {output}]\n")
            log.write(f"[exit={process.returncode}; elapsed={time.monotonic() - started:.3f}s]\n")
        if process.returncode:
            raise PipelineFailure(f"Falló {name} (código {process.returncode}). Consulta run.log.")
        return content

    def version(self, name: str) -> str:
        arguments = {"yosys": ["-V"], "ghdl": ["--version"], "iverilog": ["-V"]}
        result = subprocess.run(
            [self.executable(name), *arguments[name]],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        return result.stdout.splitlines()[0]
