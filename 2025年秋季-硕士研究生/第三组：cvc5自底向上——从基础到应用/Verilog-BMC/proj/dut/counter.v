// counter.v
module counter(
  input clk,
  input rst_n, // 低电平有效复位
  input [3:0] initval, // (在这个测试中未使用)
  output reg [3:0] out
);

  initial out = 'd0;

  always @(posedge clk) begin
    if (rst_n == 1'b0) begin
      out <= 4'b0000;
    end else begin
      out <= out + 1;
    end
  end

endmodule