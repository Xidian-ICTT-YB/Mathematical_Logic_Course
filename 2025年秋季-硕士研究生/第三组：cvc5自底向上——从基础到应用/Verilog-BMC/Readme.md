## Verilog-BMC

Verilog有界模型检查（Bounded Model Checking, BMC）。实现了在Verilog时序逻辑中，对输出变量的简单断言。

特点：

- 将Verilog转换为BTOR2中间格式，解析BTOR2文件，并使用PySMT建立模型执行检查。
- 具体SMT求解器使用cvc5。
- 自定义testbench，用于对模块输入变量进行约束，以及定义要检查的规则。

Verilog-BMC目录结构：

```txt
Verilog-BMC
├── proj
│   ├── dut
│   │   ├── xxx.v
│   │   └── xxx.btor2
│   ├── tb
│   │   └── testxx.txt
│   ├── bmc.py (执行BMC)
│   ├── convert_to_btor2.py (将Verilog转为BTOR2)
│   ├── main.py (主程序)
│   ├── parse_btor.py (解析BTOR2)
│   ├── property_parser.py  (解析testbench)
│   └── testbench_loader.py (解析testbench)
├── doc
│   ├── Verilog-BMC.md (原理介绍)
│   └── impl.md
└── Readme.md
```

---

## 