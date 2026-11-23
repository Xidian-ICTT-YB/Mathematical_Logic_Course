# 脚本

`verify_package.ps1` 用于核对交付包中的任务、配置、运行组合及原始 XML。它只检查文件，不运行 CPAchecker。

在技术包根目录的 PowerShell 中执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_package.ps1
```

若本机装有 7-Zip，还可以检查 88 份压缩 XML 的状态：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_package.ps1 -CheckRawXml
```

`source/` 中保存了两份原工程脚本的参考副本：

- `run-formal.ps1`：正式实验使用的运行脚本，含原工程绝对路径，不要直接在交付目录执行。
- `m01-summarize.py`：原结果汇总脚本。

它们保留原文件内容，用于查阅当时怎么运行和统计，不是重新执行全部88次的快捷入口。
