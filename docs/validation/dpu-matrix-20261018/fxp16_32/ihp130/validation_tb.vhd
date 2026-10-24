library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_textio.all;
use std.textio.all;
entity area_validation_tb is end;
architecture test of area_validation_tb is
  signal clk : std_logic := '0';
  signal a0,a1,a2,a3,b0,b1,b2,b3 : std_logic_vector(15 downto 0);
  signal c,r : std_logic_vector(31 downto 0);
begin
  dut: entity work.FXP16_32_DPU_perf_top
    port map(clk,a0,a1,a2,a3,b0,b1,b2,b3,c,r);
  process
    file vectors : text open read_mode is "stimuli.txt";
    file results : text open write_mode is "rtl-results.txt";
    variable line_in,line_out : line;
    variable va0,va1,va2,va3,vb0,vb1,vb2,vb3 : std_logic_vector(15 downto 0);
    variable vc : std_logic_vector(31 downto 0);
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
