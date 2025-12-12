// shortcut_counter.v
module counter(
  input clk,
  input rst_n, 
  input shortcut,  // <-- 我们的“随机”输入
  input [3:0] initval, // (在这个测试中未使用)
  output reg [3:0] out
);

  initial out = 'd0;

  // 状态逻辑
  always @(posedge clk) begin
    if (rst_n == 1'b0) begin
      out <= 4'b0000;
    end else if (shortcut == 1'b1) begin // “随机”捷径
      out <= 4'b1111; // 15
    end else begin
      out <= out + 1; // 正常计数
    end
  end

endmodule