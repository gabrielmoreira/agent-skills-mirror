# Agents

## What is an Agent?

An **agent** is an autonomous orchestration system that can:

- Fetch information from multiple sources
- Call external tools (APIs, CLIs, databases)
- Chain multiple steps autonomously
- Maintain context memory between steps

**Use an agent when you want to:**

- Read a design doc and compare with a running-config
- Query NetBox, Git, or inventories
- Run automated validations
- Orchestrate multi-step workflows

---

## Available Agents

| Agent                                           | Description                                                        | Claude | Copilot |
| ----------------------------------------------- | ------------------------------------------------------------------ | ------ | ------- |
| [config-reviewer](./config-reviewer/)           | Compares EOS configs with best practices and proposes corrections  | ✅     | ✅      |
| [avd-config-generator](./avd-config-generator/) | Generates EOS configs from PyAVD designs                           | ✅     | ✅      |
| [arista-act](./arista-act/)                     | Builds ACT topology YAML files for Arista virtual labs             | ✅     | ✅      |
| [Cloudvision-api-agent](./Cloudvision-api-agent/) | CloudVision API automation with Python (gRPC, REST)              | ✅     | ✅      |

---

## Installation

### Local Installation (from cloned repo)

```bash
# Install an agent for Claude Code
./scripts/install.sh claude agent <agent-name> /path/to/your/project

# Install an agent for GitHub Copilot
./scripts/install.sh copilot agent <agent-name> /path/to/your/repo
```

### Remote Installation (no clone required)

```bash
# Install directly from Git server
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | \
  bash -s -- <platform> agent <agent-name> [target_path]

# Examples:
# Claude Code - copies to clipboard
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | \
  bash -s -- claude agent config-reviewer

# GitHub Copilot - installs to repo
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | \
  bash -s -- copilot agent arista-act /path/to/your/repo
```

**Installation Paths**:

- **Claude Code**: Agent content copied to clipboard (paste into Claude Code)
- **GitHub Copilot**:
  - `.github/agents/<agent-name>.md` — Agent definition
  - `AGENTS.md` (root) — Active agent file

---

## Skill vs Agent Difference

| Aspect           | Skill                   | Agent                 |
| ---------------- | ----------------------- | --------------------- |
| Focus            | Expert methodology      | Orchestration         |
| Autonomy         | User-guided             | Semi-autonomous       |
| External tools   | No                      | Yes                   |
| Memory           | Session                 | Persistent context    |
| Use cases        | Generation, review      | Workflows, automation |

---

## Create a New Agent

### 3-Tier Architecture

All agents follow this structure:

```
<agent-name>/
├── core.md          # Source of truth (~150-250 lines)
├── claude.md        # Full version for Claude Code (~500-1000 lines)
├── copilot.md       # Condensed for GitHub Copilot (~150-250 lines)
└── README.md        # Installation and usage documentation
```

### Steps

1. Copy the `_templates/` folder to a new folder
2. Rename according to the agent's function
3. **Create `core.md`** with essential instructions (source of truth)
   - Agent role and purpose
   - Core workflow and methodology
   - Key constraints and rules
   - Essential API/tool references
4. **Create `claude.md`** that extends core
   - Frontmatter with metadata (`name`, `description`, `version`, `includes`)
   - Comment explaining it extends core.md
   - Advanced workflows with complete code examples
   - Troubleshooting guides
   - Error handling patterns
   - Best practices for production
5. **Create `copilot.md`** condensed version
   - Frontmatter with metadata (`name`, `description`, `version`, `based-on`)
   - Essential patterns only (~8k token budget)
   - Quick reference tables
   - Minimal working examples
   - Constraints checklist
6. **Add `README.md`**
   - Description and features
   - Supported workflows
   - Installation instructions (local and remote)
   - File structure explanation
   - Usage examples
7. Update this README with the new agent

See [_templates/](./_templates/) for templates.
