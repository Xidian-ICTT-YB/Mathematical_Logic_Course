# 实验环境

正式实验在 Windows 11 上通过 Docker Desktop 和 WSL2 运行，容器使用 Ubuntu 20.04.6 LTS。

| 工具或设置 | 本次使用情况 |
| --- | --- |
| CPAchecker | 1.6.1-svn23022 |
| MathSAT5 | 5.3.12 |
| Java | OpenJDK 8，现场检查为 1.8.0_452 |
| Python | 3.8.10 |
| BenchExec | 3.26 |
| Docker | Docker Desktop；使用 cgroups v2 |
| 镜像 | `m01-bench-cpa:xml-smoke-cgroupfix` |
| 容器根内存上限 | 8 GiB |

每次正式运行的限制：2 核 CPU、6000 MB 内存、Java 堆 4000 MB、CPU 软限制 900 秒、硬限制 1200 秒；BenchExec 同时运行 1 个任务，运行时关闭网络。具体参数以 `configs/formal-20261117-141308/` 为准。

镜像已在原电脑导出并重新加载成功。2026 年 11 月 18 日再次检查了 Ubuntu、Java、BenchExec 版本，均符合上述记录。CPAchecker 和 MathSAT5 的具体安装位置仍可从早期环境日志及原运行脚本进一步核对；本次没有在另一台电脑上重新执行完整实验。

镜像和使用说明见 `docker/README.md`，运行相关日志在 `logs/`。完整原始结果单独保存在 `CPAchecker_SMT_archive/full_results.7z`。
