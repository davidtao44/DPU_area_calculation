architecture arch of PositAdd is
   component PositDecoder_16_1_F0_uid4 is
      port ( Input : in  std_logic_vector(15 downto 0);
             Sign : out  std_logic;
             Reg : out  std_logic_vector(4 downto 0);
             Exp : out  std_logic_vector(0 downto 0);
             Frac : out  std_logic_vector(12 downto 0);
             z : out  std_logic;
             inf : out  std_logic;
             Abs_in : out  std_logic_vector(14 downto 0)   );
   end component;

   component PositDecoder_16_1_F0_uid8 is
      port ( Input : in  std_logic_vector(15 downto 0);
             Sign : out  std_logic;
             Reg : out  std_logic_vector(4 downto 0);
             Exp : out  std_logic_vector(0 downto 0);
             Frac : out  std_logic_vector(12 downto 0);
             z : out  std_logic;
             inf : out  std_logic;
             Abs_in : out  std_logic_vector(14 downto 0)   );
   end component;

   component RightShifterSticky15_by_max_15_F0_uid12 is
      port ( X : in  std_logic_vector(14 downto 0);
             S : in  std_logic_vector(3 downto 0);
             R : out  std_logic_vector(14 downto 0);
             Sticky : out  std_logic   );
   end component;

   component LZCShifter_15_to_15_counting_16_F0_uid14 is
      port ( I : in  std_logic_vector(14 downto 0);
             Count : out  std_logic_vector(3 downto 0);
             O : out  std_logic_vector(14 downto 0)   );
   end component;

   component RightShifterSticky18_by_max_15_F0_uid16 is
      port ( X : in  std_logic_vector(17 downto 0);
             S : in  std_logic_vector(3 downto 0);
             padBit : in  std_logic;
             R : out  std_logic_vector(17 downto 0);
             Sticky : out  std_logic   );
   end component;

signal sign_X :  std_logic;
signal reg_X :  std_logic_vector(4 downto 0);
signal exp_X :  std_logic_vector(0 downto 0);
signal frac_X :  std_logic_vector(12 downto 0);
signal inf_X :  std_logic;
signal X_abs :  std_logic_vector(14 downto 0);
signal sign_Y :  std_logic;
signal reg_Y :  std_logic_vector(4 downto 0);
signal exp_Y :  std_logic_vector(0 downto 0);
signal frac_Y :  std_logic_vector(12 downto 0);
signal inf_Y :  std_logic;
signal Y_abs :  std_logic_vector(14 downto 0);
signal sf_X :  std_logic_vector(5 downto 0);
signal sf_Y :  std_logic_vector(5 downto 0);
signal OP :  std_logic;
signal inf :  std_logic;
signal is_larger :  std_logic;
signal larger_sign :  std_logic;
signal larger_sf :  std_logic_vector(5 downto 0);
signal larger_frac :  std_logic_vector(12 downto 0);
signal smaller_frac :  std_logic_vector(14 downto 0);
signal sf_diff :  std_logic_vector(6 downto 0);
signal diff_msb :  std_logic_vector(5 downto 0);
signal offset :  std_logic_vector(5 downto 0);
signal sup_offset :  std_logic_vector(1 downto 0);
signal shift_saturate :  std_logic;
signal frac_offset :  std_logic_vector(3 downto 0);
signal shifted_frac :  std_logic_vector(14 downto 0);
signal sticky :  std_logic;
signal add_frac :  std_logic_vector(16 downto 0);
signal ovf_frac :  std_logic;
signal useful_frac :  std_logic_vector(12 downto 0);
signal G_tmp :  std_logic;
signal R_tmp :  std_logic;
signal S_tmp :  std_logic;
signal frac_GR :  std_logic_vector(14 downto 0);
signal lzCount :  std_logic_vector(3 downto 0);
signal normFrac :  std_logic_vector(14 downto 0);
signal sf_add :  std_logic_vector(5 downto 0);
signal nzero :  std_logic;
signal FinalExp :  std_logic_vector(0 downto 0);
signal RegimeAns_tmp :  std_logic_vector(4 downto 0);
signal reg_sign :  std_logic;
signal FinalRegime :  std_logic_vector(4 downto 0);
signal input_shifter :  std_logic_vector(17 downto 0);
signal shift_offset :  std_logic_vector(3 downto 0);
signal pad :  std_logic;
signal shifted_ans :  std_logic_vector(17 downto 0);
signal S_bit_tmp :  std_logic;
signal tmp_ans :  std_logic_vector(14 downto 0);
signal LSB :  std_logic;
signal G_bit :  std_logic;
signal R_bit :  std_logic;
signal remain :  std_logic_vector(0 downto 0);
signal S_bit :  std_logic;
signal round :  std_logic;
signal result :  std_logic_vector(15 downto 0);
begin
--------------------------- Start of vhdl generation ---------------------------
------------------------------- Data Extraction -------------------------------
   X_decoder: PositDecoder_16_1_F0_uid4
      port map ( Input => X,
                 Abs_in => X_abs,
                 Exp => exp_X,
                 Frac => frac_X,
                 Reg => reg_X,
                 Sign => sign_X,
                 inf => inf_X,
                 z => open);
   Y_decoder: PositDecoder_16_1_F0_uid8
      port map ( Input => Y,
                 Abs_in => Y_abs,
                 Exp => exp_Y,
                 Frac => frac_Y,
                 Reg => reg_Y,
                 Sign => sign_Y,
                 inf => inf_Y,
                 z => open);
   -- Gather scale factors
sf_X <= reg_X & exp_X;
sf_Y <= reg_Y & exp_Y;
---------------------- Sign and Special Cases Computation ----------------------
OP <= sign_X XOR sign_Y;
inf <= inf_X OR inf_Y;
---------------------- Compare operands and adjust values ----------------------
is_larger<= '1' when X_abs > Y_abs else '0';
with is_larger  select  larger_sign <= 
   sign_X when '1',
   sign_Y when '0',
   '-' when others;
with is_larger  select  larger_sf <= 
   sf_X when '1',
   sf_Y when '0',
   "------" when others;
with is_larger  select  larger_frac <= 
   frac_X when '1',
   frac_Y when '0',
   "-------------" when others;
with is_larger  select  smaller_frac <= 
   (frac_Y & "00")  when '1',
   (frac_X & "00")  when '0',
   "---------------" when others;
sf_diff <= (sf_X(sf_X'high) & sf_X) - (sf_Y(sf_Y'high) & sf_Y);
diff_msb <= (others => sf_diff(sf_diff'high));
offset <= (diff_msb XOR sf_diff(5 downto 0)) + sf_diff(sf_diff'high);
sup_offset <= offset(5 downto 4);
shift_saturate <= '0' when sup_offset = "00" else '1';
with shift_saturate  select  frac_offset <=
   "1111" when '1',
   offset(3 downto 0) when '0',
   "----" when others;
------------------------------- Align mantissas -------------------------------
   mantissa_shifter: RightShifterSticky15_by_max_15_F0_uid12
      port map ( S => frac_offset,
                 X => smaller_frac,
                 R => shifted_frac,
                 Sticky => sticky);
---------------------------- Add aligned mantissas ----------------------------
with OP  select  add_frac <= 
   ('0' & larger_frac & "000") + ('0' & shifted_frac & sticky) when '0',
   ('0' & larger_frac & "000") - ('0' & shifted_frac & sticky) when '1',
   "-----------------" when others;
ovf_frac <= add_frac(add_frac'high);
with ovf_frac  select  useful_frac <=
   add_frac(16 downto 4) when '1',
   add_frac(15 downto 3) when '0',
   "-------------" when others;
with ovf_frac  select  G_tmp <=
   add_frac(3) when '1',
   add_frac(2) when '0',
   '-' when others;
with ovf_frac  select  R_tmp <=
   add_frac(2) when '1',
   add_frac(1) when '0',
   '-' when others;
with ovf_frac  select  S_tmp <=
   add_frac(1) OR add_frac(0) when '1',
   add_frac(0) when '0',
   '-' when others;
frac_GR <= useful_frac & G_tmp & R_tmp;
   -- Normalization of add_frac
   align_mantissa: LZCShifter_15_to_15_counting_16_F0_uid14
      port map ( I => frac_GR,
                 Count => lzCount,
                 O => normFrac);
   -- Adjust exponent
sf_add <= larger_sf + ovf_frac - lzCount;
---------------------- Compute Regime and Exponent value ----------------------
nzero <= '0' when frac_GR = "000000000000000" else '1';
   -- Unpack scaling factors
FinalExp <= sf_add(0 downto 0);
RegimeAns_tmp <= sf_add(5 downto 1);
reg_sign <= RegimeAns_tmp(RegimeAns_tmp'high);
   -- Get Regime's absolute value
with reg_sign  select  FinalRegime <=
   (NOT RegimeAns_tmp) + 1 when '1',
   RegimeAns_tmp when '0',
   "-----" when others;
------------------------------- Packing Stage 1 -------------------------------
with reg_sign  select  input_shifter<=
   '0' & nzero    & FinalExp    & normFrac(13 downto 0) & S_tmp when '1',
   nzero & '0'    & FinalExp    & normFrac(13 downto 0) & S_tmp when '0',
   "------------------" when others;
with reg_sign  select  shift_offset <=
   FinalRegime(3 downto 0) - 1 when '1',
   FinalRegime(3 downto 0) when '0',
   "----" when others;
pad<= input_shifter(input_shifter'high);
   right_signed_shifter: RightShifterSticky18_by_max_15_F0_uid16
      port map ( S => shift_offset,
                 X => input_shifter,
                 padBit => pad,
                 R => shifted_ans,
                 Sticky => S_bit_tmp);
tmp_ans <= shifted_ans(17 downto 3);
--------------------- Packing Stage 2 - Unbiased Rounding ---------------------
LSB <= shifted_ans(3);
G_bit <= shifted_ans(2);
R_bit <= shifted_ans(1);
remain <= shifted_ans(0 downto 0);
S_bit <= S_bit_tmp when remain = "0" else '1';
round <= G_bit AND (LSB OR R_bit OR S_bit);
with larger_sign  select  result<=
   '0' & (tmp_ans + round) when '0',
   '1' & ((NOT(tmp_ans + round))+1) when '1',
   "----------------" when others;
R <= '1' & "000000000000000" when inf = '1' else 
   "0000000000000000" when nzero = '0' else
    result;
---------------------------- End of vhdl generation ----------------------------
end architecture;