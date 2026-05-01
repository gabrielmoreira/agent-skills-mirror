# Private Endpoint remediate Reference

## Table of Contents

- [Overview](#overview)
- [Verify Endpoint Status](#verify-endpoint-status)
- [Validate DNS Routing](#validate-dns-routing)
- [Common Issues and Resolutions](#common-issues-and-resolutions)
- [Managed VNet Behavior](#managed-vnet-behavior)
- [Security Best Practices](#security-best-practices)

## Overview

Managed Private Endpoints (MPE) in Microsoft Fabric enable secure connections to data sources (Azure SQL, ADLS Gen2, on-premises servers via Private Link Service) without exposing them to the public network. When enabled, Fabric creates a dedicated virtual network per workspace.

**Key behavior**: When Private Link is enabled at the tenant level or Managed VNets are enabled for a workspace, Starter Pools become unavailable. Fabric must create Spark clusters on demand, adding 2-5 minutes to session startup.

**Regional availability**: MPEs are available in most major regions including East US, West US 2, North Europe, West Europe, UK South, and others. They are **not supported** in Switzerland West and West Central US.

## Verify Endpoint Status

### In Fabric Portal

1. Open the Fabric workspace
2. Navigate to **Settings > Network security**
3. Under **Managed private endpoints**, check each endpoint's **Status**
4. Select an endpoint to view: FQDN, Connection state, Approval date, Private link resource ID

### Expected States

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| Approved | Endpoint active and usable | None |
| Pending | Awaiting approval from resource owner | Contact Azure admin to approve in Private Link Service |
| Failed | Provisioning failed | Re-create MPE; verify PLS still exists and is reachable |
| Disconnected | Previously approved, now severed | Check if PLS was deleted or workspace reassigned |

### Via PowerShell (Az Module)

```powershell
# Check subscription registration for Microsoft.Network
Get-AzResourceProvider -ProviderNamespace Microsoft.Network |
    Select-Object RegistrationState

# If not registered
Register-AzResourceProvider -ProviderNamespace Microsoft.Network
```

## Validate DNS Routing

DNS validation is critical. If the FQDN resolves to a public IP instead of a private IP, traffic bypasses the private endpoint entirely.

### From a Fabric Notebook

```python
import subprocess
result = subprocess.run(['nslookup', 'sqlserver.corp.contoso.com'], capture_output=True, text=True)
print(result.stdout)
```

### From PowerShell

```powershell
# Resolve and check if IP is private
$dns = Resolve-DnsName -Name 'sqlserver.corp.contoso.com' -Type A
$dns | ForEach-Object {
    $isPrivate = $_.IPAddress -match '^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)'
    [PSCustomObject]@{
        Name      = $_.Name
        IP        = $_.IPAddress
        IsPrivate = $isPrivate
    }
}
```

**Expected result**: IP in 10.x.x.x or 172.16-31.x.x range confirms private routing.

### Fix Public DNS Resolution

If DNS resolves to a public IP:

1. Navigate to the Azure portal > Private DNS zones
2. Locate or create the zone for your resource (e.g., `privatelink.database.windows.net`)
3. Link the zone to the Fabric workspace virtual network
4. Create an **A record** mapping the FQDN to the private endpoint IP

## Common Issues and Resolutions

| Issue | Cause | Resolution |
|-------|-------|------------|
| `ProvisioningState = Failed` | PLS rejected or deleted | Re-create MPE; verify PLS exists and is reachable |
| DNS resolves to public IP | DNS zone not linked to Fabric VNet | Add/link private DNS zone; create A record for FQDN |
| Connection timeout from Spark/Pipelines | Firewall/ACL blocking Fabric subnet | Open required ports: 1433 (SQL), 1521 (Oracle), 443 (HTTPS) |
| Approval request not visible in Azure | Auto-approval not enabled or tenant ID not listed | Ask network admin to check Private Link Service > Private endpoint connections |
| Endpoint deleted unexpectedly | Workspace or capacity reassigned | Recreate MPE; verify workspace ownership and network settings |
| Connection fails after approval | DNS or routing mismatch | Validate routing tables; use `nslookup` and `Test-NetConnection` |
| Cannot create MPE | Microsoft.Network provider not registered | Register provider on the subscription |

## Managed VNet Behavior

When Managed VNets are enabled (either explicitly or via tenant-level Private Link):

1. A managed virtual network is created **on first Spark job execution** (notebook run, Spark Job Definition, or Lakehouse Load to Table)
2. Compute clusters deploy in a **dedicated network per workspace**, isolated from the shared VNet
3. **Starter Pools become unavailable** — all clusters are created on demand
4. MPEs are created at the **workspace level** by default
5. Outbound traffic is restricted to approved private endpoints only

### Impact on Session Startup

| Configuration | Startup Time |
|---------------|-------------|
| Without VNet (Starter Pool) | 5-10 seconds |
| With Managed VNet, no libraries | 2-5 minutes |
| With Managed VNet + libraries | 2-10 minutes |

## Security Best Practices

1. **Use Azure Key Vault** for credentials and connection secrets; never hardcode passwords
2. **Limit endpoint exposure** by approving only required endpoints in Private Link Service
3. **Monitor Fabric audit logs** for endpoint creation, approval, and deletion activities
4. **Enable Customer-Managed Keys (CMK)** for encryption-at-rest with Spark workloads
5. **Restrict outbound access** using Outbound Access Protection to allow only approved endpoints
6. **Rotate credentials** and review endpoint approvals on a regular schedule
7. **Use Fabric admin API** (`Workspaces - List Networking Communication Policies`) to audit network policies across all workspaces
