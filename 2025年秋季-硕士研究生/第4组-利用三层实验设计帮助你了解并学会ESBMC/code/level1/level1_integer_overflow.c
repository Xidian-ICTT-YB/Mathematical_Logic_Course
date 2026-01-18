/**
 * level1_integer_overflow.c
 *
 * 验证目标：展示多阶段积分算法因为使用 32 位有符号整数导致累加溢出，
 * 通过 ESBMC 的 --overflow-check 把溢出编码成约束。
 */
#include <assert.h>
#include <limits.h>
#include <stdint.h>

#ifndef __ESBMC_assume
void __ESBMC_assume(_Bool cond);
#endif

extern int nondet_int(void);
extern unsigned nondet_uint(void);

/* 故障版本：直接在 int 上累加，既不检查范围也不使用更宽的类型。 */
static int faulty_integrator(int baseline, unsigned cycles)
{
  int total = baseline;
  for (unsigned step = 0; step < cycles; ++step)
  {
    total += baseline + (int)step * 64; /* 大 cycles 时立刻溢出 */
  }

  return total;
}

/* 修复版本：使用 64 位累加，并在写回 int 之前做范围裁剪。 */
static int safe_integrator(int baseline, unsigned cycles)
{
  long long total = baseline;
  for (unsigned step = 0; step < cycles; ++step)
  {
    total += baseline + (long long)step * 64;
  }

  if (total > INT_MAX)
  {
    total = INT_MAX;
  }
  else if (total < INT_MIN)
  {
    total = INT_MIN;
  }

  return (int)total;
}

int main(void)
{
  int baseline = nondet_int();
  unsigned cycles = nondet_uint();

  /* 让 baseline 足够大，使 20 次以内的累加就会溢出，缩小状态空间。 */
  __ESBMC_assume(baseline >= 100000000 && baseline <= 150000000);
  __ESBMC_assume(cycles >= 5 && cycles <= 20);

#ifdef USE_SAFE_VERSION
  int integrated = safe_integrator(baseline, cycles);
#else
  int integrated = faulty_integrator(baseline, cycles);
#endif

  /* 断言为占位符，真正的错误由 overflow check 触发。 */
  assert(integrated >= 0);
  return 0;
}

/*
ESBMC 命令 (bug 版本)：
  esbmc code/level1/level1_integer_overflow.c --unwind 25 --no-unwinding-assertions \
    --overflow-check
  --unwind 25 覆盖 cycles 的上界；配合 --no-unwinding-assertions 关闭默认的循环告警；
  --overflow-check 把有符号/无符号的算术溢出都转成 bit-vector 约束。

ESBMC 命令 (修复版本)：
  esbmc code/level1/level1_integer_overflow.c --unwind 25 --no-unwinding-assertions \
    --overflow-check -DUSE_SAFE_VERSION
  添加 -DUSE_SAFE_VERSION 后，积分在 64 位空间运行且回写前裁剪，因此无溢出反例。

解释稿：
1. 工程里常见“积分”操作是把每次采样叠加在一个 32 位累加器里。`baseline + step * 64`
   在 20 次以内就会溢出（baseline 已设到 1e8 级）。
2. 常规测试往往只跑几十次；`--unwind 25` 足以覆盖 cycles<=20 的所有路径，SMT 立刻找到溢出。
3. ESBMC 将每次加法建模成 bit-vector，并由 `--overflow-check` 生成约束，故障版本直接爆反例。
4. 修复方案的核心不是再加 if，而是用更宽的累加类型，并在写回时把范围限制成 API 约定；
   从数据结构层面消除特殊情况。
*/
