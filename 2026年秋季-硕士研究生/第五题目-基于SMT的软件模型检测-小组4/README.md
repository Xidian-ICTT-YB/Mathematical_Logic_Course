# 基于 SMT 的软件模型检测

> **数理逻辑课程大作业**  
> 课题：基于 SMT 的软件模型检测四种算法对比复现（Beyer & Dangl, VSTTE 2016）

---

## 一、小组成员信息

| 序号 | 姓名 | 学号 |
|---:|---|---|
| 1 | 汪鑫欣| 26181214293 | 
| 2 | 曾靖 | 26181214470 | 
| 3 | 唐晨阳 | 26181214686 | 
| 4 | 肖禄祎 | 26181214406 |

---

## 二、工具与参考资源主页

- **核心模型检测工具（CPAchecker）GitHub 仓库**：<https://github.com/sosy-lab/cpachecker>
- **CPAchecker 官方网站**：<https://cpachecker.sosy-lab.org/>
- **复现论文与官方补充材料主页（VSTTE 2016）**：<https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html>
- **基准数据集仓库（SV-COMP 2016 `DeviceDriversLinux64`）**：<https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks>

---

## 三、文件夹目录说明

```text
第五题目-基于SMT的软件模型检测-小组4/
├── .gitignore                                          # Git 忽略规则
├── README.md                                           # 本说明文档（含成员信息、网址与搭建思考）
├── 项目汇报PPT.pptx                                    # 汇报 PPT
├── 工具讲解视频.mp4                                    # 工具讲解与演示视频
├── 数理逻辑课程实验报告.docx                           # 作业 Word 实验报告
├── scripts/
│   ├── docker/Dockerfile                               # linux/amd64 + OpenJDK 8 实验容器定义
│   ├── select_tasks.py                                 # 从 DeviceDriversLinux64 筛选 28 个任务
│   ├── run_experiments.py                              # 多容器并发运行 4 种 CPAchecker 配置
│   ├── parse_results.py                                # 解析 run.log 与 Statistics.txt 生成汇总
│   ├── make_trace_excerpt.py                           # 提取精简反例轨迹与 SMT 模型赋值
│   └── build_report.py                                 # 生成 Markdown 复现报告
└── demo/
    ├── run.sh                                          # 一键运行脚本（check / setup / smoke / full / report）
    └── smoke_results/                                  # 2 任务 × 4 算法冒烟测试运行产物示例
```

---

## 四、工具搭建与实验复现后的主要思考

1. **跨架构原生依赖与容器化隔离的必要性**：  
   论文官方补充包里的 `CPAchecker 1.6.8-vstte` 依赖 `MathSAT5` 的 x86-64 ELF 动态库（`libmathsat5j.so`），在 Apple Silicon 等 ARM 宿主机上无法直接加载。我们通过构建 `--platform linux/amd64` 的 `ubuntu:20.04 + OpenJDK 8` 容器来封装运行环境，不仅解决了动态库兼容问题，还保证了 112 次实验的 CPU 核数、内存上限与隔离输出完全一致。

2. **工具配置细节对验证结论的决定性影响**：  
   在早期调试中，我们尝试给 `k-Induction` 外层统一叠加 `CBMC` 反例二次确认，结果导致并行子线程抛出异常并返回虚假的 `UNKNOWN`。对照论文补充包的 `test-sets/*.xml` 去掉外层包装后，`k-Induction` 才恢复正常（`T02_bgrt` 从异常转为 5.4s 证真 `TRUE`）。这让我们深刻体会到，做自动化验证实验时必须严格区分「工具配置异常」与「算法本身的能力边界」。

3. **「找缺陷」与「证安全」在数理逻辑量词结构上的本质差异**：  
   实验统计显示，`Predicate`（24/28，平均 14.3s）和 `Impact`（23/28，平均 17.9s）在证明安全上远超 `BMC`（仅 2/28，平均 62.9s，20 次超时）。原因在于找 bug 是**存在性问题**（只需找到一条到达 `__VERIFIER_error()` 的可行路径，如 `T23_kernelcapi` 经 1 次精化 8.2s 即报 `FALSE`），而证明无限循环驱动的安全性是**全称问题（∀k）**。`BMC` 即使每轮都找不到反例，只要无法通过 `checkBoundingAssertions` 证明循环已完全展开（如 `T02_bgrt` 耗时 79.19s 仍 `SAT`），就只能不断增大 `k` 直至超时；而 `k-Induction` 与插值抽象通过构造循环不变式（如 `ldv_mutex == 1`），把无限状态空间折叠为有限证明。

4. **统计口径的严谨性：绝不把 `UNKNOWN` 混作安全**：  
   在跑真实 Linux 内核驱动时，部分代码经 CIL 预处理后包含递归调用或指针复杂循环，CPAchecker 1.6.8 会明确输出 `Unsupported feature (recursion)` 或因容器 5.85 GB 内存上限发生 OOM。我们在 `parse_results.py` 中严格依据日志区分「CPU 时限耗尽（`TIMEOUT`）」与「工具限制/资源溢出（`UNKNOWN`）」，保证 112 次运行中所有 `TRUE` 与 `FALSE` 结论 100% 真实可信。

---

## 五、快速复现命令

```bash
bash demo/run.sh check   # 检查 Docker、amd64 容器支持与脚本完整性
bash demo/run.sh setup   # 自动构建镜像、下载论文补充包并稀疏检出 sv-comp16 驱动源码
bash demo/run.sh smoke   # 冒烟测试（T02_bgrt 与 T23_kernelcapi × 4 算法，约 2 分钟）
bash demo/run.sh full    # 完整运行 28 任务 × 4 算法（112 次）并生成统计与报告
```
