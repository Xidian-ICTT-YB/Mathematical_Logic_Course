/**
 * level1_array_bounds.c
 *
 * 验证目标：展示滑动窗口式的数组访问在循环展开不足时会藏着越界，
 * 需要使用 ESBMC 的 --unwind 与 --no-unwinding-assertions 控制循环深度。
 */
#include <assert.h>
#include <stddef.h>

#ifndef __ESBMC_assume
void __ESBMC_assume(_Bool cond);
#endif

extern int nondet_int(void);

#define SENSOR_COUNT 8
static const int sensor_table[SENSOR_COUNT] = {12, 18, 7, 25, 9, 15, 11, 5};

/* 故障版本：缺少上界检查，并且循环使用 <=，导致 anchor 靠近尾部时越界。 */
static int faulty_window_sum(int anchor)
{
  const int dynamic_window = 2 + (anchor & 1); /* window 取决于输入，需 --unwind 5 */
  int sum = 0;

  for (int offset = -1; offset <= dynamic_window; ++offset)
  {
    int index = anchor + offset;
    if (index < 0)
    {
      continue;
    }
    sum += sensor_table[index]; /* index 可能等于 SENSOR_COUNT，触发 bounds-check */
  }

  return sum;
}

/* 修复版本：严格控制 offset 上界，同时检查 index 是否落在合法范围。 */
static int safe_window_sum(int anchor)
{
  const int dynamic_window = 2 + (anchor & 1);
  int sum = 0;

  for (int offset = -1; offset < dynamic_window; ++offset)
  {
    int index = anchor + offset;
    if (index < 0 || index >= SENSOR_COUNT)
    {
      continue;
    }
    sum += sensor_table[index];
  }

  return sum;
}

int main(void)
{
  int anchor = nondet_int();
  /* 只考察尾部窗口，ESBMC 需要此 assume 来收敛状态空间。 */
  __ESBMC_assume(anchor >= SENSOR_COUNT - 3 && anchor < SENSOR_COUNT);

#ifdef USE_SAFE_VERSION
  int sum = safe_window_sum(anchor);
#else
  int sum = faulty_window_sum(anchor);
#endif

  /* assert 仅用于保持函数有输出，真实 bug 由默认的 bounds-check 揪出。 */
  assert(sum < 300);
  return 0;
}

/*
ESBMC 命令 (bug 版本)：
  esbmc code/level1/level1_array_bounds.c --unwind 5 --no-unwinding-assertions
  --unwind 5  保证 dynamic_window 最大 4 时循环被完全展开；
  --no-unwinding-assertions 避免 ESBMC 在达到 unwind 深度时直接报错；
  数组越界检查为默认开启（若想关闭需 `--no-bounds-check`），此处直接依赖默认配置。

ESBMC 命令 (修复版本)：
  esbmc code/level1/level1_array_bounds.c --unwind 5 --no-unwinding-assertions \
    -DUSE_SAFE_VERSION
  -DUSE_SAFE_VERSION 切换到 safe_window_sum，使得同一 unwinding 下验证可以顺利通过。

解释稿：
1. 传感器窗口的大小随 anchor 奇偶变化，导致循环次数不是编译期常量；
   若 unwinding 不足，ESBMC 会给出 unwinding-assertion 的假阳性。
2. 故障版本在 offset 使用 <=，且没检查 index 上界。当 anchor == 7、window == 3 时，
   index 最后一次迭代等于 9，越界访问 sensor_table[9] 立即被 SMT 证明。
3. 修复版本通过两个改动消除了特殊情况：offset 仅迭代到 < dynamic_window，
   并对 index 进行上下界裁剪；因此在同样的 unwinding 下，bounds-check 不再触发。
*/
