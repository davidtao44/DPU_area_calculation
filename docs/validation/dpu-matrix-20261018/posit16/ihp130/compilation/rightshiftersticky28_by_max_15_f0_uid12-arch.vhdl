architecture arch of RightShifterSticky28_by_max_15_F0_uid12 is
signal ps :  std_logic_vector(3 downto 0);
signal level4 :  std_logic_vector(27 downto 0);
signal stk3 :  std_logic;
signal level3 :  std_logic_vector(27 downto 0);
signal stk2 :  std_logic;
signal level2 :  std_logic_vector(27 downto 0);
signal stk1 :  std_logic;
signal level1 :  std_logic_vector(27 downto 0);
signal stk0 :  std_logic;
signal level0 :  std_logic_vector(27 downto 0);
begin
   ps<= S;
   level4<= X;
   stk3 <= '1' when (level4(7 downto 0)/="00000000" and ps(3)='1')   else '0';
   level3 <=  level4 when  ps(3)='0'    else (7 downto 0 => padBit) & level4(27 downto 8);
   stk2 <= '1' when (level3(3 downto 0)/="0000" and ps(2)='1') or stk3 ='1'   else '0';
   level2 <=  level3 when  ps(2)='0'    else (3 downto 0 => padBit) & level3(27 downto 4);
   stk1 <= '1' when (level2(1 downto 0)/="00" and ps(1)='1') or stk2 ='1'   else '0';
   level1 <=  level2 when  ps(1)='0'    else (1 downto 0 => padBit) & level2(27 downto 2);
   stk0 <= '1' when (level1(0 downto 0)/="0" and ps(0)='1') or stk1 ='1'   else '0';
   level0 <=  level1 when  ps(0)='0'    else (0 downto 0 => padBit) & level1(27 downto 1);
   R <= level0;
   Sticky <= stk0;
end architecture;
