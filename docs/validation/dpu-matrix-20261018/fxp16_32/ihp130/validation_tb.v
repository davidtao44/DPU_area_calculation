module area_validation_tb;
  reg clk=0;
  reg [15:0] a0,a1,a2,a3,b0,b1,b2,b3;
  reg [31:0] c,expected;
  wire [31:0] r;
  integer f,n,tested=0;
  FXP16_32_DPU_perf_top dut(
    .clk(clk),.A0_in(a0),.A1_in(a1),.A2_in(a2),.A3_in(a3),
    .B0_in(b0),.B1_in(b1),.B2_in(b2),.B3_in(b3),.C0_in(c),.R_out(r));
  initial begin
    f=$fopen("vectors.txt","r");
    if (!f) $fatal(1,"Missing vectors");
    while (!$feof(f)) begin
      n=$fscanf(f,"%h %h %h %h %h %h %h %h %h %h\n",
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
