# 课堂演示

这套演示沿着真实保存的实验记录，解释四种算法的判定、`pcd` 的耗时差异和 `vhost` 的错误路径。默认入口读取证据，现场可在已有 Linux 服务器上另执行一次短任务。

## 离线证据演示

在本项目根目录打开终端，即同时包含总README、`demo`、`scripts`和`experiment-v2`的main目录。需要 Python 3.8 或更高版本，仅使用标准库。macOS 和 Linux 使用 `python3`，Windows 可将命令开头替换为 `py -3`。

```bash
python3 demo/run.py --check
python3 demo/run.py --summary
python3 demo/run.py --case pcd
python3 demo/run.py --case vhost
```

一次显示全部内容可运行以下命令。

```bash
python3 demo/run.py --all
```

`--check` 会校验774个主实验和重复实验文件、50个程序及其属性文件、3个轨迹文件，并检查248次运行的计划、逐次结果、汇总、日志判定和CPU计时。校验失败会显示具体文件，并以非零状态退出。

`--summary` 会重新解析200份日志，与逐次结果及保存的汇总核对，然后统计四种配置的结果。CPU时间采用日志中的 `Total CPU time for CPAchecker`，缺失值保留为空。

`--case pcd` 会展示四轮原始CPU时间及抽象统计。每轮抽象调用数均为9700，但谓词抽象命中5873次缓存，实际执行3825次布尔抽象；IMPACT缓存命中为0，执行9698次布尔抽象。两种完整配置的计算量与耗时存在对应差异，单个参数的因果作用需要进一步对照。

`--case vhost` 会检查CBMC确认信息及最终FALSE，展示从模型锁状态初始化到错误函数的原始轨迹。这个补充导出运行来自独立批次。

从其他目录运行时，可以指定提交包路径。

```bash
python3 /path/to/submission/demo/run.py --root /path/to/submission --all
```

## 在已有服务器上执行一次新验证

`live-schedule.json` 固定选择 `pata_marvell` 的谓词抽象配置，共一次运行。此前该案例通常数秒完成，本次实际耗时由服务器状态决定，CPU软时限仍为900秒。

入口复用 `scripts/run_v2.py`。服务器应为 Linux x86-64，至少允许两个逻辑CPU，并已安装历史 CPAchecker 工件和 Java 8。所需目录如下。

```text
项目根目录/
├── tools/java8/bin/java
├── tools/supplements-vstte/CPAchecker/
├── experiment-v2/inputs/c/
├── experiment-v2/design-20261111/tasks50-frozen.json
├── scripts/run_v2.py
├── scripts/v2_evidence.py
└── demo/
    ├── run.py
    └── live-schedule.json
```

历史工具来自论文官方补充包。提交包内有输入程序与脚本，工具和Java按上述目录部署。[论文补充材料](https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html)

在已配置好的项目中先运行预检查。

```bash
python3 demo/run.py --root . --live
```

预检查应显示 `50 hashed tasks; 1 scheduled runs`。确认当时服务器资源可用后，使用执行参数启动验证。

```bash
python3 demo/run.py --root . --live --execute
```

运行器为这次演示创建新的 `results/v2-*` 目录，终端打印实际判定和输出路径。此次新增记录用于说明工具操作。正式结果只统计50个任务的200次运行。

在 macOS 或 Windows 上使用 `--live` 时，程序会说明需要 Linux 服务器。在 Linux 上缺少工具时，程序会显示缺失文件的准确位置。

### 完整批次入口

在完成上述工具部署的 Linux 项目根目录，可以先检查50题、200次的计划。`--root .` 会使用当前目录作为项目根目录。

```bash
python3 scripts/run_v2.py --root . --schedule experiment-v2/design-20261111/coverage200-schedule.json
```

检查应显示 `200 scheduled runs`。执行新的完整覆盖批次时加上 `--run`。

```bash
python3 scripts/run_v2.py --root . --schedule experiment-v2/design-20261111/coverage200-schedule.json --run
```

四轮重复实验使用另一份固定计划，检查应显示 `48 scheduled runs`。

```bash
python3 scripts/run_v2.py --root . --schedule experiment-v2/design-20261111/case-repeat-schedule.json
```

确认计划和资源可用后，同样加入 `--run` 执行。默认参数为900秒CPU软时限、1000秒硬保护、10000M Java堆、15GB进程组RSS监控阈值及2000秒墙钟保护，任务串行运行。共享服务器上的CPU亲和性和RSS轮询仍有报告中说明的计量限制。

新批次输出在 `results/v2-*`。本演示的 `--summary` 和 `--case` 指向随包保存的正式批次，执行新批次后的结果可从终端打印的目录内 `results.json`、各次 `result.json` 和 `run.log` 查看。

## 补充操作示例

独立的pata_marvell谓词抽象演示记录位于 `evidence/live-demo/`，包含命令、日志和结果。它用于说明工具操作，不计入50任务正式结果或性能表。
