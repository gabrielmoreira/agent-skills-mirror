param(
    [ValidateSet('On','Off')][string]$Action,
    [string]$Config
)

function Invoke-DesktopSwitch($operation, $configPath) {
    $configPath = (Resolve-Path -LiteralPath $configPath -ErrorAction Stop).Path
    $cfg = Read-DesktopConfig $configPath $operation
    if (-not (Test-DesktopAdmin)) {
        $arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $script:EntryPath + '" -Action ' + $operation + ' -Config "' + $configPath + '"'
        $child = Start-Process -FilePath "$PSHOME\powershell.exe" -Verb RunAs -ArgumentList $arguments -PassThru -ErrorAction Stop
        try {
            # Windows PowerShell 5.1 needs the handle retained before exit to read ExitCode.
            $null = $child.Handle
            $child.WaitForExit()
            if ($child.ExitCode -ne 0) { throw '操作未完成或已取消，请查看提权窗口中的错误。' }
        } finally { $child.Dispose() }
        return
    }
    Confirm-DesktopAction $operation $cfg
    if ($operation -eq 'Off') { Assert-DesktopAppsClosed $cfg }
    Write-Host '正在应用并读回防火墙，请勿重复启动。'
    $current = Invoke-SwitchBackend $operation $configPath
    if ($operation -eq 'On') {
        # A failed On/preflight must not cancel an earlier operation's recovery task.
        if ($null -ne $current.keep_until) {
            try {
                Assert-DesktopOn $current
                Write-Host '已临时开启。核对网络和出口后，在保险丝截止前输入 KEEP；否则恢复原策略。'
                $answer = Read-Host 'KEEP'
                if ($answer -cne 'KEEP' -or [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() -ge $current.keep_until) {
                    throw '未及时保留，恢复原策略。'
                }
                $current = Invoke-SwitchBackend Confirm $configPath
                Assert-DesktopOn $current
            } catch {
                $failure = $_
                $null = Invoke-SwitchBackend Off $configPath
                throw $failure
            }
        } else { Assert-DesktopOn $current }
        Write-Host '保护配置已开启并读回；实际出口与防泄漏验收另行完成。'
    } else {
        if ($current.protection -ne 'off' -or $current.startup -ne $false) { throw '恢复结果未确认。' }
        Write-Host '已恢复基线，保护已关闭，可能恢复直连。'
    }
}

function Read-DesktopConfig($path, $operation) {
    $cfg = Get-Content -LiteralPath $path -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
    if ($cfg.version -ne 1 -or $cfg.backend -ne 'windows_firewall' -or $cfg.target -ne [Environment]::MachineName) { throw '配置与当前设备不匹配。' }
    if ($operation -eq 'On' -and $cfg.windows.mode -ne 'whole_machine') { throw '旧配置仅用于恢复；请先关闭，再由 Agent 配置整机白名单。' }
    if ($cfg.protected_processes -isnot [array] -or $cfg.protected_processes.Count -eq 0) { throw '缺少受保护进程清单。' }
    foreach ($name in $cfg.protected_processes) {
        if ($name -isnot [string] -or [string]::IsNullOrWhiteSpace($name) -or $name.Contains("`n")) { throw '受保护进程名称无效。' }
    }
    return $cfg
}

function Test-DesktopAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    return (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Confirm-DesktopAction($operation, $cfg) {
    if ([Console]::IsInputRedirected) { throw '请在本机窗口确认，不接受管道确认。' }
    Write-Host ('目标设备：' + $cfg.target)
    Write-Host '整机保护影响所有软件；代理停止可能断网，国内直连、局域网、虚拟机和远程连接须先审核例外。'
    Write-Host '关闭会恢复基线及原有出站策略。请先退出受保护应用和后台进程。'
    $phrase = $operation.ToUpperInvariant() + ' ' + $cfg.target
    if ((Read-Host ('输入 ' + $phrase + ' 继续，其他输入取消')) -cne $phrase) { throw '已取消，未修改防火墙。' }
}

function Assert-DesktopAppsClosed($cfg) {
    $names = @($cfg.protected_processes | ForEach-Object { $_ -replace '(?i)\.exe$','' })
    $running = @(Get-Process -ErrorAction Stop | Where-Object { $names -contains $_.ProcessName })
    if ($running.Count -gt 0) { throw '仍有受保护应用或后台进程运行，请退出后重试。' }
}

function Assert-DesktopOn($state) {
    if ($state.protection -ne 'on' -or $state.startup -ne $true -or $state.coverage.status -ne 'pass') { throw '未读回有效整机白名单保护。' }
}

function Invoke-SwitchBackend($operation, $configPath) {
    $limits = @{On=800;Confirm=300;Off=600}
    $info = New-Object Diagnostics.ProcessStartInfo
    $info.FileName = "$PSHOME\powershell.exe"
    $info.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $PSScriptRoot 'windows-switch.ps1') + '" -Action ' + $operation + ' -Config "' + $configPath + '"'
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.StandardOutputEncoding = New-Object Text.UTF8Encoding($false)
    $info.StandardErrorEncoding = New-Object Text.UTF8Encoding($false)
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $info
    try {
        $null = $process.Start()
        $output = $process.StandardOutput.ReadToEndAsync()
        $errors = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($limits[$operation] * 1000)) {
            $process.Kill()
            throw '防火墙操作超时，状态未确认；已有保险丝保留，请按恢复说明处理。'
        }
        $text = $output.GetAwaiter().GetResult()
        $errorText = $errors.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) { throw ('后端失败：' + $errorText) }
        return ($text.Trim().TrimStart([char]0xFEFF) | ConvertFrom-Json -ErrorAction Stop)
    } finally { $process.Dispose() }
}

$script:EntryPath = $PSCommandPath
if ($MyInvocation.InvocationName -ne '.') {
    $ErrorActionPreference = 'Stop'
    $code = 0
    try {
        if (-not $Action -or -not $Config) { throw '需要 -Action On/Off 和 -Config。' }
        Invoke-DesktopSwitch $Action $Config
    } catch { Write-Host $_.Exception.Message -ForegroundColor Red; $code = 1 }
    if (-not [Console]::IsInputRedirected) { $null = Read-Host '按回车关闭窗口' }
    exit $code
}
