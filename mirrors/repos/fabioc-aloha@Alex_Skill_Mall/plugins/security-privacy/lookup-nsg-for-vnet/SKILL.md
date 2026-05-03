---
type: skill
lifecycle: stable
inheritance: inheritable
name: lookup-nsg-for-vnet
description: Checks every subnet in a Virtual Network for an associated Network Security Group, and also inspects each NIC attached to those subnets for NIC-level NSG coverage.
tier: standard
applyTo: '**/*lookup*,**/*nsg*,**/*for*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Skill: NSG Lookup for VNet

Checks every subnet in a Virtual Network for an associated Network Security Group, and also inspects each NIC attached to those subnets for NIC-level NSG coverage. Produces a full coverage report to identify unprotected resources.

**Required inputs:** VNet name, resource group, subscription ID.

---

## Step 1 — Set Azure Context and Get VNet

Run via PowerShell:

```powershell
Set-AzContext -SubscriptionId "<SUBSCRIPTION_ID>"
$vnet = Get-AzVirtualNetwork -Name "<VNET_NAME>" -ResourceGroupName "<RESOURCE_GROUP>"
```

If `$vnet` is null, tell the user the VNet was not found and ask them to verify the name, resource group, and subscription.

---

## Step 2 — Check NSG Association for Each Subnet

Run via PowerShell:

```powershell
$subnetReport = $vnet.Subnets | ForEach-Object {
    $nsgName = if ($_.NetworkSecurityGroup) { $_.NetworkSecurityGroup.Id.Split('/')[-1] } else { $null }
    [PSCustomObject]@{
        SubnetName    = $_.Name
        AddressPrefix = $_.AddressPrefix -join ', '
        NSGAssociated = if ($nsgName) { 'Yes' } else { 'No' }
        NSGName       = if ($nsgName) { $nsgName } else { '— None —' }
        NSGResourceId = if ($_.NetworkSecurityGroup) { $_.NetworkSecurityGroup.Id } else { '—' }
    }
}
$subnetReport | Format-Table -AutoSize
```

---

## Step 3 — Check NSG Association for Each NIC in the VNet

For each subnet, find all NICs whose primary IP configuration is attached to that subnet. Run via PowerShell:

```powershell
$nicReport = @()
foreach ($subnet in $vnet.Subnets) {
    $nicsInSubnet = Get-AzNetworkInterface -ResourceGroupName "<RESOURCE_GROUP>" | Where-Object {
        $_.IpConfigurations | Where-Object { $_.Subnet.Id -eq $subnet.Id }
    }
    foreach ($nic in $nicsInSubnet) {
        $nicNsgName = if ($nic.NetworkSecurityGroup) { $nic.NetworkSecurityGroup.Id.Split('/')[-1] } else { $null }
        $nicReport += [PSCustomObject]@{
            SubnetName    = $subnet.Name
            NICName       = $nic.Name
            ResourceGroup = $nic.ResourceGroupName
            NSGAssociated = if ($nicNsgName) { 'Yes' } else { 'No' }
            NSGName       = if ($nicNsgName) { $nicNsgName } else { '— None —' }
        }
    }
}
$nicReport | Format-Table -AutoSize
```

---

## Step 4 — Present Coverage Report

Output two summary tables:

### Subnet NSG Coverage

| Subnet Name | Address Prefix | NSG Associated | NSG Name |
|-------------|---------------|----------------|----------|
| (name)      | (cidr)        | Yes / No       | (name or — None —) |

### NIC NSG Coverage

| Subnet Name | NIC Name | Resource Group | NSG Associated | NSG Name |
|-------------|----------|----------------|----------------|----------|
| (subnet)    | (nic)    | (rg)           | Yes / No       | (name or — None —) |

### Coverage Summary

Report counts:
- Total subnets: N
- Subnets with NSG: N
- Subnets **without** NSG: N ⚠️
- Total NICs: N
- NICs with NIC-level NSG: N
- NICs without NIC-level NSG: N (note: covered by subnet NSG if subnet has one)

---

## Step 5 — Flag Unprotected Resources

If any subnet has **no NSG**, warn:

> ⚠️ **Subnet `<name>` has no NSG.** All traffic to/from this subnet is unrestricted. This may trigger [SFI-NS2.5.1] Overexposed Endpoints.

If a NIC has no NSG **and** its subnet also has no NSG, warn:

> ⚠️ **NIC `<name>` is fully unprotected** — neither the NIC nor its subnet (`<subnet>`) has an NSG associated.

Pass the list of unprotected subnets and NICs to the **Create and Associate NSG** skill if remediation is needed.

---

## Safety Rules

- ⚠️ This skill is read-only — it makes no changes
- ⚠️ `Get-AzNetworkInterface` without filters queries all NICs in the subscription; in large subscriptions consider scoping with `-ResourceGroupName` if the VNet and NICs share a resource group
