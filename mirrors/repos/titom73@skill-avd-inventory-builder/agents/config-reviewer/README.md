# Config Reviewer Agent

## Description

**Configuration audit** agent that compares EOS configs with best practices and proposes corrections.

## Features

- EOS configuration analysis
- Comparison with Arista best practices
- Configuration drift detection
- Audit report generation
- Correction proposals

## Supported Workflows

### 1. Single Configuration Audit

- Input: running-config of a switch
- Output: audit report with classified findings

### 2. Design vs Implementation Comparison

- Input: HLD/LLD + running-configs
- Output: gap analysis with recommendations

### 3. Pre-migration Validation

- Input: source and target configs
- Output: validation checklist, identified risks

## Installation

### Claude Code

```bash
# Copy to the project's .claude/ folder
cp claude.md /path/to/project/.claude/config-reviewer.md

# Or use the CLI
claude project add-instructions agents/config-reviewer/claude.md
```

### GitHub Copilot

```bash
cp copilot.md /path/to/repo/.github/copilot-instructions.md
```

## Files

| File          | Platform       | Description                    |
| ------------- | -------------- | ------------------------------ |
| `core.md`     | Shared         | Essential instructions         |
| `claude.md`   | Claude Code    | Full agent with workflows      |
| `copilot.md`  | GitHub Copilot | Condensed version              |

## Usage Example

```text
User: Here is my running-config. Perform an EVPN compliance audit.

Agent:
## Status
- Workflow: Config Audit
- Status: Success

## Findings

### Critical (1)
- EVPN address-family missing on spine BGP config

### High (2)
- MLAG reload-delay not configured
- Missing loopback1 for VTEP

### Medium (3)
- Non-standard VLAN naming convention
...

## Recommendations
1. Add `address-family evpn` to spine BGP
2. Configure `reload-delay mlag 300` and `reload-delay non-mlag 330`
...
```

## Status

🚧 In development
