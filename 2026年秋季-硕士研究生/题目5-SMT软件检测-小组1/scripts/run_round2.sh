#!/usr/bin/env bash
# Execute after the round-2 resource smoke test passes.
# 一般失败退出、未定义变量报错、管道前端失败可被识别。
set -euo pipefail
# 定位项目根目录。
base="$HOME/smt-project"
# 读取准备脚本生成的固定配置目录。
exp="$base/experiment/round2-50-900s"
# 进入CPAchecker根目录。
cd "$base/downloads/supplements-vstte/CPAchecker"
# 按四种算法依次检查/运行，算法之间串行。
for algorithm in bmc k-induction predicate impact; do
  # 确认对应的正式配置存在。
  test -f "$exp/$algorithm-50.xml"
done
# 时间戳创建新的结果位置；不复用上次结果。
run_dir="$base/results/round2-50-900s-$(date +%Y%m%d-%H%M%S)"
# 创建结果目录。
mkdir -p "$run_dir"
# 归档固定50任务、原30任务输入清单、抽样说明和准备脚本，不能随意删掉其中一个依赖。
cp "$exp/tasks.csv" "$exp/round1-tasks.csv" "$exp/sampling.txt" "$exp/prepare_round2.py" "$run_dir/"
# 归档四份实际执行的配置。
cp "$exp/"*-50.xml "$run_dir/"
# $0为当前脚本调用路径；复制正在执行的脚本以追溯运行方式。
cp "$0" "$run_dir/run_round2.sh"
# 开始收集环境信息。
{
  # 记录启动时间。
  date -Is
  # 记录Ubuntu发行版。
  cat /etc/os-release
  # 记录内核和体系结构。
  uname -a
  # 记录实际Java版本。
  java -version
  # 记录Python版本。
  python3 --version
  # 记录BenchExec版本。
  benchexec --version
  # 记录内存；此时尚未关闭swap，因此不能只看这份快照判断正式运行状态。
  free -h
  # 记录数据仓库实际提交。
  git -C "$base/benchmarks/sv-comp16" rev-parse HEAD
  # 记录XML和最终任务清单校验值。
  sha256sum "$run_dir/"*.xml "$run_dir/tasks.csv"
# 标准输出与标准错误都写入environment.txt。
} > "$run_dir/environment.txt" 2>&1
# 关闭本机/swapfile；这是运行资源条件的一部分，其他机器须确认设备。
sudo swapoff /swapfile
# 退出时尝试重新启用/swapfile；不保存原开关状态，也不保证强制杀进程/断电时执行。不要以sudo bash运行，否则$HOME可能变为root。
trap 'sudo swapon /swapfile' EXIT
# 记录关闭后的swap状态。
swapon --show > "$run_dir/swap-during.txt"
# 若仍有活动swap，文件非空则停止，避免不符合实验条件继续跑。
if test -s "$run_dir/swap-during.txt"; then
  echo 'Other swap devices are still enabled; stopping before experiments.'
  exit 1
fi
# 按四种算法依次检查/运行，算法之间串行。
for algorithm in bmc k-induction predicate impact; do
  mkdir -p "$run_dir/$algorithm"
  # 临时允许失败，以便显式获取并处理BenchExec退出码。
  set +e
  # 关闭容器隔离；同时只运行1个任务，但每任务仍可使用配置允许的2核。续行命令不能插入注释。
  benchexec --no-container --numOfThreads 1 \
    --outputpath "$run_dir/$algorithm/" \
    "$run_dir/$algorithm-50.xml" \
    2>&1 | tee "$run_dir/$algorithm/console.log"
  # 立刻取管道第一个命令BenchExec退出码，不使用tee的退出码。
  code=${PIPESTATUS[0]}
  # 恢复遇错停止。
  set -e
  # BenchExec异常退出则报告并停止后续算法；任务级TIMEOUT不等于BenchExec命令异常。
  if test "$code" -ne 0; then
    echo "BenchExec exited abnormally: $algorithm, code $code. Results: $run_dir"
    exit "$code"
  fi
done
# 四种配置的执行流程结束，不表示每个任务均成功。
echo "Round 2 complete. Results: $run_dir"
