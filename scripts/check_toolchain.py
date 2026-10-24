"""Fail the image build if GHDL cannot analyze, link, simulate and synthesize VHDL."""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from area_lab.domain.errors import PipelineFailure
from area_lab.infrastructure.process_runner import ProcessRunner
from area_lab.infrastructure.settings import Settings

NATIVE_LINK_SOURCE = """#include <stdlib.h>
#include <zlib.h>
/* This symbol is referenced by the pinned GHDL libgrt.a (glibc >= 2.38). */
extern long __isoc23_strtol(const char *, char **, int);
int main(void) {
    char *end;
    long parsed = __isoc23_strtol("123", &end, 10);
    return parsed != 123 || *end != '\\0' || zlibVersion() == NULL;
}
"""

SMOKE_SOURCE = """library ieee;
use ieee.std_logic_1164.all;
entity toolchain_smoke is
  port (a, b : in std_logic; y : out std_logic);
end;
architecture rtl of toolchain_smoke is
begin
  y <= a and b;
end;

library ieee;
use ieee.std_logic_1164.all;
entity toolchain_smoke_tb is end;
architecture test of toolchain_smoke_tb is
  signal a, b, y : std_logic := '0';
begin
  dut: entity work.toolchain_smoke port map(a, b, y);
  process
  begin
    wait for 1 ns;
    assert y = '0' severity failure;
    a <= '1'; b <= '1';
    wait for 1 ns;
    assert y = '1' severity failure;
    report "TOOLCHAIN_OK";
    std.env.stop;
    wait;
  end process;
end;
"""


def main() -> None:
    if shutil.which("cc") is None:
        raise SystemExit(
            "GHDL LLVM necesita cc. Instala build-essential antes de ejecutar el flujo."
        )
    settings = Settings()
    runner = ProcessRunner(settings.toolchain_bin, settings.command_timeout_seconds)
    for tool in ("ghdl", "yosys", "iverilog"):
        print(runner.version(tool), flush=True)
    with TemporaryDirectory(prefix="area-lab-toolchain-") as temporary:
        directory = Path(temporary)
        (directory / "smoke.vhd").write_text(SMOKE_SOURCE)
        try:
            # Test the actual system link dependencies, not only command availability.
            native = ProcessRunner(None, settings.command_timeout_seconds)
            (directory / "native_link.c").write_text(NATIVE_LINK_SOURCE)
            native.run("cc", ["native_link.c", "-lz", "-o", "native_link"], directory)
            native.run(str(directory / "native_link"), [], directory)
            print(
                "Native linker OK: zlib development files and glibc >= 2.38.",
                flush=True,
            )
            runner.run("ghdl", ["-a", "--std=08", "smoke.vhd"], directory)
            runner.run("ghdl", ["-e", "--std=08", "toolchain_smoke_tb"], directory)
            result = runner.run(
                "ghdl",
                ["-r", "--std=08", "toolchain_smoke_tb", "--assert-level=error"],
                directory,
            )
            if "TOOLCHAIN_OK" not in result:
                raise PipelineFailure("GHDL no confirmó la simulación de prueba.")
            runner.run(
                "ghdl",
                ["--synth", "--std=08", "--out=verilog", "toolchain_smoke"],
                directory,
                output="smoke.v",
            )
        except PipelineFailure:
            print((directory / "run.log").read_text(errors="replace"), flush=True)
            raise
    print(
        "Toolchain OK: GHDL analysis, elaboration/link, simulation and Verilog synthesis."
    )


if __name__ == "__main__":
    main()
