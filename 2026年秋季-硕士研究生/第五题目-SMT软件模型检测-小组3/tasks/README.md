# 测试程序

`SVCOMP16_DeviceDrivers64_任务包/任务文件/` 中有 22 个正式测试程序，文件名按原任务包保留。其编号和预期结果见 `experiment/formal-20261117-141308/tasks.csv`。

`SVCOMP16_DeviceDrivers64_任务包/unreach-call.prp` 是正式实验使用的属性文件，用于检查程序是否会到达指定的错误位置。正式 XML 使用了相对路径，所以任务包目录层级保留不变。

`smoke/` 中有三个自建小程序（安全、错误和 SMT 相关）及属性文件，只用于验证环境和工具能否运行，不属于22个正式任务。
