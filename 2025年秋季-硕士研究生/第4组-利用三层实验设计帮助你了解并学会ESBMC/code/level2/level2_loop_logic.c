/**
 * level2_loop_logic.c
 *
 * 验证目标：两个嵌套循环驱动的调度器，如果 break 只跳出内层，就会继续累加，
 * 最终突破全局配额。需要 ESBMC 结合 --unwind 控制循环深度，才能覆盖所有波次。
 */
#include <assert.h>

#ifndef __ESBMC_assume
void __ESBMC_assume(_Bool cond);
#endif

extern int nondet_int(void);

#define MAX_DELIVERY 40

static int compute_local_budget(int wave, int chunk)
{
  int base = (wave % chunk) + 1;
  if (wave & 1)
  {
    base += 1;
  }
  return base;
}

/* 故障版本：只 break 内层循环，导致 delivered 仍可能超过 MAX_DELIVERY。 */
static int faulty_dispatch(int demand, int chunk)
{
  int delivered = 0;

  for (int wave = 0; wave < demand; ++wave)
  {
    int local_budget = compute_local_budget(wave, chunk);
    for (int ticket = 0; ticket <= local_budget; ++ticket)
    {
      delivered += 3; /* 单次处理 3 个任务，增长较快 */
      if (delivered >= MAX_DELIVERY)
      {
        break; /* 仅跳出内层，wave+1 继续执行 */
      }
    }
  }

  return delivered;
}

/* 修复版本：当达到全局配额时双重跳出，并把循环条件写成 < 避免额外迭代。 */
static int safe_dispatch(int demand, int chunk)
{
  int delivered = 0;

  for (int wave = 0; wave < demand; ++wave)
  {
    int local_budget = compute_local_budget(wave, chunk);
    for (int ticket = 0; ticket < local_budget; ++ticket)
    {
      if (delivered + 3 > MAX_DELIVERY)
      {
        delivered = MAX_DELIVERY; /* 向上取整但不越界 */
        return delivered;         /* 直接返回，双重 break */
      }
      delivered += 3;
      if (delivered >= MAX_DELIVERY)
      {
        return delivered; /* 直接返回，双重 break */
      }
    }
  }

  return delivered;
}

int main(void)
{
  int demand = nondet_int();
  int chunk = nondet_int();

  __ESBMC_assume(demand >= 3 && demand <= 6);
  __ESBMC_assume(chunk >= 2 && chunk <= 3);

#ifdef USE_SAFE_VERSION
  int delivered = safe_dispatch(demand, chunk);
#else
  int delivered = faulty_dispatch(demand, chunk);
#endif

  /* 工程需求：无论输入如何， delivered 不得超过 MAX_DELIVERY。 */
  assert(delivered <= MAX_DELIVERY);
  return 0;
}

/*
ESBMC 命令 (bug 版本)：
  esbmc code/level2/level2_loop_logic.c --unwind 10 --no-unwinding-assertions
  --unwind 10 覆盖 demand<=6、chunk<=3 情况下的最深执行路径（3*6 次迭代）；
  --no-unwinding-assertions 防止因展开不足导致假阳性，确保真正看到 delivered>MAX_DELIVERY 的反例。

ESBMC 命令 (修复版本)：
  esbmc code/level2/level2_loop_logic.c --unwind 10 --no-unwinding-assertions -DUSE_SAFE_VERSION
  safe_dispatch 在达到配额时直接返回，且把 ticket 循环改成 < local_budget，
  因此在相同的 unwinding 下断言可以被证明。

解释稿：
1. 场景模拟“波次调度”：外层根据 demand 决定波次数，内层 ticket 消耗局部预算。
   工程上很容易只 break 内层，误以为 delivered 不会再增加。
2. BMC 将两个循环完全展开后，能够构造 wave==5、chunk==3 的路径，
   在第 5 波次中再次加 3， delivered 变为 42，断言失败。
3. 修复方案不是再加 if/flag，而是从数据结构上改变：一旦达到 MAX_DELIVERY，
   立即返回；并把 ticket 条件写成 `<`，消除 off-by-one 特殊情况。
*/
