param(
    [switch]$CheckRawXml
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent $PSScriptRoot
$batch = "formal-20261117-141308"
$experimentDir = Join-Path $packageRoot "experiment\$batch"
$issues = [System.Collections.Generic.List[string]]::new()

function Add-Issue {
    param([string]$Message)
    $issues.Add($Message)
}

function Get-Hash {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

$tasksPath = Join-Path $experimentDir "tasks.csv"
$runsPath = Join-Path $experimentDir "runs.csv"
$resultsPath = Join-Path $experimentDir "results.csv"

foreach ($path in @($tasksPath, $runsPath, $resultsPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Issue "缺少文件：$path"
    }
}

if ($issues.Count -gt 0) {
    $issues | ForEach-Object { Write-Host "[FAIL] $_" -ForegroundColor Red }
    exit 1
}

$tasks = @(Import-Csv -LiteralPath $tasksPath)
$runs = @(Import-Csv -LiteralPath $runsPath)
$results = @(Import-Csv -LiteralPath $resultsPath)

if ($tasks.Count -ne 22) { Add-Issue "tasks.csv 应有 22 条，实际为 $($tasks.Count) 条" }
if ($runs.Count -ne 88) { Add-Issue "runs.csv 应有 88 条，实际为 $($runs.Count) 条" }
if ($results.Count -ne 88) { Add-Issue "results.csv 应有 88 条，实际为 $($results.Count) 条" }

$algorithms = @("bmc", "kinduction", "predicate", "impact")
$taskIds = @($tasks.task_id)
$expectedPairs = [System.Collections.Generic.HashSet[string]]::new()
foreach ($taskId in $taskIds) {
    foreach ($algorithm in $algorithms) {
        [void]$expectedPairs.Add("$taskId|$algorithm")
    }
}

$runPairs = [System.Collections.Generic.HashSet[string]]::new()
foreach ($run in $runs) {
    $key = "$($run.task_id)|$($run.algorithm)"
    if (-not $runPairs.Add($key)) { Add-Issue "runs.csv 有重复组合：$key" }
}

$resultPairs = [System.Collections.Generic.HashSet[string]]::new()
foreach ($result in $results) {
    $key = "$($result.task_id)|$($result.algorithm)"
    if (-not $resultPairs.Add($key)) { Add-Issue "results.csv 有重复组合：$key" }
}

foreach ($pair in $expectedPairs) {
    if (-not $runPairs.Contains($pair)) { Add-Issue "runs.csv 缺少组合：$pair" }
    if (-not $resultPairs.Contains($pair)) { Add-Issue "results.csv 缺少组合：$pair" }
}
foreach ($pair in $runPairs) {
    if (-not $expectedPairs.Contains($pair)) { Add-Issue "runs.csv 有计划外组合：$pair" }
}
foreach ($pair in $resultPairs) {
    if (-not $expectedPairs.Contains($pair)) { Add-Issue "results.csv 有计划外组合：$pair" }
}

$formalTaskDir = Join-Path $packageRoot "tasks\SVCOMP16_DeviceDrivers64_任务包\任务文件"
foreach ($task in $tasks) {
    $sourcePath = Join-Path $formalTaskDir $task.file
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        Add-Issue "缺少任务文件：$($task.task_id) / $($task.file)"
        continue
    }
    if ((Get-Hash $sourcePath) -ne $task.sha256.ToUpperInvariant()) {
        Add-Issue "任务 SHA256 不一致：$($task.task_id)"
    }
}

foreach ($run in $runs) {
    $relativeConfig = $run.config.Replace("/", "\")
    $configPath = Join-Path $packageRoot $relativeConfig
    if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
        Add-Issue "缺少配置：$($run.run_id) / $relativeConfig"
        continue
    }
    if ((Get-Hash $configPath) -ne $run.config_sha256.ToUpperInvariant()) {
        Add-Issue "配置 SHA256 不一致：$($run.run_id)"
    }

    try {
        [xml]$configXml = Get-Content -LiteralPath $configPath -Raw
        $benchmark = $configXml.benchmark
        if ($benchmark.timelimit -ne "900s" -or
            $benchmark.hardtimelimit -ne "1200s" -or
            $benchmark.memlimit -ne "6000 MB" -or
            $benchmark.cpuCores -ne "2" -or
            $benchmark.threads -ne "1") {
            Add-Issue "资源限制不一致：$($run.run_id)"
        }
        $inputName = Split-Path -Leaf ([string]$benchmark.tasks.include)
        if ($inputName -ne $run.source_file) {
            Add-Issue "配置输入文件不一致：$($run.run_id)"
        }
    }
    catch {
        Add-Issue "配置 XML 无法解析：$($run.run_id)"
    }
}

$rawPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($result in $results) {
    $relativeRaw = $result.raw_result.Replace("/", "\")
    $rawPath = Join-Path (Join-Path $packageRoot "results") $relativeRaw
    if (-not (Test-Path -LiteralPath $rawPath -PathType Leaf)) {
        Add-Issue "缺少原始 XML：$($result.run_id)"
        continue
    }
    if (-not $rawPaths.Add($rawPath)) {
        Add-Issue "多个结果指向同一原始 XML：$rawPath"
    }
}

if ($CheckRawXml) {
    $sevenZip = $null
    $command = Get-Command 7z.exe -ErrorAction SilentlyContinue
    if ($command) {
        $sevenZip = $command.Source
    }
    elseif (Test-Path -LiteralPath "C:\Program Files\7-Zip\7z.exe") {
        $sevenZip = "C:\Program Files\7-Zip\7z.exe"
    }

    if (-not $sevenZip) {
        Add-Issue "深度检查需要 7-Zip，但没有找到 7z.exe"
    }
    else {
        foreach ($result in $results) {
            $relativeRaw = $result.raw_result.Replace("/", "\")
            $rawPath = Join-Path (Join-Path $packageRoot "results") $relativeRaw
            if (-not (Test-Path -LiteralPath $rawPath -PathType Leaf)) { continue }

            try {
                $xmlText = (& $sevenZip e -so $rawPath 2>$null) -join [Environment]::NewLine
                if ($LASTEXITCODE -ne 0) { throw "7-Zip exit code $LASTEXITCODE" }
                [xml]$rawXml = $xmlText
                $statusNode = @($rawXml.SelectNodes("/result/run/column[@title='status']"))
                if ($statusNode.Count -ne 1) {
                    Add-Issue "原始 XML 的 status 列异常：$($result.run_id)"
                }
                elseif ($statusNode[0].GetAttribute("value") -ne $result.status) {
                    Add-Issue "原始 XML 状态与 results.csv 不一致：$($result.run_id)"
                }
            }
            catch {
                Add-Issue "原始 XML 无法解压或解析：$($result.run_id)"
            }
        }
    }
}

if ($issues.Count -gt 0) {
    Write-Host ""
    $issues | ForEach-Object { Write-Host "[FAIL] $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "核验失败，共 $($issues.Count) 项。" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] 22 个任务和 SHA256" -ForegroundColor Green
Write-Host "[OK] 88 份配置、SHA256 和资源限制" -ForegroundColor Green
Write-Host "[OK] 22 × 4 运行组合与 88 条结果" -ForegroundColor Green
Write-Host "[OK] 88 份原始 XML 文件" -ForegroundColor Green
if ($CheckRawXml) {
    Write-Host "[OK] 88 份原始 XML 可解压、可解析，状态一致" -ForegroundColor Green
}
Write-Host "交付包核验通过。" -ForegroundColor Green
