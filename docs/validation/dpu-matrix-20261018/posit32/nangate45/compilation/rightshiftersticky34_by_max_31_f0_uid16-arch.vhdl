architecture arch of RightShifterSticky34_by_max_31_F0_uid16 is
signal ps :  std_logic_vector(4 downto 0);
signal level5 :  std_logic_vector(33 downto 0);
signal stk4 :  std_logic;
signal level4 :  std_logic_vector(33 downto 0);
signal stk3 :  std_logic;
signal level3 :  std_logic_vector(33 downto 0);
signal stk2 :  std_logic;
signal level2 :  std_logic_vector(33 downto 0);
signal stk1 :  std_logic;
signal level1 :  std_logic_vector(33 downto 0);
signal stk0 :  std_logic;
signal level0 :  std_logic_vector(33 downto 0);
begin
   ps<= S;
   level5<= X;
   stk4 <= '1' when (level5(15 downto 0)/="0000000000000000" and ps(4)='1')   else '0';
   level4 <=  level5 when  ps(4)='0'    else (15 downto 0 => padBit) & level5(33 downto 16);
   stk3 <= '1' when (level4(7 downto 0)/="00000000" and ps(3)='1') or stk4 ='1'   else '0';
   level3 <=  level4 when  ps(3)='0'    else (7 downto 0 => padBit) & level4(33 downto 8);
   stk2 <= '1' when (level3(3 downto 0)/="0000" and ps(2)='1') or stk3 ='1'   else '0';
   level2 <=  level3 when  ps(2)='0'    else (3 downto 0 => padBit) & level3(33 downto 4);
   stk1 <= '1' when (level2(1 downto 0)/="00" and ps(1)='1') or stk2 ='1'   else '0';
   level1 <=  level2 when  ps(1)='0'    else (1 downto 0 => padBit) & level2(33 downto 2);
   stk0 <= '1' when (level1(0 downto 0)/="0" and ps(0)='1') or stk1 ='1'   else '0';
   level0 <=  level1 when  ps(0)='0'    else (0 downto 0 => padBit) & level1(33 downto 1);
   R <= level0;
   Sticky <= stk0;
end architecture;
