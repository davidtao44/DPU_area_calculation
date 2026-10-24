--------------------------------------------------------------------------------
--                  RightShifterSticky30_by_max_30_F0_uid12
-- VHDL generated for Kintex7 @ 0MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: Bogdan Pasca (2008-2011), Florent de Dinechin (2008-2019)
--------------------------------------------------------------------------------
-- combinatorial
-- Clock period (ns): inf
-- Target frequency (MHz): 0
-- Input signals: X S
-- Output signals: R Sticky

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
library std;
use std.textio.all;
library work;

entity RightShifterSticky30_by_max_30_F0_uid12 is
    port (X : in  std_logic_vector(29 downto 0);
          S : in  std_logic_vector(4 downto 0);
          R : out  std_logic_vector(29 downto 0);
          Sticky : out  std_logic   );
end entity;
