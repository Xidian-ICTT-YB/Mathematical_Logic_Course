/**
 * level1_null_pointer.c
 *
 * 验证目标：配置驱动的指针在特定路径上会为 NULL，却仍被解引用；
 * ESBMC 默认的 pointer check（若要关闭需 --no-pointer-check）配合 trace
 * 可以快速定位该问题。
 */
#include <assert.h>
#include <stddef.h>

#ifndef __ESBMC_assume
void __ESBMC_assume(_Bool cond);
#endif

extern int nondet_int(void);
extern _Bool nondet_bool(void);

struct packet
{
  int length;
  int *payload;
};

static int buffer_storage[4] = {1, 2, 3, 4};

/* 故障版本：keepalive 案例 length==0 时，仍然假设 payload 有效。 */
static int faulty_parser(struct packet *pkt)
{
  if (pkt->length > 0 && pkt->payload != NULL)
  {
    return pkt->payload[0];
  }

  if (pkt->length == 0)
  {
    /* payload 可能为 NULL，但仍然被访问。 */
    return pkt->payload[0];
  }

  return -1;
}

/* 修复版本：为 keepalive 建立独立分支，完全避免访问 payload。 */
static int safe_parser(struct packet *pkt)
{
  if (pkt->length > 0 && pkt->payload != NULL)
  {
    return pkt->payload[0];
  }

  if (pkt->length == 0)
  {
    return 0; /* keepalive 消息不应访问 payload */
  }

  return -1;
}

int main(void)
{
  struct packet pkt;
  pkt.length = nondet_int();
  _Bool has_payload = nondet_bool();

  __ESBMC_assume(pkt.length >= -1 && pkt.length <= 3);
  if (has_payload)
  {
    pkt.payload = buffer_storage;
  }
  else
  {
    pkt.payload = NULL;
  }

#ifdef USE_SAFE_VERSION
  int result = safe_parser(&pkt);
#else
  int result = faulty_parser(&pkt);
#endif

  assert(result >= -1);
  return 0;
}

/*
ESBMC 命令 (bug 版本)：
  esbmc code/level1/level1_null_pointer.c
  指针检查默认启用，如需观察路径可再手动加 `--symex-trace`；
  如果想跳过检查可通过 `--no-pointer-check` 关闭（本示例保持开启）。

ESBMC 命令 (修复版本)：
  esbmc code/level1/level1_null_pointer.c -DUSE_SAFE_VERSION
  -DUSE_SAFE_VERSION 选择 safe_parser，keepalive 分支不再访问 payload。

解释稿：
1. 该示例模拟工业协议里“keepalive 消息不带 payload”的特性。测试通常只覆盖带数据的路径，
   因此 parser 把 keepalive 当普通数据包对待，导致 NULL 解引用。
2. ESBMC 用 nondet_bool 让 payload 既可能为 NULL 也可能有效，默认的 pointer check
   生成 `payload != NULL` 的约束；当 length==0 且 has_payload==false 时，SMT 立刻返回反例。
3. 修复不需要新增 if 层级，而是把 keepalive 的建模当成独立数据结构（length==0 即虚拟包），
   避免 payload 与 length 之间的隐式依赖，让“特殊情况”回归正常情况。
*/
