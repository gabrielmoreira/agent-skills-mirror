param(
    [ValidateSet('Start','Status','Commit','Recover','Worker','Step')][string]$Action = 'Status',
    [string]$Plan,
    [string]$StepId,
    [ValidateSet('Prepare','Apply','Check','Restore','CheckRestore')][string]$Operation,
    [string]$Permit
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$Root = Join-Path $env:ProgramData 'ClaudeGuardian\NetworkTransaction'
$TaskName = 'ClaudeGuardian-NetworkTransaction'
$PowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

function Save-State($directory, $state) {
    $path = Join-Path $directory 'state.json'
    $tmp = $path + '.new'
    $state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $tmp -Encoding UTF8
    if (Test-Path -LiteralPath $path) { [IO.File]::Replace($tmp, $path, [NullString]::Value) }
    else { [IO.File]::Move($tmp, $path) }
}
function Read-State($directory) {
    $path = Join-Path $directory 'state.json'
    # Readers must allow atomic replacement; Windows may briefly hold the rename handle.
    for ($attempt=0; ; $attempt++) {
        try {
            $stream = [IO.File]::Open($path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
            break
        } catch [IO.IOException], [UnauthorizedAccessException] {
            if ($attempt -ge 9) { throw }
            Start-Sleep -Milliseconds 50
        }
    }
    $reader = New-Object IO.StreamReader($stream)
    try { $reader.ReadToEnd() | ConvertFrom-Json }
    finally { $reader.Dispose() }
}
function Write-Failure($directory, $failure) {
    $failure | Out-String | Add-Content -LiteralPath (Join-Path $directory 'worker-errors.log') -Encoding UTF8
}
function Test-Terminal($state) { $state.phase -in @('committed','restored','prepare_failed') }
function Get-ScriptHash($path) {
    # Python launched from pwsh can pass PS7 module paths to Windows PowerShell 5.1.
    $stream = [IO.File]::OpenRead($path)
    $hash = [Security.Cryptography.SHA256]::Create()
    try { [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-', '') }
    finally { $stream.Dispose(); $hash.Dispose() }
}
function Read-Plan($path) {
    $p = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($p.version -ne 1 -or $p.target -ne [Environment]::MachineName -or
        ($p.timeout_seconds -isnot [long] -and $p.timeout_seconds -isnot [int])) { throw 'Invalid plan or target' }
    if ($p.timeout_seconds -lt 60 -or $p.timeout_seconds -gt 1800 -or
        @($p.steps).Count -lt 1 -or @($p.steps).Count -gt 20 -or
        [string]::IsNullOrWhiteSpace($p.restore_goal)) { throw 'Invalid recovery scope' }
    $ids = @()
    foreach ($step in $p.steps) {
        if ($step.id -notmatch '^[a-zA-Z0-9_-]{1,40}$' -or $ids -contains $step.id -or
            ($step.script -notmatch '^[a-zA-Z0-9_-]+\.ps1$' -or $step.script -eq 'worker.ps1') -or [string]::IsNullOrWhiteSpace($step.scope)) { throw 'Invalid step' }
        if (@($step.PSObject.Properties.Name | Where-Object { $_ -notin @('id','script','scope') }).Count) { throw 'Unknown step field' }
        $ids += $step.id
        $script = Get-Item -LiteralPath (Join-Path (Split-Path -Parent $path) $step.script)
        if ($script.PSIsContainer -or ($script.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Use ordinary local scripts' }
        $step | Add-Member -NotePropertyName sha256 -NotePropertyValue (Get-ScriptHash $script.FullName)
    }
    return $p
}
function Stop-Step($directory) {
    $record = Join-Path $directory 'child.json'
    if (-not (Test-Path -LiteralPath $record)) { return }
    $saved = Get-Content -LiteralPath $record -Raw -Encoding UTF8 | ConvertFrom-Json
    $child = Get-Process -Id $saved.pid -ErrorAction SilentlyContinue
    if ($child -and $child.StartTime.ToUniversalTime().Ticks -eq $saved.started) {
        & "$env:SystemRoot\System32\taskkill.exe" /PID $child.Id /T /F | Out-Null
        if (-not $child.WaitForExit(5000)) { throw 'STEP_STILL_RUNNING' }
    }
    Remove-Item -LiteralPath $record
}
function Invoke-Step($directory, $step, $operation, $seconds = 30) {
    $script = Join-Path $directory $step.script
    if ((Get-ScriptHash $script) -ne $step.sha256) { throw 'Step script changed' }
    $permit = [guid]::NewGuid().ToString('N')
    $argsText = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + (Join-Path $directory 'worker.ps1') + '" -Action Step -StepId ' + $step.id + ' -Operation ' + $operation + ' -Permit ' + $permit
    $child = Start-Process -FilePath $PowerShell -ArgumentList $argsText -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $directory ($step.id + '.stdout.log')) `
        -RedirectStandardError (Join-Path $directory ($step.id + '.stderr.log'))
    # Windows PowerShell 5.1 needs the handle retained before exit to read ExitCode.
    $null = $child.Handle
    # The child waits for permission until its exact process identity is retained for recovery.
    @{pid=$child.Id; started=$child.StartTime.ToUniversalTime().Ticks} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $directory 'child.json') -Encoding UTF8
    New-Item -ItemType File -Path (Join-Path $directory $permit) | Out-Null
    if (-not $child.WaitForExit([Math]::Max(1, $seconds) * 1000)) {
        Stop-Step $directory
        throw 'Step timed out'
    }
    $child.Refresh()
    Remove-Item -LiteralPath (Join-Path $directory 'child.json')
    Remove-Item -LiteralPath (Join-Path $directory $permit) -ErrorAction SilentlyContinue
    if ($child.ExitCode -ne 0) { throw "Step failed (exit code '$($child.ExitCode)'); inspect private step log" }
}
function Run-Step($directory, $id, $operation, $permit) {
    if ($permit -notmatch '^[a-f0-9]{32}$') { throw 'Invalid step permission' }
    $state = Read-State $directory
    $step = @($state.steps | Where-Object { $_.id -eq $id })
    if ($state.target -ne [Environment]::MachineName -or $step.Count -ne 1) { throw 'Step target mismatch' }
    $script = Join-Path $directory $step[0].script
    if ((Get-ScriptHash $script) -ne $step[0].sha256) { throw 'Step changed' }
    for ($i=0; $i -lt 100; $i++) {
        if (Test-Path -LiteralPath (Join-Path $directory $permit)) {
            & $script -Operation $operation -Snapshot (Join-Path $directory ($id + '.snapshot.json'))
            return
        }
        Start-Sleep -Milliseconds 100
    }
    throw 'Parent did not retain child identity; no step executed'
}
function Restore-Transaction($directory, $state) {
    $state.phase = 'restoring'; Save-State $directory $state
    $failed = @()
    # Include the step that failed midway, not only previously successful steps.
    for ($i = @($state.started).Count - 1; $i -ge 0; $i--) {
        $id = $state.started[$i]
        if (@($state.restored) -contains $id) { continue }
        $step = @($state.steps | Where-Object { $_.id -eq $id })[0]
        try {
            Invoke-Step $directory $step 'Restore'
            Invoke-Step $directory $step 'CheckRestore'
            $state.restored = @($state.restored) + $id
        } catch {
            Write-Failure $directory $_
            if ($_.Exception.Message -eq 'STEP_STILL_RUNNING') { throw }
            $failed += $id
        }
        $state.failed = $failed; Save-State $directory $state
    }
    $state.failed = $failed
    $state.phase = if ($failed.Count) {'recovery_failed'} else {'restored'}
    Save-State $directory $state
}
function Run-Transaction($directory) {
    $state = Read-State $directory
    if ($state.target -ne [Environment]::MachineName) { throw 'Transaction target changed' }
    if (Test-Terminal $state) { return }
    if (-not (Test-Path -LiteralPath (Join-Path $directory 'released'))) { return }
    Stop-Step $directory
    # An interrupted worker never resumes writes. It returns to the captured baseline.
    if ($state.phase -notin @('queued','awaiting_commit')) {
        Restore-Transaction $directory $state
        return
    }
    if ($state.phase -eq 'queued') {
        try {
            $state.phase = 'preparing'; Save-State $directory $state
            foreach ($step in $state.steps) {
                Invoke-Step $directory $step 'Prepare'
                if (-not (Test-Path -LiteralPath (Join-Path $directory ($step.id + '.snapshot.json')) -PathType Leaf)) { throw 'Snapshot missing' }
                Invoke-Step $directory $step 'CheckRestore'
            }
        } catch {
            Write-Failure $directory $_
            if ($_.Exception.Message -eq 'STEP_STILL_RUNNING') { throw }
            $state.phase = 'prepare_failed'; Save-State $directory $state
            return
        }
        $state.deadline = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() + $state.timeout_seconds
        $state.phase = 'armed'; Save-State $directory $state
        try {
            foreach ($step in $state.steps) {
                if ((Test-Path -LiteralPath (Join-Path $directory 'recover')) -or
                    [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() -ge $state.deadline) { throw 'Recovery requested or deadline reached' }
                $state.phase = 'applying'; $state.started = @($state.started) + $step.id
                Save-State $directory $state
                $remaining = [Math]::Min(30, $state.deadline - [DateTimeOffset]::UtcNow.ToUnixTimeSeconds())
                Invoke-Step $directory $step 'Apply' $remaining
                Invoke-Step $directory $step 'Check'
            }
            $state.phase = 'awaiting_commit'; Save-State $directory $state
        } catch {
            Write-Failure $directory $_
            if ($_.Exception.Message -eq 'STEP_STILL_RUNNING') { throw }
            Restore-Transaction $directory $state
            return
        }
    }
    while ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() -lt $state.deadline) {
        if (Test-Path -LiteralPath (Join-Path $directory 'recover')) { break }
        if ((Test-Path -LiteralPath (Join-Path $directory 'commit')) -and
            (Get-Content -LiteralPath (Join-Path $directory 'commit') -Raw).Trim() -eq $state.id) {
            try {
                foreach ($step in $state.steps) { Invoke-Step $directory $step 'Check' }
                if ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() -ge $state.deadline -or
                    (Test-Path -LiteralPath (Join-Path $directory 'recover'))) { throw 'Commit expired' }
                $state.phase = 'committed'; Save-State $directory $state
                return
            } catch {
                Write-Failure $directory $_
                if ($_.Exception.Message -eq 'STEP_STILL_RUNNING') { throw }
                break
            }
        }
        Start-Sleep -Seconds 1
    }
    Restore-Transaction $directory $state
}
function Require-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Administrator required' }
}
function Confirm-Local($phrase) {
    if ([Console]::IsInputRedirected) { throw 'Interactive local confirmation required' }
    if ((Read-Host "输入 $phrase 继续") -cne $phrase) { throw 'Cancelled' }
}
function Start-Transaction($path) {
    $path = [IO.Path]::GetFullPath($path)
    $p = Read-Plan $path
    if ((Test-Path -LiteralPath $Root) -and -not (Test-Path -LiteralPath (Join-Path $Root 'state.json'))) { throw 'Incomplete private directory; inspect before starting a new plan' }
    if (Test-Path -LiteralPath (Join-Path $Root 'state.json')) {
        if (-not (Test-Terminal (Read-State $Root))) { throw 'Previous transaction unresolved; inspect or recover first' }
    }
    Write-Host ('目标：' + $p.target + "`n恢复目标：" + $p.restore_goal)
    foreach ($step in $p.steps) { Write-Host ($step.id + ': ' + $step.scope + ' [' + $step.script + ' SHA256 ' + $step.sha256 + ']') }
    Write-Host '整批操作由临时 SYSTEM 计划任务执行；断网或关闭终端不取消恢复。请先审核每步脚本、备份与恢复目标，退出受保护业务。未确认会恢复原状态，可能恢复直连。'
    Confirm-Local ('START ' + $p.target)
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        if ((Get-ScheduledTask -TaskName $TaskName).State -eq 'Running') { throw 'Previous worker still running' }
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    if (Test-Path -LiteralPath $Root) { Move-Item -LiteralPath $Root -Destination ($Root + '-' + [guid]::NewGuid().ToString('N')) }
    New-Item -ItemType Directory -Path $Root -Force | Out-Null
    $acl = New-Object Security.AccessControl.DirectorySecurity
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($sid in @('S-1-5-18','S-1-5-32-544')) {
        $acl.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule((New-Object Security.Principal.SecurityIdentifier($sid)), 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')))
    }
    Set-Acl -LiteralPath $Root -AclObject $acl
    Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $Root 'worker.ps1')
    foreach ($step in $p.steps) {
        Copy-Item -LiteralPath (Join-Path (Split-Path -Parent $path) $step.script) -Destination (Join-Path $Root $step.script)
        if ((Get-ScriptHash (Join-Path $Root $step.script)) -ne $step.sha256) { throw 'Plan script changed since review' }
    }
    $state = [pscustomobject]@{version=1; id=[guid]::NewGuid().ToString('N'); target=$p.target; phase='queued';
        timeout_seconds=$p.timeout_seconds; deadline=0; steps=@($p.steps); started=@(); restored=@(); failed=@()}
    Save-State $Root $state
    $taskAction = New-ScheduledTaskAction -Execute $PowerShell -Argument ('-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + (Join-Path $Root 'worker.ps1') + '" -Action Worker')
    $timer = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1)
    $boot = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $TaskName -Action $taskAction -Trigger @($timer,$boot) -Settings $settings -User SYSTEM -RunLevel Highest | Out-Null
    $registered = Get-ScheduledTask -TaskName $TaskName
    if ($registered.Actions.Execute -ne $PowerShell -or $registered.Actions.Arguments -ne $taskAction.Arguments -or
        $registered.Principal.UserId -notin @('SYSTEM','S-1-5-18') -or $registered.State -eq 'Disabled' -or
        @($registered.Actions).Count -ne 1 -or @($registered.Triggers).Count -ne 2 -or
        $registered.Settings.RunOnlyIfNetworkAvailable -or $registered.Settings.DisallowStartIfOnBatteries -or
        $registered.Settings.StopIfGoingOnBatteries -or -not $registered.Settings.StartWhenAvailable -or
        $registered.Settings.MultipleInstances -ne $settings.MultipleInstances) { throw 'Recovery task readback failed; no network writes started' }
    New-Item -ItemType File -Path (Join-Path $Root 'released') | Out-Null
    Start-ScheduledTask -TaskName $TaskName
    Write-Host ('事务已交给本机任务，编号 ' + $state.id + '。用 Status 查看；实际网络验收通过后再 Commit，否则自动恢复。')
}

Require-Administrator
switch ($Action) {
    'Start' { Start-Transaction $Plan }
    'Step' { Run-Step $Root $StepId $Operation $Permit }
    'Worker' {
        $mutex = New-Object Threading.Mutex($false, 'Global\ClaudeGuardian-NetworkTransaction')
        $locked = $false
        try {
            try { $locked = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $locked = $true }
            if ($locked) {
                Run-Transaction $Root
                if (Test-Terminal (Read-State $Root)) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false }
            }
        } finally {
            if ($locked) { $mutex.ReleaseMutex() }
            $mutex.Dispose()
        }
    }
    'Commit' {
        $state = Read-State $Root
        if ($state.phase -ne 'awaiting_commit' -or [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() -ge $state.deadline) { throw 'No transaction awaiting confirmation' }
        Write-Host '请确认实际网络、Agent 控制连接和出口验收均通过；规则读回不代替真实验收。'
        Confirm-Local ('KEEP ' + $state.id)
        $state.id | Set-Content -LiteralPath (Join-Path $Root 'commit') -Encoding UTF8
    }
    'Recover' {
        $state = Read-State $Root
        if (Test-Terminal $state) { throw 'Transaction already finished' }
        if (-not (Test-Path -LiteralPath (Join-Path $Root 'released'))) {
            $state.phase = 'prepare_failed'; Save-State $Root $state
            if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false }
            break
        }
        New-Item -ItemType File -Path (Join-Path $Root 'recover') -Force | Out-Null
        Start-ScheduledTask -TaskName $TaskName
    }
    'Status' {
        $state = Read-State $Root
        $state | Select-Object id,target,phase,deadline,started,restored,failed | ConvertTo-Json -Depth 5
    }
}
