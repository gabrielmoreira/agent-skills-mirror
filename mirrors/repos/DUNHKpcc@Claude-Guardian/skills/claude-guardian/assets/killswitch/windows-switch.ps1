param(
    [Parameter(Mandatory=$true)][ValidateSet('Status','Audit','Preview','Snapshot','On','Confirm','Off','Uninstall','Recover')][string]$Action,
    [Parameter(Mandatory=$true)][string]$Config,
    [int]$WriterPid,
    [long]$WriterStarted
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$cfg = Get-Content -LiteralPath $Config -Raw -Encoding UTF8 | ConvertFrom-Json
if ($cfg.version -ne 1 -or $cfg.backend -ne 'windows_firewall' -or $cfg.target -ne [Environment]::MachineName) { throw 'Wrong target or schema' }
$settings = $cfg.windows
if ($settings.mode -ne 'whole_machine' -and $Action -notin @('Off','Uninstall','Recover')) { throw 'Legacy configuration is recovery-only; restore it before configuring whole_machine' }
$names = @($settings.enable_rules) + @($settings.disable_rules)
$autoDisable = $settings.mode -eq 'whole_machine' -and @($settings.disable_rules).Count -eq 0
if (@($settings.enable_rules).Count -eq 0 -or ($names | Select-Object -Unique).Count -ne $names.Count) { throw 'Invalid rule list' }
foreach ($name in $names) { if ($name -notmatch '^[A-Za-z0-9_.-]+$') { throw 'Use exact rule Name' } }
$state = [string]$settings.state_path
if (-not [IO.Path]::IsPathRooted($state)) { throw 'Use absolute state path' }
$task = 'ClaudeGuardian-Switch-Fuse'
$fuseScript = Join-Path (Split-Path -Parent $state) 'fuse.ps1'
$fuseConfig = Join-Path (Split-Path -Parent $state) 'fuse-config.json'
$profiles = @('Domain','Private','Public')

function Index-Unique($items, $property) {
    $index = @{}
    foreach ($item in $items) {
        $key = [string]$item.$property
        if ($index.ContainsKey($key)) { $index[$key] = $null }
        else { $index[$key] = $item }
    }
    return $index
}

function Read-Policy($store) {
    $rules = @(Get-NetFirewallRule -PolicyStore $store)
    @{
        store=$store
        profiles=@(Get-NetFirewallProfile -PolicyStore $store)
        rules=$rules
        byName=(Index-Unique $rules Name)
        filters=@{}
    }
}

function Get-RuleFilter($rule, $policy, $kind) {
    if (-not $policy.filters.ContainsKey($kind)) {
        # Match CIM InstanceID within one store. Enumeration order is not an association.
        $filters = @(& "Get-NetFirewall${kind}Filter" -PolicyStore $policy.store -All)
        $policy.filters[$kind] = Index-Unique $filters InstanceID
    }
    $match = $policy.filters[$kind][[string]$rule.InstanceID]
    if ($null -eq $match) { throw 'Missing or ambiguous firewall filter' }
    return $match
}

function Get-RuleConditions($rule, $policy) {
    $app = Get-RuleFilter $rule $policy Application
    $service = Get-RuleFilter $rule $policy Service
    $iface = Get-RuleFilter $rule $policy Interface
    $type = Get-RuleFilter $rule $policy InterfaceType
    $conditions = [ordered]@{
        Program=[string]$app.Program; Package=[string]$app.Package
        Service=[string]$service.Service
        InterfaceAlias=@($iface.InterfaceAlias | Sort-Object); InterfaceType=[string]$type.InterfaceType
        Direction=[string]$rule.Direction; Action=[string]$rule.Action; Profile=[string]$rule.Profile
    }
    $address = Get-RuleFilter $rule $policy Address
    $port = Get-RuleFilter $rule $policy Port
    $security = Get-RuleFilter $rule $policy Security
    $conditions.LocalAddress = @($address.LocalAddress | Sort-Object)
    $conditions.RemoteAddress = @($address.RemoteAddress | Sort-Object)
    $conditions.Protocol = [string]$port.Protocol
    $conditions.LocalPort = @($port.LocalPort | Sort-Object)
    $conditions.RemotePort = @($port.RemotePort | Sort-Object)
    $conditions.IcmpType = @($port.IcmpType | Sort-Object)
    $conditions.DynamicTarget = [string]$port.DynamicTarget
    foreach ($field in @('Authentication','Encryption','OverrideBlockRules','LocalUser','RemoteUser','RemoteMachine')) {
        $conditions[$field] = [string]$security.$field
    }
    $conditions.EdgeTraversalPolicy = [string]$rule.EdgeTraversalPolicy
    $conditions.LooseSourceMapping = [string]$rule.LooseSourceMapping
    $conditions.LocalOnlyMapping = [string]$rule.LocalOnlyMapping
    $conditions.PolicyAppId = [string]$rule.PolicyAppId
    return $conditions
}

function Get-DisableRules($baseline) {
    if ($null -ne $baseline.auto_disable_rules) { return $baseline.auto_disable_rules }
    return $settings.disable_rules
}

function Get-Coverage($baseline, $active, $stored, [switch]$Planned, [switch]$Audit, [switch]$CheckWhitelist) {
    $result = @{status='unknown';message='Actual egress acceptance is separate from firewall configuration.'}
    try {
        if ($baseline.mode -ne 'whole_machine') {
            return @{status='unknown';message='Whole-machine mode needs a reviewed whole-machine snapshot; old baseline remains usable for recovery.'}
        }
        if ($null -eq $active) { $active = Read-Policy ActiveStore }
        if ($null -eq $stored -and ($Audit -or $CheckWhitelist)) { $stored = Read-Policy PersistentStore }
        # A new effective Allow can bypass default Block.
        $disabled = @(Get-DisableRules $baseline)
        foreach ($policy in (@($active,$stored) -ne $null)) {
            $allowed = @($policy.rules | Where-Object {
                if ([string]$_.Direction -ne 'Outbound' -or [string]$_.Action -ne 'Allow') { return $false }
                if ($Planned) { ($settings.enable_rules -contains $_.Name) -or ([string]$_.Enabled -eq 'True' -and $disabled -notcontains $_.Name) }
                else { [string]$_.Enabled -eq 'True' }
            })
            if ((@($allowed.Name | Sort-Object) -join ',') -ne (@($settings.enable_rules | Sort-Object) -join ',')) {
                return @{status='fail';message='Effective outbound allow list differs from the reviewed list; review unexpected, duplicate or missing rules.'}
            }
            if (-not $Planned) {
                $effectiveProfiles = $policy.profiles
                if ((@($effectiveProfiles.Name | Sort-Object) -join ',') -ne 'Domain,Private,Public' -or
                    @($effectiveProfiles | Where-Object { [string]$_.Enabled -ne 'True' -or [string]$_.DefaultOutboundAction -ne 'Block' }).Count -gt 0) {
                    return @{status='fail';message='All three effective profiles must be enabled with outbound default Block.'}
                }
            }
        }
        if (-not ($Audit -or $CheckWhitelist)) {
            $result.message = 'Quick status. Run audit to check rule conditions, paths, services and interfaces.'
            return $result
        }
        $conditionPolicy = if ($Planned -and -not $Audit) { $stored } else { $active }
        $adapterAliases = $null
        $ipAliases = $null
        foreach ($name in $settings.enable_rules) {
            $rule = $conditionPolicy.byName[$name]
            $savedRule = $stored.byName[$name]
            if ($null -eq $rule -or $null -eq $savedRule) { return @{status='fail';message='Configured rule missing or ambiguous.'} }
            $conditions = Get-RuleConditions $rule $conditionPolicy
            $currentJson = $conditions | ConvertTo-Json -Depth 6 -Compress
            if ($Audit) {
                $expected = Get-RuleConditions $savedRule $stored
                if ($currentJson -ne ($expected | ConvertTo-Json -Depth 6 -Compress)) { return @{status='fail';message='Active and persistent rule conditions differ.'} }
            }
            $old = @($baseline.rules | Where-Object { $_.Name -eq $name })
            if ($old.Count -ne 1 -or $null -eq $old[0].conditions.RemoteAddress) { return @{status='unknown';message='Reviewed egress conditions missing from baseline.'} }
            if ($old.Count -eq 1 -and $null -ne $old[0].conditions -and $currentJson -ne ($old[0].conditions | ConvertTo-Json -Depth 6 -Compress)) { return @{status='fail';message='Rule conditions changed since the reviewed baseline.'} }
            if ($conditions.Direction -ne 'Outbound' -or $conditions.Action -ne 'Allow') { return @{status='fail';message='Whole-machine enable_rules must be the complete reviewed outbound allow list.'} }
            if ($conditions.Program -eq 'Any' -and $conditions.Service -eq 'Any' -and ($conditions.InterfaceAlias -join ',') -eq 'Any' -and
                ($conditions.RemoteAddress -join ',') -eq 'Any' -and $conditions.Protocol -eq 'Any') {
                return @{status='fail';message='Unrestricted outbound allow rule is incompatible with whole-machine protection.'}
            }
            if (-not $Audit) { continue }
            $program = $conditions.Program
            if ($program -and $program -notin @('Any','System')) {
                if (-not (Test-Path -LiteralPath ([Environment]::ExpandEnvironmentVariables($program)) -PathType Leaf)) { return @{status='fail';message='Configured program path no longer exists; review the updated installation.'} }
            }
            if ($conditions.Service -and $conditions.Service -ne 'Any') {
                if (-not (Get-Service -Name $conditions.Service -ErrorAction Stop)) { return @{status='fail';message='Configured service missing.'} }
            }
            foreach ($alias in $conditions.InterfaceAlias) {
                if ($alias -eq 'Any') { continue }
                if ($null -eq $adapterAliases) { $adapterAliases = @((Get-NetAdapter -IncludeHidden).Name) }
                if ($adapterAliases -contains $alias) { continue }
                # Windows software loopback appears in the IP interface table only.
                if ($null -eq $ipAliases) { $ipAliases = @((Get-NetIPInterface).InterfaceAlias) }
                if ($ipAliases -notcontains $alias) { return @{status='unknown';message='Configured firewall interface not found.'} }
            }
        }
        return @{status='pass';message='Reviewed whole-machine outbound configuration matches. Claude installation inventory is not used. Actual egress acceptance is separate.'}
    } catch {
        $result.message = 'Application, service, interface or effective outbound policy readback unavailable; coverage is unknown.'
    }
    return $result
}
function Get-Snapshot($stored, $active) {
    $p = @($stored.profiles | Select-Object Name,Enabled,DefaultOutboundAction)
    $activeProfiles = @($active.profiles | Select-Object Name,Enabled,DefaultOutboundAction)
    if ($p.Count -ne 3 -or $activeProfiles.Count -ne 3) { throw 'Incomplete baseline profiles' }
    $snapshotNames = $names
    if ($autoDisable) {
        $discovered = @(($stored.rules + $active.rules) | Where-Object {
            [string]$_.Enabled -eq 'True' -and [string]$_.Direction -eq 'Outbound' -and
            [string]$_.Action -eq 'Allow' -and $_.Name -notin $settings.enable_rules
        } | Select-Object -ExpandProperty Name | Sort-Object -Unique)
        foreach ($name in $discovered) {
            if ($name -notmatch '^[A-Za-z0-9_.{}-]+$') { throw 'Cannot select an outbound rule by exact name' }
            if ($null -eq $stored.byName[$name] -or [string]$stored.byName[$name].Enabled -ne 'True') {
                throw 'An effective outbound allow rule cannot be managed in the local policy store'
            }
        }
        $snapshotNames = @($settings.enable_rules) + $discovered
    }
    $r = @(foreach ($name in $snapshotNames) {
        $savedRule = $stored.byName[$name]
        $liveRule = $active.byName[$name]
        if ($null -eq $savedRule -or $null -eq $liveRule) { throw 'Missing or ambiguous baseline rule' }
        $entry = [ordered]@{Name=$savedRule.Name;Enabled=$savedRule.Enabled}
        if ($settings.enable_rules -contains $name) { $entry.conditions = Get-RuleConditions $savedRule $stored }
        [pscustomobject]$entry
    })
    $activeRules = @(foreach ($name in $snapshotNames) { $active.byName[$name] | Select-Object Name,Enabled })
    $snapshot = @{ target=$cfg.target; mode=$settings.mode; profiles=$p; rules=$r; active_profiles=$activeProfiles; active_rules=$activeRules; names=@($snapshotNames | Sort-Object) }
    if ($autoDisable) { $snapshot.auto_disable_rules = $discovered }
    return $snapshot
}

function Read-Baseline {
    $b = Get-Content -LiteralPath $state -Raw -Encoding UTF8 | ConvertFrom-Json
    $expectedNames = $names
    if ($null -ne $b.auto_disable_rules) {
        if (-not $autoDisable) { throw 'Rule selection changed; review baseline' }
        $expectedNames = @($settings.enable_rules) + @($b.auto_disable_rules)
    }
    if ($b.target -ne $cfg.target -or @($b.profiles).Count -ne 3 -or @($b.rules).Count -ne $expectedNames.Count) { throw 'Baseline mismatch' }
    if ((@($b.names) -join ',') -ne (@($expectedNames | Sort-Object) -join ',')) { throw 'Rules changed; review baseline' }
    return $b
}
function Assert-BaselineRestored($baseline) {
    foreach ($store in @('PersistentStore','ActiveStore')) {
        $policy = Read-Policy $store
        $current = $policy.profiles
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
            $actual = $policy.byName[$r.Name]
            if ($null -eq $actual -or [int]$actual.Enabled -ne [int]$r.Enabled) { throw 'Restore rule mismatch; recovery task retained' }
        }
    }
}
function Set-RuleStateChanges($policy, $targetNames, $enabled) {
    $changes = @(foreach ($name in $targetNames) {
        $rule = $policy.byName[$name]
        if ($null -eq $rule) { throw 'Configured rule missing or ambiguous' }
        $actual = if ($enabled -is [string]) { [string]$rule.Enabled } else { [int]$rule.Enabled }
        if ($actual -ne $enabled) { $rule }
    })
    if ($changes.Count -gt 0) {
        # Reuse the already enumerated PersistentStore instances and skip name-based WMI queries.
        Set-NetFirewallRule -InputObject $changes -Enabled $enabled -ThrottleLimit 32 -Confirm:$false
    }
}

function Restore-Baseline {
    $b = Read-Baseline
    $stored = Read-Policy PersistentStore
    # Restore only the exact profile values and rule states recorded in the baseline.
    foreach ($p in $b.profiles) {
        $actual = @($stored.profiles | Where-Object { $_.Name -eq $p.Name })
        if ($actual.Count -ne 1) { throw 'Restore profile readback incomplete; recovery task retained' }
        if ([int]$actual[0].Enabled -ne [int]$p.Enabled -or [int]$actual[0].DefaultOutboundAction -ne [int]$p.DefaultOutboundAction) {
            Set-NetFirewallProfile -PolicyStore PersistentStore -Profile $p.Name -Enabled $p.Enabled -DefaultOutboundAction $p.DefaultOutboundAction
        }
    }
    foreach ($group in ($b.rules | Group-Object -Property { $_.Enabled })) {
        Set-RuleStateChanges $stored $group.Group.Name $group.Group[0].Enabled
    }
    Assert-BaselineRestored $b
    if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $task -Confirm:$false }
}

function Get-State($active, $stored, $coverage, $baseline, [switch]$Audit, [switch]$CheckWhitelist) {
    if ($null -eq $baseline -and -not (Test-Path -LiteralPath $state)) { return @{protection='unknown';startup=$null;coverage=@{scope=$settings.mode;status='unknown';message='Baseline missing.'};message='Create a baseline before enabling protection.';checked_at=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()} }
    $b = if ($null -eq $baseline) { Read-Baseline } else { $baseline }
    if ($null -eq $active) { $active = Read-Policy ActiveStore }
    $p = $active.profiles
    $on = $p.Count -eq 3
    $off = $p.Count -eq 3
    foreach ($profile in $p) {
        $old = @($b.profiles | Where-Object { $_.Name -eq $profile.Name })
        $on = $on -and ([string]$profile.Enabled -eq 'True') -and ([string]$profile.DefaultOutboundAction -eq 'Block')
        $off = $off -and $old.Count -eq 1 -and ([int]$profile.Enabled -eq [int]$old[0].Enabled) -and ([int]$profile.DefaultOutboundAction -eq [int]$old[0].DefaultOutboundAction)
    }
    $baselineRules = Index-Unique $b.rules Name
    foreach ($name in $b.names) {
        $r = $active.byName[$name]
        if ($null -eq $r) { $on=$false; $off=$false; continue }
        $wanted = if ($settings.enable_rules -contains $name) {'True'} else {'False'}
        $old = $baselineRules[$name]
        $on = $on -and ([string]$r.Enabled -eq $wanted)
        $off = $off -and $null -ne $old -and ([int]$r.Enabled -eq [int]$old.Enabled)
    }
    $label = if ($on) {'on'} elseif ($off) {'off'} else {'unknown'}
    $startup = if ($on) {$true} elseif ($off) {$false} else {$null}
    if ($null -eq $coverage) { $coverage = Get-Coverage $b $active $stored -Planned:($label -eq 'off') -Audit:$Audit -CheckWhitelist:$CheckWhitelist }
    $coverage.stage = if ($label -eq 'off') {'planned'} else {'effective'}
    $coverage.scope = 'whole_machine'
    @{protection=$label;startup=$startup;coverage=$coverage;planned_disable_count=@(Get-DisableRules $b).Count;message='Switch configuration read back only; application coverage and egress acceptance are separate.';checked_at=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()}
}
function Assert-Fuse($phase) {
    $entry = Get-ScheduledTask -TaskName $task
    $deadline = [DateTimeOffset]::Parse($entry.Triggers[0].StartBoundary)
    if ($entry.Triggers[0].Id -ne $phase -or [string]$entry.State -ne 'Ready' -or
        $deadline -le [DateTimeOffset]::Now.AddSeconds(5)) { throw 'Recovery deadline expired or recovery started' }
}

function Set-FusePhase($before, $after, $seconds) {
    Assert-Fuse $before
    $deadline = (Get-Date).AddSeconds($seconds)
    $trigger = New-ScheduledTaskTrigger -Once -At $deadline
    $trigger.Id = $after
    Set-ScheduledTask -TaskName $task -Trigger $trigger | Out-Null
    Assert-Fuse $after
    return ([DateTimeOffset]$deadline).ToUnixTimeSeconds()
}

function Assert-Enabled($current) {
    if ($current.protection -ne 'on' -or $current.coverage.status -eq 'fail' -or
        ($current.coverage.status -ne 'pass')) {
        throw 'Switch configuration or application coverage failed'
    }
}

function Restore-ExpiredSwitch {
    # The independent task stops only the process recorded when the fuse was armed.
    $writer = if ($WriterPid -gt 0) { Get-Process -Id $WriterPid -ErrorAction SilentlyContinue }
    if ($null -ne $writer -and $writer.StartTime.ToUniversalTime().Ticks -eq $WriterStarted) {
        Stop-Process -InputObject $writer -Force
        if (-not $writer.WaitForExit(10000)) { throw 'Switch writer still running; recovery will retry' }
    }
    Restore-Baseline
}

if ($Action -notin @('Status','Audit','Preview')) {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Administrator required' }
}
if ($Action -in @('Preview','Snapshot')) {
    if (Test-Path -LiteralPath $state) { throw 'Baseline already exists; do not overwrite' }
    $stored = Read-Policy PersistentStore
    $active = Read-Policy ActiveStore
    $b = Get-Snapshot $stored $active
    $coverage = Get-Coverage $b $active $stored -Planned -Audit
    if ($coverage.status -ne 'pass') { throw "Whole-machine plan not verified: $($coverage.message)" }
    foreach ($p in $b.profiles) { if ([string]$p.DefaultOutboundAction -ne 'Allow' -or [string]$p.Enabled -ne 'True') { throw 'Baseline must have enabled profiles with explicit Allow; inspect the pre-deployment backup' } }
    if ($Action -eq 'Snapshot') {
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
    Get-State $active $stored $coverage $b | ConvertTo-Json -Depth 6 -Compress
    exit 0
}

switch ($Action) {
    'On' {
        $baseline = Read-Baseline
        $stored = Read-Policy PersistentStore
        $active = Read-Policy ActiveStore
        if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { throw 'Previous fuse still exists; recover first' }
        $before = Get-State $active $stored $null $baseline -CheckWhitelist
        if ($before.coverage.status -ne 'pass') { throw 'Coverage not verified; existing rules retained' }
        if ($before.protection -eq 'on') {
            $before | ConvertTo-Json -Depth 6 -Compress
            exit 0
        }
        if ($before.protection -ne 'off') { throw 'Switch state is mixed; recover first' }
        if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { throw 'Previous fuse still exists; recover first' }
        Copy-Item -LiteralPath $PSCommandPath -Destination $fuseScript -Force
        $cfg | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $fuseConfig -Encoding UTF8
        $configPath = $fuseConfig
        if ($configPath.Contains('"') -or $PSCommandPath.Contains('"')) { throw 'Invalid path' }
        $writerStarted = (Get-Process -Id $PID).StartTime.ToUniversalTime().Ticks
        $argsText = '-NoProfile -ExecutionPolicy Bypass -File "' + $fuseScript + '" -Action Recover -Config "' + $configPath + '" -WriterPid ' + $PID + ' -WriterStarted ' + $writerStarted
        $ticket = [guid]::NewGuid().ToString('N')
        $applying = "GuardianSwitch-applying-$ticket"
        $waiting = "GuardianSwitch-waiting-$ticket"
        $taskAction = New-ScheduledTaskAction -Execute "$PSHOME\powershell.exe" -Argument $argsText
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(240)
        $trigger.Id = $applying
        $taskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        Register-ScheduledTask -TaskName $task -Action $taskAction -Trigger $trigger -Settings $taskSettings -User SYSTEM -RunLevel Highest | Out-Null
        try {
            Assert-Fuse $applying
            Set-RuleStateChanges $stored $settings.enable_rules True
            Set-RuleStateChanges $stored @(Get-DisableRules $baseline) False
            $changedProfiles = @($stored.profiles | Where-Object { [string]$_.Enabled -ne 'True' -or [string]$_.DefaultOutboundAction -ne 'Block' })
            if ($changedProfiles.Count -gt 0) {
                Set-NetFirewallProfile -PolicyStore PersistentStore -Profile $changedProfiles.Name -Enabled True -DefaultOutboundAction Block
            }
            $current = Get-State -CheckWhitelist
            Assert-Enabled $current
            $current.keep_until = Set-FusePhase $applying $waiting 180
        } catch { Restore-Baseline; throw }
        $current | ConvertTo-Json -Depth 6 -Compress
        exit 0
    }
    'Confirm' {
        $waiting = (Get-ScheduledTask -TaskName $task).Triggers[0].Id
        if ($waiting -notmatch '^GuardianSwitch-waiting-[0-9a-f]{32}$') { throw 'Switch is not waiting for KEEP' }
        $checking = $waiting.Replace('-waiting-','-checking-')
        $null = Set-FusePhase $waiting $checking 240
        $current = Get-State -CheckWhitelist
        Assert-Enabled $current
        Assert-Fuse $checking
        Unregister-ScheduledTask -TaskName $task -Confirm:$false
        $current | ConvertTo-Json -Depth 6 -Compress
        exit 0
    }
    'Recover' { Restore-ExpiredSwitch; exit 0 }
    { $_ -in 'Off','Uninstall' } {
        Restore-Baseline
        if ($Action -eq 'Uninstall') {
            Remove-Item -LiteralPath $state
            foreach ($file in @($fuseScript,$fuseConfig)) { if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file } }
        }
        @{protection='off';startup=$false;message='Baseline restored; original firewall rules retained.';checked_at=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()} | ConvertTo-Json -Compress
        exit 0
    }
}
Get-State -Audit:($Action -eq 'Audit') | ConvertTo-Json -Depth 6 -Compress
