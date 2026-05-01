# AVD Config Generator Agent

## Description

Orchestration agent to generate Arista EOS configurations from PyAVD designs.

## Difference with AVD Skill

| Aspect           | AVD Skill               | AVD Agent                          |
| ---------------- | ----------------------- | ---------------------------------- |
| **Focus**        | PyAVD methodology       | Complete workflow                  |
| **Autonomy**     | User-guided             | Semi-autonomous                    |
| **Integrations** | No                      | Git, NetBox, CloudVision           |
| **Output**       | Python/YAML code        | Generated EOS configs              |

## Features

- Multi-device configuration generation
- AVD design validation
- Templates for common topologies (spine-leaf, MLAG, EVPN)
- Git integration for versioning
- NetBox support for inventory
- CloudVision deployment

## Files

| File          | Description                                 | Lines  |
| ------------- | ------------------------------------------- | ------ |
| `core.md`     | Essential instructions (source of truth)    | ~115   |
| `claude.md`   | Full version with templates                 | ~150   |
| `copilot.md`  | Condensed version for Copilot               | ~60    |

## Installation

### Claude Code

```bash
# Option 1: Copy to .claude/
cp claude.md /path/to/project/.claude/avd-agent.md

# Option 2: Use the CLI
claude project add-instructions agents/avd-config-generator/claude.md
```

### GitHub Copilot

```bash
cp copilot.md /path/to/repo/.github/copilot-instructions.md
```

## Use Cases

- Deploy a new EVPN/VXLAN fabric
- Generate configs for all devices at a site
- Add new leafs to an existing fabric
- Create configs from a NetBox inventory

## Interaction Example

```text
User: Generate a fabric with 2 spines and 4 leafs in MLAG

Agent:
1. I collect missing information (ASN, IP pools)
2. I build the AVD design
3. I validate with validate_inputs()
4. I generate the 6 configurations
5. I provide the summary and configs
```

## Resources

- [PyAVD Documentation](https://avd.arista.com/stable/docs/pyavd/pyavd.html)
- [Arista AVD GitHub](https://github.com/aristanetworks/avd)
