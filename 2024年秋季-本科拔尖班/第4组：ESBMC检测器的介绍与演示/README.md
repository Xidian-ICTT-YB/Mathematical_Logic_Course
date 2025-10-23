# An introduction to ESBMC and its application

## 小组成员

| 学号 | 姓名 |
| ---- | ---- |
| 22009200777 | 周泽楷 |
| 22009290042 | 张继开 |
| 22009290027 | 褚思诺 |

## 工作简介

- 简要介绍了ESBMC的发展背景和设计思想，并展示了ESBMC的搭建过程。
- 通过两个简单的例子，展示了如何使用ESBMC。
- 分享了一些我们经过学习ESBMC相关知识之后的思考。

## 相关链接

- [ESBMC主页](https://github.com/esbmc/esbmc?tab=readme-ov-file)
- [The main website of ESBMC](https://ssvlab.github.io/esbmc/)

## 思考

对ESBMC的思考
	1.	优势
	•	结合符号执行和SMT求解，精准检测程序错误。
	•	支持上下文限制，适用于多线程程序和嵌入式系统验证。
	•	生成详细反例，便于错误定位和修复。
	2.	局限
	•	大型程序性能受限，状态空间可能爆炸。
	•	对现代C++特性和动态行为支持不足。
	•	高度依赖SMT求解器，复杂问题验证效率有限。
