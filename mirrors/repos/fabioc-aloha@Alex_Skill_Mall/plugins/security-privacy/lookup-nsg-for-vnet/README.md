# lookup-nsg-for-vnet

Checks every subnet in a Virtual Network for an associated Network Security Group, and also inspects each NIC attached to those subnets for NIC-level NSG coverage.

## Quick Facts

| Field | Value |
| --- | --- |
| **Category** | security-privacy |
| **Shape** | `.S..` |
| **Tier** | standard |
| **Token cost** | ~1265 tokens |
| **Engines** | copilot |
| **Requires Edition** | >=1.0.0 |
| **Keywords** | lookup, nsg, for, vnet, checks, every, subnet, virtual |

## Installation

From ACT Edition:

```text
/mall install lookup-nsg-for-vnet
```

Or manually copy the plugin contents to `.github/skills/local/lookup-nsg-for-vnet/`.

## Artifacts

- **skill**: `SKILL.md`

## Shape: `.S..`

Skill only -- domain knowledge loaded when pattern matches.
