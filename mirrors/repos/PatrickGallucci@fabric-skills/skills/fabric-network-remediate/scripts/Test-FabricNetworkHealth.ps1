<#
.SYNOPSIS
    Tests Microsoft Fabric network health and diagnoses connectivity issues.

.DESCRIPTION
    Performs automated network diagnostics for Microsoft Fabric environments including
    endpoint reachability, DNS resolution, private endpoint validation, firewall
    endpoint auditing, and Spark startup assessment.

.PARAMETER WorkspaceId
    The Fabric workspace ID to diagnose. Required for PrivateEndpoint and SparkStartup checks.

.PARAMETER CheckType
    The type of diagnostic check to perform.
    Valid values: All, FirewallEndpoints, DnsResolution, PrivateEndpoint, SparkStartup, OneLakeConnectivity

.PARAMETER OutputPath
    Optional path to save the diagnostic report. Defaults to ./fabric-network-report.json.

.PARAMETER Verbose
    Enable verbose output for detailed diagnostic information.

.EXAMPLE
    .\Test-FabricNetworkHealth.ps1 -CheckType FirewallEndpoints

.EXAMPLE
    .\Test-FabricNetworkHealth.ps1 -WorkspaceId "abc-123" -CheckType PrivateEndpoint

.EXAMPLE
    .\Test-FabricNetworkHealth.ps1 -CheckType All -OutputPath ./report.json
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$WorkspaceId,

    [Parameter()]
    [ValidateSet('All', 'FirewallEndpoints', 'DnsResolution', 'PrivateEndpoint', 'SparkStartup', 'OneLakeConnectivity')]
    [string]$CheckType = 'All',

    [Parameter()]
    [string]$OutputPath = './fabric-network-report.json'
)

#region Configuration
$script:FabricEndpoints = @{
    OneLakeDfs       = '*.onelake.dfs.fabric.microsoft.com'
    OneLakeBlob      = '*.onelake.blob.fabric.microsoft.com'
    OneLakeApi       = 'api.onelake.fabric.microsoft.com'
    PowerBI          = '*.powerbi.com'
    PbiDedicated     = '*.pbidedicated.windows.net'
    DataWarehouse    = '*.datawarehouse.fabric.microsoft.com'
    DWDedicated      = '*.datawarehouse.pbidedicated.windows.net'
    ServiceBus       = '*.servicebus.windows.net'
    LoginMicrosoft   = 'login.microsoftonline.com'
    AadCdn           = 'aadcdn.msauth.net'
    FrontendCDH      = '*.frontend.clouddatahub.net'
}

$script:TestEndpoints = @(
    @{ Name = 'OneLake DFS API';   Host = 'onelake.dfs.fabric.microsoft.com';        Port = 443 }
    @{ Name = 'OneLake Blob API';  Host = 'onelake.blob.fabric.microsoft.com';       Port = 443 }
    @{ Name = 'OneLake API';       Host = 'api.onelake.fabric.microsoft.com';        Port = 443 }
    @{ Name = 'Power BI Service';  Host = 'app.powerbi.com';                         Port = 443 }
    @{ Name = 'Entra ID Login';    Host = 'login.microsoftonline.com';               Port = 443 }
    @{ Name = 'Fabric DW';        Host = 'datawarehouse.fabric.microsoft.com';       Port = 443 }
)

$script:ServiceTags = @(
    @{ Tag = 'PowerBI';           Purpose = 'Fabric core + Power BI';        Direction = 'Both';     Regional = $true }
    @{ Tag = 'DataFactory';       Purpose = 'Pipeline operations';           Direction = 'Both';     Regional = $true }
    @{ Tag = 'DataFactoryMgmt';   Purpose = 'On-prem pipeline activity';     Direction = 'Outbound'; Regional = $false }
    @{ Tag = 'PowerQueryOnline';  Purpose = 'Dataflow processing';           Direction = 'Both';     Regional = $false }
    @{ Tag = 'SQL';               Purpose = 'Warehouse connectivity';        Direction = 'Outbound'; Regional = $true }
    @{ Tag = 'EventHub';          Purpose = 'Real-Time Analytics';           Direction = 'Outbound'; Regional = $true }
    @{ Tag = 'KustoAnalytics';    Purpose = 'Real-Time Analytics';           Direction = 'Both';     Regional = $false }
)
#endregion

#region Helper Functions
function Write-DiagHeader {
    param([string]$Title)
    $divider = '=' * 60
    Write-Host "`n$divider" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "$divider`n" -ForegroundColor Cyan
}

function Write-DiagResult {
    param(
        [string]$Test,
        [bool]$Passed,
        [string]$Detail = ''
    )
    $icon   = if ($Passed) { '[PASS]' } else { '[FAIL]' }
    $color  = if ($Passed) { 'Green'  } else { 'Red'    }
    Write-Host "  $icon " -ForegroundColor $color -NoNewline
    Write-Host "$Test" -NoNewline
    if ($Detail) { Write-Host " - $Detail" -ForegroundColor DarkGray } else { Write-Host '' }
}

function Write-DiagWarning {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
}

function Test-TcpPort {
    param(
        [string]$ComputerName,
        [int]$Port,
        [int]$TimeoutMs = 5000
    )
    try {
        $result = Test-NetConnection -ComputerName $ComputerName -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
        return @{
            Success     = $result
            Latency     = $null
            Error       = $null
        }
    }
    catch {
        return @{
            Success = $false
            Latency = $null
            Error   = $_.Exception.Message
        }
    }
}

function Resolve-FabricDns {
    param([string]$HostName)
    try {
        $dns = Resolve-DnsName -Name $HostName -Type A -ErrorAction Stop
        $ips = $dns | Where-Object { $_.QueryType -eq 'A' } | Select-Object -ExpandProperty IPAddress
        $isPrivate = $ips | Where-Object {
            $_ -match '^10\.' -or $_ -match '^172\.(1[6-9]|2[0-9]|3[01])\.' -or $_ -match '^192\.168\.'
        }
        return @{
            Success    = $true
            IpAddresses = $ips
            IsPrivate  = [bool]$isPrivate
            Error      = $null
        }
    }
    catch {
        return @{
            Success     = $false
            IpAddresses = @()
            IsPrivate   = $false
            Error       = $_.Exception.Message
        }
    }
}
#endregion

#region Check Functions
function Invoke-FirewallEndpointCheck {
    Write-DiagHeader 'Firewall Endpoint Reachability'

    $results = @()
    foreach ($ep in $script:TestEndpoints) {
        $test = Test-TcpPort -ComputerName $ep.Host -Port $ep.Port
        $passed = $test.Success
        Write-DiagResult -Test "$($ep.Name) ($($ep.Host):$($ep.Port))" -Passed $passed -Detail $(if (-not $passed) { $test.Error } else { 'Reachable' })
        $results += @{
            Endpoint = $ep.Name
            Host     = $ep.Host
            Port     = $ep.Port
            Passed   = $passed
            Error    = $test.Error
        }
    }

    Write-Host ''
    Write-Host '  Service Tags Required:' -ForegroundColor White
    foreach ($tag in $script:ServiceTags) {
        Write-Host "    - $($tag.Tag): $($tag.Purpose) [$($tag.Direction)]" -ForegroundColor DarkGray
    }

    return @{ Check = 'FirewallEndpoints'; Results = $results; Timestamp = (Get-Date -Format 'o') }
}

function Invoke-DnsResolutionCheck {
    Write-DiagHeader 'DNS Resolution Validation'

    $dnsTargets = @(
        'onelake.dfs.fabric.microsoft.com'
        'onelake.blob.fabric.microsoft.com'
        'api.onelake.fabric.microsoft.com'
        'app.powerbi.com'
        'login.microsoftonline.com'
    )

    $results = @()
    foreach ($target in $dnsTargets) {
        $dns = Resolve-FabricDns -HostName $target
        if ($dns.Success) {
            $ipList = $dns.IpAddresses -join ', '
            $scope  = if ($dns.IsPrivate) { 'Private' } else { 'Public' }
            Write-DiagResult -Test $target -Passed $true -Detail "$ipList ($scope)"
        }
        else {
            Write-DiagResult -Test $target -Passed $false -Detail $dns.Error
        }
        $results += @{
            Host      = $target
            Resolved  = $dns.Success
            IPs       = $dns.IpAddresses
            IsPrivate = $dns.IsPrivate
            Error     = $dns.Error
        }
    }

    return @{ Check = 'DnsResolution'; Results = $results; Timestamp = (Get-Date -Format 'o') }
}

function Invoke-PrivateEndpointCheck {
    Write-DiagHeader 'Managed Private Endpoint Validation'

    if (-not $WorkspaceId) {
        Write-DiagWarning 'WorkspaceId is required for private endpoint checks. Use -WorkspaceId parameter.'
        return @{ Check = 'PrivateEndpoint'; Results = @(); Skipped = $true; Timestamp = (Get-Date -Format 'o') }
    }

    Write-Host '  Checking prerequisites...' -ForegroundColor DarkGray

    # Check if Az module is available
    $azAvailable = Get-Module -ListAvailable -Name Az.Accounts -ErrorAction SilentlyContinue
    if (-not $azAvailable) {
        Write-DiagWarning 'Az PowerShell module not installed. Install with: Install-Module Az -Scope CurrentUser'
        Write-Host ''
        Write-Host '  Manual verification steps:' -ForegroundColor White
        Write-Host '    1. Open Fabric workspace Settings > Network security' -ForegroundColor DarkGray
        Write-Host '    2. Check Managed private endpoints status = Approved' -ForegroundColor DarkGray
        Write-Host '    3. Run nslookup <target-fqdn> from within the VNet' -ForegroundColor DarkGray
        Write-Host '    4. Verify resolved IP is in private range (10.x/172.x/192.168.x)' -ForegroundColor DarkGray
        return @{ Check = 'PrivateEndpoint'; Results = @(); Skipped = $true; Reason = 'Az module not available'; Timestamp = (Get-Date -Format 'o') }
    }

    # Check Azure context
    try {
        $context = Get-AzContext -ErrorAction Stop
        if (-not $context) {
            Write-DiagWarning 'Not logged into Azure. Run Connect-AzAccount first.'
            return @{ Check = 'PrivateEndpoint'; Results = @(); Skipped = $true; Reason = 'Not authenticated'; Timestamp = (Get-Date -Format 'o') }
        }
        Write-DiagResult -Test "Azure Context" -Passed $true -Detail "Subscription: $($context.Subscription.Name)"
    }
    catch {
        Write-DiagWarning "Azure context error: $($_.Exception.Message)"
        return @{ Check = 'PrivateEndpoint'; Results = @(); Skipped = $true; Reason = $_.Exception.Message; Timestamp = (Get-Date -Format 'o') }
    }

    Write-Host ''
    Write-Host '  Checklist for Private Endpoint Validation:' -ForegroundColor White
    Write-Host '    [?] Endpoint Status = Approved in Fabric workspace settings' -ForegroundColor Yellow
    Write-Host '    [?] DNS resolves FQDN to private IP (10.x / 172.x)' -ForegroundColor Yellow
    Write-Host '    [?] Required ports open (1433 SQL, 1521 Oracle, 443 HTTPS)' -ForegroundColor Yellow
    Write-Host '    [?] Private Link Service and Fabric in same Azure geography' -ForegroundColor Yellow
    Write-Host '    [?] Microsoft.Network resource provider registered on subscription' -ForegroundColor Yellow

    return @{ Check = 'PrivateEndpoint'; Results = @(); WorkspaceId = $WorkspaceId; Timestamp = (Get-Date -Format 'o') }
}

function Invoke-OneLakeConnectivityCheck {
    Write-DiagHeader 'OneLake Connectivity Validation'

    $onelakeEndpoints = @(
        @{ Name = 'OneLake DFS (Primary)';  Host = 'onelake.dfs.fabric.microsoft.com';  Port = 443 }
        @{ Name = 'OneLake Blob';            Host = 'onelake.blob.fabric.microsoft.com'; Port = 443 }
        @{ Name = 'OneLake API';             Host = 'api.onelake.fabric.microsoft.com';  Port = 443 }
    )

    $results = @()
    foreach ($ep in $onelakeEndpoints) {
        $test = Test-TcpPort -ComputerName $ep.Host -Port $ep.Port
        Write-DiagResult -Test $ep.Name -Passed $test.Success -Detail $(if ($test.Success) { 'Reachable on TCP 443' } else { $test.Error })
        $results += @{
            Endpoint = $ep.Name
            Host     = $ep.Host
            Passed   = $test.Success
            Error    = $test.Error
        }
    }

    Write-Host ''
    Write-Host '  Common OneLake issues:' -ForegroundColor White
    Write-Host '    - URL validation: Some ADLS tools reject dfs.fabric.microsoft.com' -ForegroundColor DarkGray
    Write-Host '    - Use custom endpoint setting if tool allows it' -ForegroundColor DarkGray
    Write-Host '    - OneLake uses ADLS Gen2 compatible APIs (DFS + Blob)' -ForegroundColor DarkGray

    return @{ Check = 'OneLakeConnectivity'; Results = $results; Timestamp = (Get-Date -Format 'o') }
}

function Invoke-SparkStartupCheck {
    Write-DiagHeader 'Spark Session Startup Assessment'

    if (-not $WorkspaceId) {
        Write-DiagWarning 'WorkspaceId is required for Spark startup checks. Use -WorkspaceId parameter.'
        return @{ Check = 'SparkStartup'; Results = @(); Skipped = $true; Timestamp = (Get-Date -Format 'o') }
    }

    Write-Host '  Factors affecting Spark startup time:' -ForegroundColor White
    Write-Host ''

    $factors = @(
        @{ Factor = 'Private Links / Managed VNets enabled'; Impact = 'High'; Detail = 'Starter Pools unavailable; cluster created on demand (+2-5 min)' }
        @{ Factor = 'Custom library dependencies';           Impact = 'Medium'; Detail = 'Library installation adds 30 sec - 5 min' }
        @{ Factor = 'Regional Starter Pool exhaustion';      Impact = 'Medium'; Detail = 'New cluster spun up (+2-5 min)' }
        @{ Factor = 'Capacity SKU size';                     Impact = 'Low';    Detail = 'Larger SKUs have higher queue limits and node counts' }
        @{ Factor = 'Cross-workspace environment';           Impact = 'Medium'; Detail = 'Must match capacity and network security settings' }
    )

    foreach ($f in $factors) {
        $color = switch ($f.Impact) { 'High' { 'Red' } 'Medium' { 'Yellow' } 'Low' { 'DarkGray' } }
        Write-Host "    [$($f.Impact.PadRight(6))] " -ForegroundColor $color -NoNewline
        Write-Host "$($f.Factor)" -NoNewline
        Write-Host " - $($f.Detail)" -ForegroundColor DarkGray
    }

    Write-Host ''
    Write-Host '  Recommendations:' -ForegroundColor White
    Write-Host '    1. If using Private Links, expect 2-5 min startup (by design)' -ForegroundColor DarkGray
    Write-Host '    2. Pre-install libraries in the Environment to reduce session time' -ForegroundColor DarkGray
    Write-Host '    3. Use resource profiles (writeHeavy, readHeavyForSpark) for workload tuning' -ForegroundColor DarkGray
    Write-Host '    4. Monitor queue depth via Monitoring Hub' -ForegroundColor DarkGray

    return @{ Check = 'SparkStartup'; Factors = $factors; WorkspaceId = $WorkspaceId; Timestamp = (Get-Date -Format 'o') }
}
#endregion

#region Main Execution
$report = @{
    DiagnosticRun = Get-Date -Format 'o'
    MachineName   = $env:COMPUTERNAME
    CheckType     = $CheckType
    WorkspaceId   = $WorkspaceId
    Checks        = @()
}

Write-Host ''
Write-Host '  Microsoft Fabric Network Diagnostics' -ForegroundColor White
Write-Host "  Run at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
Write-Host "  Check type: $CheckType" -ForegroundColor DarkGray
if ($WorkspaceId) { Write-Host "  Workspace: $WorkspaceId" -ForegroundColor DarkGray }

switch ($CheckType) {
    'All' {
        $report.Checks += Invoke-FirewallEndpointCheck
        $report.Checks += Invoke-DnsResolutionCheck
        $report.Checks += Invoke-OneLakeConnectivityCheck
        $report.Checks += Invoke-PrivateEndpointCheck
        $report.Checks += Invoke-SparkStartupCheck
    }
    'FirewallEndpoints'    { $report.Checks += Invoke-FirewallEndpointCheck }
    'DnsResolution'        { $report.Checks += Invoke-DnsResolutionCheck }
    'PrivateEndpoint'      { $report.Checks += Invoke-PrivateEndpointCheck }
    'SparkStartup'         { $report.Checks += Invoke-SparkStartupCheck }
    'OneLakeConnectivity'  { $report.Checks += Invoke-OneLakeConnectivityCheck }
}

# Save report
$report | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding utf8
Write-Host ''
Write-Host "  Report saved to: $OutputPath" -ForegroundColor Green
Write-Host ''
#endregion
