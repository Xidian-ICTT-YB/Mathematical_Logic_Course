/**
 * level2_linked_list_memory.c
 *
 * 验证目标：展示单向链表在复杂删除路径上的两个典型问题：
 * (1) 命中特定阈值时跳过 free 导致内存泄漏；
 * (2) free 后仍访问 curr->next 造成 use-after-free。
 * 需配合 ESBMC 的 --memory-leak-check，并依赖默认开启的 pointer check。
 */
#include <assert.h>
#include <stdlib.h>

#ifndef __ESBMC_assume
void __ESBMC_assume(_Bool cond);
#endif

extern int nondet_int(void);
extern _Bool nondet_bool(void);

struct node
{
  int data;
  struct node *next;
};

static struct node *push_front(struct node *head, int value)
{
  struct node *n = (struct node *)malloc(sizeof(struct node));
  __ESBMC_assume(n != NULL); /* 简化模型：假设分配成功，聚焦删除逻辑 */
  n->data = value;
  n->next = head;
  return n;
}

/* 故障删除：漏掉 data==threshold 的 free，且在 free 后读取 curr->next。 */
static struct node *faulty_prune(struct node *head, int threshold)
{
  struct node *prev = NULL;
  struct node *curr = head;

  while (curr != NULL)
  {
    if (curr->data >= threshold)
    {
      if (prev == NULL)
      {
        head = curr->next;
      }
      else
      {
        prev->next = curr->next;
      }

      if (curr->data == threshold)
      {
        /* 认为阈值节点要“留着日志”，结果泄漏且 prev 指针被悬挂。 */
        prev = curr;
        curr = curr->next; /* curr 已经被逻辑移除，但仍然在链上产生泄漏。 */
        continue;
      }

      free(curr);
      curr = curr->next; /* use-after-free：curr 此时已无效 */
      continue;
    }

    prev = curr;
    curr = curr->next;
  }

  return head;
}

/* 修复版本：无论值为何都立即 free，并缓存 next 后再释放以避免 UAF。 */
static struct node *safe_prune(struct node *head, int threshold)
{
  struct node *prev = NULL;
  struct node *curr = head;

  while (curr != NULL)
  {
    if (curr->data >= threshold)
    {
      struct node *next = curr->next; /* 提前缓存，防止 use-after-free */

      if (prev == NULL)
      {
        head = next;
      }
      else
      {
        prev->next = next;
      }

      free(curr);
      curr = next;
      continue;
    }

    prev = curr;
    curr = curr->next;
  }

  return head;
}

static void free_list(struct node *head)
{
  while (head)
  {
    struct node *next = head->next;
    free(head);
    head = next;
  }
}

int main(void)
{
  struct node *head = NULL;
  head = push_front(head, nondet_int());
  head = push_front(head, nondet_int());
  head = push_front(head, nondet_int());

  int threshold = nondet_int();
  __ESBMC_assume(threshold >= -5 && threshold <= 5);

#ifdef USE_SAFE_VERSION
  head = safe_prune(head, threshold);
#else
  head = faulty_prune(head, threshold);
#endif

  /* 清理剩余节点，safe 版本应当在此处 free 完成，不留泄漏。 */
  free_list(head);

  assert(1); /* 占位断言，真正的错误由内存检查暴露。 */
  return 0;
}

/*
ESBMC 命令 (bug 版本)：
  esbmc code/level2/level2_linked_list_memory.c --memory-leak-check \
    --unwind 4 --no-unwinding-assertions
  --memory-leak-check 捕获 threshold 命中时的泄漏；
  默认的 pointer check 揭示 `curr = curr->next` 时的 use-after-free；
  --unwind 4 覆盖 push_front 构造的 3 个节点及一次删除循环。

ESBMC 命令 (修复版本)：
  esbmc code/level2/level2_linked_list_memory.c --memory-leak-check \
    --unwind 4 --no-unwinding-assertions -DUSE_SAFE_VERSION
  safe_prune 先缓存 next 后 free，且删除逻辑统一，不再漏掉 threshold 分支，因此两种检查均通过。

解释稿：
1. 链表删除常见陷阱是“想保留节点信息就先不 free”，结果导致路径泄漏；
   BMC 在有限 unwinding 内枚举 threshold==data 的情形，把泄漏当场指出。
2. 第二个坑是 free 后立刻访问 curr->next。测试通常靠地址稳定性掩盖问题，
   但在 bit-vector 语义里，该访问被视为非法指针解引用（默认 pointer check 启用）。
3. 修复方案通过统一的数据结构操作（先缓存 next，再 free），
   避免逻辑分支造成不同的资源生命周期，因而无需再补丁式的 if/else。
*/
