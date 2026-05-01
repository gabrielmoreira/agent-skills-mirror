# Firewall Endpoints and Allowlist Reference

## Table of Contents

- [Required Endpoints by Service](#required-endpoints-by-service)
- [Azure Service Tags](#azure-service-tags)
- [Gateway Firewall Rules](#gateway-firewall-rules)
- [PowerShell: Configure Azure Firewall Service Tags](#powershell-configure-azure-firewall-service-tags)
- [Validation Script Usage](#validation-script-usage)

## Required Endpoints by Service

### OneLake

| Purpose | Endpoint | Port |
|---------|----------|------|
| DFS APIs (primary endpoint) | `*.onelake.dfs.fabric.microsoft.com` | TCP 443 |
| Blob APIs | `*.onelake.blob.fabric.microsoft.com` | TCP 443 |
| Regional DFS (optional) | `*<region>-onelake.dfs.fabric.microsoft.com` | TCP 443 |
| Regional Blob (optional) | `*<region>-onelake.blob.fabric.microsoft.com` | TCP 443 |

### Core Fabric / Power BI

| Purpose | Endpoint | Port |
|---------|----------|------|
| Portal | `*.powerbi.com` | TCP 443 |
| Backend APIs | `*.pbidedicated.windows.net` | TCP 443 |

### Data Warehouse

| Purpose | Endpoint | Port |
|---------|----------|------|
| Warehouse connectivity | `*.datawarehouse.fabric.microsoft.com` | TCP 443 |
| Warehouse dedicated | `*.datawarehouse.pbidedicated.windows.net` | TCP 1433 |

### Pipelines

| Purpose | Endpoint | Port |
|---------|----------|------|
| Cloud pipelines | No specific endpoint | N/A |
| On-prem gateway login | `*.login.windows.net`, `login.live.com`, `aadcdn.msauth.net`, `login.microsoftonline.com`, `*.microsoftonline-p.com` | TCP 443 |
| On-prem gateway messaging | `*.servicebus.windows.net` | TCP 443, 5671-5672, 9350-9354 |
| On-prem gateway pipelines | `*.frontend.clouddatahub.net` | TCP 443 |

### Dataflow Gen2 (Behind Gateway)

| Purpose | Endpoint | Port |
|---------|----------|------|
| Staging lakehouse | `*.datawarehouse.pbidedicated.windows.net` | TCP 1433 |
| Staging lakehouse | `*.datawarehouse.fabric.microsoft.com` | TCP 1433 |
| OneLake staging | `*.dfs.fabric.microsoft.com` | TCP 443 |

**Tip**: To narrow the Dataflow endpoint scope, navigate to the Fabric workspace, locate `DataflowsStagingLakehouse`, select **View Details**, and copy the SQL connection string.

### Authentication

| Purpose | Endpoint | Port |
|---------|----------|------|
| Microsoft Entra ID | `login.microsoftonline.com` | TCP 443 |
| MSAL/Auth | `aadcdn.msauth.net` | TCP 443 |

## Azure Service Tags

Service tags simplify firewall rule management by representing groups of IP addresses managed automatically by Microsoft.

| Tag | Purpose | Direction | Regional | Azure Firewall |
|-----|---------|-----------|----------|----------------|
| `PowerBI` | Fabric core + Power BI | Inbound & Outbound | Yes | Yes |
| `DataFactory` | Pipeline operations | Inbound & Outbound | Yes | Yes |
| `DataFactoryManagement` | On-prem pipeline activity | Outbound | No | Yes |
| `PowerQueryOnline` | Dataflow processing | Inbound & Outbound | No | Yes |
| `SQL` | Warehouse connectivity | Outbound | Yes | Yes |
| `EventHub` | Real-Time Analytics | Outbound | Yes | Yes |
| `KustoAnalytics` | Real-Time Analytics | Inbound & Outbound | No | No |

**Note**: There is no service tag for untrusted code used in Data Engineering items. The `DataFactory` tag is the closest for pipeline-related network rules.

### Using Service Tags in NSG Rules

```powershell
# Example: Allow outbound to Fabric from a subnet
$rule = New-AzNetworkSecurityRuleConfig `
    -Name 'AllowFabricOutbound' `
    -Description 'Allow outbound to Microsoft Fabric' `
    -Access Allow `
    -Protocol Tcp `
    -Direction Outbound `
    -Priority 100 `
    -SourceAddressPrefix 'VirtualNetwork' `
    -SourcePortRange '*' `
    -DestinationAddressPrefix 'PowerBI' `
    -DestinationPortRange '443'
```

### Downloading Service Tag JSON

```powershell
# Download latest Azure IP ranges and service tags
$downloadUrl = 'https://www.microsoft.com/download/details.aspx?id=56519'
# Or use Az module
$tags = Get-AzNetworkServiceTag -Location 'eastus'
$fabricTags = $tags.Values | Where-Object { $_.Name -match 'PowerBI|DataFactory|SQL' }
$fabricTags | ForEach-Object {
    Write-Host "$($_.Name): $($_.Properties.AddressPrefixes.Count) prefixes"
}
```

## Gateway Firewall Rules

For on-premises data gateways connecting to Fabric:

### Required Outbound Rules

| Endpoint | Port | Protocol | Purpose |
|----------|------|----------|---------|
| `*.servicebus.windows.net` | 443, 5671-5672, 9350-9354 | TCP | Gateway relay communication |
| `login.microsoftonline.com` | 443 | TCP | Authentication |
| `*.frontend.clouddatahub.net` | 443 | TCP | Pipeline orchestration |
| `*.powerbi.com` | 443 | TCP | Fabric portal |
| `*.pbidedicated.windows.net` | 443 | TCP | Backend APIs |

### Proxy Server Considerations

If using a corporate proxy, configure the gateway to route through it:

1. Open the on-premises data gateway configuration app
2. Navigate to **Network** settings
3. Configure proxy server address and port
4. Add Fabric endpoints to the proxy allowlist

## PowerShell: Configure Azure Firewall Service Tags

```powershell
# Get existing firewall
$fw = Get-AzFirewall -Name 'MyFirewall' -ResourceGroupName 'MyRG'

# Create network rule for Fabric
$fabricRule = New-AzFirewallNetworkRule `
    -Name 'AllowFabric' `
    -Protocol TCP `
    -SourceAddress '10.0.0.0/16' `
    -DestinationAddress 'PowerBI' `
    -DestinationPort 443

$dataFactoryRule = New-AzFirewallNetworkRule `
    -Name 'AllowDataFactory' `
    -Protocol TCP `
    -SourceAddress '10.0.0.0/16' `
    -DestinationAddress 'DataFactory' `
    -DestinationPort 443

$ruleCollection = New-AzFirewallNetworkRuleCollection `
    -Name 'FabricAccess' `
    -Priority 200 `
    -ActionType Allow `
    -Rule $fabricRule, $dataFactoryRule

$fw.NetworkRuleCollections.Add($ruleCollection)
Set-AzFirewall -AzureFirewall $fw
```

## Validation Script Usage

Run the diagnostic script to verify all required endpoints are reachable:

```powershell
# Check all firewall endpoints
.\scripts\Test-FabricNetworkHealth.ps1 -CheckType FirewallEndpoints

# Full diagnostic including DNS
.\scripts\Test-FabricNetworkHealth.ps1 -CheckType All -OutputPath ./network-report.json
```

The script tests TCP connectivity to each critical endpoint and reports pass/fail status with error details.
