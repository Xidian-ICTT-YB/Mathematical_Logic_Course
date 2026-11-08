#!/usr/bin/env bash
# 原有用法注释：三个位置参数分别为工具、配置、新结果目录。
# Usage: bash run_experiments.sh CPA_DIRECTORY CONFIG_DIRECTORY NEW_RESULT_DIRECTORY
# -e一般命令失败停止；-u未定义变量报错；pipefail让管道前端失败也被识别。
set -euo pipefail
# 检查参数个数；$#为个数，-ne表示不等于。
if [ "$#" -ne 3 ]; then
  # 参数错误时输出正确用法。
  echo 'Usage: bash run_experiments.sh CPA_DIRECTORY CONFIG_DIRECTORY NEW_RESULT_DIRECTORY'
  # 非零退出码2表示调用参数有问题。
  exit 2
# 结束参数检查。
fi
# 命令替换取得CPAchecker绝对路径；$1是第一个参数，双引号保护空格。
cpa=$(realpath "$1")
# 取得配置目录绝对路径；$2是第二个参数。
config=$(realpath "$2")
# 取得新结果目录绝对路径；-m允许目标尚不存在。
result=$(realpath -m "$3")
# 要求结果路径不存在；否则打印提示并退出，防止覆盖原实验。
test ! -e "$result" || { echo 'Result directory exists; stopping.'; exit 1; }
# 检查CPAchecker的scripts/cpa.sh存在。
test -f "$cpa/scripts/cpa.sh"
# 循环检查四份配置均存在；任一缺失即停止。
for alg in bmc k-induction predicate impact; do test -f "$config/$alg.xml"; done
# 查找benchexec命令；不等于已经完成cgroups权限检查。
command -v benchexec
# 原有提示：匹配实验需先关闭swap、结束后恢复；本脚本不自动操作swap。
# To match the experiment, disable swap before execution and restore it afterwards.
# swapon列出现有交换空间；-n判断输出非空，存在活动swap就停止。
if test -n "$(swapon --show --noheadings)"; then
  # 提示由操作者关闭相应swap。
  echo 'Swap is active. Disable the intended swap device before running.'
  # 退出，避免不符合条件时继续实验。
  exit 1
# 结束swap检查。
fi
# 创建结果目录和所需父目录。
mkdir -p "$result"
# 复制配置到结果目录归档；后面运行这份副本。
cp "$config/"*.xml "$result/"
# 开始命令组，将环境信息统一重定向到文件。
{
  # 记录ISO格式时间。
  date -Is
  # 记录系统和内核信息。
  uname -a
  # 记录Java版本，其输出通常在标准错误中。
  java -version
  # 记录BenchExec版本。
  benchexec --version
  # 记录内存和swap概况；-h表示易读单位。
  free -h
  # 记录交换空间启用情况。
  swapon --show
# 标准输出写入environment.txt，2>&1把标准错误也合并进去。
} > "$result/environment.txt" 2>&1
# 切换到CPAchecker根目录。
cd "$cpa"
# 按顺序运行四种配置，四种算法不同时启动。
for alg in bmc k-induction predicate impact; do
  # 创建当前算法的结果子目录。
  mkdir -p "$result/$alg"
  # 调用BenchExec：不使用容器；只并发1个任务；输出到对应目录。下一行是同一命令，不能在续行之间插注释。
  benchexec --no-container --numOfThreads 1 --outputpath "$result/$alg/" \
    "$result/$alg.xml" 2>&1 | tee "$result/$alg/console.log"
# 结束四算法循环。
done
# 显示四个配置执行结束；不表示每个任务都验证成功。
echo "Completed 4 algorithm configurations. Results: $result"
