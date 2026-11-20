# BenchExec 原始结果

`formal-20261117-141308/` 中共有 88 份 `.xml.bz2`，按任务编号和算法存放，例如：

`T05/bmc/benchexec/T05-bmc....xml.bz2`

记录了该次运行的状态和测量数据，是 `experiment/formal-20261117-141308/results.csv` 的原始依据。

这里只复制了原始 XML，没有收进每次运行生成的全部 HTML、日志和图文件。六个例子的精选文件在 `cases/`。

如需复核，进入技术包根目录执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_package.ps1 -CheckRawXml
```
