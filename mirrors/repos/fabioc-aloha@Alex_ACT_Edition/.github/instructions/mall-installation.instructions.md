---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "How heirs install plugins from the Alex ACT Plugin Mall into local/ paths so Edition upgrades don't clobber them"
applyTo: "**/.github/skills/local/**,**/.github/instructions/local/**,**/.github/muscles/local/**,**/.github/prompts/local/**,**/.mcp.json,**/mcp.json"
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# Mall Installation

The [Alex ACT Plugin Mall](https://github.com/fabioc-aloha/Alex_Skill_Mall) is a curated catalog of optional plugins. Heirs pull what they need on demand.

## Plugin Structure

Each plugin in the Mall is a self-contained folder under `plugins/<category>/<name>/`:

| File | Purpose |
| --- | --- |
| `README.md` | Human-readable: what the plugin does, when to use it |
| `plugin.json` | Machine manifest: shape, artifacts, dependencies, token cost |
| `SKILL.md` | Brain artifact (the rules or knowledge) |
| `*.instructions.md` | Optional instruction artifact |
| `*.prompt.md` | Optional prompt artifact |
| `*.cjs` | Optional muscle (executable code) |

Read `plugin.json` to understand what you're installing:

- `shape` tells you the complexity (`.S..` = 1 file, `ISP.` = 3 files)
- `engines` tells you which AI hosts support the plugin (`["copilot"]`, `["copilot", "claude"]`)
- `token_cost` tells you the approximate context-window impact
- `requires_edition` tells you the minimum Edition version

| Shape | What it includes |
| --- | --- |
| `.S..` | Skill only (1 file) |
| `.S.M` | Skill + muscle (2 files) |
| `ISP.` | Instruction + skill + prompt (3 files) |
| `ISPM` | Full stack (4+ files) |

## Plugin Selection Protocol

### Step 1: Assess project needs

Read `copilot-instructions.local.md`, `README.md`, `package.json`, and directory structure. Identify the primary language, domain, and workflows.

### Step 2: Check what's already installed

- `.github/skills/local/` contains already-installed plugins
- `.github/skills/` contains Edition baseline (do not duplicate)

### Step 3: Search the catalog

Fetch `CATALOG.json` from GitHub or local clone:

```bash
gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/CATALOG.json --jq .content | base64 -d
```

Or read from local clone at `~/Alex_ACT_Plugin_Mall/CATALOG.json`.

The catalog has 282 plugins across 16 categories. Filter by:

- `category`: security-privacy, devops-process, documentation, cloud-infrastructure, code-quality, ai-agents, media-graphics, data-analytics, reasoning-metacognition, platform-tooling, architecture-patterns, supervisor-fleet, domain-expertise, converters, communication-people, academic-research
- `shape`: plugin complexity
- `tier`: core, standard, extended
- `token_cost`: approximate context window cost

### Step 4: Apply the selection filter

| Question | If no, skip |
| --- | --- |
| Does the project actually do what this plugin covers? | Skip |
| Is this already covered by an Edition baseline artifact? | Skip |
| Would this plugin be used in the next 30 days? | Skip |
| Is the `token_cost` justified for this project? | Skip |

### Step 5: Read the plugin's README

Every plugin has a README that explains what it does, what Edition version it needs, and what artifacts it installs. Read it before installing.

## Installation

### Cardinal Rule: Use `local/` Subdirs

Edition's `sync-policy.json` declares these as **heir-owned** (never overwritten on upgrade):

- `.github/skills/local/**`
- `.github/instructions/local/**`
- `.github/muscles/local/**`
- `.github/prompts/local/**`

Installing outside `local/` means `upgrade-self.cjs --apply` will **delete it**.

### Install a Plugin

1. **Read `plugin.json`** to see what artifacts ship and where they go:

   ```bash
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/plugin.json \
     --jq .content | base64 -d
   ```

2. **Copy each artifact to its `local/` path**:

   ```bash
   # Skill
   mkdir -p .github/skills/local/<name>
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/SKILL.md \
     --jq .content | base64 -d > .github/skills/local/<name>/SKILL.md

   # Instruction (if plugin.json lists one)
   mkdir -p .github/instructions/local
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/<instruction-file> \
     --jq .content | base64 -d > .github/instructions/local/<instruction-file>

   # Muscle (if plugin.json lists one)
   mkdir -p .github/muscles/local
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/plugins/<category>/<name>/<muscle-file> \
     --jq .content | base64 -d > .github/muscles/local/<muscle-file>
   ```

3. **Alternative: local clone** (for bulk installs):

   ```bash
   git clone https://github.com/fabioc-aloha/Alex_Skill_Mall.git ~/Alex_ACT_Plugin_Mall
   mkdir -p .github/skills/local/<name>
   cp ~/Alex_ACT_Plugin_Mall/plugins/<category>/<name>/SKILL.md .github/skills/local/<name>/
   # Copy other artifacts per plugin.json install_paths
   ```

4. **Check dependencies**: read `requires_edition` in plugin.json. If your Edition version is older, upgrade first.

5. **Commit**:

   ```bash
   git add .github/skills/local .github/instructions/local .github/muscles/local .github/prompts/local
   git commit -m "Install plugin: <name> from ACT Plugin Mall"
   ```

## MCP Server Configs

When the Mall ships MCP configs, merge into the heir's `.mcp.json` at workspace root. MCP configs are not edition-owned, so Edition upgrades never touch them.

### Placement

Prefer workspace-root `.mcp.json` over `.vscode/mcp.json`. Both work in VS Code 1.118+, but workspace-root is the cross-editor standard (works in Claude Code, Cursor, and other MCP-aware editors without adaptation).

### Deduplication

When the same server name appears at both user-level and workspace-level, workspace-level wins. This means a Mall-installed MCP config in the project's `.mcp.json` overrides any user-global config with the same server name, which is the intended behavior for project-specific tool servers.

## Scaffolds

Scaffolds bootstrap new repos. They are not installed into existing projects. Use them via `cp -r` to start a new project.

## Falsifiability

- The `local/` path convention is wrong if Edition upgrades consistently clobber heir-installed plugins despite following this guide
- The installation procedure is stale if Mall folder structure changes (e.g., plugin.json schema evolves) and this guide does not reflect the new paths
- The knowledge-package vs plugin distinction adds no value if heirs report confusion about which to use, or install the wrong type >30% of the time
