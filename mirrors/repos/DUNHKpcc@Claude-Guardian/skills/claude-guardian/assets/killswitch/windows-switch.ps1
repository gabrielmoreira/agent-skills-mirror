param(
    [Parameter(Mandatory=$true)][ValidateSet('Status','Snapshot','On','Confirm','Off','Uninstall')][string]$Action,
    [Parameter(Mandatory=$true)][string]$Config
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$cfg = Get-Content -LiteralPath $Config -Raw -Encoding UTF8 | ConvertFrom-Json
if ($cfg.version -ne 1 -or $cfg.backend -ne 'windows_firewall' -or $cfg.target -ne [Environment]::MachineName) { throw 'Wrong target or schema' }
$settings = $cfg.windows
if ($null -ne $settings.mode -and $settings.mode -notin @('application_paths','whole_machine')) { throw 'Unsupported Windows mode' }
$names = @($settings.enable_rules) + @($settings.disable_rules)
if (@($settings.enable_rules).Count -eq 0 -or ($names | Select-Object -Unique).Count -ne $names.Count) { throw 'Invalid rule list' }
foreach ($name in $names) { if ($name -notmatch '^[A-Za-z0-9_.-]+$') { throw 'Use exact rule Name' } }
$state = [string]$settings.state_path
if (-not [IO.Path]::IsPathRooted($state)) { throw 'Use absolute state path' }
$task = 'ClaudeGuardian-Switch-Fuse'
$fuseScript = Join-Path (Split-Path -Parent $state) 'fuse.ps1'
$fuseConfig = Join-Path (Split-Path -Parent $state) 'fuse-config.json'
$profiles = @('Domain','Private','Public')

function Get-RuleConditions($rule) {
    $app = @($rule | Get-NetFirewallApplicationFilter)
    $service = @($rule | Get-NetFirewallServiceFilter)
    $iface = @($rule | Get-NetFirewallInterfaceFilter)
    $type = @($rule | Get-NetFirewallInterfaceTypeFilter)
    if ($app.Count -ne 1 -or $service.Count -ne 1 -or $iface.Count -ne 1 -or $type.Count -ne 1) { throw 'Incomplete rule filters' }
    $conditions = [ordered]@{
        Program=[string]$app[0].Program; Package=[string]$app[0].Package
        Service=[string]$service[0].Service
        InterfaceAlias=@($iface[0].InterfaceAlias | Sort-Object); InterfaceType=[string]$type[0].InterfaceType
        Direction=[string]$rule.Direction; Action=[string]$rule.Action; Profile=[string]$rule.Profile
    }
    if ($settings.mode -eq 'whole_machine') {
        $address = @($rule | Get-NetFirewallAddressFilter)
        $port = @($rule | Get-NetFirewallPortFilter)
        $security = @($rule | Get-NetFirewallSecurityFilter)
        if ($address.Count -ne 1 -or $port.Count -ne 1 -or $security.Count -ne 1) { throw 'Incomplete egress filters' }
        $conditions.LocalAddress = @($address[0].LocalAddress | Sort-Object)
        $conditions.RemoteAddress = @($address[0].RemoteAddress | Sort-Object)
        $conditions.Protocol = [string]$port[0].Protocol
        $conditions.LocalPort = @($port[0].LocalPort | Sort-Object)
        $conditions.RemotePort = @($port[0].RemotePort | Sort-Object)
        $conditions.IcmpType = @($port[0].IcmpType | Sort-Object)
        $conditions.DynamicTarget = [string]$port[0].DynamicTarget
        foreach ($field in @('Authentication','Encryption','OverrideBlockRules','LocalUser','RemoteUser','RemoteMachine')) {
            $conditions[$field] = [string]$security[0].$field
        }
        $conditions.EdgeTraversalPolicy = [string]$rule.EdgeTraversalPolicy
        $conditions.LooseSourceMapping = [string]$rule.LooseSourceMapping
        $conditions.LocalOnlyMapping = [string]$rule.LocalOnlyMapping
        $conditions.PolicyAppId = [string]$rule.PolicyAppId
    }
    return $conditions
}
function Get-Coverage($baseline, [switch]$Planned) {
    # Rule readback cannot discover newly added helpers or certify application traffic.
    $result = @{status='unknown';message='Current package, external runtimes and Cowork inventory require target-machine acceptance; do not resume applications from switch state alone.'}
    try {
        if ($settings.mode -eq 'whole_machine' -and $baseline.mode -ne 'whole_machine') {
            return @{status='unknown';message='Whole-machine mode needs a reviewed whole-machine snapshot; old baseline remains usable for recovery.'}
        }
        foreach ($name in $settings.enable_rules) {
            $active = @(Get-NetFirewallRule -PolicyStore ActiveStore -Name $name)
            $stored = @(Get-NetFirewallRule -PolicyStore PersistentStore -Name $name)
            if ($active.Count -ne 1 -or $stored.Count -ne 1) { return @{status='fail';message='Configured rule missing or ambiguous.'} }
            $conditions = Get-RuleConditions $active[0]
            $expected = Get-RuleConditions $stored[0]
            $currentJson = $conditions | ConvertTo-Json -Depth 6 -Compress
            if ($currentJson -ne ($expected | ConvertTo-Json -Depth 6 -Compress)) { return @{status='fail';message='Active and persistent rule conditions differ.'} }
            $old = @($baseline.rules | Where-Object { $_.Name -eq $name })
            if ($settings.mode -eq 'whole_machine' -and ($old.Count -ne 1 -or $null -eq $old[0].conditions.RemoteAddress)) { return @{status='unknown';message='Reviewed egress conditions missing from baseline.'} }
            if ($old.Count -eq 1 -and $null -ne $old[0].conditions -and $currentJson -ne ($old[0].conditions | ConvertTo-Json -Depth 6 -Compress)) { return @{status='fail';message='Rule conditions changed since the reviewed baseline.'} }
            if ($settings.mode -eq 'whole_machine') {
                if ($conditions.Direction -ne 'Outbound' -or $conditions.Action -ne 'Allow') { return @{status='fail';message='Whole-machine enable_rules must be the complete reviewed outbound allow list.'} }
                if ($conditions.Program -eq 'Any' -and $conditions.Service -eq 'Any' -and ($conditions.InterfaceAlias -join ',') -eq 'Any' -and
                    ($conditions.RemoteAddress -join ',') -eq 'Any' -and $conditions.Protocol -eq 'Any') {
                    return @{status='fail';message='Unrestricted outbound allow rule is incompatible with whole-machine protection.'}
                }
            }
            $program = $conditions.Program
            if ($program -and $program -notin @('Any','System')) {
                if (-not (Test-Path -LiteralPath ([Environment]::ExpandEnvironmentVariables($program)) -PathType Leaf)) { return @{status='fail';message='Configured program path no longer exists; review the updated installation.'} }
            }
            if ($conditions.Service -and $conditions.Service -ne 'Any') {
                if (-not (Get-Service -Name $conditions.Service -ErrorAction Stop)) { return @{status='fail';message='Configured service missing.'} }
            }
            foreach ($alias in $conditions.InterfaceAlias) {
                if ($alias -ne 'Any' -and -not (Get-NetAdapter -Name $alias -IncludeHidden -ErrorAction Stop)) { return @{status='fail';message='Configured interface missing.'} }
            }
        }
        if ($settings.mode -eq 'whole_machine') {
            # Audit the effective policy too: a newly installed Allow rule can bypass default Block.
            foreach ($store in @('PersistentStore','ActiveStore')) {
                $allowed = @(Get-NetFirewallRule -PolicyStore $store -Direction Outbound -Action Allow | Where-Object {
                    if ($Planned) { ($settings.enable_rules -contains $_.Name) -or ([string]$_.Enabled -eq 'True' -and $settings.disable_rules -notcontains $_.Name) }
                    else { [string]$_.Enabled -eq 'True' }
                })
                if ((@($allowed.Name | Sort-Object) -join ',') -ne (@($settings.enable_rules | Sort-Object) -join ',')) {
                    return @{status='fail';message='Effective outbound allow list differs from the reviewed list; review unexpected, duplicate or missing rules.'}
                }
                if (-not $Planned) {
                    $effectiveProfiles = @(Get-NetFirewallProfile -PolicyStore $store)
                    if ((@($effectiveProfiles.Name | Sort-Object) -join ',') -ne 'Domain,Private,Public' -or
                        @($effectiveProfiles | Where-Object { [string]$_.Enabled -ne 'True' -or [string]$_.DefaultOutboundAction -ne 'Block' }).Count -gt 0) {
                        return @{status='fail';message='All three effective profiles must be enabled with outbound default Block.'}
                    }
                }
            }
            return @{status='pass';message='Reviewed whole-machine outbound configuration matches. Claude installation inventory is not used. Actual egress acceptance is separate.'}
        }
    } catch {
        $result.message = 'Application, service, interface or effective outbound policy readback unavailable; coverage is unknown.'
    }
    return $result
}
function Get-Snapshot {
    $p = @(Get-NetFirewallProfile -PolicyStore PersistentStore | Select-Object Name,Enabled,DefaultOutboundAction)
    $r = @(foreach ($name in $names) { Get-NetFirewallRule -PolicyStore PersistentStore -Name $name | Select-Object Name,Enabled,@{Name='conditions';Expression={Get-RuleConditions $_}} })
    $activeProfiles = @(Get-NetFirewallProfile -PolicyStore ActiveStore | Select-Object Name,Enabled,DefaultOutboundAction)
    $activeRules = @(foreach ($name in $names) { Get-NetFirewallRule -PolicyStore ActiveStore -Name $name | Select-Object Name,Enabled })
    if ($p.Count -ne 3 -or $r.Count -ne $names.Count -or $activeProfiles.Count -ne 3 -or $activeRules.Count -ne $names.Count) { throw 'Incomplete baseline' }
    @{ target=$cfg.target; mode=$settings.mode; profiles=$p; rules=$r; active_profiles=$activeProfiles; active_rules=$activeRules; names=@($names | Sort-Object) }
}
function Read-Baseline {
    $b = Get-Content -LiteralPath $state -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($b.target -ne $cfg.target -or @($b.profiles).Count -ne 3 -or @($b.rules).Count -ne $names.Count) { throw 'Baseline mismatch' }
    if ((@($b.names) -join ',') -ne (@($names | Sort-Object) -join ',')) { throw 'Rules changed; review baseline' }
    return $b
}
function Assert-BaselineRestored($baseline) {
    foreach ($store in @('PersistentStore','ActiveStore')) {
        $current = @(Get-NetFirewallProfile -PolicyStore $store)
        if ($current.Count -ne 3) { throw 'Restore profile readback incomplete; recovery task retained' }
        $expectedProfiles = $baseline.profiles
        $expectedRules = $baseline.rules
        if ($store -eq 'ActiveStore' -and $null -ne $baseline.active_profiles) {
            $expectedProfiles = $baseline.active_profiles; $expectedRules = $baseline.active_rules
        }
        foreach ($p in $expectedProfiles) {
            $actual = @($current | Where-Object { $_.Name -eq $p.Name })
            if ($actual.Count -ne 1 -or [int]$actual[0].Enabled -ne [int]$p.Enabled -or
                [int]$actual[0].DefaultOutboundAction -ne [int]$p.DefaultOutboundAction) { throw 'Restore profile mismatch; recovery task retained' }
        }
        foreach ($r in $expectedRules) {
            $actual = @(Get-NetFirewallRule -PolicyStore $store -Name $r.Name)
            if ($actual.Count -ne 1 -or [int]$actual[0].Enabled -ne [int]$r.Enabled) { throw 'Restore rule mismatch; recovery task retained' }
        }
    }
}
function Restore-Baseline {
    $b = Read-Baseline
    # Restore only the settings this switch owns, not a machine-wide firewall import.
    foreach ($p in $b.profiles) { Set-NetFirewallProfile -PolicyStore PersistentStore -Profile $p.Name -Enabled $p.Enabled -DefaultOutboundAction $p.DefaultOutboundAction }
    foreach ($r in $b.rules) { Set-NetFirewallRule -PolicyStore PersistentStore -Name $r.Name -Enabled $r.Enabled }
    Assert-BaselineRestored $b
    if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $task -Confirm:$false }
}
function Get-State {
    if (-not (Test-Path -LiteralPath $state)) { return @{protection='unknown';startup=$null;coverage=@{scope=$settings.mode;status='unknown';message='Baseline missing.'};message='Create a baseline before enabling protection.';checked_at=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()} }
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
    $coverage = Get-Coverage $b -Planned:($label -eq 'off')
    $coverage.stage = if ($label -eq 'off') {'planned'} else {'effective'}
    $coverage.scope = if ($settings.mode -eq 'whole_machine') {'whole_machine'} else {'application_paths'}
    @{protection=$label;startup=$startup;coverage=$coverage;message='Switch configuration read back only; application coverage and egress acceptance are separate.';checked_at=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()}
}
if ($Action -ne 'Status') {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Administrator required' }
}
switch ($Action) {
    'Snapshot' {
        if (Test-Path -LiteralPath $state) { throw 'Baseline already exists; do not overwrite' }
        $b = Get-Snapshot
        if ($settings.mode -eq 'whole_machine' -and (Get-Coverage $b -Planned).status -ne 'pass') { throw 'Whole-machine plan not verified; review all outbound allow rules before snapshot' }
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
        $baseline = Read-Baseline
        $coverage = Get-Coverage $baseline -Planned
        if ($coverage.status -eq 'fail' -or ($settings.mode -eq 'whole_machine' -and $coverage.status -ne 'pass')) { throw 'Coverage not verified; existing rules retained' }
        if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { throw 'Previous fuse still exists; recover first' }
        Copy-Item -LiteralPath $PSCommandPath -Destination $fuseScript -Force
        $cfg | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $fuseConfig -Encoding UTF8
        $configPath = $fuseConfig
        if ($configPath.Contains('"') -or $PSCommandPath.Contains('"')) { throw 'Invalid path' }
        $argsText = '-NoProfile -ExecutionPolicy Bypass -File "' + $fuseScript + '" -Action Off -Config "' + $configPath + '"'
        $taskAction = New-ScheduledTaskAction -Execute "$PSHOME\powershell.exe" -Argument $argsText
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(180)
        $taskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        Register-ScheduledTask -TaskName $task -Action $taskAction -Trigger $trigger -Settings $taskSettings -User SYSTEM -RunLevel Highest | Out-Null
        try {
            foreach ($name in $settings.enable_rules) { Set-NetFirewallRule -PolicyStore PersistentStore -Name $name -Enabled True }
            foreach ($name in $settings.disable_rules) { Set-NetFirewallRule -PolicyStore PersistentStore -Name $name -Enabled False }
            Set-NetFirewallProfile -PolicyStore PersistentStore -Profile $profiles -Enabled True -DefaultOutboundAction Block
        } catch { Restore-Baseline; throw }
    }
    'Confirm' {
        $current = Get-State
        if ($current.protection -ne 'on' -or $current.coverage.status -eq 'fail' -or ($settings.mode -eq 'whole_machine' -and $current.coverage.status -ne 'pass')) { throw 'Switch configuration or application coverage failed' }
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
