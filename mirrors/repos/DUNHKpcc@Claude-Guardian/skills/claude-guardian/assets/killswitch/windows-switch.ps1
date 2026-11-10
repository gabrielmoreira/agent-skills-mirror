param(
    [Parameter(Mandatory=$true)][ValidateSet('Status','Snapshot','On','Confirm','Off','Uninstall')][string]$Action,
    [Parameter(Mandatory=$true)][string]$Config
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$cfg = Get-Content -LiteralPath $Config -Raw -Encoding UTF8 | ConvertFrom-Json
if ($cfg.version -ne 1 -or $cfg.backend -ne 'windows_firewall' -or $cfg.target -ne [Environment]::MachineName) { throw 'Wrong target or schema' }
$settings = $cfg.windows
$names = @($settings.enable_rules) + @($settings.disable_rules)
if (@($settings.enable_rules).Count -eq 0 -or ($names | Select-Object -Unique).Count -ne $names.Count) { throw 'Invalid rule list' }
foreach ($name in $names) { if ($name -notmatch '^[A-Za-z0-9_.-]+$') { throw 'Use exact rule Name' } }
$state = [string]$settings.state_path
if (-not [IO.Path]::IsPathRooted($state)) { throw 'Use absolute state path' }
$task = 'ClaudeGuardian-Switch-Fuse'
$fuseScript = Join-Path (Split-Path -Parent $state) 'fuse.ps1'
$fuseConfig = Join-Path (Split-Path -Parent $state) 'fuse-config.json'
$profiles = @('Domain','Private','Public')

function Get-Snapshot {
    $p = @(Get-NetFirewallProfile -PolicyStore PersistentStore | Select-Object Name,Enabled,DefaultOutboundAction)
    $r = @(foreach ($name in $names) { Get-NetFirewallRule -PolicyStore PersistentStore -Name $name | Select-Object Name,Enabled })
    if ($p.Count -ne 3 -or $r.Count -ne $names.Count) { throw 'Incomplete baseline' }
    @{ target=$cfg.target; profiles=$p; rules=$r; names=@($names | Sort-Object) }
}
function Read-Baseline {
    $b = Get-Content -LiteralPath $state -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($b.target -ne $cfg.target -or @($b.profiles).Count -ne 3 -or @($b.rules).Count -ne $names.Count) { throw 'Baseline mismatch' }
    if ((@($b.names) -join ',') -ne (@($names | Sort-Object) -join ',')) { throw 'Rules changed; review baseline' }
    return $b
}
function Restore-Baseline {
    $b = Read-Baseline
    # Restore only the settings this switch owns, not a machine-wide firewall import.
    foreach ($p in $b.profiles) { Set-NetFirewallProfile -PolicyStore PersistentStore -Profile $p.Name -Enabled $p.Enabled -DefaultOutboundAction $p.DefaultOutboundAction }
    foreach ($r in $b.rules) { Set-NetFirewallRule -PolicyStore PersistentStore -Name $r.Name -Enabled $r.Enabled }
    if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $task -Confirm:$false }
}
function Get-State {
    if (-not (Test-Path -LiteralPath $state)) { return @{protection='unknown';startup=$null;message='Create a baseline before enabling protection.';checked_at=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()} }
    $b = Read-Baseline
    $p = @(Get-NetFirewallProfile -PolicyStore ActiveStore)
    $on = $p.Count -eq 3
    $off = $p.Count -eq 3
    foreach ($profile in $p) {
        $old = @($b.profiles | Where-Object { $_.Name -eq $profile.Name })
        $on = $on -and ([string]$profile.Enabled -eq 'True') -and ([string]$profile.DefaultOutboundAction -eq 'Block')
        $off = $off -and $old.Count -eq 1 -and ([int]$profile.Enabled -eq [int]$old[0].Enabled) -and ([int]$profile.DefaultOutboundAction -eq [int]$old[0].DefaultOutboundAction)
    }
    foreach ($name in $names) {
        $r = @(Get-NetFirewallRule -PolicyStore ActiveStore -Name $name)
        if ($r.Count -ne 1) { $on=$false; $off=$false; continue }
        $wanted = if ($settings.enable_rules -contains $name) {'True'} else {'False'}
        $old = @($b.rules | Where-Object { $_.Name -eq $name })
        $on = $on -and ([string]$r[0].Enabled -eq $wanted)
        $off = $off -and $old.Count -eq 1 -and ([int]$r[0].Enabled -eq [int]$old[0].Enabled)
    }
    $label = if ($on) {'on'} elseif ($off) {'off'} else {'unknown'}
    $startup = if ($on) {$true} elseif ($off) {$false} else {$null}
    @{protection=$label;startup=$startup;message='Effective profiles and configured rules read back; egress acceptance is separate.';checked_at=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()}
}
if ($Action -ne 'Status') {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Administrator required' }
}
switch ($Action) {
    'Snapshot' {
        if (Test-Path -LiteralPath $state) { throw 'Baseline already exists; do not overwrite' }
        $b = Get-Snapshot
        foreach ($p in $b.profiles) { if ([string]$p.DefaultOutboundAction -ne 'Allow' -or [string]$p.Enabled -ne 'True') { throw 'Baseline must have enabled profiles with explicit Allow; inspect the pre-deployment backup' } }
        $parent = Split-Path -Parent $state
        $expected = Join-Path $env:ProgramData 'ClaudeGuardian\Switch'
        if ([IO.Path]::GetFullPath($parent) -ne [IO.Path]::GetFullPath($expected)) { throw 'Baseline must be in ProgramData/ClaudeGuardian/Switch' }
        if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
        $acl = New-Object Security.AccessControl.DirectorySecurity
        $acl.SetAccessRuleProtection($true, $false)
        foreach ($sid in @('S-1-5-18','S-1-5-32-544')) {
            $rule = New-Object Security.AccessControl.FileSystemAccessRule((New-Object Security.Principal.SecurityIdentifier($sid)), 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
            $acl.AddAccessRule($rule)
        }
        Set-Acl -LiteralPath $parent -AclObject $acl
        $b | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $state -Encoding UTF8
    }
    'On' {
        $null = Read-Baseline
        if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { throw 'Previous fuse still exists; recover first' }
        Copy-Item -LiteralPath $PSCommandPath -Destination $fuseScript -Force
        $cfg | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $fuseConfig -Encoding UTF8
        $configPath = $fuseConfig
        if ($configPath.Contains('"') -or $PSCommandPath.Contains('"')) { throw 'Invalid path' }
        $argsText = '-NoProfile -ExecutionPolicy Bypass -File "' + $fuseScript + '" -Action Off -Config "' + $configPath + '"'
        $taskAction = New-ScheduledTaskAction -Execute "$PSHOME\powershell.exe" -Argument $argsText
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(180)
        $taskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable
        Register-ScheduledTask -TaskName $task -Action $taskAction -Trigger $trigger -Settings $taskSettings -User SYSTEM -RunLevel Highest | Out-Null
        try {
            foreach ($name in $settings.enable_rules) { Set-NetFirewallRule -PolicyStore PersistentStore -Name $name -Enabled True }
            foreach ($name in $settings.disable_rules) { Set-NetFirewallRule -PolicyStore PersistentStore -Name $name -Enabled False }
            Set-NetFirewallProfile -PolicyStore PersistentStore -Profile $profiles -Enabled True -DefaultOutboundAction Block
        } catch { Restore-Baseline; throw }
    }
    'Confirm' {
        if ((Get-State).protection -ne 'on') { throw 'Effective protection not on' }
        Unregister-ScheduledTask -TaskName $task -Confirm:$false
    }
    'Off' { Restore-Baseline }
    'Uninstall' {
        Restore-Baseline
        if ((Get-State).protection -ne 'off') { throw 'Baseline restore not verified' }
        Remove-Item -LiteralPath $state
        foreach ($file in @($fuseScript,$fuseConfig)) { if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file } }
        @{protection='off';startup=$false;message='Baseline restored; original firewall rules retained.'} | ConvertTo-Json -Compress
        exit 0
    }
}
Get-State | ConvertTo-Json -Depth 6 -Compress
