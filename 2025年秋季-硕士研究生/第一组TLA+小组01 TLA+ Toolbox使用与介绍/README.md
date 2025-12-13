# TLA+ 的介绍与使用方法展示

## 小组成员

| 学号 | 姓名 |
| ---- | ---- |
| 25031212253 | 黄智新 |
| 25031212226 | 雷梓翊 |
| 25031212258 | 杜文森 |


## 工作简介

- 介绍了什么是TLA+，为什么选择TLA+，TLA+的核心概念
- 主要通过囚犯谜题和咖啡馆问题对TLA+ ToolBox工具的使用进行了展示
- 通过分析两个案例的代码，介绍了TLA+的核心逻辑



## 相关链接

[TLA+ 官方网站](https://lamport.azurewebsites.net/tla/tla.html)   

[TLA+ 教程](https://learntla.com/)  

[TLA+官方仓库](https://github.com/tlaplus/tlaplus)

[TLA+官方示例仓库](https://github.com/tlaplus/Examples)

[TLA+ Toolbox工具下载](https://lamport.azurewebsites.net/tla/toolbox.html)

## 思考

在使用 TLA+ 的过程中可以体会到，它关注的并不是“代码如何实现”，而是“系统在所有可能情况下是否正确”。通过对状态、不变式和行为的形式化建模，TLA+ 促使设计者在实现之前就澄清系统的关键假设和逻辑约束，尤其适合发现并发和非确定性场景下隐藏的设计缺陷。虽然形式化建模本身具有一定成本，也难以覆盖全部系统细节，但在核心算法和关键协议的设计阶段，TLA+ 为系统正确性提供了一种比传统测试更根本的保障。