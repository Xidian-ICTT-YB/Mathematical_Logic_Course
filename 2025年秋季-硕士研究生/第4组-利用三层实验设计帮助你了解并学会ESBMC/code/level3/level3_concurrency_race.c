/**
 * level3_concurrency_race.c
 *
 * 验证目标：两个线程在没有同步的情况下递增共享计数器，某些调度会让 counter
 * 小于理论值；加入互斥锁后，同样的 context bound 内可证明性质成立。
 */
#include <assert.h>
#include <pthread.h>

#define THREAD_ITERS 5
#define THREADS 2

#ifndef USE_SAFE_VERSION
#define LOCK()
#define UNLOCK()
#else
static pthread_mutex_t counter_lock = PTHREAD_MUTEX_INITIALIZER;
#define LOCK() pthread_mutex_lock(&counter_lock)
#define UNLOCK() pthread_mutex_unlock(&counter_lock)
#endif

static int counter = 0;

static void *worker(void *arg)
{
  (void)arg;
  for (int i = 0; i < THREAD_ITERS; ++i)
  {
    LOCK();
    int local = counter;
    local += 1;
    counter = local; /* 无锁版本对 counter 的读改写会被打断 */
    UNLOCK();
  }
  return NULL;
}

int main(void)
{
  pthread_t tids[THREADS];

  for (int i = 0; i < THREADS; ++i)
  {
    pthread_create(&tids[i], NULL, worker, NULL);
  }

  for (int i = 0; i < THREADS; ++i)
  {
    pthread_join(tids[i], NULL);
  }

  assert(counter == THREADS * THREAD_ITERS);
  return 0;
}

/*
ESBMC 命令 (无锁 bug 版本)：
  esbmc code/level3/level3_concurrency_race.c --context-bound 2 --unwind 6 \
    --no-unwinding-assertions
  --context-bound 2 枚举上下文切换次数，足以打断两个线程；
  --unwind 6 展开 worker 内部的循环。

ESBMC 命令 (加锁版本)：
  esbmc code/level3/level3_concurrency_race.c --context-bound 2 --unwind 6 \
    --no-unwinding-assertions -DUSE_SAFE_VERSION
  开启 USE_SAFE_VERSION 后，LOCK/UNLOCK 保护 counter，ESBMC 在同样的调度界限内证明断言成立。

讲解稿：
1. 并发性质需要在“调度空间”里搜索反例，context bound 就是限制上下文切换次数，
   例如 --context-bound 2 代表最多允许两次线程切换。
2. 无锁版本存在 read-modify-write 竞争：线程 A 读取 counter=3，切换到线程 B，
   B 也读到 3 并写回 4，切回 A 后 A 仍写回 4，最终 assert 失败。
3. 加锁版本让两个线程在持有 mutex 时互斥，调度空间虽然同样大，但 SMT 会证明
   counter 的更新是串行的；出于实用主义，我们只需保证在给定 bound 内性质成立即可。
4. 方法的优点是能真实重现稀有竞态；局限是 context bound 越大，状态空间爆炸越严重，
   因此要根据经验挑选“最可能出错”的调度深度。
*/
