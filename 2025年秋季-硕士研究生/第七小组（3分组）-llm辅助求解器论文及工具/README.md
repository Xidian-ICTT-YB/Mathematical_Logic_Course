# 介绍 HeurAgenix原理，并演示其应用

## 小组成员

| 学号 | 姓名 |
| ---- | ---- |
| 25031212056 | 郭晨曦 |
| 25000300024 | 张佳佳 |
| 25031111060 | 周博   |

## 工作简介

- 张佳佳：介绍HeurAgenix的原理及PPT制作
- 周博：环境搭建及HeurAgenix解决TSP问题的工具演示
- 郭晨曦：环境搭建及HeurAgenix解决VRP问题和JSSP问题的工具演示

## 相关链接

- 代码开源链接：[GitHub - microsoft/HeurAgenix](https://github.com/microsoft/HeurAgenix)
- 论文地址： [ HeurAgenix: Leveraging LLMs for Solving Complex Combinatorial Optimization Challenges](https://arxiv.org/abs/2506.15196)

## 思考

HeurAgenix 采用了一种纯数据驱动的演化方式：系统先运行现有的启发式算法得到一个基础解，并对该解做若干次轻微扰动以优化效果。接着借助 LLMs 分析是哪些变动带来了改进，并自动提出进化策略。反复多轮执行该流程后，算法会在不同数据上迭代出多样化且更高效的启发式，整个过程无需任何领域先验或人工干预。
