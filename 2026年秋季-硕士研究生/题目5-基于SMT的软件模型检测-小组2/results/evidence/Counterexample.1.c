void __VERIFIER_error();
typedef unsigned char __u8;
typedef unsigned short __u16;
typedef unsigned int __u32;
typedef unsigned long long __u64;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef long long s64;
typedef unsigned long long u64;
typedef unsigned short __kernel_mode_t;
typedef unsigned int __kernel_size_t;
typedef int __kernel_ssize_t;
typedef long __kernel_time_t;
typedef int __kernel_clockid_t;
typedef long long __kernel_loff_t;
typedef __u32 __kernel_dev_t;
typedef __kernel_dev_t dev_t;
typedef __kernel_mode_t mode_t;
typedef __kernel_clockid_t clockid_t;
typedef _Bool bool;
typedef __kernel_loff_t loff_t;
typedef __kernel_size_t size_t;
typedef __kernel_ssize_t ssize_t;
typedef unsigned int gfp_t;
typedef u32 phys_addr_t;
typedef phys_addr_t resource_size_t;
struct __anonstruct_atomic_t_6 {
  int counter;
} ;
typedef struct __anonstruct_atomic_t_6 atomic_t;
struct list_head {
  struct list_head *next;
  struct list_head *prev;
} ;
struct resource {
  resource_size_t start;
  resource_size_t end;
  const char *name;
  unsigned long flags;
  struct resource *parent;
  struct resource *sibling;
  struct resource *child;
} ;
struct device ;
struct task_struct ;
struct lockdep_map ;
struct thread_info ;
struct module ;
struct completion ;
typedef atomic_t atomic_long_t;
struct stack_trace {
  unsigned int nr_entries;
  unsigned int max_entries;
  unsigned long *entries;
  int skip;
} ;
struct lockdep_subclass_key {
  char __one_byte;
} ;
struct lock_class_key {
  struct lockdep_subclass_key subkeys[8U];
} ;
struct lock_class {
  struct list_head hash_entry;
  struct list_head lock_entry;
  struct lockdep_subclass_key *key;
  unsigned int subclass;
  unsigned int dep_gen_id;
  unsigned long usage_mask;
  struct stack_trace usage_traces[13U];
  struct list_head locks_after;
  struct list_head locks_before;
  unsigned int version;
  unsigned long ops;
  const char *name;
  int name_version;
  unsigned long contention_point[4U];
  unsigned long contending_point[4U];
} ;
struct lockdep_map {
  struct lock_class_key *key;
  struct lock_class *class_cache[2U];
  const char *name;
  int cpu;
  unsigned long ip;
} ;
struct sock ;
struct kobject ;
enum kobj_ns_type {
  KOBJ_NS_TYPE_NONE = 0,
  KOBJ_NS_TYPE_NET = 1,
  KOBJ_NS_TYPES = 2
} ;
struct kobj_ns_type_operations {
  enum kobj_ns_type type;
  const void * (*current_ns)();
  const void * (*netlink_ns)(struct sock *);
  const void * (*initial_ns)();
} ;
struct attribute {
  const char *name;
  mode_t mode;
  struct lock_class_key *key;
  struct lock_class_key skey;
} ;
struct attribute_group {
  const char *name;
  mode_t  (*is_visible)(struct kobject *, struct attribute *, int);
  struct attribute **attrs;
} ;
struct file ;
struct vm_area_struct ;
struct bin_attribute {
  struct attribute attr;
  size_t size;
  void *private;
  ssize_t  (*read)(struct file *, struct kobject *, struct bin_attribute *, char *, loff_t , size_t );
  ssize_t  (*write)(struct file *, struct kobject *, struct bin_attribute *, char *, loff_t , size_t );
  int (*mmap)(struct file *, struct kobject *, struct bin_attribute *, struct vm_area_struct *);
} ;
struct sysfs_ops {
  ssize_t  (*show)(struct kobject *, struct attribute *, char *);
  ssize_t  (*store)(struct kobject *, struct attribute *, const char *, size_t );
} ;
struct sysfs_dirent ;
struct timespec ;
struct __anonstruct_futex_9 {
  u32 *uaddr;
  u32 val;
  u32 flags;
  u32 bitset;
  u64 time;
  u32 *uaddr2;
} ;
struct __anonstruct_nanosleep_10 {
  clockid_t index;
  struct timespec *rmtp;
  u64 expires;
} ;
struct pollfd ;
struct __anonstruct_poll_11 {
  struct pollfd *ufds;
  int nfds;
  int has_timeout;
  unsigned long tv_sec;
  unsigned long tv_nsec;
} ;
union __anonunion_ldv_2937_8 {
  struct __anonstruct_futex_9 futex;
  struct __anonstruct_nanosleep_10 nanosleep;
  struct __anonstruct_poll_11 poll;
} ;
struct restart_block {
  long int (*fn)(struct restart_block *);
  union __anonunion_ldv_2937_8 ldv_2937;
} ;
struct vfp_hard_struct {
  __u64 fpregs[16U];
  __u32 fpexc;
  __u32 fpscr;
  __u32 fpinst;
  __u32 fpinst2;
} ;
union vfp_state {
  struct vfp_hard_struct hard;
} ;
struct fp_hard_struct {
  unsigned int save[35U];
} ;
struct fp_soft_struct {
  unsigned int save[35U];
} ;
union fp_state {
  struct fp_hard_struct hard;
  struct fp_soft_struct soft;
} ;
struct crunch_state {
  unsigned int mvdx[16U][2U];
  unsigned int mvax[4U][3U];
  unsigned int dspsc[2U];
} ;
struct exec_domain ;
typedef unsigned long mm_segment_t;
struct cpu_context_save {
  __u32 r4;
  __u32 r5;
  __u32 r6;
  __u32 r7;
  __u32 r8;
  __u32 r9;
  __u32 sl;
  __u32 fp;
  __u32 sp;
  __u32 pc;
  __u32 extra[2U];
} ;
struct thread_info {
  unsigned long flags;
  int preempt_count;
  mm_segment_t addr_limit;
  struct task_struct *task;
  struct exec_domain *exec_domain;
  __u32 cpu;
  __u32 cpu_domain;
  struct cpu_context_save cpu_context;
  __u32 syscall;
  __u8 used_cp[16U];
  unsigned long tp_value;
  struct crunch_state crunchstate;
  union fp_state fpstate;
  union vfp_state vfpstate;
  struct restart_block restart_block;
} ;
struct __anonstruct_arch_spinlock_t_12 {
  volatile unsigned int slock;
} ;
typedef struct __anonstruct_arch_spinlock_t_12 arch_spinlock_t;
struct raw_spinlock {
  arch_spinlock_t raw_lock;
  unsigned int magic;
  unsigned int owner_cpu;
  void *owner;
  struct lockdep_map dep_map;
} ;
struct __anonstruct_ldv_3075_15 {
  u8 __padding[1U];
  struct lockdep_map dep_map;
} ;
union __anonunion_ldv_3076_14 {
  struct raw_spinlock rlock;
  struct __anonstruct_ldv_3075_15 ldv_3075;
} ;
struct spinlock {
  union __anonunion_ldv_3076_14 ldv_3076;
} ;
typedef struct spinlock spinlock_t;
struct kref {
  atomic_t refcount;
} ;
struct __wait_queue_head {
  spinlock_t lock;
  struct list_head task_list;
} ;
typedef struct __wait_queue_head wait_queue_head_t;
struct kset ;
struct kobj_type ;
struct kobject {
  const char *name;
  struct list_head entry;
  struct kobject *parent;
  struct kset *kset;
  struct kobj_type *ktype;
  struct sysfs_dirent *sd;
  struct kref kref;
  unsigned char state_initialized;
  unsigned char state_in_sysfs;
  unsigned char state_add_uevent_sent;
  unsigned char state_remove_uevent_sent;
  unsigned char uevent_suppress;
} ;
struct kobj_type {
  void (*release)(struct kobject *);
  const struct sysfs_ops *sysfs_ops;
  struct attribute **default_attrs;
  const struct kobj_ns_type_operations * (*child_ns_type)(struct kobject *);
  const void * (*namespace)(struct kobject *);
} ;
struct kobj_uevent_env {
  char *envp[32U];
  int envp_idx;
  char buf[2048U];
  int buflen;
} ;
struct kset_uevent_ops {
  const int (*filter)(struct kset *, struct kobject *);
  const const char * (*name)(struct kset *, struct kobject *);
  const int (*uevent)(struct kset *, struct kobject *, struct kobj_uevent_env *);
} ;
struct kset {
  struct list_head list;
  spinlock_t list_lock;
  struct kobject kobj;
  const struct kset_uevent_ops *uevent_ops;
} ;
struct klist_node ;
struct klist_node {
  void *n_klist;
  struct list_head n_node;
  struct kref n_ref;
} ;
struct timespec {
  __kernel_time_t tv_sec;
  long tv_nsec;
} ;
typedef void (*ctor_fn_t)();
struct page ;
struct mutex {
  atomic_t count;
  spinlock_t wait_lock;
  struct list_head wait_list;
  struct thread_info *owner;
  const char *name;
  void *magic;
  struct lockdep_map dep_map;
} ;
union ktime {
  s64 tv64;
} ;
typedef union ktime ktime_t;
struct tvec_base ;
struct timer_list {
  struct list_head entry;
  unsigned long expires;
  struct tvec_base *base;
  void (*function)(unsigned long);
  unsigned long data;
  int slack;
  int start_pid;
  void *start_site;
  char start_comm[16U];
  struct lockdep_map lockdep_map;
} ;
struct work_struct ;
struct work_struct {
  atomic_long_t data;
  struct list_head entry;
  void (*func)(struct work_struct *);
  struct lockdep_map lockdep_map;
} ;
typedef __u32 Elf32_Addr;
typedef __u16 Elf32_Half;
typedef __u32 Elf32_Word;
struct elf32_sym {
  Elf32_Word st_name;
  Elf32_Addr st_value;
  Elf32_Word st_size;
  unsigned char st_info;
  unsigned char st_other;
  Elf32_Half st_shndx;
} ;
typedef struct elf32_sym Elf32_Sym;
struct kernel_param ;
struct kernel_param_ops {
  int (*set)(const char *, const struct kernel_param *);
  int (*get)(char *, const struct kernel_param *);
  void (*free)(void *);
} ;
struct kparam_string ;
struct kparam_array ;
union __anonunion_ldv_6603_22 {
  void *arg;
  const struct kparam_string *str;
  const struct kparam_array *arr;
} ;
struct kernel_param {
  const char *name;
  const struct kernel_param_ops *ops;
  u16 perm;
  u16 flags;
  union __anonunion_ldv_6603_22 ldv_6603;
} ;
struct kparam_string {
  unsigned int maxlen;
  char *string;
} ;
struct kparam_array {
  unsigned int max;
  unsigned int *num;
  const struct kernel_param_ops *ops;
  unsigned int elemsize;
  void *elem;
} ;
struct completion {
  unsigned int done;
  wait_queue_head_t wait;
} ;
struct tracepoint ;
struct tracepoint_func {
  void *func;
  void *data;
} ;
struct tracepoint {
  const char *name;
  int state;
  void (*regfunc)();
  void (*unregfunc)();
  struct tracepoint_func *funcs;
} ;
struct unwind_table ;
struct mod_arch_specific {
  struct unwind_table *unwind[5U];
} ;
struct kernel_symbol {
  unsigned long value;
  const char *name;
} ;
struct module_attribute {
  struct attribute attr;
  ssize_t  (*show)(struct module_attribute *, struct module *, char *);
  ssize_t  (*store)(struct module_attribute *, struct module *, const char *, size_t );
  void (*setup)(struct module *, const char *);
  int (*test)(struct module *);
  void (*free)(struct module *);
} ;
struct module_param_attrs ;
struct module_kobject {
  struct kobject kobj;
  struct module *mod;
  struct kobject *drivers_dir;
  struct module_param_attrs *mp;
} ;
struct exception_table_entry ;
enum module_state {
  MODULE_STATE_LIVE = 0,
  MODULE_STATE_COMING = 1,
  MODULE_STATE_GOING = 2
} ;
struct module_ref {
  unsigned int incs;
  unsigned int decs;
} ;
struct module_sect_attrs ;
struct module_notes_attrs ;
struct ftrace_event_call ;
struct module {
  enum module_state state;
  struct list_head list;
  char name[60U];
  struct module_kobject mkobj;
  struct module_attribute *modinfo_attrs;
  const char *version;
  const char *srcversion;
  struct kobject *holders_dir;
  const struct kernel_symbol *syms;
  const unsigned long *crcs;
  unsigned int num_syms;
  struct kernel_param *kp;
  unsigned int num_kp;
  unsigned int num_gpl_syms;
  const struct kernel_symbol *gpl_syms;
  const unsigned long *gpl_crcs;
  const struct kernel_symbol *unused_syms;
  const unsigned long *unused_crcs;
  unsigned int num_unused_syms;
  unsigned int num_unused_gpl_syms;
  const struct kernel_symbol *unused_gpl_syms;
  const unsigned long *unused_gpl_crcs;
  const struct kernel_symbol *gpl_future_syms;
  const unsigned long *gpl_future_crcs;
  unsigned int num_gpl_future_syms;
  unsigned int num_exentries;
  struct exception_table_entry *extable;
  int (*init)();
  void *module_init;
  void *module_core;
  unsigned int init_size;
  unsigned int core_size;
  unsigned int init_text_size;
  unsigned int core_text_size;
  unsigned int init_ro_size;
  unsigned int core_ro_size;
  struct mod_arch_specific arch;
  unsigned int taints;
  Elf32_Sym *symtab;
  Elf32_Sym *core_symtab;
  unsigned int num_symtab;
  unsigned int core_num_syms;
  char *strtab;
  char *core_strtab;
  struct module_sect_attrs *sect_attrs;
  struct module_notes_attrs *notes_attrs;
  char *args;
  const struct tracepoint **tracepoints_ptrs;
  unsigned int num_tracepoints;
  const char **trace_bprintk_fmt_start;
  unsigned int num_trace_bprintk_fmt;
  struct ftrace_event_call **trace_events;
  unsigned int num_trace_events;
  struct list_head source_list;
  struct list_head target_list;
  struct task_struct *waiter;
  void (*exit)();
  struct module_ref *refptr;
  ctor_fn_t  (**ctors)();
  unsigned int num_ctors;
} ;
struct pm_message {
  int event;
} ;
typedef struct pm_message pm_message_t;
struct dev_pm_ops {
  int (*prepare)(struct device *);
  void (*complete)(struct device *);
  int (*suspend)(struct device *);
  int (*resume)(struct device *);
  int (*freeze)(struct device *);
  int (*thaw)(struct device *);
  int (*poweroff)(struct device *);
  int (*restore)(struct device *);
  int (*suspend_noirq)(struct device *);
  int (*resume_noirq)(struct device *);
  int (*freeze_noirq)(struct device *);
  int (*thaw_noirq)(struct device *);
  int (*poweroff_noirq)(struct device *);
  int (*restore_noirq)(struct device *);
  int (*runtime_suspend)(struct device *);
  int (*runtime_resume)(struct device *);
  int (*runtime_idle)(struct device *);
} ;
enum rpm_status {
  RPM_ACTIVE = 0,
  RPM_RESUMING = 1,
  RPM_SUSPENDED = 2,
  RPM_SUSPENDING = 3
} ;
enum rpm_request {
  RPM_REQ_NONE = 0,
  RPM_REQ_IDLE = 1,
  RPM_REQ_SUSPEND = 2,
  RPM_REQ_AUTOSUSPEND = 3,
  RPM_REQ_RESUME = 4
} ;
struct wakeup_source ;
struct dev_pm_info {
  pm_message_t power_state;
  unsigned char can_wakeup;
  unsigned char async_suspend;
  unsigned char in_suspend;
  spinlock_t lock;
  struct list_head entry;
  struct completion completion;
  struct wakeup_source *wakeup;
  struct timer_list suspend_timer;
  unsigned long timer_expires;
  struct work_struct work;
  wait_queue_head_t wait_queue;
  atomic_t usage_count;
  atomic_t child_count;
  unsigned char disable_depth;
  unsigned char ignore_children;
  unsigned char idle_notification;
  unsigned char request_pending;
  unsigned char deferred_resume;
  unsigned char run_wake;
  unsigned char runtime_auto;
  unsigned char no_callbacks;
  unsigned char irq_safe;
  unsigned char use_autosuspend;
  unsigned char timer_autosuspends;
  enum rpm_request request;
  enum rpm_status runtime_status;
  int runtime_error;
  int autosuspend_delay;
  unsigned long last_busy;
  unsigned long active_jiffies;
  unsigned long suspended_jiffies;
  unsigned long accounting_timestamp;
} ;
struct dev_power_domain {
  struct dev_pm_ops ops;
} ;
struct dev_archdata {
} ;
struct pdev_archdata {
} ;
struct device_private ;
struct device_driver ;
struct driver_private ;
struct class ;
struct subsys_private ;
struct bus_type ;
struct device_node ;
struct bus_attribute {
  struct attribute attr;
  ssize_t  (*show)(struct bus_type *, char *);
  ssize_t  (*store)(struct bus_type *, const char *, size_t );
} ;
struct device_attribute ;
struct driver_attribute ;
struct bus_type {
  const char *name;
  struct bus_attribute *bus_attrs;
  struct device_attribute *dev_attrs;
  struct driver_attribute *drv_attrs;
  int (*match)(struct device *, struct device_driver *);
  int (*uevent)(struct device *, struct kobj_uevent_env *);
  int (*probe)(struct device *);
  int (*remove)(struct device *);
  void (*shutdown)(struct device *);
  int (*suspend)(struct device *, pm_message_t );
  int (*resume)(struct device *);
  const struct dev_pm_ops *pm;
  struct subsys_private *p;
} ;
struct of_device_id ;
struct device_driver {
  const char *name;
  struct bus_type *bus;
  struct module *owner;
  const char *mod_name;
  bool suppress_bind_attrs;
  const struct of_device_id *of_match_table;
  int (*probe)(struct device *);
  int (*remove)(struct device *);
  void (*shutdown)(struct device *);
  int (*suspend)(struct device *, pm_message_t );
  int (*resume)(struct device *);
  const struct attribute_group **groups;
  const struct dev_pm_ops *pm;
  struct driver_private *p;
} ;
struct driver_attribute {
  struct attribute attr;
  ssize_t  (*show)(struct device_driver *, char *);
  ssize_t  (*store)(struct device_driver *, const char *, size_t );
} ;
struct class_attribute ;
struct class {
  const char *name;
  struct module *owner;
  struct class_attribute *class_attrs;
  struct device_attribute *dev_attrs;
  struct bin_attribute *dev_bin_attrs;
  struct kobject *dev_kobj;
  int (*dev_uevent)(struct device *, struct kobj_uevent_env *);
  char * (*devnode)(struct device *, mode_t *);
  void (*class_release)(struct class *);
  void (*dev_release)(struct device *);
  int (*suspend)(struct device *, pm_message_t );
  int (*resume)(struct device *);
  const struct kobj_ns_type_operations *ns_type;
  const void * (*namespace)(struct device *);
  const struct dev_pm_ops *pm;
  struct subsys_private *p;
} ;
struct device_type ;
struct class_attribute {
  struct attribute attr;
  ssize_t  (*show)(struct class *, struct class_attribute *, char *);
  ssize_t  (*store)(struct class *, struct class_attribute *, const char *, size_t );
} ;
struct device_type {
  const char *name;
  const struct attribute_group **groups;
  int (*uevent)(struct device *, struct kobj_uevent_env *);
  char * (*devnode)(struct device *, mode_t *);
  void (*release)(struct device *);
  const struct dev_pm_ops *pm;
} ;
struct device_attribute {
  struct attribute attr;
  ssize_t  (*show)(struct device *, struct device_attribute *, char *);
  ssize_t  (*store)(struct device *, struct device_attribute *, const char *, size_t );
} ;
struct device_dma_parameters {
  unsigned int max_segment_size;
  unsigned long segment_boundary_mask;
} ;
struct dma_coherent_mem ;
struct device {
  struct device *parent;
  struct device_private *p;
  struct kobject kobj;
  const char *init_name;
  struct device_type *type;
  struct mutex mutex;
  struct bus_type *bus;
  struct device_driver *driver;
  void *platform_data;
  struct dev_pm_info power;
  struct dev_power_domain *pwr_domain;
  u64 *dma_mask;
  u64 coherent_dma_mask;
  struct device_dma_parameters *dma_parms;
  struct list_head dma_pools;
  struct dma_coherent_mem *dma_mem;
  struct dev_archdata archdata;
  struct device_node *of_node;
  dev_t devt;
  spinlock_t devres_lock;
  struct list_head devres_head;
  struct klist_node knode_class;
  struct class *class;
  const struct attribute_group **groups;
  void (*release)(struct device *);
} ;
struct wakeup_source {
  char *name;
  struct list_head entry;
  spinlock_t lock;
  struct timer_list timer;
  unsigned long timer_expires;
  ktime_t total_time;
  ktime_t max_time;
  ktime_t last_time;
  unsigned long event_count;
  unsigned long active_count;
  unsigned long relax_count;
  unsigned long hit_count;
  unsigned char active;
} ;
struct kmem_cache ;
struct kmem_cache_cpu {
  void **freelist;
  struct page *page;
  int node;
  unsigned int stat[19U];
} ;
struct kmem_cache_node {
  spinlock_t list_lock;
  unsigned long nr_partial;
  struct list_head partial;
  atomic_long_t nr_slabs;
  atomic_long_t total_objects;
  struct list_head full;
} ;
struct kmem_cache_order_objects {
  unsigned long x;
} ;
struct kmem_cache {
  struct kmem_cache_cpu *cpu_slab;
  unsigned long flags;
  unsigned long min_partial;
  int size;
  int objsize;
  int offset;
  struct kmem_cache_order_objects oo;
  struct kmem_cache_order_objects max;
  struct kmem_cache_order_objects min;
  gfp_t allocflags;
  int refcount;
  void (*ctor)(void *);
  int inuse;
  int align;
  int reserved;
  const char *name;
  struct list_head list;
  struct kobject kobj;
  struct kmem_cache_node *node[1U];
} ;
typedef unsigned long kernel_ulong_t;
struct of_device_id {
  char name[32U];
  char type[32U];
  char compatible[128U];
  void *data;
} ;
struct platform_device_id {
  char name[20U];
  kernel_ulong_t driver_data;
} ;
struct mfd_cell ;
struct platform_device {
  const char *name;
  int id;
  struct device dev;
  u32 num_resources;
  struct resource *resource;
  const struct platform_device_id *id_entry;
  struct mfd_cell *mfd_cell;
  struct pdev_archdata archdata;
} ;
struct platform_driver {
  int (*probe)(struct platform_device *);
  int (*remove)(struct platform_device *);
  void (*shutdown)(struct platform_device *);
  int (*suspend)(struct platform_device *, pm_message_t );
  int (*resume)(struct platform_device *);
  struct device_driver driver;
  const struct platform_device_id *id_table;
} ;
struct sensor_device_attribute {
  struct device_attribute dev_attr;
  int index;
} ;
struct s3c_adc_client ;
struct s3c_hwmon_chcfg {
  const char *name;
  unsigned int mult;
  unsigned int div;
} ;
struct s3c_hwmon_pdata {
  struct s3c_hwmon_chcfg *in[8U];
} ;
struct s3c_hwmon_attr {
  struct sensor_device_attribute in;
  struct sensor_device_attribute label;
  char in_name[12U];
  char label_name[12U];
} ;
struct s3c_hwmon {
  struct mutex lock;
  struct s3c_adc_client *client;
  struct device *hwmon_dev;
  struct s3c_hwmon_attr attrs[8U];
} ;
long int ldv_is_err(const void *ptr);
long int ldv_ptr_err(const void *ptr);
int snprintf(char *, size_t , const char *, ...);
void __mutex_init(struct mutex *, const char *, struct lock_class_key *);
int mutex_lock_interruptible_nested(struct mutex *, unsigned int);
void mutex_unlock(struct mutex *);
extern struct module __this_module;
int ldv_device_create_file_5(struct device *ldv_func_arg1, const struct device_attribute *ldv_func_arg2);
int ldv_device_create_file_6(struct device *ldv_func_arg1, const struct device_attribute *ldv_func_arg2);
void device_remove_file(struct device *, const struct device_attribute *);
void * dev_get_drvdata(const struct device *);
void dev_set_drvdata(struct device *, void *);
int dev_printk(const char *, const struct device *, const char *, ...);
int dev_err(const struct device *, const char *, ...);
int dev_warn(const struct device *, const char *, ...);
int ldv_device_create_file_dev_attr_of_sensor_device_attribute(const struct device_attribute *attr);
void kfree(const void *);
void * __kmalloc(size_t , gfp_t );
void * kmalloc(size_t size, gfp_t flags);
void * kzalloc(size_t size, gfp_t flags);
long int PTR_ERR(const void *ptr);
long int IS_ERR(const void *ptr);
int platform_driver_register(struct platform_driver *);
void platform_driver_unregister(struct platform_driver *);
void * platform_get_drvdata(const struct platform_device *pdev);
void platform_set_drvdata(struct platform_device *pdev, void *data);
struct device * hwmon_device_register(struct device *);
void hwmon_device_unregister(struct device *);
int s3c_adc_read(struct s3c_adc_client *, unsigned int);
struct s3c_adc_client * s3c_adc_register(struct platform_device *, void (*)(struct s3c_adc_client *, unsigned int), void (*)(struct s3c_adc_client *, unsigned int, unsigned int, unsigned int *), unsigned int);
void s3c_adc_release(struct s3c_adc_client *);
int s3c_hwmon_read_ch(struct device *dev, struct s3c_hwmon *hwmon, int channel);
int s3c_hwmon_add_raw(struct device *dev);
void s3c_hwmon_remove_raw(struct device *dev);
ssize_t  s3c_hwmon_ch_show(struct device *dev, struct device_attribute *attr, char *buf);
ssize_t  s3c_hwmon_label_show(struct device *dev, struct device_attribute *attr, char *buf);
int s3c_hwmon_create_attr(struct device *dev, struct s3c_hwmon_chcfg *cfg, struct s3c_hwmon_attr *attrs, int channel);
void s3c_hwmon_remove_attr(struct device *dev, struct s3c_hwmon_attr *attrs);
int s3c_hwmon_probe(struct platform_device *dev);
int s3c_hwmon_remove(struct platform_device *dev);
struct platform_driver s3c_hwmon_driver = { &s3c_hwmon_probe, &s3c_hwmon_remove, 0, 0, 0, { "s3c-hwmon", 0, &__this_module, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }, 0 };
int s3c_hwmon_init();
void s3c_hwmon_exit();
void ldv_check_final_state();
void ldv_check_return_value(int);
void ldv_check_return_value_probe(int);
void ldv_initialize();
void ldv_handler_precall();
int __VERIFIER_nondet_int();
int LDV_IN_INTERRUPT = 0;
int main();
long int ldv__builtin_expect(long exp, long c);
void ldv_error();
void * ldv_err_ptr(long error);
long int ldv_is_err_or_null(const void *ptr);
int ldv_count_1 = 0;
int ldv_count_2 = 0;
void ldv_sysfs();
int ldv_call_dev_attr_of_sensor_device_attribute = 0;
extern void __VERIFIER_error(void);
int main_0();
void ldv_initialize_1();
int s3c_hwmon_init_2();
int s3c_hwmon_probe_3(struct platform_device *dev);
void * kzalloc_4(size_t size, gfp_t flags);
void * kmalloc_5(size_t size, gfp_t flags);
void platform_set_drvdata_6(struct platform_device *pdev, void *data);
long int IS_ERR_7(const void *ptr);
long int ldv_is_err_8(const void *ptr);
int s3c_hwmon_add_raw_9(struct device *dev);
long int IS_ERR_10(const void *ptr);
long int ldv_is_err_11(const void *ptr);
int s3c_hwmon_create_attr_12(struct device *dev, struct s3c_hwmon_chcfg *cfg, struct s3c_hwmon_attr *attrs, int channel);
int ldv_device_create_file_5_13(struct device *ldv_func_arg1, const struct device_attribute *ldv_func_arg2);
int ldv_device_create_file_dev_attr_of_sensor_device_attribute_14(const struct device_attribute *attr);
void ldv_error_15();
int main_0() {
  struct platform_device *var_group1;
  int res_s3c_hwmon_probe_10;
  int ldv_s_s3c_hwmon_driver_platform_driver;
  int tmp;
  int tmp___0;
  int tmp___1;
  ldv_s_s3c_hwmon_driver_platform_driver = 0;
  LDV_IN_INTERRUPT = 1;
  ldv_initialize_1();
  ldv_handler_precall();
  tmp = s3c_hwmon_init_2();
  __CPROVER_assume(!(tmp != 0));
  tmp___1 = __VERIFIER_nondet_int();
  __CPROVER_assume(tmp___1 != 0);
  tmp___0 = __VERIFIER_nondet_int();
  __CPROVER_assume(tmp___0 == 0);
  __CPROVER_assume(ldv_s_s3c_hwmon_driver_platform_driver == 0);
  res_s3c_hwmon_probe_10 = s3c_hwmon_probe_3(var_group1);
}

void ldv_initialize_1() {
  return;
}

int s3c_hwmon_init_2() {
  int tmp;
  tmp = platform_driver_register(&s3c_hwmon_driver);
  return tmp;
}

int s3c_hwmon_probe_3(struct platform_device *dev) {
  struct s3c_hwmon_pdata *pdata;
  struct s3c_hwmon *hwmon;
  int ret;
  int i;
  void *tmp;
  struct lock_class_key __key;
  long tmp___0;
  long tmp___1;
  long tmp___2;
  long tmp___3;
  struct s3c_hwmon_chcfg *cfg;
  pdata = (struct s3c_hwmon_pdata *)(dev->dev.platform_data);
  ret = 0;
  __CPROVER_assume(!(((unsigned long)pdata) == ((unsigned long)((struct s3c_hwmon_pdata *)0))));
  tmp = kzalloc_4(800U, 208U);
  hwmon = (struct s3c_hwmon *)tmp;
  __CPROVER_assume(!(((unsigned long)hwmon) == ((unsigned long)((struct s3c_hwmon *)0))));
  platform_set_drvdata_6(dev, (void *)hwmon);
  __mutex_init(&(hwmon->lock), "&hwmon->lock", &__key);
  hwmon->client = s3c_adc_register(dev, 0, 0, 0U);
  const void *__CPAchecker_TMP_0 = (const void *)(hwmon->client);
  tmp___1 = IS_ERR_7(__CPAchecker_TMP_0);
  __CPROVER_assume(!(tmp___1 != 0L));
  ret = s3c_hwmon_add_raw_9(&(dev->dev));
  __CPROVER_assume(!(ret != 0));
  hwmon->hwmon_dev = hwmon_device_register(&(dev->dev));
  const void *__CPAchecker_TMP_2 = (const void *)(hwmon->hwmon_dev);
  tmp___3 = IS_ERR_10(__CPAchecker_TMP_2);
  __CPROVER_assume(!(tmp___3 != 0L));
  i = 0;
  __CPROVER_assume(((unsigned int)i) <= 7U);
  cfg = (pdata->in)[i];
  __CPROVER_assume(!(((unsigned long)cfg) == ((unsigned long)((struct s3c_hwmon_chcfg *)0))));
  __CPROVER_assume((cfg->mult) > 65535U);
  dev_warn((const struct device *)(&(dev->dev)), "channel %d multiplier too large\n", i);
  __CPROVER_assume(!((cfg->div) == 0U));
  ret = s3c_hwmon_create_attr_12(&(dev->dev), (pdata->in)[i], ((struct s3c_hwmon_attr *)(&(hwmon->attrs))) + ((unsigned int)i), i);
}

void * kzalloc_4(size_t size, gfp_t flags) {
  void *tmp;
  tmp = kmalloc_5(size, flags | 32768U);
  return tmp;
}

void * kmalloc_5(size_t size, gfp_t flags) {
  void *tmp___2;
  tmp___2 = __kmalloc(size, flags);
  return tmp___2;
}

void platform_set_drvdata_6(struct platform_device *pdev, void *data) {
  dev_set_drvdata(&(pdev->dev), data);
  return;
}

long int IS_ERR_7(const void *ptr) {
  long tmp;
  tmp = ldv_is_err_8(ptr);
  return tmp;
}

long int ldv_is_err_8(const void *ptr) {
  return ((unsigned long)ptr) > 2012UL;
}

int s3c_hwmon_add_raw_9(struct device *dev) {
  return 0;
}

long int IS_ERR_10(const void *ptr) {
  long tmp;
  tmp = ldv_is_err_11(ptr);
  return tmp;
}

long int ldv_is_err_11(const void *ptr) {
  return ((unsigned long)ptr) > 2012UL;
}

int s3c_hwmon_create_attr_12(struct device *dev, struct s3c_hwmon_chcfg *cfg, struct s3c_hwmon_attr *attrs, int channel) {
  struct sensor_device_attribute *attr;
  int ret;
  snprintf((char *)(&(attrs->in_name)), 12U, "in%d_input", channel);
  attr = &(attrs->in);
  attr->index = channel;
  attr->dev_attr.attr.name = (const char *)(&(attrs->in_name));
  attr->dev_attr.attr.mode = 292U;
  attr->dev_attr.show = &s3c_hwmon_ch_show;
  ret = ldv_device_create_file_5_13(dev, (const struct device_attribute *)(&(attr->dev_attr)));
}

int ldv_device_create_file_5_13(struct device *ldv_func_arg1, const struct device_attribute *ldv_func_arg2) {
  int tmp;
  tmp = ldv_device_create_file_dev_attr_of_sensor_device_attribute_14(ldv_func_arg2);
}

int ldv_device_create_file_dev_attr_of_sensor_device_attribute_14(const struct device_attribute *attr) {
  __CPROVER_assume(ldv_call_dev_attr_of_sensor_device_attribute == 0);
  ldv_count_2 = ldv_count_2 + 1;
  ldv_call_dev_attr_of_sensor_device_attribute = 1;
  __CPROVER_assume(!(ldv_count_1 >= ldv_count_2));
  ldv_error_15();
}

void ldv_error_15() {
  __VERIFIER_error(); // target state
  __VERIFIER_error();
}
