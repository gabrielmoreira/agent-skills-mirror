---
name: hermes-agent-skill-authoring
description: "Authors in-repo hermes-agent SKILL.md files: frontmatter validator rules, peer-matched metadata, writing quality, and git placement under the package skills tree. Use when adding or reviewing a skill that ships with hermes-agent. Not for user-local ~/.hermes/skills via skill_manage create, Cursor skills (create-skill), or workflow-pattern architecture (designing-workflow-skills)."
version: 1.1.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [plan, requesting-code-review]
---

# Authoring Hermes-Agent Skills (In-Repo)

## Overview

There are two locations a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill's focus):** `<hermes-agent-checkout>/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

> **Windows host note:** If you are running on a Windows host (PowerShell), the repo may be checked out at a path like `~\agent-skills\library\hermes-agent-skill-authoring\` or similar. Adjust path separators accordingly. The validator and all commands below work the same regardless of OS; just use the correct path style for your shell.

## When to Use

- User asks you to add a skill "in this branch / repo / commit."
- You are committing a reusable workflow that should ship with hermes-agent.
- You are editing an existing skill under `<hermes-agent-checkout>/skills/` (use `patch` for small edits, `write_file` for rewrites).
- You are reviewing a peer skill for structure, frontmatter, or writing quality.

**Don't use for:**
- Creating a personal user-local skill (use `skill_manage(action='create')` instead — it targets `~/.hermes/skills/`).
- One-off scratch instructions that won't be reused.

## Prerequisites

- Write access to a hermes-agent git checkout (resolve the repo root; do not assume a publisher home directory).
- `git` on the active branch where the skill should land.
- Python 3 with `pyyaml` installed (for local validation).
- Familiarity with `skill_manage` tool actions: `create`, `patch`, `edit`, `write_file`, `view`.

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the **first bytes** (no leading blank line, no BOM).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present, ≤ **64 chars** (`MAX_NAME_LENGTH`), lowercase + hyphens.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by every skill under `skills/software-development/`:

```yaml
---
name: my-skill-name
description: Use when <trigger>. <one-line behavior>.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version`, `author`, `license`, and `metadata` are NOT enforced by the validator, but every peer has them — omit and your skill sticks out.

## Size Limits

| Field | Limit | Enforced? |
|---|---|---|
| `description` | ≤ 1024 chars | Yes |
| Full SKILL.md | ≤ 100,000 chars (`MAX_SKILL_CONTENT_CHARS`, ~36k tokens) | Yes |
| Peer skills in `software-development/` | 8–14k chars | Target range |

If you push past 20k chars, split into `references/*.md` and reference them from SKILL.md.

## Writing Quality Principles

A skill exists to make the agent's process more predictable. Predictability does **not** mean identical output every run; it means the agent reliably follows the same useful discipline.

1. **Optimize for process predictability.** Ask: what behavior should change when this skill loads? If a line does not change behavior, cut it.
2. **Choose the right context load.** A model-invoked Hermes skill pays for its description every turn. Keep descriptions focused on trigger classes and the skill's distinctive behavior. Put details in the body or linked references.
3. **Use an information hierarchy.** Put always-needed steps in `SKILL.md`; put branch-specific or bulky reference material in `references/`, `templates/`, or `scripts/` and point to it only when needed.
4. **End steps with completion criteria.** Each ordered step should say how the agent knows it is done. Good criteria are checkable and, when it matters, exhaustive: "every modified file accounted for" beats "summarize changes."
5. **Co-locate rules with the concept they govern.** Avoid scattering one idea across the file. Keep definition, caveats, examples, and verification near each other.
6. **Use strong leading words.** Prefer compact concepts the model already knows — e.g. "tight loop," "tracer bullet," "root cause," "regression test" — over long repeated explanations. A good leading word saves tokens and anchors behavior.
7. **Prune duplication and no-ops.** Keep each meaning in one source of truth. Sentence by sentence, ask whether the sentence changes agent behavior versus the default. If not, delete it rather than polishing it.
8. **Watch for premature completion.** If agents tend to rush a step, first sharpen that step's completion criterion. Split the sequence only when later steps distract from doing the current step well.

**Common quality failures:**

- **Premature completion** — the skill lets the agent move on before the work is genuinely done.
- **Duplication** — the same rule appears in multiple places and drifts.
- **Sediment** — stale lines remain because adding felt safer than deleting.
- **Sprawl** — too much always-visible material; push branch-specific reference behind pointers.
- **No-op prose** — generic advice the agent would already follow without the skill.

## Peer-Matched Structure

Every in-repo skill follows roughly:

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (peer test runners in the hermes-agent repo, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

Not every section is mandatory, but `Overview` + `When to Use` + actionable body + pitfalls are the minimum for the skill to feel like a peer.

## Directory Placement

```
skills/<category>/<skill-name>/SKILL.md
```

Categories currently in repo (confirm with `ls skills/`): `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Pick the closest existing category. Don't invent new top-level categories casually.

### Supporting Files

When a skill needs bulky reference material, templates, or scripts, place them in subdirectories:

- `skills/<category>/<name>/references/<file>.md` — load when the agent needs deep branch-specific detail.
- `skills/<category>/<name>/templates/<file>` — load when the agent needs a copy-paste template.
- `skills/<category>/<name>/scripts/<file>` — load when the agent needs to run a helper script.
- `skills/<category>/<name>/assets/<file>` — load for static assets (images, data files).

`skill_manage(action='write_file')` enforces the supporting-subdir allowlist (`references`, `templates`, `scripts`, and `assets`). Use `write_file` directly for the same effect.

## Procedure

### 1. Survey peers in the target category

```bash
ls skills/<category>/
```

Read 2–3 peer SKILL.md files to match tone and structure. **Completion criterion:** you can name the common sections and frontmatter fields used by peers.

### 2. Check validator constraints

If unsure about any constraint, inspect the source of truth:

```bash
grep -n "MAX_DESCRIPTION_LENGTH\|MAX_NAME_LENGTH\|MAX_SKILL_CONTENT_CHARS" tools/skill_manager_tool.py
```

**Completion criterion:** you have confirmed the current numeric limits from source, not memory.

### 3. Draft the SKILL.md

Use `write_file` to create `skills/<category>/<name>/SKILL.md`. Follow the peer-matched structure above. Ensure:

- First bytes are exactly `---` (no BOM, no leading newline).
- Frontmatter closes with `\n---\n`.
- Description starts with "Use when ..." and describes the trigger class.
- Each ordered step ends with a checkable completion criterion.

**Completion criterion:** file exists at the correct path and opens without encoding errors.

### 4. Validate locally

Run this Python snippet to confirm frontmatter and size constraints:

```python
import yaml, re, pathlib
content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
assert content.startswith("---"), "File must start with --- at byte 0"
m = re.search(r'\n---\s*\n', content[3:])
assert m, "Frontmatter must close with \\n---\\n"
fm = yaml.safe_load(content[3:m.start()+3])
assert "name" in fm, "Missing name field"
assert "description" in fm, "Missing description field"
assert len(fm["description"]) <= 1024, f"Description too long: {len(fm['description'])}"
assert len(content) <= 100_000, f"File too large: {len(content)} chars"
print("VALID")
```

**Completion criterion:** script prints `VALID` with no assertion errors.

### 5. Git add + commit

```bash
git add skills/<category>/<name>/
git commit -m "Add skill: <name>"
```

**Completion criterion:** `git log --oneline -1` shows your commit on the intended branch.

### 6. Confirm session cache limitation

The current session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug. To verify, start a fresh session or use `skill_view` with the exact path.

**Completion criterion:** you have informed the user that a new session is needed to see the skill in `skills_list`.

## Cross-Referencing Other Skills

`metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh. Prefer referencing only in-repo skills from in-repo skills. If a frequently-referenced skill lives only in `~/.hermes/skills/`, consider promoting it to the repo.

## Editing Existing In-Repo Skills

| Edit type | Tool | Notes |
|---|---|---|
| Small fix (typo, added pitfall, tightened trigger) | `skill_manage(action='patch', name=..., old_string=..., new_string=...)` | Works fine on in-repo skills. |
| Major rewrite | `write_file` the whole SKILL.md | `skill_manage(action='edit')` also works but requires full new content. |
| Adding supporting files | `write_file` to `references/`, `templates/`, `scripts/`, or `assets/` | `skill_manage(action='write_file')` also works and enforces subdir allowlist. |

**Always commit** the edit — in-repo skills are source, not runtime state.

## Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file` for in-repo creation.

2. **Leading whitespace before `---`.** The validator checks `content.startswith("---")`; any leading blank line or BOM fails validation. Ensure the file's first three bytes are exactly `---`.

3. **Description too generic.** Peer descriptions start with "Use when ..." and describe the *trigger class*, not the one task. "Use when debugging X" > "Debug X".

4. **Forgetting the author/license/metadata block.** Not validator-enforced, but every peer has it; omitting makes the skill look half-finished.

5. **Writing a skill that duplicates a peer.** Before creating, `ls skills/<category>/` and open 2–3 peers. Prefer extending an existing skill to creating a narrow sibling.

6. **Expecting the current session to see the new skill.** It won't. The skill loader is initialized at session start. Verify in a fresh session or via `skill_view` using the exact path.

7. **Letting skills accumulate sediment.** A skill should get shorter or sharper over time. When adding a rule, remove the old wording it replaces; don't layer advice forever.

8. **Writing no-op prose.** "Be careful," "be thorough," and "use best practices" rarely change model behavior. Replace with a checkable completion criterion or a stronger leading word.

9. **Linking to skills that don't exist in-repo.** `related_skills: [some-user-local-skill]` works for you but breaks for other clones. Prefer only in-repo links.

10. **Exceeding size limits.** Description > 1024 chars or file > 100,000 chars fails validation. If approaching limits, move detail to `references/*.md`.

## Verification

Run each check below after authoring or editing a skill:

```bash
# 1. Confirm file is in the repo tree, not user-local
ls skills/<category>/<name>/SKILL.md

# 2. Confirm first bytes are ---
head -c 3 skills/<category>/<name>/SKILL.md
# Expected output: ---

# 3. Confirm frontmatter parses and constraints hold
python3 -c "
import yaml, re, pathlib
c = pathlib.Path('skills/<category>/<name>/SKILL.md').read_text()
assert c.startswith('---')
m = re.search(r'\n---\s*\n', c[3:])
fm = yaml.safe_load(c[3:m.start()+3])
assert 'name' in fm and 'description' in fm
assert len(fm['description']) <= 1024
assert len(c) <= 100_000
print('VALID')
"

# 4. Confirm git status is clean (committed)
git status --porcelain skills/<category>/<name>/
# Expected: no output (all committed)

# 5. Confirm related_skills resolve in-repo
# For each skill listed in metadata.hermes.related_skills, verify:
ls skills/<category>/<referenced-skill>/SKILL.md
```

**Verification checklist:**

- [ ] File is at `skills/<category>/<name>/SKILL.md` (not in `~/.hermes/skills/`)
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Description ≤ 1024 chars and starts with "Use when ..."
- [ ] Total file ≤ 100,000 chars (aim for 8–15k)
- [ ] Structure: `# Title` → `## Overview` → `## When to Use` → body → `## Pitfalls` → `## Verification`
- [ ] Each ordered step has a checkable completion criterion
- [ ] Description is trigger-focused and avoids duplicated body content
- [ ] Bulky or branch-specific reference is progressively disclosed in linked files (`references/`, `templates/`, `scripts/`)
- [ ] No-op prose and duplicated rules removed
- [ ] `related_skills` references resolve in-repo (or are explicitly OK to be user-local)
- [ ] `git add skills/<category>/<name>/ && git commit` completed on the intended branch

## Related Skills

- `plan` — for planning multi-step skill authoring work
- `requesting-code-review` — for reviewing a skill before commit
