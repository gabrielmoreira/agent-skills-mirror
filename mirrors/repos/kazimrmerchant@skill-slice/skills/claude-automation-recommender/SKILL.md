---
name: claude-automation-recommender
description: "Read-only analyzer that recommends Claude Code hooks, subagents, skills, plugins, and MCP servers from codebase signals; does not create those files. Use when the user asks how to set up Claude Code, which automations to add, or how to optimize a Claude Code workflow. Not for implementing the recommendations, authoring Cursor SKILL.md (create-skill), or writing AGENTS.md (agents-md)."
version: 1.0.1
tools: Read, Glob, Grep, Bash
---

# Claude Automation Recommender

Analyze codebase patterns to recommend tailored Claude Code automations across all extensibility options.

**This skill is read-only.** It analyzes the codebase and outputs recommendations. It does NOT create or modify any files. Users implement the recommendations themselves or ask Claude separately to help build them.

## When to Use

Trigger this skill when the user:

- Asks for automation recommendations for their project
- Wants to optimize or improve their Claude Code setup
- Mentions improving Claude Code workflows
- Asks how to first set up Claude Code for a project
- Wants to know what Claude Code features they should use
- Asks about a specific automation type (hooks, subagents, skills, plugins, MCP servers)

## Prerequisites

- Read access to the target codebase (project root)
- `claude` CLI installed and on PATH for any install/verification commands mentioned in recommendations
- On Windows host (primary), use PowerShell. Commands shown as `ls -la` are Bash equivalents; in PowerShell use `Get-ChildItem -Force` or `dir /a` if running natively. If running inside Claude Code's built-in Bash on Windows, the Bash commands work as-is.

## Procedure

### Phase 1: Codebase Analysis

Gather project context before generating any recommendations.

1. **Detect project type and tooling.**

```bash
# Detect project manifest files
ls -la package.json pyproject.toml Cargo.toml go.mod pom.xml 2>/dev/null

# Inspect package.json (first 50 lines)
cat package.json 2>/dev/null | head -50
```

PowerShell equivalent if running natively:

```powershell
Get-ChildItem -Force package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml -ErrorAction SilentlyContinue
Get-Content package.json -TotalCount 50 -ErrorAction SilentlyContinue
```

2. **Check dependencies for MCP server recommendations.**

```bash
cat package.json 2>/dev/null | grep -E '"(react|vue|angular|next|express|fastapi|django|prisma|supabase|convex|stripe)"'
```

3. **Check for existing Claude Code configuration.**

```bash
ls -la .claude/ CLAUDE.md 2>/dev/null
```

4. **Analyze project structure.**

```bash
ls -la src/ app/ lib/ tests/ components/ pages/ api/ 2>/dev/null
```

5. **Capture key indicators** using the table below.

| Category | What to Look For | Informs Recommendations For |
|----------|------------------|------------------------------|
| Language/Framework | package.json, pyproject.toml, import patterns | Hooks, MCP servers |
| Frontend stack | React, Vue, Angular, Next.js | Playwright MCP, frontend skills |
| Backend stack | Express, FastAPI, Django | API documentation tools |
| Database | Prisma, Supabase, Convex, raw SQL | Database / backend MCP servers |
| External APIs | Stripe, OpenAI, AWS SDKs | context7 MCP for docs |
| Testing | Jest, pytest, Playwright configs | Testing hooks, subagents |
| CI/CD | GitHub Actions, CircleCI | GitHub MCP server |
| Issue tracking | Linear, Jira references | Issue tracker MCP |
| Docs patterns | OpenAPI, JSDoc, docstrings | Documentation skills |

### Phase 2: Generate Recommendations

Based on analysis, generate recommendations across all categories. **Only include 1-2 recommendations per category** — the most valuable ones for this specific codebase. Skip categories that aren't relevant.

If the user asks for a specific type, focus only on that type and provide 3-5 recommendations instead.

#### A. MCP Server Recommendations

**Load `references/mcp-servers.md`** when generating MCP server recommendations for detailed patterns and install commands.

| Codebase Signal | Recommended MCP Server |
|-----------------|------------------------|
| Uses popular libraries (React, Express, etc.) | **context7** — Live documentation lookup |
| Frontend with UI testing needs | **Playwright** — Browser automation/testing |
| Uses Supabase | **Supabase MCP** — Direct database operations |
| Uses Convex | **Convex MCP** — Live deployment introspection, run queries/mutations, manage env vars and logs |
| PostgreSQL/MySQL database | **Database MCP** — Query and schema tools |
| GitHub repository | **GitHub MCP** — Issues, PRs, actions |
| Uses Linear for issues | **Linear MCP** — Issue management |
| AWS infrastructure | **AWS MCP** — Cloud resource management |
| Slack workspace | **Slack MCP** — Team notifications |
| Memory/context persistence | **Memory MCP** — Cross-session memory |
| Sentry error tracking | **Sentry MCP** — Error investigation |
| Docker containers | **Docker MCP** — Container management |

#### B. Skills Recommendations

**Load `references/skills-reference.md`** when generating skills recommendations for details on available skills and plugins.

Create skills in `.claude/skills/<name>/SKILL.md`. Some are also available via plugins:

| Codebase Signal | Skill | Plugin |
|-----------------|-------|--------|
| Building plugins | skill-development | plugin-dev |
| Git commits | commit | commit-commands |
| React/Vue/Angular | frontend-design | frontend-design |
| Automation rules | writing-rules | hookify |
| Feature planning | feature-dev | feature-dev |

**Custom skills to create** (with templates, scripts, examples):

| Codebase Signal | Skill to Create | Invocation |
|-----------------|-----------------|------------|
| API routes | **api-doc** (with OpenAPI template) | Both |
| Database project | **create-migration** (with validation script) | User-only |
| Test suite | **gen-test** (with example tests) | User-only |
| Component library | **new-component** (with templates) | User-only |
| PR workflow | **pr-check** (with checklist) | User-only |
| Releases | **release-notes** (with git context) | User-only |
| Code style | **project-conventions** | Claude-only |
| Onboarding | **setup-dev** (with prereq script) | User-only |

**Invocation control flags:**
- `disable-model-invocation: true` — User-only (for side effects: deploy, commit, send)
- `user-invocable: false` — Claude-only (for background knowledge)
- Default (omit both) — Both can invoke

#### C. Hooks Recommendations

**Load `references/hooks-patterns.md`** when generating hooks recommendations for configurations.

| Codebase Signal | Recommended Hook |
|-----------------|------------------|
| Prettier configured | PostToolUse: auto-format on edit |
| ESLint/Ruff configured | PostToolUse: auto-lint on edit |
| TypeScript project | PostToolUse: type-check on edit |
| Tests directory exists | PostToolUse: run related tests |
| `.env` files present | PreToolUse: block `.env` edits |
| Lock files present | PreToolUse: block lock file edits |
| Security-sensitive code | PreToolUse: require confirmation |

#### D. Subagent Recommendations

**Load `references/subagent-templates.md`** when generating subagent recommendations for templates.

| Codebase Signal | Recommended Subagent |
|-----------------|---------------------|
| Large codebase (>500 files) | **code-reviewer** — Parallel code review |
| Auth/payments code | **security-reviewer** — Security audits |
| API project | **api-documenter** — OpenAPI generation |
| Performance critical | **performance-analyzer** — Bottleneck detection |
| Frontend heavy | **ui-reviewer** — Accessibility review |
| Needs more tests | **test-writer** — Test generation |

#### E. Plugin Recommendations

**Load `references/plugins-reference.md`** when generating plugin recommendations for available plugins.

| Codebase Signal | Recommended Plugin |
|-----------------|-------------------|
| General productivity | **anthropic-agent-skills** — Core skills bundle |
| Document workflows | Install docx, xlsx, pdf skills |
| Frontend development | **frontend-design** plugin |
| Building AI tools | **mcp-builder** for MCP development |

### Phase 3: Output Recommendations Report

Format recommendations using the template below. Go beyond the reference lists — use web search to find recommendations specific to the codebase's tools, frameworks, and libraries. End by noting the user can request more recommendations for any specific category.

```markdown
## Claude Code Automation Recommendations

I've analyzed your codebase and identified the top automations for each category. Here are my top 1-2 recommendations per type:

### Codebase Profile
- **Type**: [detected language/runtime]
- **Framework**: [detected framework]
- **Key Libraries**: [relevant libraries detected]

---

### 🔌 MCP Servers

#### context7
**Why**: [specific reason based on detected libraries]
**Install**: `claude mcp add context7`

---

### 🎯 Skills

#### [skill name]
**Why**: [specific reason]
**Create**: `.claude/skills/[name]/SKILL.md`
**Invocation**: User-only / Both / Claude-only
**Also available in**: [plugin-name] plugin (if applicable)
```yaml
---
name: [skill-name]
description: [what it does]
disable-model-invocation: true  # for user-only
---
```

---

### ⚡ Hooks

#### [hook name]
**Why**: [specific reason based on detected config]
**Where**: `.claude/settings.json`

---

### 🤖 Subagents

#### [agent name]
**Why**: [specific reason based on codebase patterns]
**Where**: `.claude/agents/[name].md`

---

**Want more?** Ask for additional recommendations for any specific category (e.g., "show me more MCP server options" or "what other hooks would help?").

**Want help implementing any of these?** Just ask and I can help you set up any of the recommendations above.
```

## Decision Framework

### When to Recommend MCP Servers
- External service integration needed (databases, APIs)
- Documentation lookup for libraries/SDKs
- Browser automation or testing
- Team tool integration (GitHub, Linear, Slack)
- Cloud infrastructure management

### When to Recommend Skills
- Document generation (docx, xlsx, pptx, pdf — also in plugins)
- Frequently repeated prompts or workflows
- Project-specific tasks with arguments
- Applying templates or scripts to tasks (skills can bundle supporting files)
- Quick actions invoked with `/skill-name`
- Workflows that should run in isolation (`context: fork`)

### When to Recommend Hooks
- Repetitive post-edit actions (formatting, linting)
- Protection rules (block sensitive file edits)
- Validation checks (tests, type checks)

### When to Recommend Subagents
- Specialized expertise needed (security, performance)
- Parallel review workflows
- Background quality checks

### When to Recommend Plugins
- Need multiple related skills
- Want pre-packaged automation bundles
- Team-wide standardization

## Configuration Tips

### MCP Server Setup

**Team sharing**: Check `.mcp.json` into repo so entire team gets same MCP servers.

**Debugging**: Use `--mcp-debug` flag to identify configuration issues.

**Prerequisites to recommend:**
- GitHub CLI (`gh`) — enables native GitHub operations
- Puppeteer/Playwright CLI — for browser MCP servers

### Headless Mode (for CI/Automation)

Recommend headless Claude for automated pipelines:

```bash
# Pre-commit hook example
claude -p "fix lint errors in src/" --allowedTools Edit,Write

# CI pipeline with structured output
claude -p "<prompt>" --output-format stream-json | your_command
```

### Permissions for Hooks

Configure allowed tools in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Edit", "Write", "Bash(npm test:*)", "Bash(git commit:*)"]
  }
}
```

## Pitfalls

- **Do NOT create or modify files.** This skill is read-only. It analyzes and outputs recommendations only. Users implement them or ask Claude separately.
- **Do not overwhelm with options.** Default to 1-2 recommendations per category. Only expand to 3-5 when the user explicitly asks for a specific type.
- **Do not skip the codebase analysis phase.** Generic recommendations without codebase-specific reasoning are low value. Always tie "Why" to detected signals.
- **Do not invent MCP server names or CLI flags.** Only recommend servers that exist. Use `references/mcp-servers.md` for verified patterns.
- **Do not forget invocation control flags.** Skills with side effects (deploy, commit, send) should use `disable-model-invocation: true`. Background knowledge skills should use `user-invocable: false`.
- **Windows path awareness**: When recommending file paths in hooks or skill configs, use forward slashes in JSON (`./.claude/settings.json`) even on Windows — Claude Code config files use Unix-style paths.
- **Do not recommend hooks that block the user's own edits without explanation.** PreToolUse hooks that block `.env` or lock file edits should clearly state why in the recommendation output.

## Verification

After generating recommendations, verify the analysis was thorough:

1. **Confirm codebase profile accuracy.**
```bash
# Re-check detected framework
cat package.json 2>/dev/null | grep -E '"(name|version|description)"'
```

2. **Confirm existing Claude config was checked.**
```bash
ls -la .claude/ CLAUDE.md .mcp.json 2>/dev/null
```

3. **Confirm each recommendation has a codebase-specific "Why".** If any recommendation's "Why" could apply to any project, it is too generic — revise it.

4. **Confirm the output ends with the "Want more?" and "Want help implementing?" prompts** so the user knows they can request deeper detail or implementation help.

## Related Skills

- **skill-development** — For when the user wants to actually build a recommended skill
- **writing-rules** (hookify plugin) — For when the user wants to implement recommended hooks
- **commit** (commit-commands plugin) — For when the user wants to set up commit automation
