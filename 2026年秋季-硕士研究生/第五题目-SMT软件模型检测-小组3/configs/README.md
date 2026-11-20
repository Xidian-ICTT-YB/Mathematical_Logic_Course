# 算法配置

`formal-20261117-141308/` 保存本次正式实验用过的 88 份 XML：T01 至 T22 各对应 BMC、k-induction、predicate、Impact 四份配置。

统一的限制是：CPU 软限制 900 秒、硬限制 1200 秒，内存 6000 MB，2 个 CPU 核，Java 堆 4000 MB，BenchExec 同时运行 1 个任务。88 份 XML 的哈希与 `experiment/formal-20261117-141308/runs.csv` 一致。

`templates/` 放四算法的配置模板；根目录的 `smoke-*.xml` 是环境测试时用过的配置，并非正式批次的结果。

正式 XML 中的程序路径按原任务包目录编写，依赖 `tasks/SVCOMP16_DeviceDrivers64_任务包/任务文件/` 的层级。
