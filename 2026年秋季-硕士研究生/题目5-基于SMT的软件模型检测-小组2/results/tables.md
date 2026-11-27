### 表 1 四算法汇总（22 个任务）

| 算法 | 安全 TRUE | 错误 FALSE | 超时 | 内存耗尽 | 其他不确定 | 正确结论 | 中位 CPU 时间* |
|---|---:|---:|---:|---:|---:|---:|---:|
| BMC | 6 | 6 | 10 | 0 | 0 | 12/22 | 5.6s |
| k-induction | 11 | 5 | 5 | 1 | 0 | 16/22 | 5.7s |
| 谓词抽象 | 16 | 5 | 0 | 1 | 0 | 21/22 | 6.4s |
| Impact | 16 | 5 | 0 | 1 | 0 | 21/22 | 6.5s |

*CPAchecker 自报 `Total CPU time`，仅统计给出 TRUE/FALSE 的运行；不含容器与 JVM 启动开销。

### 表 2 逐任务结果

| 层 | 任务 | 真值 | BMC | k-ind | 谓词 | Impact |
|---|---|---|---|---|---|---|
| A 一致安全 | media--rc--keymaps--rc-msi-digivox-iii | safe | ✓TRUE | ✓TRUE | ✓TRUE | ✓TRUE |
| A 一致安全 | scsi--scsi_wait_scan | safe | ✓TRUE | ✓TRUE | ✓TRUE | ✓TRUE |
| A 一致安全 | cpufreq--cpufreq_powersave | safe | ✓TRUE | ✓TRUE | ✓TRUE | ✓TRUE |
| A 一致安全 | watchdog--iTCO_vendor_support | safe | ✓TRUE | ✓TRUE | ✓TRUE | ✓TRUE |
| A 一致安全 | w1--slaves--w1_smem | safe | ✓TRUE | ✓TRUE | ✓TRUE | ✓TRUE |
| A 一致安全 | auxdisplay--ks0108 | safe | ✓TRUE | ✓TRUE | ✓TRUE | ✓TRUE |
| B 一致错误 | hwmon-s3c-hwmon-ko--130_7a--af3071a-1.c | unsafe | ✗FALSE | ✗FALSE | ✗FALSE | ✗FALSE |
| B 一致错误 | staging-comedi-drivers-ni_670x-ko--107_1a--adbbc | unsafe | ✗FALSE | ✗FALSE | ✗FALSE | ✗FALSE |
| B 一致错误 | usb--image--microtek | unsafe | ✗FALSE | ✗FALSE | ✗FALSE | ✗FALSE |
| B 一致错误 | staging-comedi-drivers-ni_6527-ko--107_1a--adbbc | unsafe | ✗FALSE | ✗FALSE | ✗FALSE | ✗FALSE |
| B 一致错误 | staging-comedi-drivers-ni_65xx-ko--107_1a--adbbc | unsafe | ✗FALSE | ✗FALSE | ✗FALSE | ✗FALSE |
| C2 BMC 失败/k-ind 成功 | media--rc--keymaps--rc-npgtech | safe | TO | ✓TRUE | ✓TRUE | ✓TRUE |
| C2 BMC 失败/k-ind 成功 | watchdog--iTCO_vendor_support | safe | TO | ✓TRUE | ✓TRUE | ✓TRUE |
| C2 BMC 失败/k-ind 成功 | staging--speakup--speakup_txprt | safe | TO | ✓TRUE | ✓TRUE | ✓TRUE |
| C2 BMC 失败/k-ind 成功 | cpufreq--cpufreq_powersave | safe | TO | ✓TRUE | ✓TRUE | ✓TRUE |
| C2 BMC 失败/k-ind 成功 | w1--slaves--w1_smem | safe | TO | ✓TRUE | ✓TRUE | ✓TRUE |
| C4 仅谓词/Impact | leds--leds-ot200 | safe | TO | TO | ✓TRUE | ✓TRUE |
| C4 仅谓词/Impact | drivers-net-pppox | safe | TO | TO | ✓TRUE | ✓TRUE |
| C4 仅谓词/Impact | w1--slaves--w1_ds2433 | safe | TO | TO | ✓TRUE | ✓TRUE |
| C4 仅谓词/Impact | hwmon-ibmpex-ko--130_7a--d631323.c | safe | TO | TO | ✓TRUE | ✓TRUE |
| C4 仅谓词/Impact | net--ppp--pppox | safe | TO | TO | ✓TRUE | ✓TRUE |
| C3 仅 BMC | vhost-vhost_net-ko--32_7a--linux-3.7.3.c | unsafe | ✗FALSE | OOM | OOM | OOM |

### 表 3 实测与论文结论对照

- 两方都给出结论的运行：70 次；一致 70 次，冲突 0 次。
