architecture arch of PositMult_16_1_F0_uid2 is
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

   component RightShifterSticky28_by_max_15_F0_uid12 is
      port ( X : in  std_logic_vector(27 downto 0);
             S : in  std_logic_vector(3 downto 0);
             padBit : in  std_logic;
             R : out  std_logic_vector(27 downto 0);
             Sticky : out  std_logic   );
   end component;

signal sign_X :  std_logic;
signal reg_X :  std_logic_vector(4 downto 0);
signal exp_X :  std_logic_vector(0 downto 0);
signal frac_X :  std_logic_vector(12 downto 0);
signal z_X :  std_logic;
signal inf_X :  std_logic;
signal sign_Y :  std_logic;
signal reg_Y :  std_logic_vector(4 downto 0);
signal exp_Y :  std_logic_vector(0 downto 0);
signal frac_Y :  std_logic_vector(12 downto 0);
signal z_Y :  std_logic;
signal inf_Y :  std_logic;
signal sf_X :  std_logic_vector(5 downto 0);
signal sf_Y :  std_logic_vector(5 downto 0);
signal sign :  std_logic;
signal z :  std_logic;
signal inf :  std_logic;
signal frac_mult :  std_logic_vector(25 downto 0);
signal ovf_m :  std_logic;
signal normFrac :  std_logic_vector(26 downto 0);
signal sf_mult :  std_logic_vector(6 downto 0);
signal sf_sign :  std_logic;
signal nzero :  std_logic;
signal FinalExp :  std_logic_vector(0 downto 0);
signal RegimeAns_tmp :  std_logic_vector(4 downto 0);
signal RegimeAns :  std_logic_vector(4 downto 0);
signal reg_ovf :  std_logic;
signal FinalRegime :  std_logic_vector(4 downto 0);
signal input_shifter :  std_logic_vector(27 downto 0);
signal shift_offset :  std_logic_vector(3 downto 0);
signal pad :  std_logic;
signal shifted_frac :  std_logic_vector(27 downto 0);
signal S_bit_tmp :  std_logic;
signal tmp_ans :  std_logic_vector(14 downto 0);
signal LSB :  std_logic;
signal G_bit :  std_logic;
signal R_bit :  std_logic;
signal S_bit :  std_logic;
signal round :  std_logic;
signal result :  std_logic_vector(15 downto 0);
begin
--------------------------- Start of vhdl generation ---------------------------
------------------------------- Data Extraction -------------------------------
   X_decoder: PositDecoder_16_1_F0_uid4
      port map ( Input => X,
                 Abs_in => open,
                 Exp => exp_X,
                 Frac => frac_X,
                 Reg => reg_X,
                 Sign => sign_X,
                 inf => inf_X,
                 z => z_X);
   Y_decoder: PositDecoder_16_1_F0_uid8
      port map ( Input => Y,
                 Abs_in => open,
                 Exp => exp_Y,
                 Frac => frac_Y,
                 Reg => reg_Y,
                 Sign => sign_Y,
                 inf => inf_Y,
                 z => z_Y);
   -- Gather scale factors
sf_X <= reg_X & exp_X;
sf_Y <= reg_Y & exp_Y;
---------------------- Sign and Special Cases Computation ----------------------
sign <= sign_X XOR sign_Y;
z <= z_X OR z_Y;
inf <= inf_X OR inf_Y;
--------------- Multiply the fractions & add the exponent values ---------------
frac_mult <= frac_X * frac_Y;
   -- Adjust for overflow
ovf_m <= frac_mult(frac_mult'high);
with ovf_m  select  normFrac<= 
   frac_mult & '0' when '0',
   '0' & frac_mult when '1',
   "---------------------------" when others;
sf_mult <= (sf_X(sf_X'high) & sf_X) + (sf_Y(sf_Y'high) & sf_Y) + ovf_m;
sf_sign <= sf_mult(sf_mult'high);
---------------------- Compute Regime and Exponent value ----------------------
nzero <= '0' when frac_mult = "00000000000000000000000000" else '1';
   -- Unpack scaling factors
FinalExp <= sf_mult(0 downto 0);
RegimeAns_tmp <= sf_mult(5 downto 1);
   -- Get Regime's absolute value
with sf_sign  select  RegimeAns<=
   (NOT RegimeAns_tmp) + 1 when '1',
   RegimeAns_tmp when '0',
   "-----" when others;
   -- Check for Regime overflow
reg_ovf <= '1' when RegimeAns > "01110" else '0';
with reg_ovf  select  FinalRegime <=
   "01110" when '1',
   RegimeAns when '0',
   "-----" when others;
------------------------------- Packing Stage 1 -------------------------------
with sf_sign  select  input_shifter<=
   '0' & nzero    & FinalExp    & normFrac(24 downto 0) when '1',
   nzero & '0'    & FinalExp    & normFrac(24 downto 0) when '0',
   "----------------------------" when others;
with sf_sign  select  shift_offset <=
   FinalRegime(3 downto 0) - 1 when '1',
   FinalRegime(3 downto 0) when '0',
   "----" when others;
pad<= input_shifter(input_shifter'high);
   right_signed_shifter: RightShifterSticky28_by_max_15_F0_uid12
      port map ( S => shift_offset,
                 X => input_shifter,
                 padBit => pad,
                 R => shifted_frac,
                 Sticky => S_bit_tmp);
tmp_ans <= shifted_frac(27 downto 13);
--------------------- Packing Stage 2 - Unbiased Rounding ---------------------
LSB <= shifted_frac(13);
G_bit <= shifted_frac(12);
R_bit <= shifted_frac(11);
S_bit <= S_bit_tmp when shifted_frac(10 downto 0) = "00000000000" else '1';
with reg_ovf  select  round<=
   '0' when '1',
   G_bit AND (LSB OR R_bit OR S_bit) when '0',
   '-' when others;
with sign  select  result<=
   '0' & (tmp_ans + round) when '0',
   '1' & ((NOT(tmp_ans + round))+1) when '1',
   "----------------" when others;
R <= '1' & "000000000000000" when inf = '1' else 
   "0000000000000000" when z = '1' else
    result;
---------------------------- End of vhdl generation ----------------------------
end architecture;