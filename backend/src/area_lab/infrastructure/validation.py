"""Deterministic, width-aware RTL oracle and strict mapped-netlist comparison.

The RTL oracle establishes preservation of the supplied implementation, not an
independent proof of floating/posit/LNS arithmetic. Integer profiles additionally
check every RTL result against an independent signed modulo dot product.
"""

import random
import re
from pathlib import Path

from area_lab.domain.errors import PipelineFailure
from area_lab.domain.models import Design
from area_lab.infrastructure.process_runner import ProcessRunner

VECTOR_COUNT = 256
SEED = 20261005


def _special_words(design: Design) -> tuple[list[int], list[int]]:
    n, m = design.operand_bits, design.result_bits
    sign = 1 << (n - 1)
    if design.family == "floating":
        exponent = {8: 4, 16: 5, 32: 8}[n]
        fraction = n - exponent - 1
        one = ((1 << (exponent - 1)) - 1) << fraction
        infinity = ((1 << exponent) - 1) << fraction
        words = [
            0,
            sign,
            one,
            one | sign,
            1,
            (1 << fraction) - 1,
            1 << fraction,
            infinity - 1,
            infinity,
            infinity | sign,
            infinity | 1,
        ]
    elif design.family == "posit":
        words = [0, sign >> 1, (3 * sign) >> 1, 1, sign - 1, sign, sign + 1, (1 << n) - 1]
    elif design.family == "logarithmic":
        # LNS exception 00=zero, 01=normal, 10=infinity, 11=NaN.
        words = [0, 0x4000, 0x6000, 0x4001, 0x5FFF, 0x8000, 0xC000, 0xFFFF]
    elif design.family == "fixed":
        one = 1 << (5 if n == 8 else 10)
        words = [0, one, (-one) & ((1 << n) - 1), 1, sign - 1, sign, (1 << n) - 1]
    else:
        words = [0, 1, sign - 1, sign, (1 << n) - 1]
    accumulator_words = words if n == m else [0, 1, (1 << (m - 1)) - 1, 1 << (m - 1), (1 << m) - 1]
    return words, accumulator_words


def write_vectors(directory: Path, design: Design) -> int:
    """Write nine raw input words per stimulus; expected words come from RTL."""
    rng = random.Random(SEED)
    n, m = design.operand_bits, design.result_bits
    mask = (1 << n) - 1
    result_mask = (1 << m) - 1
    if design.id == "int8_16":
        # Preserve the pilot's original 256 stimuli for reproducibility.
        cases = [
            ([0] * 4, [0] * 4, 0),
            ([1, 2, 3, 4], [4, 3, 2, 1], 7),
            ([-128] * 4, [-128] * 4, 0),
            ([127] * 4, [127] * 4, 32767),
            ([-128, 127, -1, 0], [127, -128, -1, 0], -32768),
        ]
        while len(cases) < VECTOR_COUNT:
            cases.append(
                (
                    [rng.randint(-128, 127) for _ in range(4)],
                    [rng.randint(-128, 127) for _ in range(4)],
                    rng.randint(-32768, 32767),
                )
            )
    else:
        words, accumulators = _special_words(design)
        cases = []
        for index, word in enumerate(words):
            other = words[(index + 1) % len(words)]
            c = accumulators[index % len(accumulators)]
            cases.extend(
                [([word] * 4, [other] * 4, c), ([word, other, 0, word], [other, word, word, 0], c)]
            )
        # Exercise each lane separately, sign/cancellation, boundaries, then raw bits.
        for lane in range(4):
            a, b = [0] * 4, [0] * 4
            a[lane], b[lane] = words[1], words[2]
            cases.append((a, b, 0))
        while len(cases) < VECTOR_COUNT:
            if design.family == "logarithmic" and len(cases) % 2 == 0:
                # Raw LNS words mostly hit exception paths. Exercise the
                # correction tables too, with normal signed magnitudes 0.25..4.
                def normal_lns():
                    return 0x4000 | (rng.getrandbits(1) << 13) | (rng.randint(-1024, 1024) & 0x1FFF)

                cases.append(
                    (
                        [normal_lns() for _ in range(4)],
                        [normal_lns() for _ in range(4)],
                        normal_lns(),
                    )
                )
            else:
                cases.append(
                    (
                        [rng.getrandbits(n) for _ in range(4)],
                        [rng.getrandbits(n) for _ in range(4)],
                        rng.getrandbits(m),
                    )
                )
    lines = []
    for a, b, accumulator in cases:
        encoded = [f"{value & mask:0{n // 4}X}" for value in a + b]
        lines.append(" ".join([*encoded, f"{accumulator & result_mask:0{m // 4}X}"]))
    (directory / "stimuli.txt").write_text("\n".join(lines) + "\n")
    return len(cases)


VHDL_TESTBENCH = """library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_textio.all;
use std.textio.all;
entity area_validation_tb is end;
architecture test of area_validation_tb is
  signal clk : std_logic := '0';
  signal a0,a1,a2,a3,b0,b1,b2,b3 : std_logic_vector(@OPERAND_MSB@ downto 0);
  signal c,r : std_logic_vector(@RESULT_MSB@ downto 0);
begin
  dut: entity work.@TOP@
    port map(clk,a0,a1,a2,a3,b0,b1,b2,b3,c,r);
  process
    file vectors : text open read_mode is "stimuli.txt";
    file results : text open write_mode is "rtl-results.txt";
    variable line_in,line_out : line;
    variable va0,va1,va2,va3,vb0,vb1,vb2,vb3 : std_logic_vector(@OPERAND_MSB@ downto 0);
    variable vc : std_logic_vector(@RESULT_MSB@ downto 0);
    variable tested : integer := 0;
  begin
    while not endfile(vectors) loop
      readline(vectors,line_in);
      hread(line_in,va0); hread(line_in,va1); hread(line_in,va2); hread(line_in,va3);
      hread(line_in,vb0); hread(line_in,vb1); hread(line_in,vb2); hread(line_in,vb3);
      hread(line_in,vc);
      a0<=va0; a1<=va1; a2<=va2; a3<=va3;
      b0<=vb0; b1<=vb1; b2<=vb2; b3<=vb3; c<=vc;
      clk<='0'; wait for 5 ns; clk<='1'; wait for 5 ns;
      clk<='0'; wait for 5 ns; clk<='1'; wait for 1 ns;
      assert not is_x(r) report "RTL undefined output at vector " & integer'image(tested)
        severity failure;
      hwrite(line_out,r); writeline(results,line_out);
      tested:=tested+1;
      clk<='0'; wait for 4 ns;
    end loop;
    report "VALIDATION_OK " & integer'image(tested);
    std.env.stop;
    wait;
  end process;
end;
"""

VERILOG_TESTBENCH = """module area_validation_tb;
  reg clk=0;
  reg [@OPERAND_MSB@:0] a0,a1,a2,a3,b0,b1,b2,b3;
  reg [@RESULT_MSB@:0] c,expected;
  wire [@RESULT_MSB@:0] r;
  integer f,n,tested=0;
  @TOP@ dut(
    .clk(clk),.A0_in(a0),.A1_in(a1),.A2_in(a2),.A3_in(a3),
    .B0_in(b0),.B1_in(b1),.B2_in(b2),.B3_in(b3),.C0_in(c),.R_out(r));
  initial begin
    f=$fopen("vectors.txt","r");
    if (!f) $fatal(1,"Missing vectors");
    while (!$feof(f)) begin
      n=$fscanf(f,"%h %h %h %h %h %h %h %h %h %h\\n",
        a0,a1,a2,a3,b0,b1,b2,b3,c,expected);
      if (n==10) begin
        clk=0; #5; clk=1; #5; clk=0; #5; clk=1; #1;
        if (r !== expected) $fatal(1,"Mapped mismatch vector %0d: %h != %h",tested,r,expected);
        tested=tested+1; clk=0; #4;
      end else if (!$feof(f)) $fatal(1,"Malformed vector");
    end
    $display("VALIDATION_OK %0d",tested);
    $finish;
  end
endmodule
"""


def _testbench(template: str, design: Design) -> str:
    return (
        template.replace("@TOP@", design.top)
        .replace("@OPERAND_MSB@", str(design.operand_bits - 1))
        .replace("@RESULT_MSB@", str(design.result_bits - 1))
    )


def check_rtl_results(directory: Path, design: Design) -> None:
    inputs = (directory / "stimuli.txt").read_text().splitlines()
    results = (directory / "rtl-results.txt").read_text().splitlines()
    if len(inputs) != VECTOR_COUNT or len(results) != VECTOR_COUNT:
        raise PipelineFailure("La referencia RTL no generó todos los resultados.")
    lines = []
    for index, (stimulus, result) in enumerate(zip(inputs, results, strict=True)):
        if not re.fullmatch(r"[0-9a-fA-F]{" + str(design.result_bits // 4) + "}", result):
            raise PipelineFailure(f"Referencia RTL indefinida en el vector {index}.")
        if design.reference == "signed_dot_modulo":
            words = [int(word, 16) for word in stimulus.split()]
            sign = 1 << (design.operand_bits - 1)
            signed = [(word ^ sign) - sign for word in words[:8]]
            expected = (
                sum(x * y for x, y in zip(signed[:4], signed[4:], strict=True)) + words[8]
            ) & ((1 << design.result_bits) - 1)
            if int(result, 16) != expected:
                raise PipelineFailure(f"RTL no coincide con la referencia entera, vector {index}.")
        lines.append(f"{stimulus} {result}")
    (directory / "vectors.txt").write_text("\n".join(lines) + "\n")


def validate_rtl(runner: ProcessRunner, directory: Path, design: Design) -> None:
    (directory / "validation_tb.vhd").write_text(_testbench(VHDL_TESTBENCH, design))
    runner.run(
        "ghdl", ["-a", "--std=08", "-fsynopsys", "-fexplicit", "validation_tb.vhd"], directory
    )
    runner.run(
        "ghdl", ["-e", "--std=08", "-fsynopsys", "-fexplicit", "area_validation_tb"], directory
    )
    output = runner.run(
        "ghdl",
        [
            "-r",
            "--std=08",
            "-fsynopsys",
            "-fexplicit",
            "area_validation_tb",
            "--assert-level=error",
            "--ieee-asserts=disable-at-0",
        ],
        directory,
    )
    if f"VALIDATION_OK {VECTOR_COUNT}" not in output:
        raise PipelineFailure("La validación RTL no confirmó todos los vectores.")
    check_rtl_results(directory, design)


def validate_mapped(runner: ProcessRunner, directory: Path, design: Design) -> None:
    (directory / "validation_tb.v").write_text(_testbench(VERILOG_TESTBENCH, design))
    runner.run("yosys", ["-s", "simulation_cells.ys"], directory)
    runner.run(
        "iverilog",
        [
            "-g2012",
            "-s",
            "area_validation_tb",
            "-o",
            "mapped_sim",
            "validation_tb.v",
            "mapped.v",
            "cells_sim.v",
        ],
        directory,
    )
    output = runner.run("vvp", ["mapped_sim"], directory)
    if f"VALIDATION_OK {VECTOR_COUNT}" not in output:
        raise PipelineFailure("La validación mapeada no confirmó todos los vectores.")
