architecture arch of PositDecoder_16_1_F0_uid8 is
   component LZOCShifter_14_to_14_counting_16_F0_uid10 is
      port ( I : in  std_logic_vector(13 downto 0);
             OZb : in  std_logic;
             Count : out  std_logic_vector(3 downto 0);
             O : out  std_logic_vector(13 downto 0)   );
   end component;

signal s :  std_logic;
signal nzero :  std_logic;
signal is_zero :  std_logic;
signal is_NAR :  std_logic;
signal rep_sign :  std_logic_vector(14 downto 0);
signal twos :  std_logic_vector(14 downto 0);
signal rc :  std_logic;
signal remainder :  std_logic_vector(13 downto 0);
signal lzCount :  std_logic_vector(3 downto 0);
signal usefulBits :  std_logic_vector(13 downto 0);
signal final_reg :  std_logic_vector(4 downto 0);
begin
--------------------------- Start of vhdl generation ---------------------------
------------------------------- Extract Sign bit -------------------------------
s <= Input(15);
Sign <= s;
-------------------------------- Special Cases --------------------------------
nzero <= Input(14) when Input(13 downto 0) = "00000000000000" else '1';
   -- 1 if Input is zero
is_zero <= s NOR nzero;
z <= is_zero;
   -- 1 if Input is infinity
is_NAR<= s AND (NOT nzero);
inf <= is_NAR;
--------------------------- 2's Complement of Input ---------------------------
rep_sign <= (others => s);
twos <= (rep_sign XOR Input(14 downto 0)) + s;
rc <= twos(twos'high);
----------------- Count leading zeros of regime & shift it out -----------------
remainder<= twos(13 downto 0);
   lzoc: LZOCShifter_14_to_14_counting_16_F0_uid10
      port map ( I => remainder,
                 OZb => rc,
                 Count => lzCount,
                 O => usefulBits);
------------------------ Extract fraction and exponent ------------------------
Frac <= nzero & usefulBits(11 downto 0);
Exp <= usefulBits(12 downto 12);
-------------------------------- Select regime --------------------------------
with rc  select  final_reg<= 
   "0" & lzCount when '1',
   NOT("0" & lzCount)  when '0',
   "-----" when others;
Reg <= final_reg;
Abs_in <= twos;
---------------------------- End of vhdl generation ----------------------------
end architecture;
