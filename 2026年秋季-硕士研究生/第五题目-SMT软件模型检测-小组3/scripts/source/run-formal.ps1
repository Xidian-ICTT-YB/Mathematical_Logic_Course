param(
    [ValidateSet("T05", "ALL")]
    [string]$Scope = "T05"
)

$ErrorActionPreference = "Stop"

$project = Join-Path $env:USERPROFILE "Documents\math-logic-CPAchecker-M01"
$batch = "formal-20261117-141308"
$imageName = "m01-bench-cpa:xml-smoke-cgroupfix"

$plan = Join-Path $project "experiment\$batch\runs.csv"
$summaryCsv = Join-Path $project "experiment\$batch\results.csv"
$resultRoot = Join-Path $project "results\$batch"
$logs = Join-Path $project "logs"
$journal = Join-Path $project "docs\development-journal.md"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$prefix = Join-Path $logs "formal-run-$Scope-$stamp"

$reportPath = "$prefix.report.txt"
$transcriptPath = "$prefix.transcript.log"

$report = New-Object 'System.Collections.Generic.List[string]'

$dockerExe = (Get-Command docker.exe -ErrorAction Stop).Source

$runs = @(Import-Csv -LiteralPath $plan)

if ($runs.Count -ne 88) {
    throw "正式运行清单不是88条"
}

if ($Scope -eq "T05") {
    $selected = @($runs | Where-Object { $_.task_id -eq "T05" })
}
else {
    $selected = $runs
}

if ($selected.Count -eq 0) {
    throw "没有符合条件的运行记录"
}

New-Item -ItemType Directory -Path $logs -Force | Out-Null
New-Item -ItemType Directory -Path $resultRoot -Force | Out-Null

function Update-ResultCsv {
    $argsList = @(
        "run", "--rm",
        "--network", "none",
        "--mount",
        "type=bind,source=$project,target=/workspace",
        "--workdir", "/workspace",
        "--entrypoint", "python3",
        $imageName,
        "/workspace/scripts/m01-summarize.py",
        "/workspace/experiment/$batch/runs.csv",
        "/workspace/results/$batch",
        "/workspace/experiment/$batch/results.csv"
    )

    $out = "$prefix.summary.stdout.txt"
    $err = "$prefix.summary.stderr.txt"

    $p = Start-Process `
        -FilePath $dockerExe `
        -ArgumentList $argsList `
        -Wait -PassThru -NoNewWindow `
        -RedirectStandardOutput $out `
        -RedirectStandardError $err

    if ($p.ExitCode -ne 0) {
        throw "统计脚本执行失败，查看：$err"
    }
}

$started = $false
$completed = 0
$skipped = 0
$failure = $null

try {
    Start-Transcript -Path $transcriptPath -NoClobber | Out-Null
    $started = $true

    $report.Add("批次：$batch")
    $report.Add("范围：$Scope")
    $report.Add("本次计划检查：$($selected.Count)条")
    $report.Add("")

    foreach ($r in $selected) {
        $id = $r.task_id
        $alg = $r.algorithm

        $xmlPath = Join-Path $project (
            $r.config.Replace("/", "\")
        )

        $sourcePath = Join-Path (
            Join-Path $project "tasks\SVCOMP16_DeviceDrivers64_任务包\任务文件"
        ) $r.source_file

        $caseDir = Join-Path $resultRoot "$id\$alg"
        $marker = Join-Path $caseDir "run-complete.txt"

        # 只有原始结果与完成标记同时存在，才允许跳过
        if (Test-Path -LiteralPath $marker) {
            $existing = @(
                Get-ChildItem `
                    -LiteralPath (Join-Path $caseDir "benchexec") `
                    -File -Filter "*.xml.bz2" `
                    -ErrorAction SilentlyContinue
            )

            if ($existing.Count -ne 1) {
                throw "$id/$alg 有完成标记但原始结果异常"
            }

            Write-Host "[SKIP] $id / $alg 已完成"
            $report.Add("SKIP $id/$alg")
            $skipped++
            continue
        }

        if (Test-Path -LiteralPath $caseDir) {
            throw "$id/$alg 已有未完成目录，停止以避免覆盖：$caseDir"
        }

        if (-not (Test-Path -LiteralPath $xmlPath -PathType Leaf)) {
            throw "缺少 XML：$xmlPath"
        }

        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
            throw "缺少源程序：$sourcePath"
        }

        $xmlHash = (
            Get-FileHash -LiteralPath $xmlPath -Algorithm SHA256
        ).Hash

        $sourceHash = (
            Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256
        ).Hash

        if ($xmlHash -ne $r.config_sha256) {
            throw "$id/$alg XML SHA256不一致"
        }

        if ($sourceHash -ne $r.source_sha256) {
            throw "$id 源程序 SHA256不一致"
        }

        $cpaOut = Join-Path $caseDir "cpa-output"
        $benchOut = Join-Path $caseDir "benchexec"

        New-Item -ItemType Directory -Path $cpaOut -Force | Out-Null
        New-Item -ItemType Directory -Path $benchOut -Force | Out-Null

        $stdout = "$prefix.$id.$alg.stdout.txt"
        $stderr = "$prefix.$id.$alg.stderr.txt"

        $dockerArgs = @(
            "run", "--rm",
            "--privileged",
            "--cap-drop=ALL",
            "--cap-add=SETUID",
            "--cap-add=SETGID",
            "--network", "none",
            "--memory=8g",
            "--memory-swap=8g",
            "--cpus=2",
            "--mount",
            "type=bind,source=$project,target=/workspace",
            "--mount",
            "type=bind,source=$cpaOut,target=/home/benchexec/cpa-output",
            "--workdir", "/opt/cpachecker",
            $imageName,
            "benchexec",
            "--tool-directory", "/opt/cpachecker",
            "--read-only-dir", "/",
            "--full-access-dir", "/home/benchexec/cpa-output",
            "--outputpath",
            "/workspace/results/$batch/$id/$alg/benchexec",
            "/workspace/$($r.config)"
        )

        Write-Host ""
        Write-Host "[RUN] $id / $alg" -ForegroundColor Cyan
        Write-Host "Expected: $($r.expected)"
        Write-Host "CPU: 900s soft / 1200s hard"

        $startTime = Get-Date

        $p = Start-Process `
            -FilePath $dockerExe `
            -ArgumentList $dockerArgs `
            -Wait -PassThru -NoNewWindow `
            -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr

        $endTime = Get-Date

        $rawFiles = @(
            Get-ChildItem -LiteralPath $benchOut `
                -File -Filter "*.xml.bz2"
        )

        if ($p.ExitCode -ne 0) {
            throw "$id/$alg Docker退出码=$($p.ExitCode)，查看 $stderr"
        }

        if ($rawFiles.Count -ne 1) {
            throw "$id/$alg 缺少唯一的BenchExec XML.bz2结果"
        }

        @(
            "run_id=$($r.run_id)"
            "task_id=$id"
            "algorithm=$alg"
            "start=$($startTime.ToString('o'))"
            "end=$($endTime.ToString('o'))"
            "docker_exit=$($p.ExitCode)"
            "source_sha256=$sourceHash"
            "config_sha256=$xmlHash"
            "raw_result=$($rawFiles[0].Name)"
        ) | Set-Content -LiteralPath $marker -Encoding UTF8

        $completed++

        $report.Add("COMPLETE $id/$alg")
        $report.Add("RAW $($rawFiles[0].FullName)")
        $report.Add("STDOUT $stdout")
        $report.Add("STDERR $stderr")
        $report.Add("")

        # 每条运行完成后刷新统计CSV
        Update-ResultCsv

        Write-Host "[SAVED] $id / $alg" -ForegroundColor Green
    }

    Update-ResultCsv
}
catch {
    $failure = $_
    $report.Add("ERROR: $($_.Exception.Message)")
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red

    try {
        Update-ResultCsv
    }
    catch {
        $report.Add("统计更新失败：$($_.Exception.Message)")
    }
}
finally {
    $report.Add("")
    $report.Add("本次新增完成：$completed")
    $report.Add("跳过已有完成：$skipped")
    $report.Add("汇总CSV：$summaryCsv")

    $report.ToArray() |
        Set-Content -LiteralPath $reportPath -Encoding UTF8

    if (Test-Path -LiteralPath $journal -PathType Leaf) {
        try {
            $backup = "$journal.bak-$stamp"
            Copy-Item -LiteralPath $journal -Destination $backup

            $state = if ($null -eq $failure) {
                "流程完成"
            } else {
                "运行中断"
            }

            $entry = @"

### $stamp 正式实验运行
- 批次：$batch。
- 范围：$Scope。
- 状态：$state。
- 本次新增完成：$completed。
- 已完成跳过：$skipped。
- 使用已生成的88份正式XML，900s/1200s、6000MB、4000M Heap、2核、并发1。
- BenchExec原始结果、CPAchecker完整输出分别保存在results/$batch/。
- 汇总CSV：experiment/$batch/results.csv。
- 本次日志：logs/$(Split-Path $reportPath -Leaf)。
- 开发日志修改前备份：$(Split-Path $backup -Leaf)。

"@

            Add-Content -LiteralPath $journal `
                -Value $entry -Encoding UTF8
        }
        catch {
            Write-Host "[WARNING] 开发日志更新失败：$($_.Exception.Message)"
        }
    }

    if ($started) {
        Stop-Transcript | Out-Null
    }

    Write-Host ""
    Write-Host "===== 本次执行结果 ====="
    Write-Host "新增完成：$completed"
    Write-Host "跳过已有：$skipped"
    Write-Host "运行报告：$reportPath"
    Write-Host "统计CSV：$summaryCsv"
}

if ($null -ne $failure) {
    throw $failure
}