---
description: "How heirs install skills, trifectas, MCP configs, patterns, and scaffolds from Alex_Skill_Mall — into the right paths so Edition upgrades don't clobber them"
applyTo: "**/.github/skills/local/**,**/.github/instructions/local/**,**/.github/muscles/local/**,**/.github/prompts/local/**,**/.mcp.json,**/mcp.json"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Mall Installation

[Alex_Skill_Mall](https://github.com/fabioc-aloha/Alex_Skill_Mall) is a public catalog of optional add-ons. Heirs pull what they need on-demand — the brain stays small by default.

## Skill Selection Protocol

Before installing from the Mall, assess what the project actually needs. Do not install everything available — install only what earns its token cost.

### Step 1 — Inventory what the project does

Read the project's `copilot-instructions.local.md`, `README.md`, `package.json`, and top-level directory structure. Identify:

- Primary language/framework (Node, Python, .NET, Bicep, etc.)
- Domain (healthcare, publishing, finance, infrastructure, etc.)
- Key workflows (MCP server, VS Code extension, data pipeline, etc.)

### Step 2 — Check what the heir already has

List `.github/skills/local/` — these are already installed. Do not reinstall or duplicate.

List `.github/skills/` (edition-owned) — the Edition baseline already covers general-purpose skills. Do not install Mall skills that overlap with Edition baseline.

### Step 3 — Match project needs to Mall categories

Consult the Mall `CATALOG.json`. Fetch directly from GitHub if no local clone:

```bash
gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/CATALOG.json --jq .content | base64 -d
```

Or read from local clone at `~/Alex_Skill_Mall/CATALOG.json` if available. Match by:

| Project signal | Mall category to check |
| --- | --- |
| VS Code extension (`package.json` has `engines.vscode`) | `vscode/`, `quality/testing-strategies` |
| MCP server code | `ai-llm/mcp-builder`, `ai-llm/mcp-development` |
| Azure resources (Bicep, ARM, Fabric) | `azure/`, `infrastructure/` |
| Healthcare/clinical data | `domain/healthcare-informatics` |
| Book/publishing project | `publishing/`, `academic/` |
| Security-sensitive (auth, tokens, APIs) | `security/` |
| Data analysis (Python, KQL, notebooks) | `data/` |
| Document conversion (Pandoc, PDF, Word) | `converters/` |

### Step 4 — Apply the selection filter

For each candidate skill, ask:

| Question | If no, skip |
| --- | --- |
| Does this project actually do the thing this skill covers? | Skip — aspirational installs waste tokens |
| Is this already covered by an Edition baseline instruction or skill? | Skip — don't shadow Edition |
| Would this skill be used in the next 30 days of work? | Skip — install on demand later |
| Is the skill's `tier` appropriate? (`core` = always, `standard` = common, `extended` = niche) | Skip extended unless the project is in that niche |

### Step 5 — Install selected skills

Follow the installation steps below. Copy contents, not folders. Commit once after all installs.

## What's in the Mall

| Type | Path in Mall | Where it goes in heir |
|------|--------------|----------------------|
| Skill (alone) | `skills/<category>/<name>/SKILL.md` | `.github/skills/local/<name>/SKILL.md` |
| Skill + muscle | `skills/<category>/<name>/SKILL.md` + `<name>.cjs` | `.github/skills/local/<name>/SKILL.md` AND `.github/muscles/local/<name>.cjs` |
| Trifecta (skill + instruction + muscle) | `skills/<category>/<name>/` containing all three | Each part to its `local/` home |
| MCP server config | `mcp/<name>.json` | merge into heir's `.mcp.json` (root) — see MCP section |
| Pattern | `patterns/<name>.md` | `.github/instructions/local/<name>.instructions.md` (with frontmatter added) |
| Config | `configs/<name>/` | `.vscode/`, `.github/config/local/`, or repo root — see Config section |
| Scaffold | `scaffolds/<name>/` | bootstrap a new repo, not added to existing one |

## Cardinal Rule: Use `local/` Subdirs

Edition's `sync-policy.json` declares these as **heir-owned** (never overwritten on upgrade):

- `.github/skills/local/**`
- `.github/instructions/local/**`
- `.github/muscles/local/**`
- `.github/prompts/local/**`

Putting Mall content directly under `.github/skills/<name>/` (no `local/`) means the next `upgrade-self.cjs --apply` will **delete it** because that path is edition-owned. Always install into `local/`.

## Install a Skill (most common case)

1. **Search** the catalog: `/find-skill <keyword>` or browse <https://github.com/fabioc-aloha/Alex_Skill_Mall/blob/main/CATALOG.json>

2. **Download from GitHub** (preferred — no local clone needed):

   Use `gh` CLI to fetch skill contents directly from the Mall repo:

   ```bash
   # Create local skill directory
   mkdir -p .github/skills/local/<name>

   # Download SKILL.md from Mall
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/skills/<category>/<name>/SKILL.md \
     --jq .content | base64 -d > .github/skills/local/<name>/SKILL.md
   ```

   For skills with multiple files (references/, scripts/), list the directory first:

   ```bash
   # List all files in the skill
   gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/skills/<category>/<name> \
     --jq '.[].path'
   ```

   Then download each file the same way. The AI should automate this — read the directory listing and download all files.

3. **Alternative — local clone** (if `gh` is unavailable or for bulk installs):

   ```bash
   git clone https://github.com/fabioc-aloha/Alex_Skill_Mall.git ~/Alex_Skill_Mall
   mkdir -p .github/skills/local/<name>
   cp -r ~/Alex_Skill_Mall/skills/<category>/<name>/* .github/skills/local/<name>/
   ```

   **Critical**: The `/*` glob copies files INTO the target. Without it, you get nested `<name>/<name>/SKILL.md`.

4. **If the skill ships a `.cjs` companion**, move it to muscles:

   ```bash
   mkdir -p .github/muscles/local
   mv .github/skills/local/<name>/<name>.cjs .github/muscles/local/<name>.cjs
   ```

   Then update any path references in `SKILL.md` from `<name>.cjs` to `.github/muscles/local/<name>.cjs`.

5. **Verify** the SKILL.md's `External Dependencies` section — install Pandoc, jszip, etc. if listed.
6. **Commit**:

   ```bash
   git add .github/skills/local .github/muscles/local
   git commit -m "Install <name> from Alex_Skill_Mall"
   ```

## Install a Pattern

Patterns in the Mall are plain `.md` files with no frontmatter. Convert to a heir instruction:

1. Copy `patterns/<name>.md` to `.github/instructions/local/<name>.instructions.md`
2. Prepend YAML frontmatter:

   ```yaml
   ---
   description: "<one-line summary from the pattern>"
   applyTo: "<glob matching files where this pattern should auto-load>"
   ---
   ```

3. Commit.

## Install an MCP Server (forward-looking)

When the Mall ships MCP configs (under `mcp/<name>.json`), the install pattern is:

1. Read the Mall's `mcp/<name>.json` — it contains a single MCP server definition
2. Merge into the heir's MCP config file:
   - VS Code: `.mcp.json` at repo root, or user-level `~/.config/Code/User/mcp.json`
   - Claude Code: `.mcp.json` at repo root
3. Install any required CLI/runtime listed in the config's `requires` field
4. Restart the AI client to pick up the new server
5. Commit `.mcp.json` (do NOT commit secrets — use env vars or user-level config for those)

MCP configs are **not** edition-owned — they live at repo root, not under `.github/`, so Edition upgrades never touch them.

## Install a Config

Configs in the Mall are portable, drop-in tool configurations (VS Code themes, editor settings, linter rules) — consumed by tooling, not by AI assistants.

1. Read the config's own `README.md` in `configs/<name>/` for tool-specific install steps
2. Typical destinations:
   - `.vscode/` — VS Code settings, themes, snippets
   - `.github/config/local/` — heir-owned configs that should travel with the repo's brain
   - Repo root — `.editorconfig`, `.eslintrc`, etc.
3. Reference it from the consuming tool's config file (e.g. `markdown.styles` in `.vscode/settings.json`)
4. Commit

Configs in `.github/config/local/` are heir-owned per `sync-policy.json` — Edition upgrades never touch them.

## Install a Scaffold

Scaffolds are full project starters. Don't drop them into an existing heir — use them to bootstrap a new repo:

```bash
cp -r ~/Alex_Skill_Mall/scaffolds/<name> /path/to/new-project
cd /path/to/new-project
git init && git add -A && git commit -m "Initial commit from Alex_Skill_Mall scaffold/<name>"
node .github/scripts/bootstrap-heir.cjs --heir-id <name> --owner <you>
```

## Verifying the Install

After any Mall install, verify Edition won't clobber it:

```bash
node .github/scripts/upgrade-self.cjs   # dry-run, no --apply
```

The dry-run output should NOT list your installed `local/` files in the "would write" or "would delete" sections. If it does, you put them in the wrong path — move them under `local/`.

## Updating an Installed Skill

The Mall is independent of your heir — there's no automatic update channel. To refresh:

1. `git -C ~/Alex_Skill_Mall pull`
2. Diff the new version against your installed copy: `diff -r ~/Alex_Skill_Mall/skills/<cat>/<name>/ .github/skills/local/<name>/`
3. Apply changes manually if you want them — or keep your local edits

If you customised an installed skill, your edits are heir-owned. The Mall version is upstream — you choose what to bring in.

## Promoting a Local Skill to the Mall

If a `local/` skill matures and could help others, contribute it back:

1. Strip per `cross-project-isolation.instructions.md` (no client names, no project specifics)
2. Open a PR against `Alex_Skill_Mall` adding it to the right category
3. Once merged, you can `cp` from the canonical Mall path so the local is no longer custom-edited

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Installed under `.github/skills/<name>/` (no `local/`) | Skill disappears on next `upgrade-self.cjs --apply` | Move under `.github/skills/local/<name>/` |
| Forgot to move `.cjs` companion to `muscles/local/` | SKILL.md path references break | Move file, update path in SKILL.md |
| Pattern installed with no frontmatter | Instruction never auto-loads | Add `description` + `applyTo` frontmatter |
| Skipped External Dependencies check | Skill fails with `command not found` | Read SKILL.md fully before using |
