# DrvHorn：引用计数缺陷检测的 CHC 归约复现

课程：计算机科学使用的数理逻辑  
学期：2026 秋  
组别：第一组

## 小组成员

| 姓名   | 学号        | 主要分工                          |
| ------ | ----------- | --------------------------------- |
| 章九章 | 24029100256 | 论文原理解释、PPT与讲稿制作、汇报 |
| 王通   | 24039100413 | 分析真实缺陷案例                  |
| 曹润初 | 24049200173 | 分析误报案例                      |
| 程广越 | 24009290025 | 分析无缺陷案例                    |

## 工具来源

- 官方 GitHub 仓库：<https://github.com/joehattori/drvhorn>
- 论文：Joe Hattori, Naoki Kobayashi, Ken Sakayori.  
  *Automatic Detection of Reference Counting Bugs in Linux Kernel Drivers*.  
  arXiv:2605.13246v2 [cs.CR]. The University of Tokyo.  
  <https://arxiv.org/abs/2605.13246>
- Linux 修复提交示例：`torvalds/linux` commit `5d8e2971e817bb64225fc0b6327a78752f58a9aa`

DrvHorn、SeaHorn、Z3 与 LLVM 的原始代码来自其各自作者。本目录提交课程 PPT、运行日志、三案例分析报告。

## 任务简介

本项目复现 DrvHorn 的引用计数缺陷检测流程，核心思想是**将引用计数验证归约为 LLVM 断言检查问题**：

1. **入口改造**：把驱动入口改造为“调用初始化函数 → 失败则进入 `drvhorn.fail`”；
2. **断言插入**：在 `drvhorn.fail` 中插入受跟踪对象的计数断言（`refcount == 1`，即失败路径上 ΔRC == 0）；
3. **内核建模与切片**：建模 device / fwnode / devm 接口，切片保留与 refcount 相关的路径，剥离无关操作；
4. **后端求解**：断言问题交给 **SeaHorn**，归约为 **CHC**，由 SMT 求解器判定断言是否可被违反；
5. **结果判定**：`sat` 表示存在反例路径；`unsat` 表示该路径上断言不可违反（需检查是否为空验证）。

项目完成了官方 `scripts/eval.sh` 所列 **17 个 platform driver 的轻量评测**，并重点分析了三个单案例：真实缺陷 `tpm_bios_measurements_ops`（TP）、无缺陷 `ns2_led_driver`（TN）、误报 `acpi_wmi_driver`（FP）。

## 运行环境

- Ubuntu 24.04.1 LTS（WSL2，`systemd=true`）
- Docker 29.1.3（apt 包 `docker.io`），containerd 2.2.1，runc 1.3.4
- 作者镜像：`joehattori/drvhorn:latest`，manifest digest `sha256:536168e391d7c08c8247276dafc4a518ac68a1a5fcea44068f5c03b5b345f80c`
  - 压缩大小约 2.18 GB；解压占用约 8.73 GB
  - 内置 `simple_kernel.bc`（89 MB，裁剪版内核 bitcode，**非完整 v6.6 `allyesconfig`**）
  - 工具链：`sea` / `seapp` / `seaopt` / `seahorn` / `z3`
- 源码获取：`codeload.github.com/joehattori/drvhorn`（直连 GitHub `git clone` 超时，改用 codeload 下载 tar.gz）
- 镜像获取：Docker Hub 直连超时，经镜像站 `docker.1ms.run` 拉取后 `docker tag` 重命名

## 实际结果

### 17 驱动批量评测（官方 `eval.sh`）

- 单容器串行执行，墙钟耗时 **6 分 12 秒**；
- 结果分布：`sat` 7 例，`unsat` 10 例；
- **16/17 与预期一致**，唯一不符为 `acpi_wmi_driver`（预期 `unsat`，实际 `sat`），即官方 README 明确标注的假阳性样本；
- **3 例 `unsat` 属空验证**：`ged_driver`、`platform_driver`、`xvtc_driver`（日志含 `WARNING: no assertion was found`），其 `unsat` 不能作为“无缺陷”的证据。

## 工具搭建后的主要思考

1. **工具复现的主要成本来自环境与镜像获取链路的一致性。** Docker Hub 直连超时、`git clone` 超时、`docker` 组权限需 `newgrp` 或 `sg docker -c` 借组，这些工程问题会直接影响能否复现，而不只是分析器本身能否编译。最终通过固定 digest 与镜像站拉取保证了字节级一致性。

2. **归约设计的关键是把“生命周期”转成“断言”。** DrvHorn 不直接证明 refcount 正确，而是利用驱动接口的规律（失败时必须释放已获取资源），把问题转化为 LLVM bitcode 上的断言检查。断言以 `counter == 1` 表达模型基线，同时覆盖漏 put（>1，内存泄漏）与多 put（==0，UAF）两类缺陷。后端可替换是这一设计的重要收益。

3. **切片与建模是“精度”与“规模”的两次取舍。** 切片把无关操作与复杂函数体（如 `seq_open`）替换为非确定值，使求解器能同时探索成功/失败分支；建模把硬件接口（如 `of_node`）抽象为简化替身，降低求解复杂度。但一旦简化不够精准，就会引入假阳性。

4. **`sat` / `unsat` 必须在语义层次上解读。** `sat` 表示建模+切片后的程序中存在违反断言的可达路径，它既可能是真实缺陷（如 `tpm_bios`），也可能源于模型失真（如 `acpi_wmi`）；`unsat` 需先排除空验证（`no assertion was found`），否则不能作为无缺陷证据。求解器的结论仅在当前程序模型下成立。

5. **误报归因需要反例轨迹，而本次获取失败。** `acpi_wmi_driver` 的误报最可能与 `SetupEntrypoint.cc:40` 作者注释所指出的 `of_node` 建模缺陷有关（机制可通：未初始化栈内存充当固件节点，计数断言失效），但 `--cex` 尝试因 `sea` 阶段串联失效而在 280 秒内未完成，因此归因只能停留在“最可能”，不能写成已确认结论。这一点也提示：报告必须区分**模型内可满足**与**真实环境可触发**。

6. **切片非健全性与漏报是同一枚硬币的两面。** 论文指出的 27 个切片假阳性与 `d029ede` 漏报案例同源——均源于切片不考虑间接信息流。这提示后续若改进，应优先扩展切片的依赖跟踪，而非单纯替换后端求解器。

