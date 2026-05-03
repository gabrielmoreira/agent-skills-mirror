---
type: skill
lifecycle: stable
inheritance: inheritable
name: create-associate-nsg
description: Creates a new Network Security Group and associates it with the specified subnets and/or NICs of a Virtual Network.
tier: standard
applyTo: '**/*create*,**/*associate*,**/*nsg*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Skill: Create and Associate NSG

Creates a new Network Security Group and associates it with the specified subnets and/or NICs of a Virtual Network. Typically run after the **NSG Lookup for VNet** skill identifies unprotected resources.

**Required inputs:** VNet name, VNet resource group, subscription ID, new NSG name, Azure region/location.  
**Optional inputs:** List of subnet names to associate, list of NIC names (with their resource groups) to associate. If not specified, the skill associates with all subnets and NICs that currently have no NSG.

---

## Pre-flight Check

Before creating anything, show the user what will be changed:

```powershell
Set-AzContext -SubscriptionId "<SUBSCRIPTION_ID>"
$vnet = Get-AzVirtualNetwork -Name "<VNET_NAME>" -ResourceGroupName "<VNET_RESOURCE_GROUP>"

# Subnets without an NSG
$unprotectedSubnets = $vnet.Subnets | Where-Object { -not $_.NetworkSecurityGroup }
$unprotectedSubnets | Select-Object Name, AddressPrefix | Format-Table -AutoSize

# NICs without an NSG (scoped to subnets of this VNet)
$allSubnetIds = $vnet.Subnets.Id
$unprotectedNics = Get-AzNetworkInterface | Where-Object {
    ($_.IpConfigurations | Where-Object { $allSubnetIds -contains $_.Subnet.Id }) -and
    (-not $_.NetworkSecurityGroup)
}
$unprotectedNics | Select-Object Name, ResourceGroupName | Format-Table -AutoSize
```

Present a confirmation prompt:

> The following will be created and associated:
> - **New NSG:** `<NSG_NAME>` in resource group `<RESOURCE_GROUP>`, location `<LOCATION>`
> - **Subnets to associate:** (list)
> - **NICs to associate:** (list)
>
> Proceed? (yes / no)

**Do NOT continue until the user confirms.**

---

## Step 1 — Create the NSG

```powershell
Set-AzContext -SubscriptionId "<SUBSCRIPTION_ID>"
$nsg = New-AzNetworkSecurityGroup `
    -Name "<NSG_NAME>" `
    -ResourceGroupName "<RESOURCE_GROUP>" `
    -Location "<LOCATION>"

Write-Output "Created NSG: $($nsg.Id)"
```

If the command fails, show the error and stop.

---

## Step 2 — Associate with Subnets

For each subnet to associate, update the subnet config on the VNet and commit:

```powershell
$vnet = Get-AzVirtualNetwork -Name "<VNET_NAME>" -ResourceGroupName "<VNET_RESOURCE_GROUP>"

foreach ($subnetName in @("<SUBNET_NAME_1>", "<SUBNET_NAME_2>")) {
    $subnet = $vnet.Subnets | Where-Object { $_.Name -eq $subnetName }

    if ($subnet.NetworkSecurityGroup) {
        Write-Warning "Subnet '$subnetName' already has NSG '$($subnet.NetworkSecurityGroup.Id.Split('/')[-1])' — skipping."
        continue
    }

    Set-AzVirtualNetworkSubnetConfig `
        -Name $subnetName `
        -VirtualNetwork $vnet `
        -AddressPrefix $subnet.AddressPrefix `
        -NetworkSecurityGroup $nsg | Out-Null

    Write-Output "Staged NSG association for subnet: $subnetName"
}

# Commit all subnet changes in one call
$vnet | Set-AzVirtualNetwork | Out-Null
Write-Output "Committed subnet NSG associations."
```

If any subnet already has an NSG, skip it and warn — do **not** overwrite an existing NSG without explicit user instruction.

---

## Step 3 — Associate with NICs

For each NIC to associate:

```powershell
foreach ($entry in @(
    @{ Name = "<NIC_NAME_1>"; ResourceGroup = "<NIC_RG_1>" },
    @{ Name = "<NIC_NAME_2>"; ResourceGroup = "<NIC_RG_2>" }
)) {
    $nic = Get-AzNetworkInterface -Name $entry.Name -ResourceGroupName $entry.ResourceGroup

    if ($nic.NetworkSecurityGroup) {
        Write-Warning "NIC '$($entry.Name)' already has NSG '$($nic.NetworkSecurityGroup.Id.Split('/')[-1])' — skipping."
        continue
    }

    $nic.NetworkSecurityGroup = $nsg
    $nic | Set-AzNetworkInterface | Out-Null
    Write-Output "Associated NSG with NIC: $($entry.Name)"
}
```

If any NIC already has an NSG, skip it and warn — do **not** overwrite.

---

## Step 4 — Verify Associations

Re-fetch and confirm every targeted subnet and NIC now shows the NSG:

```powershell
# Verify subnets
$vnet = Get-AzVirtualNetwork -Name "<VNET_NAME>" -ResourceGroupName "<VNET_RESOURCE_GROUP>"
$vnet.Subnets | Select-Object Name, @{N='NSG';E={
    if ($_.NetworkSecurityGroup) { $_.NetworkSecurityGroup.Id.Split('/')[-1] } else { '— None —' }
}} | Format-Table -AutoSize

# Verify NICs
foreach ($entry in @(
    @{ Name = "<NIC_NAME_1>"; ResourceGroup = "<NIC_RG_1>" }
)) {
    $nic = Get-AzNetworkInterface -Name $entry.Name -ResourceGroupName $entry.ResourceGroup
    $nsgAssoc = if ($nic.NetworkSecurityGroup) { $nic.NetworkSecurityGroup.Id.Split('/')[-1] } else { '— None —' }
    Write-Output "NIC: $($entry.Name) | NSG: $nsgAssoc"
}
```

---

## Step 5 — Output Summary

Provide a summary table:

| Resource Type | Resource Name | NSG Associated | NSG Name |
|---------------|---------------|----------------|----------|
| Subnet        | (name)        | ✅ Yes          | (nsg name) |
| Subnet        | (name)        | ✅ Yes          | (nsg name) |
| NIC           | (name)        | ✅ Yes          | (nsg name) |

Also output the NSG Resource ID:
```
/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.Network/networkSecurityGroups/<NSG_NAME>
```

> **Next step:** The NSG has no rules yet — it will deny all traffic by default (Azure default deny-all). Run the **NSG Remediation** skill to apply M365NetIsoNsg compliance rules, or add rules manually.

---

## Safety Rules

- ⚠️ Always show the pre-flight summary and require user confirmation before creating or associating anything
- ⚠️ Never overwrite an existing NSG association — skip and warn instead
- ⚠️ A newly created NSG with no rules uses Azure default rules: deny all inbound from Internet, allow VNet-to-VNet, allow Azure Load Balancer — inform the user so they are not surprised
- ⚠️ Subnet NSG changes require updating and re-committing the parent VNet object — do not set subnet config without calling `Set-AzVirtualNetwork`
- ⚠️ If any PowerShell command fails, show the error and do NOT continue to the next step
