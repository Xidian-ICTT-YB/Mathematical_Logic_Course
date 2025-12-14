/**
 * level3_environment_model.c
 *
 * 验证目标：有限状态的 watchdog 控制器在“总线忙碌时”会漏掉心跳，导致倒计时归零；
 * 通过对环境加入约束（心跳至多 2 个周期缺失）来模拟真实设备，再由 ESBMC 检查
 * bounded correctness。修复版会排队 pending feed，保证忙碌结束后立即喂狗。
 */
#include <assert.h>

#ifndef __ESBMC_assume
void __ESBMC_assume(_Bool cond);
#endif

extern _Bool nondet_bool(void);

#define RESET_VALUE 3
#define MAX_TICKS 6

struct watchdog_ctx
{
  int countdown;
  _Bool pending_feed;
};

/* 故障版本：若心跳发生在总线忙碌期间，直接丢弃，不会稍后补偿。 */
static void faulty_tick(struct watchdog_ctx *ctx, _Bool heartbeat, _Bool bus_idle)
{
  if (heartbeat && bus_idle)
  {
    ctx->countdown = RESET_VALUE;
  }
  else
  {
    if (!ctx->pending_feed)
    {
      ctx->countdown -= 1; /* 仅在没有待处理心跳时才递减 */
    }
  }

  if (ctx->countdown < -1)
  {
    ctx->countdown = -1;
  }
}

/* 修复版本：把忙碌时期的心跳排队，等总线空闲后再喂。 */
static void safe_tick(struct watchdog_ctx *ctx, _Bool heartbeat, _Bool bus_idle)
{
  if (heartbeat && bus_idle)
  {
    ctx->countdown = RESET_VALUE;
    ctx->pending_feed = 0;
  }
  else if (heartbeat && !bus_idle)
  {
    ctx->pending_feed = 1; /* 记录需要补喂，忙碌时不扣减倒计时 */
  }
  else
  {
    if (!ctx->pending_feed)
    {
      ctx->countdown -= 1; /* 仅在没有待补心跳时递减 */
    }
  }

  if (ctx->pending_feed && bus_idle)
  {
    ctx->countdown = RESET_VALUE;
    ctx->pending_feed = 0;
  }

  if (ctx->countdown < -1)
  {
    ctx->countdown = -1;
  }
}

int main(void)
{
  struct watchdog_ctx ctx = {.countdown = RESET_VALUE, .pending_feed = 0};
  int since_last_heartbeat = 0;

  for (int tick = 0; tick < MAX_TICKS; ++tick)
  {
    _Bool heartbeat = nondet_bool();
    _Bool bus_idle = nondet_bool();

    if (heartbeat)
    {
      since_last_heartbeat = 0;
    }
    else
    {
      since_last_heartbeat += 1;
    }

    /* 环境建模：任意时间心跳缺失不会超过 2 个周期。 */
    __ESBMC_assume(since_last_heartbeat <= 2);

#ifdef USE_SAFE_VERSION
    safe_tick(&ctx, heartbeat, bus_idle);
#else
    faulty_tick(&ctx, heartbeat, bus_idle);
#endif

    /* 要求：系统处于 RUN 状态时 watchdog 倒计时必须保持为正。 */
    assert(ctx.countdown > 0);
  }

  return 0;
}

/*
ESBMC 命令 (bug 版本)：
  esbmc code/level3/level3_environment_model.c --unwind 6 --no-unwinding-assertions --k-step 1
  --unwind 6 覆盖 MAX_TICKS 次循环；--no-unwinding-assertions 防止在到达上界时提前终止；
  --k-step 1 让 ESBMC 逐步增加搜索深度（可观察“界内正确，界外未知”的效果）。

ESBMC 命令 (修复版本)：
  esbmc code/level3/level3_environment_model.c --unwind 6 --no-unwinding-assertions \
    --k-step 1 -DUSE_SAFE_VERSION
  safe_tick 会在 bus_idle==false 时设置 pending_feed，并在下一次空闲时补喂，
  因此在同样的界限下断言成立。

讲解稿：
1. 实际硬件往往有“环境保证”：心跳不会超过 N 个周期缺失。`__ESBMC_assume` 将该约束
   编码进模型，避免状态空间被不现实的输入淹没。
2. 故障版本在总线忙碌时丢掉心跳，导致 countdown 连续自减直至 <=0，
   虽然环境确实提供了足够的心跳，watchdog 仍然 timeout。
3. 修复方案并不增加复杂条件，而是引入 `pending_feed` 数据结构，把“忙碌时收到心跳”
   视为正常状态；当 bus_idle 重新为真时再一次性喂狗，消除了特殊情况。
4. `--k-step` / bounded 模型检查强调：我们只保证 MAX_TICKS 内性质成立，若要覆盖更长时间，
   需要增加 unwind 或引入循环不变式。实用主义意味着我们选择一个可被解释的上界。
*/
