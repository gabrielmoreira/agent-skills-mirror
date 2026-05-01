# PyAVD Network Configuration Builder

## Description

Skill for using PyAVD to generate Arista EOS configurations from network design intent.

## Features

- EOS configuration generation via PyAVD
- Design data validation (EOS Designs)
- Structured config validation (EOS CLI Config Gen)
- Support for 450+ AVD schema fragments

## Files

| File          | Description                                    | Lines  |
| ------------- | ---------------------------------------------- | ------ |
| `core.md`     | Essential instructions (source of truth)       | ~130   |
| `claude.md`   | Full version with advanced examples            | ~275   |
| `copilot.md`  | Condensed version for Copilot                  | ~60    |

## Installation

### Claude Code

```bash
# Option 1: Copy to .claude/
cp claude.md /path/to/project/.claude/avd.md

# Option 2: Use the CLI
claude project add-instructions skills/avd/claude.md
```

### GitHub Copilot

```bash
cp copilot.md /path/to/repo/.github/copilot-instructions.md
```

## Use Cases

- Automate network configuration generation
- Validate designs before deployment
- Generate configurations for CI/CD pipelines
- Convert intent-based designs to EOS CLI

## Quick Example

```python
from pyavd import validate_inputs, get_avd_facts, get_device_structured_config, get_device_config

design = {"fabric_name": "DC1", "spine": {...}, "l3leaf": {...}}
result = validate_inputs(design)
avd_facts = get_avd_facts(design)
config = get_device_structured_config("leaf1", design, avd_facts)
eos_cli = get_device_config(config)
```

## Resources

- [PyAVD Documentation](https://avd.arista.com/stable/docs/pyavd/pyavd.html)
- [Arista AVD GitHub](https://github.com/aristanetworks/avd)
