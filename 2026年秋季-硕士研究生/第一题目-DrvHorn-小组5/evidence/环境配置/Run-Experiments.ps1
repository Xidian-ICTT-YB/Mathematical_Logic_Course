param(
    [ValidateSet('Selected', 'All')][string]$Suite = 'Selected',
    [string]$Distro = 'DrvHorn-Ubuntu22.04',
    [ValidateRange(1, 3600)][int]$TimeoutSeconds = 500
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$OutputEncoding = [Text.UTF8Encoding]::new($false)
$image = 'joehattori/drvhorn@sha256:536168e391d7c08c8247276dafc4a518ac68a1a5fcea44068f5c03b5b345f80c'
& wsl.exe -d $Distro -u drvhorn --exec docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'The experiment WSL distribution and Docker must be ready first.' }
$projectDirectory = Split-Path -Parent $PSScriptRoot
$cases = @()
if ($Suite -eq 'Selected') {
    $cases = @(
        [pscustomobject]@{Name='tpm_bios_measurements_ops';Option='--file-operations=tpm_bios_measurements_ops';GroundTruth='sat';Category='real-bug';AuthorReported='sat'},
        [pscustomobject]@{Name='ged_driver';Option='--platform-driver=ged_driver';GroundTruth='unsat';Category='no-bug';AuthorReported='unsat'},
        [pscustomobject]@{Name='acpi_wmi_driver';Option='--platform-driver=acpi_wmi_driver';GroundTruth='unsat';Category='false-positive';AuthorReported='sat'}
    )
} else {
    $evaluationScript = Join-Path $projectDirectory 'drvhorn\scripts\eval.sh'
    foreach ($line in Get-Content -LiteralPath $evaluationScript -Encoding UTF8) {
        if ($line -match '^expected\[([^\]]+)\]=(sat|unsat)\s*$') {
            $name = $Matches[1]
            $truth = $Matches[2]
            $reported = $null
            if ($name -eq 'acpi_wmi_driver') { $reported = 'sat' }
            $cases += [pscustomobject]@{Name=$name;Option="--platform-driver=$name";GroundTruth=$truth;Category='author-lightweight-suite';AuthorReported=$reported}
        }
    }
    if ($cases.Count -eq 0) { throw 'No driver cases were found in the author evaluation script.' }
}
$runDirectory = Join-Path (Join-Path $projectDirectory 'experiment-results') (Get-Date -Format 'yyyyMMdd-HHmmss')
New-Item -ItemType Directory -Path $runDirectory -Force | Out-Null
$summaryPath = Join-Path $runDirectory 'summary.json'
$results = @()
foreach ($case in $cases) {
    Write-Output ("Running {0}..." -f $case.Name)
    $stdoutPath = Join-Path $runDirectory ($case.Name + '.stdout.txt')
    $stderrPath = Join-Path $runDirectory ($case.Name + '.stderr.txt')
    $dockerArguments = @('-d', $Distro, '-u', 'drvhorn', '--exec', 'docker', 'run', '--rm', '--network', 'none', $image,
        'timeout', '--kill-after=10s', [string]$TimeoutSeconds, '/drvhorn/build/run/bin/sea', 'kernel', $case.Option, '/drvhorn/simple_kernel.bc')
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $ErrorActionPreference = 'Continue'
    & wsl.exe @dockerArguments 1> $stdoutPath 2> $stderrPath
    $commandExit = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    $watch.Stop()
    $solverLines = @(Get-Content -LiteralPath $stdoutPath | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^(sat|unsat)$' })
    $actual = 'unknown'
    if ($commandExit -eq 124 -or $commandExit -eq 137) { $actual = 'timeout-or-killed' }
    elseif ($commandExit -ne 0) { $actual = 'execution-error' }
    elseif ($solverLines.Count -eq 1) { $actual = $solverLines[0] }
    $matchesAuthor = $null
    if ($null -ne $case.AuthorReported) { $matchesAuthor = ($actual -eq $case.AuthorReported) }
    $results += [pscustomobject]@{
        name = $case.Name
        category = $case.Category
        expectedGroundTruth = $case.GroundTruth
        authorReportedObservation = $case.AuthorReported
        actualObservation = $actual
        matchesGroundTruth = ($actual -eq $case.GroundTruth)
        matchesAuthorReportedObservation = $matchesAuthor
        exitCode = $commandExit
        elapsedSeconds = [math]::Round($watch.Elapsed.TotalSeconds, 3)
        wslArguments = $dockerArguments
        stdoutFile = $stdoutPath
        stderrFile = $stderrPath
    }
    $summary = [ordered]@{image=$image;suite=$Suite;distro=$Distro;timeoutSeconds=$TimeoutSeconds;results=$results}
    [IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
    Write-Output ("{0}: observed={1}, ground-truth={2}, exit={3}" -f $case.Name, $actual, $case.GroundTruth, $commandExit)
}
Write-Output ("Results: {0}" -f $summaryPath)
$unresolved = @($results | Where-Object { $_.actualObservation -notin @('sat', 'unsat') })
if ($unresolved.Count -gt 0) { exit 1 }
