# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a **content-only** collection of Arista EOS AI skills and agents — no build system, package manager, tests, or runtime dependencies exist. All content is Markdown.

## Installation

The install scripts copy skill/agent files into target projects:

```bash
# From a cloned repo
./scripts/install.sh <platform> <type> <name> [target_path]

# Without cloning (remote)
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | bash -s -- <platform> <type> <name> [target_path]
```

- `platform`: `claude` or `copilot`
- `type`: `skill` or `agent`
- `name`: `eos-fabric-design`, `avd`, `config-reviewer`, or `avd-config-generator`

**Claude Code destinations**:
- agent → `.claude/agents/<name>.md` (discoverable via `/agents` in Claude Code)
- skill → `.claude/commands/<name>.md` (discoverable via `/<name>` in Claude Code)

**Copilot destination**: `.github/copilot-instructions.md` or `.github/agents/`

## Architecture

### Skills vs Agents

| | Skill | Agent |
|--|--|--|
| Purpose | Expert methodology, user-guided | Orchestrated workflows, semi-autonomous |
| External tools | No | Yes (Git, NetBox, CVP, APIs) |
| Examples | Fabric design, config generation | Config audit pipeline, multi-device AVD generation |

### 3-Tier File Structure

Every skill and agent follows this pattern:

```
<name>/
├── core.md      # Source of truth (~100-150 lines) — defines principles, never duplicate this
├── claude.md    # Full version for Claude Code (examples, templates, ~300-500 lines)
├── copilot.md   # Condensed for GitHub Copilot (~50-100 lines, ~8k token budget)
└── README.md    # Usage and installation docs
```

`core.md` is the authoritative definition. `claude.md` and `copilot.md` extend it for platform-specific context windows. When updating a skill/agent, update `core.md` first, then propagate to the platform variants.

### Available Components

**Skills** (`skills/`):
- `eos-fabric-design` — Senior Network Architect persona for EVPN/VXLAN leaf-spine design
- `avd` — PyAVD expert for configuration generation via `validate_inputs()`, `get_avd_facts()`, `get_device_structured_config()`, `get_device_config()`

**Agents** (`agents/`):
- `config-reviewer` — Audit configs for EVPN/VXLAN, MLAG, BGP, security compliance
- `avd-config-generator` — Multi-device config generation with Git, NetBox, CloudVision integration

**Templates** (`skills/_templates/`, `agents/_templates/`) — boilerplate for new components.

## Key Design Constraints

- **claude.md** is optimized for Claude's ~200k token context window — long-form instructions, decision trees, full examples are appropriate
- **copilot.md** must stay within ~8k tokens — strip examples, compress rules, keep only essentials
- `core.md` must never duplicate content from platform files; platform files extend `core.md`
- All configurations referenced in instructions must be production-ready EOS syntax
