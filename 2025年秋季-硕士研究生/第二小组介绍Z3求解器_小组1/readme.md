# Z3求解器

## 小组成员

|    学号     | 姓名   |
| :---------: | ------ |
| 25031212320 | 李小越 |
| 25031111101 | 张舒俞 |
| 25031111098 | 郭奕彤 |
| 25031212086 | 郝灿   |

## 工作介绍

郭奕彤：介绍了Z3求解器的基本原理，进行ppt制作；

张舒俞、李小越：基于python搭建Z3求解器的场景，然后介绍了Z3求解器的使用场景；

郝灿：进行ppt制作与讲解。

## 相关链接

[z3求解器(SMT)解各类方程各种逻辑题非常简单直观-CSDN博客](https://blog.csdn.net/as604049322/article/details/120279521)

[约束求解器-Z3_z3约束求解-CSDN博客](https://blog.csdn.net/yalecaltech/article/details/90575076?utm_medium=distribute.pc_relevant.none-task-blog-2~default~baidujs_baidulandingword~default-0-90575076-blog-120279521.235^v43^control&spm=1001.2101.3001.4242.1&utm_relevant_index=2)

## 思考

Z3求解器的核心优势：

Z3 基于一阶逻辑与 SMT（Satisfiability Modulo Theories），能够在统一框架下处理位向量、整数、实数、数组、布尔逻辑等多种约束类型；用户只需描述约束，无需关心如何求解，降低了复杂问题的建模成本。

使用Z3过程中，需要正确合理的进行约束描述，不合理的变量范围、冗余约束会影响求解效率，Z3求解器在约束规模过大、非线性复杂场景下的性能会明显降低。