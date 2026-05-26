# Index — Master Section Index

**Scope**: Project-wide
**Last Updated**: 2026-05-25

> This file is the **master index** of all instruction sections across all `.ai/instruct.md` files in the project.
> It enables fast lookup: find the authoritative source for any topic without reading every file.
>
> **Maintenance**: Update this file whenever any `.ai/instruct.md` is created, modified, or retired.
> Run `/ai-update-index` in Copilot Chat to rebuild automatically.
> In this template repository, some indexed files intentionally contain placeholders until `/ai-onboard` (or manual onboarding) fills project-specific values.

---

## How to Use

1. Search this index for keywords related to your topic
2. Follow the link to the exact file
3. Read that section — it is the **single source of truth**
4. Do not restate or copy the content elsewhere; cross-reference it

**If a topic is not in this index**, it has not been formally defined. Flag the gap and add it to the appropriate `.ai/instruct.md`, then rerun `/ai-update-index`.

> **Note on link granularity**: Entries in the tables below link to the **file**, not to the specific section anchor. This is intentional — section headings drift faster than file paths, so file-level links stay valid through more edits. Within each linked file, use the file's own Contents table to jump to the section.

---

## Index

### Meta & System

| Section | File | Description |
|---------|------|-------------|
| The Depth-Priority Hierarchical Paradigm | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | How the `.ai/` hierarchy works; deeper = more authoritative |
| Global Shared Instructions | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Purpose of the `.ai/` directory |
| AI Prompt Files | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Slash-command prompt files in `.github/prompts/`; `/ai-` prefix convention |
| `/ai-onboard` | [`.github/prompts/ai-onboard.prompt.md`](../.github/prompts/ai-onboard.prompt.md) | Interactive wizard that asks, infers, and confirms edits to template fields (identity, license, dev-specs, modules) and rebuilds the index |
| `/ai-update-index` | [`.github/prompts/ai-update-index.prompt.md`](../.github/prompts/ai-update-index.prompt.md) | Rebuilds `.ai/index.md` from every instruction file |
| `/ai-archive` | [`.github/prompts/ai-archive.prompt.md`](../.github/prompts/ai-archive.prompt.md) | Safely archive a file or directory using the convention |
| `/ai-new-module` | [`.github/prompts/ai-new-module.prompt.md`](../.github/prompts/ai-new-module.prompt.md) | Scaffold a new module: `.ai/instruct.md` + `.dev-docs/index.md`, register it, rebuild index |
| `/ai-validate` | [`.github/prompts/ai-validate.prompt.md`](../.github/prompts/ai-validate.prompt.md) | Run the AI-INSTRUCT drift validator and report findings (no edits) |
| `/ai-env-check` | [`.github/prompts/ai-env-check.prompt.md`](../.github/prompts/ai-env-check.prompt.md) | Audit host-vs-container isolation state and recommend containment (no edits) |
| `/ai-commit` | [`.github/prompts/ai-commit.prompt.md`](../.github/prompts/ai-commit.prompt.md) | Refresh `Last Updated` dates, validate, draft a Conventional Commits message, optionally push |
| Custom Agents | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Custom agent definitions in `.github/agents/` |
| Skills | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Domain knowledge skill packs in `.github/skills/` |
| Git Hooks | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Hook scripts in `.github/hooks/` and how to install them |
| Code Comment Convention | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Comment on why not what; no docblocks unless asked |
| AI-INSTRUCT Maintenance Rule | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Update instruction files as part of every architectural change; run `/ai-update-index` after |
| `.github/` File Placement Rules | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Where to put prompts, agents, debug scripts, tmp files; `.vscode/` for shared editor settings |
| Automatic Date Maintenance | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | AI auto-fills `Last Updated` and `[PLACEHOLDER]` values when context is unambiguous |
| Read Project Specs First | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | AI must read `.github/dev-specs.md` at session start before suggesting commands or paths |
| MCP Server Configuration | [`.vscode/mcp.json`](../.vscode/mcp.json) | Model Context Protocol servers that extend AI capabilities (commented templates) |
| PR Template | [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) | AI-INSTRUCT-aware PR checklist (instruction discipline, safety, credentials) |
| Suggested GitHub Topics | [`.github/TOPICS.md`](../.github/TOPICS.md) | Recommended repo topics for discoverability |
| Cursor Compatibility | [`.cursor/rules/project.mdc`](../.cursor/rules/project.mdc) | Pointer rule so Cursor reads the same `.ai/` hierarchy |
| One-shot Setup Scripts | [`setup.sh`](../setup.sh) / [`setup.ps1`](../setup.ps1) | Install hooks, scaffold `.env`, run validator |

### Project Specs

| Section | File | Description |
|---------|------|-------------|
| Development Platform | [`.github/dev-specs.md`](../.github/dev-specs.md) | Developer OS, shell, editor |
| Target Platform | [`.github/dev-specs.md`](../.github/dev-specs.md) | Where the code is deployed; path & line-ending convention |
| Language & Runtime | [`.github/dev-specs.md`](../.github/dev-specs.md) | Primary languages and versions |
| Frameworks & Libraries | [`.github/dev-specs.md`](../.github/dev-specs.md) | Frontend, backend, database, ORM |
| Package Manager | [`.github/dev-specs.md`](../.github/dev-specs.md) | Dependency management tooling |
| Infrastructure & DevOps | [`.github/dev-specs.md`](../.github/dev-specs.md) | Containers, CI/CD, cloud |
| Testing | [`.github/dev-specs.md`](../.github/dev-specs.md) | Test frameworks and strategy |
| Architecture Pattern | [`.github/dev-specs.md`](../.github/dev-specs.md) | Repo and system structure |
| Notes | [`.github/dev-specs.md`](../.github/dev-specs.md) | Free-form project context |

### Conventions

| Section | File | Description |
|---------|------|-------------|
| Directory Naming | [`.ai/conventions.md`](conventions.md) | kebab-case for all directories; dot-prefix for archive dirs |
| File Naming | [`.ai/conventions.md`](conventions.md) | Language-specific file naming; no spaces |
| Documentation Naming | [`.ai/conventions.md`](conventions.md) | Numbered kebab-case for user-facing guides |
| AI Instruction File Naming | [`.ai/conventions.md`](conventions.md) | Standard name for instruction files; one type: `instruct.md` |
| .dev-docs Convention | [`.ai/conventions.md`](conventions.md) | Dev documentation subdirectory structure and rules |
| TOC Requirement | [`.ai/conventions.md`](conventions.md) | Files with 5+ sections must have a Contents table |
| Cross-Reference Convention | [`.ai/conventions.md`](conventions.md) | Exact format for referencing source-of-truth sections |
| No-Duplication Rule | [`.ai/conventions.md`](conventions.md) | Instructions live in exactly one place |
| Versioning | [`.ai/conventions.md`](conventions.md) | Semver, instruction file dating, Last Updated auto-update rule |
| Code Organization | [`.ai/conventions.md`](conventions.md) | Project-specific structure rules (fill in per project) |
| .gitignore Decisions | [`.ai/conventions.md`](conventions.md) | What to commit vs. ignore; personal override pattern |
| AI Enforcement | [`.ai/conventions.md`](conventions.md) | How AI handles naming and organization violations |
| Stack-Specific Conventions (TypeScript+React) | [`.ai/stack-examples/typescript-react.md`](stack-examples/typescript-react.md) | Reference Code Organization rules for TS/React projects |
| Stack-Specific Conventions (Python+FastAPI) | [`.ai/stack-examples/python-fastapi.md`](stack-examples/python-fastapi.md) | Reference Code Organization rules for FastAPI projects |
| Stack-Specific Conventions (Embedded C/C++) | [`.ai/stack-examples/embedded-c.md`](stack-examples/embedded-c.md) | Reference Code Organization rules for firmware projects |

### Maintenance & Safety

| Section | File | Description |
|---------|------|-------------|
| Never Delete Rule | [`.ai/maintenance.md`](maintenance.md) | Always archive instead of permanently deleting |
| Archive Patterns | [`.ai/maintenance.md`](maintenance.md) | Path-mirroring and `YYYYMMDD/` dated snapshots; `.old` for single files |
| Never Reset Databases | [`.ai/maintenance.md`](maintenance.md) | What requires explicit confirmation before running |
| Stale Instruction Files | [`.ai/maintenance.md`](maintenance.md) | How to deprecate outdated instruction files |
| What AI Can Do Without Asking | [`.ai/maintenance.md`](maintenance.md) | Pre-approved reversible actions vs. actions requiring confirmation |

### Credentials & Security

| Section | File | Description |
|---------|------|-------------|
| Never Commit Credentials | [`.ai/credentials.md`](credentials.md) | Hard rule: no secrets in git, ever |
| .env File Convention | [`.ai/credentials.md`](credentials.md) | Flat per-module: `.env.example` (committed) + `.env` (gitignored) at each directory root |
| .gitignore Requirements | [`.ai/credentials.md`](credentials.md) | Mandatory gitignore patterns for all modules |
| Credential Warehouse Pattern | [`.ai/credentials.md`](credentials.md) | Where credentials live by environment |
| Rotating a Leaked Credential | [`.ai/credentials.md`](credentials.md) | Steps when a secret is accidentally committed |
| AI Behavior Rules | [`.ai/credentials.md`](credentials.md) | How AI handles credentials — never print, always use env vars |

### Environment & Host Isolation

| Section | File | Description |
|---------|------|-------------|
| Why This Exists | [`.ai/environment.md`](environment.md) | The problem host-mutating AI causes for a template-driven workspace |
| The Core Rule | [`.ai/environment.md`](environment.md) | Detect-then-act: containment first, host last; never silently mutate the host |
| Environment Detection | [`.ai/environment.md`](environment.md) | How to tell whether you are on the host or inside a container/venv/WSL |
| Allowed vs. Restricted Operations | [`.ai/environment.md`](environment.md) | Matrix of which commands are free, ask-first, or refuse-first by context |
| Per-Stack Containment | [`.ai/environment.md`](environment.md) | TypeScript/Node, Python, C/C++ — preferred isolation per stack |
| Devcontainers & Docker | [`.ai/environment.md`](environment.md) | When to recommend, what to scaffold |
| AI Behavior Rules | [`.ai/environment.md`](environment.md) | What the AI must do, ask, or refuse for env-mutating commands |

### Root Project

| Section | File | Description |
|---------|------|-------------|
| Project Overview | [`.ai/instruct.md`](instruct.md) | Template root authority scaffold; describes the adopted project's purpose |
| Architecture Overview | [`.ai/instruct.md`](instruct.md) | Template root architecture scaffold; filled during onboarding |
| Key Directories | [`.ai/instruct.md`](instruct.md) | Directory map with links to module .ai/ instructions |
| Global Rules Reference | [`.ai/instruct.md`](instruct.md) | Links to the canonical global rule files |

### Module: .example-module

| Section | File | Description |
|---------|------|-------------|
| Module Overview | [`.example-module/.ai/instruct.md`](../.example-module/.ai/instruct.md) | What .example-module does and its responsibilities |
| Subdirectory Rules | [`.example-module/.ai/instruct.md`](../.example-module/.ai/instruct.md) | Rules specific to this module |
| Global Rules Reference | [`.example-module/.ai/instruct.md`](../.example-module/.ai/instruct.md) | Cross-references to global rules |

### Example Showcase: .examples/

| Section | File | Description |
|---------|------|-------------|
| Showcase Overview | [`.examples/README.md`](../.examples/README.md) | What the filled-in examples demonstrate and how to use them |
| Module: auth-api | [`.examples/auth-api/.ai/instruct.md`](../.examples/auth-api/.ai/instruct.md) | Express+JWT+Postgres: layering, security, testing rules |
| Module: auth-api Before/After | [`.examples/auth-api/BEFORE-AFTER.md`](../.examples/auth-api/BEFORE-AFTER.md) | Side-by-side of AI behavior with/without module rules |
| Module: data-layer | [`.examples/data-layer/.ai/instruct.md`](../.examples/data-layer/.ai/instruct.md) | TypeORM entity, repository, migration discipline |
| Module: data-layer Before/After | [`.examples/data-layer/BEFORE-AFTER.md`](../.examples/data-layer/BEFORE-AFTER.md) | Side-by-side of AI behavior with/without module rules |
| Module: ui-component | [`.examples/ui-component/.ai/instruct.md`](../.examples/ui-component/.ai/instruct.md) | React+Tailwind component library rules |
| Module: ui-component Before/After | [`.examples/ui-component/BEFORE-AFTER.md`](../.examples/ui-component/BEFORE-AFTER.md) | Side-by-side of AI behavior with/without module rules |

---

## Rebuilding This Index

Run `/ai-update-index` in Copilot Chat to scan all instruction files and regenerate the tables above.

Manual process:
1. Find all instruction files: `file_search` for `**/.ai/instruct.md` and `.ai/*.md`
2. Exclude `.dev-docs/.old/`, `.archive/`
3. For each file, extract all `##` headings
4. Group by file, add a one-line description inferred from the section content
5. Update the tables above and the "Last Updated" date

**Do not alter** the "How to Use" or "Rebuilding This Index" sections during a rebuild.
