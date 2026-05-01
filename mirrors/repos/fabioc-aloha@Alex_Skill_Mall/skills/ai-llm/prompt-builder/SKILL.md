---
type: skill
lifecycle: stable
inheritance: inheritable
name: prompt-builder
description: Create and validate .prompt.md files that pass brain-qa on first attempt
tier: standard
applyTo: '**/*prompt*,**/*builder*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Prompt Builder


> Build `.prompt.md` files that pass brain-qa on first attempt — no regressions

---

## When to Use

- Creating a new `.prompt.md` file
- Fixing a failing prompt in brain-qa
- Adding prompts to the loop menu config
- Reviewing prompt frontmatter for completeness

---

## Prompt Anatomy

Every `.prompt.md` has two parts: **YAML frontmatter** and **Markdown body**.

### Frontmatter (Required Fields)

| Field | Required | Gate | Purpose |
|-------|----------|------|---------|
| `description` | **Yes** | **Yes** | What the prompt does (1 sentence) |
| `application` | **Yes** | **Yes** | When/why to use it (distinct from description) |
| `mode` | Conditional | No | Set to `agent` for loop prompts |
| `agent` | Conditional | No | Named agent for root prompts |
| `tools` | Conditional | No | Tool array for loop prompts |

**Gate fields** (`description` + `application`) are mandatory — brain-qa fails without both.

### brain-qa Scoring (4 points)

| Flag | Points | Rule |
|------|--------|------|
| `desc` | 1 | `description:` exists in frontmatter |
| `app` | 1 | `application:` exists in frontmatter |
| `agent` | 1 | `agent:` OR `mode: agent` exists |
| `>20L` | 1 | Body exceeds 20 lines |

**Pass** = both gates (`desc` + `app`) AND score >= 3.

---

## Two Archetypes

### Root Prompts (`.github/prompts/*.prompt.md`)

Invoked directly by name. Typically route to a named agent.

```yaml
---
description: "What this prompt does"
application: "When to use this prompt"
agent: the AI assistant
---
```

**Key rules:**

- Use `agent:` to name the target agent (the AI assistant, Researcher, Validator, etc.)
- Do NOT use `mode:` or `tools:` — those are for loop prompts
- Body should be 20+ lines with clear instructions

### Loop Prompts (`.github/prompts/loop/*.prompt.md`)

Sidebar buttons in the extension Loop tab. Loaded by `loopMenu.ts`.

```yaml
---
mode: agent
description: "What this prompt does"
application: "When to use this prompt"
tools: ["read_file", "create_file", "run_in_terminal"]
---
```

**Key rules:**

- Always include `mode: agent`
- Always include `tools:` array with relevant tool names
- Do NOT use `agent:` — loop prompts use mode-based routing
- Body should be 20+ lines with phase-based instructions

---

## Field Writing Rules

### `description` vs `application`

These are distinct fields — do not duplicate content between them.

| Field | Answers | Example |
|-------|---------|---------|
| `description` | "What does this do?" | "3-pass code review with confidence scoring" |
| `application` | "When should I use this?" | "Review code for correctness, security, and maintainability" |

**Anti-pattern:** Making `application` a rephrasing of `description`.

### `tools` Array (Loop Prompts Only)

Include only tools the prompt actually needs:

| Tool | When to Include |
|------|-----------------|
| `read_file` | Reads existing code or docs |
| `create_file` | Generates new files |
| `replace_string_in_file` | Edits existing files |
| `run_in_terminal` | Runs commands (build, test, deploy) |
| `grep_search` | Searches codebase for patterns |
| `semantic_search` | Semantic code search |
| `list_dir` | Explores directory structure |
| `fetch_webpage` | Web research |
| `view_image` | Image analysis |
| `get_errors` | Reads diagnostics |
| `codebase` | VS Code codebase tool |
| `terminal` | VS Code terminal tool |
| `editFiles` | VS Code edit tool |

---

## Body Structure

### Minimum Viable Body (20+ Lines)

```markdown
# {Title}

{1-2 sentence intro describing the workflow}

## Phase 1: {Discovery/Setup}

{Steps for initial context gathering}

## Phase 2: {Execution}

{Core workflow steps}

## Phase 3: {Validation}

{How to verify the work}

## Output

{What the user should expect}
```

### Using Variables

- `$ARGUMENTS` — User's input text (root prompts)
- `${{input}}` — VS Code variable for selected text
- Reference skills with: "Load `.github/skills/{name}/SKILL.md`"

---

## Checklist Before Commit

Run mentally before saving any `.prompt.md`:

- [ ] `description:` present and meaningful
- [ ] `application:` present and distinct from description
- [ ] Root prompt has `agent:` OR loop prompt has `mode: agent` + `tools:`
- [ ] Body exceeds 20 lines
- [ ] No duplicate of existing prompt (check `.github/prompts/`)
- [ ] If loop prompt: registered in `.github/config/loop-menu.json`

---

## Common Failures and Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| `app=0` | Missing `application:` | Add field after `description:` |
| `desc=0` | Missing `description:` | Add field in frontmatter |
| `agent=0` | No `agent:` or `mode: agent` | Add appropriate field |
| `>20L=0` | Body too short | Expand with phases/instructions |
| Score 3 but FAIL | Has score but missing a gate | Ensure both `description` AND `application` exist |
