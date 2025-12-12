// load_counter.v
module counter(
  input clk,
  input rst_n, 
  input load,      // 新增：加载使能信号
  input [3:0] initval, // 现在用作加载数据
  output reg [3:0] out
);

  initial out = 'd0;

  always @(posedge clk) begin
    if (rst_n == 1'b0) begin
      out <= 4'b0000;
    end else if (load == 1'b1) begin // 优先级高于计数
      out <= initval; 
    end else begin
      out <= out + 1;
    end
  end

endmodule