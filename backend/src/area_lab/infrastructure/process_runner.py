import os
import shutil
import signal
import subprocess
import time
from contextlib import nullcontext
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
        log_path = directory / "run.log"
        with log_path.open("a", encoding="utf-8") as log:
            log.write("\n$ " + " ".join(command) + "\n")
            log.flush()
            output_start = log.tell()
            result_path = directory / output if output else None
            # Stream diagnostics directly to disk, including while the tool is running.
            # Generated files (e.g. design.v) must contain stdout only.
            with result_path.open("w") if result_path else nullcontext(log) as stdout:
                process = subprocess.Popen(
                    command,
                    cwd=directory,
                    stdout=stdout,
                    stderr=log if result_path else subprocess.STDOUT,
                    start_new_session=True,
                    env={**os.environ, "LC_ALL": "C"},
                )
                try:
                    process.wait(timeout=self.timeout)
                except subprocess.TimeoutExpired as exc:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    if output:
                        log.write(f"[stdout guardado en {output}]\n")
                    log.write(f"[timeout={self.timeout}s; process group terminated]\n")
                    log.flush()
                    raise PipelineFailure(
                        self._failure_message(
                            f"{name} excedió el tiempo máximo ({self.timeout} s).",
                            log_path,
                            output_start,
                        )
                    ) from exc
            output_end = log.tell()
            if output:
                log.write(f"[stdout guardado en {output}]\n")
            log.write(f"[exit={process.returncode}; elapsed={time.monotonic() - started:.3f}s]\n")
        if process.returncode:
            raise PipelineFailure(
                self._failure_message(
                    f"Falló {name} (código {process.returncode}).", log_path, output_start
                )
            )
        if result_path:
            return result_path.read_text(errors="replace")
        with log_path.open("rb") as stream:
            stream.seek(output_start)
            return stream.read(output_end - output_start).decode("utf-8", errors="replace")

    @staticmethod
    def _failure_message(message: str, log_path: Path, output_start: int) -> str:
        # A large synthesis log must not be loaded into memory on the failure path.
        with log_path.open("rb") as stream:
            stream.seek(0, os.SEEK_END)
            stream.seek(max(output_start, stream.tell() - 8000))
            tail = stream.read().decode("utf-8", errors="replace")
        tail = "\n".join(tail.splitlines()[-40:])
        return f"{message} Consulta run.log.\nÚltimas líneas:\n{tail}"

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
