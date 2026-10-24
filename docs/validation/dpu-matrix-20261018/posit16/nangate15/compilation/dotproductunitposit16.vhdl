library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity DotProductUnitPosit16 is
    Port (
        aX0 : in  std_logic_vector(15 downto 0);
        aX1 : in  std_logic_vector(15 downto 0);
        aX2 : in  std_logic_vector(15 downto 0);
        aX3 : in  std_logic_vector(15 downto 0);
        bY0 : in  std_logic_vector(15 downto 0);
        bY1 : in  std_logic_vector(15 downto 0);
        bY2 : in  std_logic_vector(15 downto 0);
        bY3 : in  std_logic_vector(15 downto 0);
        cX0 : in  std_logic_vector(15 downto 0);
        R  : out std_logic_vector(15 downto 0)
    );
end DotProductUnitPosit16;
