---
type: skill
lifecycle: stable
inheritance: inheritable
name: remediate-nsg
description: Applies M365NetIsoNsg compliance rules to an existing Azure NSG and outputs the ARM template for Safe Deployment.
tier: standard
applyTo: '**/*remediate*,**/*nsg*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Skill: NSG Remediation

Applies M365NetIsoNsg compliance rules to an existing Azure NSG and outputs the ARM template for Safe Deployment.

**Required inputs:** NSG name, resource group, subscription ID, environment (Production/Non-Production).

## Pre-flight Check

```powershell
Set-AzContext -SubscriptionId "<SUBSCRIPTION_ID>"
$nsg = Get-AzNetworkSecurityGroup -Name "<NSG_NAME>" -ResourceGroupName "<RESOURCE_GROUP>"
$nsg.SecurityRules | Select-Object Name, Priority, Access, Direction, Protocol, SourceAddressPrefix, DestinationPortRange | Format-Table -AutoSize
```

Show existing rules. **If any rules occupy priority 100-119, STOP and warn** — they must be moved to 120+ first. Get user confirmation before proceeding.

## Apply M365NetIsoNsg Rules

The only difference between Production and Non-Production is **Rule 100**:
- **Production**: `SourceAddressPrefix "M365RemoteDesktopGateway"`
- **Non-Production**: `SourceAddressPrefix @("M365RemoteDesktopGateway","CorpNetSaw","CorpNetPublic")`

Rules 101-106 are identical for both environments.

```powershell
Set-AzContext -SubscriptionId "<SUBSCRIPTION_ID>"
$nsg = Get-AzNetworkSecurityGroup -Name "<NSG_NAME>" -ResourceGroupName "<RESOURCE_GROUP>"

# Rule 100 — Production: "M365RemoteDesktopGateway" | Non-Prod: @("M365RemoteDesktopGateway","CorpNetSaw","CorpNetPublic")
$nsg | Add-AzNetworkSecurityRuleConfig -Name "M365-NetIso-AllowRAv3SAWGateways" -Description "Please see https://aka.ms/M365NetIsoWiki for more info." -Access Allow -Protocol * -Direction Inbound -Priority 100 -SourceAddressPrefix <SEE_ABOVE> -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange 3389 | Set-AzNetworkSecurityGroup

$nsg | Add-AzNetworkSecurityRuleConfig -Name "M365-NetIso-AllowVirtualNetwork" -Description "Please see https://aka.ms/M365NetIsoWiki for more info." -Access Allow -Protocol * -Direction Inbound -Priority 101 -SourceAddressPrefix "VirtualNetwork" -SourcePortRange * -DestinationAddressPrefix "VirtualNetwork" -DestinationPortRange * | Set-AzNetworkSecurityGroup

$nsg | Add-AzNetworkSecurityRuleConfig -Name "M365-NetIso-AllowPortsFromSAWs" -Description "Please see https://aka.ms/M365NetIsoWiki for more info." -Access Allow -Protocol * -Direction Inbound -Priority 102 -SourceAddressPrefix "CorpNetSaw" -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange * | Set-AzNetworkSecurityGroup

$nsg | Add-AzNetworkSecurityRuleConfig -Name "M365-NetIso-AllowTorusManagement" -Description "Please see https://aka.ms/M365NetIsoWiki for more info." -Access Allow -Protocol * -Direction Inbound -Priority 103 -SourceAddressPrefix @("13.107.6.152/31","13.107.9.152/31","13.107.18.10/31","13.107.19.10/31","13.107.128.0/22","23.103.160.0/20","23.103.224.0/19","40.96.0.0/13","40.104.0.0/15","52.96.0.0/14","70.37.151.128/25","111.221.112.0/21","131.253.33.215/32","132.245.0.0/16","134.170.68.0/23","150.171.32.0/22","157.56.96.16/28","157.56.96.224/28","157.56.232.0/21","157.56.240.0/20","191.232.96.0/19","191.234.6.152/32","191.234.140.0/22","191.234.224.0/22","204.79.197.215/32","206.191.224.0/19") -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange 9796 | Set-AzNetworkSecurityGroup

$nsg | Add-AzNetworkSecurityRuleConfig -Name "M365-NetIso-AllowLoadBalancer" -Description "Please see https://aka.ms/M365NetIsoWiki for more info." -Access Allow -Protocol * -Direction Inbound -Priority 104 -SourceAddressPrefix "AzureLoadBalancer" -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange * | Set-AzNetworkSecurityGroup

$nsg | Add-AzNetworkSecurityRuleConfig -Name "M365-NetIso-DenyTorusManagementFromInternet" -Description "Please see https://aka.ms/M365NetIsoWiki for more info." -Access Deny -Protocol * -Direction Inbound -Priority 105 -SourceAddressPrefix "Internet" -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange 9796 | Set-AzNetworkSecurityGroup

$nsg | Add-AzNetworkSecurityRuleConfig -Name "M365-NetIso-DenyHighRiskPorts" -Description "Please see https://aka.ms/M365NetIsoWiki for more info." -Access Deny -Protocol * -Direction Inbound -Priority 106 -SourceAddressPrefix "Internet" -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange @("13","17","19","20","21","22","23","53","69","111","115","119","123","135","137","138","139","161","162","389","445","512","514","593","636","873","1337","1433","1434","1801","1900","2049","2301","2381","3268","3306","3389","3637","4333","5353","5432","5601","5723","5724","5800","5900","5984","5985","5986","6379","6984","7000","7001","7199","7473","7474","7687","8888","9042","9142","9160","9200","9300","9798","9987","11211","15000","16379","19888","26379","27017","27018","27019","28017","42080","50030","50060","50070","50090","50075","50111","61620","61621","3702","19000","19080") | Set-AzNetworkSecurityGroup
```

## Verify

```powershell
$nsg = Get-AzNetworkSecurityGroup -Name "<NSG_NAME>" -ResourceGroupName "<RESOURCE_GROUP>"
$nsg.SecurityRules | Select-Object Name, Priority, Access, Direction, SourceAddressPrefix, DestinationPortRange | Format-Table -AutoSize
```

Confirm all 7 rules are present at priorities 100-106.

## Output ARM Template

Generate the ARM template JSON. The only difference between environments is Rule 100:
- **Production**: `"sourceAddressPrefix": "M365RemoteDesktopGateway"` with `"sourceAddressPrefixes": []`
- **Non-Production**: `"sourceAddressPrefix": ""` with `"sourceAddressPrefixes": ["M365RemoteDesktopGateway","CorpNetSaw","CorpNetPublic"]`

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "networkSecurityGroupName": {
      "type": "string",
      "defaultValue": "<NSG_NAME>",
      "metadata": { "description": "Your NSG name goes here" }
    }
  },
  "variables": { "location": "[resourceGroup().location]" },
  "resources": [{
    "type": "Microsoft.Network/networkSecurityGroups",
    "apiVersion": "2020-05-01",
    "name": "[parameters('networkSecurityGroupName')]",
    "location": "[variables('location')]",
    "properties": {
      "securityRules": [
        {
          "name": "M365-NetIso-AllowRAv3SAWGateways",
          "properties": {
            "priority": 100, "access": "Allow", "direction": "Inbound", "protocol": "*",
            "sourceAddressPrefix": "<PROD: M365RemoteDesktopGateway | NON-PROD: empty string>",
            "sourceAddressPrefixes": "<PROD: [] | NON-PROD: [M365RemoteDesktopGateway, CorpNetSaw, CorpNetPublic]>",
            "sourcePortRange": "*", "sourcePortRanges": [],
            "destinationAddressPrefix": "*", "destinationAddressPrefixes": [],
            "destinationPortRange": "3389", "destinationPortRanges": [],
            "description": "Created by M365 Core Network Security managed policy. Please see https://aka.ms/M365NetIsoWiki for more info."
          }
        },
        {
          "name": "M365-NetIso-AllowVirtualNetwork",
          "properties": {
            "priority": 101, "access": "Allow", "direction": "Inbound", "protocol": "*",
            "sourceAddressPrefix": "VirtualNetwork", "sourceAddressPrefixes": [],
            "sourcePortRange": "*", "sourcePortRanges": [],
            "destinationAddressPrefix": "VirtualNetwork", "destinationAddressPrefixes": [],
            "destinationPortRange": "*", "destinationPortRanges": [],
            "description": "Created by M365 Core Network Security managed policy. Please see https://aka.ms/M365NetIsoWiki for more info."
          }
        },
        {
          "name": "M365-NetIso-AllowPortsFromSAWs",
          "properties": {
            "priority": 102, "access": "Allow", "direction": "Inbound", "protocol": "*",
            "sourceAddressPrefix": "CorpNetSaw", "sourceAddressPrefixes": [],
            "sourcePortRange": "*", "sourcePortRanges": [],
            "destinationAddressPrefix": "*", "destinationAddressPrefixes": [],
            "destinationPortRange": "*", "destinationPortRanges": [],
            "description": "Created by M365 Core Network Security managed policy. Please see https://aka.ms/M365NetIsoWiki for more info."
          }
        },
        {
          "name": "M365-NetIso-AllowTorusManagement",
          "properties": {
            "priority": 103, "access": "Allow", "direction": "Inbound", "protocol": "*",
            "sourceAddressPrefixes": [
              "13.107.6.152/31","13.107.9.152/31","13.107.18.10/31","13.107.19.10/31",
              "13.107.128.0/22","23.103.160.0/20","23.103.224.0/19","40.96.0.0/13",
              "40.104.0.0/15","52.96.0.0/14","70.37.151.128/25","111.221.112.0/21",
              "131.253.33.215/32","132.245.0.0/16","134.170.68.0/23","150.171.32.0/22",
              "157.56.96.16/28","157.56.96.224/28","157.56.232.0/21","157.56.240.0/20",
              "191.232.96.0/19","191.234.6.152/32","191.234.140.0/22","191.234.224.0/22",
              "204.79.197.215/32","206.191.224.0/19"
            ],
            "sourcePortRange": "*", "sourcePortRanges": [],
            "destinationAddressPrefix": "*", "destinationAddressPrefixes": [],
            "destinationPortRange": "9796", "destinationPortRanges": [],
            "description": "Created by M365 Core Network Security managed policy. Please see https://aka.ms/M365NetIsoWiki for more info."
          }
        },
        {
          "name": "M365-NetIso-AllowLoadBalancer",
          "properties": {
            "priority": 104, "access": "Allow", "direction": "Inbound", "protocol": "*",
            "sourceAddressPrefix": "AzureLoadBalancer", "sourceAddressPrefixes": [],
            "sourcePortRange": "*", "sourcePortRanges": [],
            "destinationAddressPrefix": "*", "destinationAddressPrefixes": [],
            "destinationPortRange": "*", "destinationPortRanges": [],
            "description": "Created by M365 Core Network Security managed policy. Please see https://aka.ms/M365NetIsoWiki for more info."
          }
        },
        {
          "name": "M365-NetIso-DenyTorusManagementFromInternet",
          "properties": {
            "priority": 105, "access": "Deny", "direction": "Inbound", "protocol": "*",
            "sourceAddressPrefix": "Internet", "sourceAddressPrefixes": [],
            "sourcePortRange": "*", "sourcePortRanges": [],
            "destinationAddressPrefix": "*", "destinationAddressPrefixes": [],
            "destinationPortRange": "9796", "destinationPortRanges": [],
            "description": "Created by M365 Core Network Security managed policy. Please see https://aka.ms/M365NetIsoWiki for more info."
          }
        },
        {
          "name": "M365-NetIso-DenyHighRiskPorts",
          "properties": {
            "priority": 106, "access": "Deny", "direction": "Inbound", "protocol": "*",
            "sourceAddressPrefix": "Internet", "sourceAddressPrefixes": [],
            "sourcePortRange": "*", "sourcePortRanges": [],
            "destinationAddressPrefix": "*", "destinationAddressPrefixes": [],
            "destinationPortRange": "",
            "destinationPortRanges": ["13","17","19","20","21","22","23","53","69","111","115","119","123","135","137","138","139","161","162","389","445","512","514","593","636","873","1337","1433","1434","1801","1900","2049","2301","2381","3268","3306","3389","3637","4333","5353","5432","5601","5723","5724","5800","5900","5984","5985","5986","6379","6984","7000","7001","7199","7473","7474","7687","8888","9042","9142","9160","9200","9300","9798","9987","11211","15000","16379","19888","26379","27017","27018","27019","28017","42080","50030","50060","50070","50090","50075","50111","61620","61621","3702","19000","19080"],
            "description": "Created by M365 Core Network Security managed policy. Please see https://aka.ms/M365NetIsoWiki for more info."
          }
        }
      ]
    }
  }]
}
```

Also output a **parameters file**:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "networkSecurityGroupName": { "value": "<NSG_NAME>" }
  }
}
```

Replace `<NSG_NAME>` with the actual NSG name.

## Safety

- ⚠️ If rules at priority 100-119 already exist, STOP and warn — do NOT overwrite without explicit user approval
- ⚠️ If any PowerShell command fails, show the error and do NOT continue to the next rule
- ⚠️ Internal Service Tags (CorpNetSaw, M365RemoteDesktopGateway, CorpNetPublic) must be applied via PowerShell, NOT Azure Portal UI
