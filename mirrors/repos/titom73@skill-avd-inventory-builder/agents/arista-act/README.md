# Arista Cloud Test (ACT) Topology Builder Agent

## Description

**ACT topology builder** agent that generates YAML topology files for Arista Cloud Test (ACT) virtual network labs — vEOS switches, CloudVision Portal (CVP), and Linux servers.

## Features

- ACT topology YAML generation
- Multi-DC topology support with DCI (Data Center Interconnect)
- CVP auto-configuration workflows
- ZTP (Zero Touch Provisioning) automation patterns
- MLAG pair topology validation
- IP address allocation planning
- Interface mapping and link validation

## Supported Workflows

### 1. Build Topology from Scratch

- Input: Requirements (device count, topology type, features)
- Output: Complete ACT topology YAML file

### 2. Convert AVD Inventory to ACT Topology

- Input: AVD (Arista Validated Designs) inventory + group_vars
- Output: ACT topology file compatible with ACT platform

### 3. Multi-DC Topology with DCI

- Input: Multi-site requirements (2+ DCs, border leaves for inter-DC connectivity)
- Output: Multi-DC topology with border leaf connections

### 4. ZTP Automation Patterns

- Full auto ZTP with CVP DHCP
- Partial ZTP (specific devices only)
- Manual ZTP configuration

## Installation

### Claude Code

```bash
# From repository root
./scripts/install.sh claude agent arista-act /path/to/your/project

# Or remote installation (no clone required)
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | bash -s -- claude agent arista-act
```

The agent will be copied to your clipboard. Paste it into Claude Code.

### GitHub Copilot

```bash
# From repository root
./scripts/install.sh copilot agent arista-act /path/to/your/repo

# Or remote installation
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | bash -s -- copilot agent arista-act /path/to/your/repo
```

This creates:
- `.github/agents/arista-act.md` — agent definition
- `AGENTS.md` (root) — active agent file for GitHub Copilot

## Files

| File | Description | Target Platform | Size |
|------|-------------|-----------------|------|
| `core.md` | Source of truth — complete ACT topology specification | Reference | ~400 lines |
| `claude.md` | Full version with workflows, advanced patterns, troubleshooting | Claude Code | ~670 lines |
| `copilot.md` | Condensed version with essential rules and quick reference | GitHub Copilot | ~150 lines |

## Architecture

```
core.md (source of truth)
├── claude.md   (core + advanced workflows + troubleshooting + examples)
└── copilot.md  (condensed for ~8k token budget)
```

### Content Split

**core.md** contains:
- ACT topology file format
- Node attributes reference (vEOS, CVP, generic)
- Links section syntax
- Naming conventions and IP allocation patterns
- Common topology patterns (spine-leaf, multi-DC, MLAG)
- Supported vEOS device models
- ZTP modes
- Validation checklist
- Complete single-DC example

**claude.md** adds:
- Workflow: Build topology from scratch
- Workflow: Convert AVD inventory to ACT
- Workflow: Multi-DC topology with DCI
- Advanced ZTP automation patterns
- Multi-CVP patterns
- Troubleshooting guide (interface conflicts, MLAG issues, CVP auto-config failures)
- Complete multi-DC example with border leaves
- Common mistakes and how to avoid them
- Advanced validation techniques

**copilot.md** provides:
- Condensed YAML structure
- Essential node attributes (table format)
- Links syntax (brief)
- Naming patterns and IP allocation (quick reference)
- Common topology patterns (bullets)
- Validation checklist (condensed)
- Minimal working example

## Usage Examples

### Example 1: Generate Single-DC Topology

**User request**:
> Generate an ACT topology for a single DC with 2 spines, 2 MLAG leaf pairs, CVP with auto-configuration, and 2 hosts.

**Agent output**: Complete YAML topology file with:
- Global vEOS/CVP/generic sections
- 2 spines (192.168.0.11–.12)
- 4 leaves in 2 MLAG pairs (192.168.0.101–.104)
- CVP with auto-configuration (192.168.0.5)
- 2 generic hosts (192.168.0.201–.202)
- All spine-to-leaf uplinks
- MLAG peer-link connections (Ethernet3 + Ethernet4)
- Host downlinks

### Example 2: Multi-DC with Border Leaves

**User request**:
> Create a multi-DC topology with DC1 and DC2, each with 2 spines, 1 MLAG leaf pair, and 1 MLAG border leaf pair. Connect the border leaves for DCI.

**Agent output**: Multi-DC topology with:
- DC-prefixed naming (`dc1-spine01`, `dc2-spine01`)
- IP allocation per DC (DC1: .11–.12 spines, .101–.106 leaves; DC2: .21–.22 spines, .111–.116 leaves)
- DCI links between border leaf pairs (Ethernet6)
- MLAG peer-links for all leaf and border pairs

### Example 3: ZTP Automation

**User request**:
> Generate a topology with CVP auto-configuration and full ZTP automation for all vEOS devices.

**Agent output**: Topology with:
- CVP with `auto_configuration: true`, `instance_type: xlarge`, `ztp_dhcp: {enabled: true}`
- All vEOS nodes with `ztp: true`
- Result: Devices boot in ZTP mode, CVP acts as DHCP server, auto-onboards all devices to **Undefined** container

## Validation

The agent includes comprehensive validation:

- Unique device names and IP addresses
- Interface uniqueness (no interface used twice)
- MLAG pair consistency (2 peer-link connections)
- CVP auto-configuration requirements (`instance_type: xlarge`)
- YAML syntax validation (2-space indentation, no tabs)

## Resources

- [ACT Documentation](https://www.arista.com/en/support/act)
- [Arista vEOS-lab User Guide](https://www.arista.com/en/support/software-download)
- [CloudVision Portal Documentation](https://www.arista.com/en/cg-cv)
- [AVD Documentation](https://avd.arista.com/)

## Version

- **Current Version**: 1.0
- **Last Updated**: 2026-04-10
- **Compatibility**: ACT platform, EOS 4.27.x+, CVP 2020.1.x – 2025.3.x
