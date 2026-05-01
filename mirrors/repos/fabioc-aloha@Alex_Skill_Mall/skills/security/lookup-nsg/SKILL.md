---
type: skill
lifecycle: stable
inheritance: inheritable
name: lookup-nsg
description: Finds the Network Interface Card (NIC) and associated Network Security Group (NSG) for a VM given its public IP address.
tier: standard
applyTo: '**/*lookup*,**/*nsg*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Skill: NSG Lookup

Finds the Network Interface Card (NIC) and associated Network Security Group (NSG) for a VM given its public IP address.

## Step 1 — Find the Public IP Resource

Run via PowerShell:

```powershell
Search-AzGraph -Query "resources | where type =~ 'microsoft.network/publicipaddresses' | where properties.ipAddress == '<IP_ADDRESS>' | project publicIpName=name, resourceGroup, subscriptionId, ipAddress=properties.ipAddress, attachedResource=properties.ipConfiguration.id"
```

Replace `<IP_ADDRESS>` with the user's IP. If no results, tell the user the IP was not found and ask them to verify.

## Step 2 — Look Up the NIC and NSG

Extract the NIC resource ID from `attachedResource` by removing the `/ipConfigurations/...` suffix. Then:

```powershell
Search-AzGraph -Query "resources | where type =~ 'microsoft.network/networkinterfaces' | where id == '<NIC_RESOURCE_ID>' | project nicName=name, nicNsgId=properties.networkSecurityGroup.id, subnetId=properties.ipConfigurations[0].properties.subnet.id"
```

## Step 3 — Present Results

Show a summary table:

| Property | Value |
|----------|-------|
| **Public IP** | (ip address) |
| **Public IP Resource** | (name) |
| **Resource Group** | (resource group) |
| **Subscription** | (subscription id) |
| **NIC Name** | (nic name) |
| **Associated NSG** | (nsg id, or "None") |
| **Subnet** | (subnet id) |

If the NIC has **no NSG**, warn the user it is unprotected.

Extract the **NSG name**, **resource group**, and **subscription ID** from the results to pass into the NSG Remediation skill.
