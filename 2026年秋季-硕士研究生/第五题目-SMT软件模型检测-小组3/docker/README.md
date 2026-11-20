# Docker 环境

正式实验使用的镜像是 `m01-bench-cpa:xml-smoke-cgroupfix`。

在原电脑上完成的检查：

| 项目 | 检查结果 |
| --- | --- |
| 镜像 ID | `sha256:88e2fae14ebf3d04612d2bd2e6fc9106931029ec6f038e4b1db9abf9e46ecf47` |
| 平台 | `linux/amd64` |
| Docker 显示的镜像大小 | 828.06 MB |
| 容器系统 | Ubuntu 20.04.6 LTS |
| Java | OpenJDK 1.8.0_452 |
| BenchExec | 3.26 |

镜像已使用 `docker image save` 导出到 `CPAchecker_SMT_archive/docker_image.tar`。

随后在同一台电脑使用 `docker image load` 成功加载，镜像 ID 与导出前一致。导出的 TAR 约 252 MB。

## 导入镜像

在 Docker Desktop 可以使用的 Windows 电脑上，打开 PowerShell：

```powershell
docker image load --input .\docker_image.tar
docker image inspect m01-bench-cpa:xml-smoke-cgroupfix --format '{{.Id}}'
```

以上命令在存放 `docker_image.tar` 的目录下执行，也可以换成文件绝对路径。

## 本目录中的文件

- `Dockerfile.*`：环境配置过程中使用过的各阶段 Dockerfile。
- `init.sh`：容器初始化脚本。
- `patch-benchexec-cgroupsv2.py`：针对 BenchExec 和 cgroups v2 的适配脚本。

实际构建过程和镜像标识见 `logs/cgroupsv2-build-20261116-202016.log`。历史检查记录还包含 CPAchecker 1.6.1-svn23022、MathSAT5 5.3.12 和 cgroups v2 的检查信息。
