---
name: skill-development
description: "Authors Claude Code plugin skills under plugin-name/skills/ with progressive disclosure, third-person triggers, and lean SKILL.md bodies. Use when creating or improving plugin skills, plugin.json skill layout, or Claude Code skill structure. Not for Cursor skills (create-skill), Hermes in-repo chairs (hermes-agent-skill-authoring), or MCP server design (mcp-server-authoring)."
version: 0.1.1
---

# Skill Development for Claude Code Plugins

## Overview

Skills are modular, self-contained packages that extend Claude's capabilities with specialized workflows, tool integrations, domain expertise, and bundled resources. Each skill transforms a general-purpose agent into a domain specialist by providing procedural knowledge the model cannot fully possess.

### Skill Anatomy

```
skill-name/
├── SKILL.md              (required — frontmatter + markdown body)
├── references/           (optional — docs loaded into context as needed)
├── examples/             (optional — working, copy-adaptable code)
├── scripts/              (optional — executable utilities)
└── assets/               (optional — files used in output, not loaded into context)
```

### Progressive Disclosure (Three Levels)

| Level | What | When Loaded | Target Size |
|-------|------|-------------|-------------|
| 1 — Metadata | `name` + `description` in YAML frontmatter | Always in context | ~100 words |
| 2 — SKILL.md body | Core instructions, procedures, pointers | When skill triggers | 1,500–2,000 words (max 5,000) |
| 3 — Bundled resources | `references/`, `examples/`, `scripts/`, `assets/` | As needed by Claude | Unlimited (scripts can execute without reading) |

## When to Use

Trigger this skill when the user:

- Asks to "create a skill" or "write a new skill"
- Wants to "add a skill to plugin" or "add a skill to my plugin"
- Needs to "improve skill description" or "fix skill triggers"
- Wants to "organize skill content" or "restructure a skill"
- Asks about progressive disclosure, skill structure, or SKILL.md best practices
- Requests validation or review of an existing skill

## Prerequisites

- A Claude Code plugin directory with a `.claude-plugin/plugin.json` file
- Skills live under `plugin-name/skills/skill-name/`
- Windows host is primary; use PowerShell commands unless otherwise noted
- No external packaging tools required — plugin skills are distributed as part of the plugin

## Procedure

### Step 1 — Understand the Skill with Concrete Examples

Skip only when usage patterns are already clear. Ask focused questions (avoid overwhelming the user in a single message):

- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"
- "Are there edge cases or related tasks to cover?"

Conclude when there is a clear sense of the functionality the skill should support.

### Step 2 — Plan Reusable Skill Contents

Analyze each concrete example:

1. Consider how to execute the example from scratch
2. Identify what scripts, references, examples, and assets would help when executing repeatedly

| Resource Type | When to Include | Example |
|---------------|----------------|---------|
| `scripts/` | Same code rewritten repeatedly or deterministic reliability needed | a PDF-rotation helper in the scripts folder |
| `references/` | Documentation Claude should reference while working | a schema document in the references folder |
| `examples/` | Complete, runnable code users can copy and adapt | `examples/hook-example.sh` |
| `assets/` | Files used in output, not loaded into context | `assets/logo.png` |

**Key principle:** Information should live in either SKILL.md or references files — never both. Prefer references for detailed information; keep SKILL.md lean.

### Step 3 — Create Skill Structure

On Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path "plugin-name\skills\skill-name\references"
New-Item -ItemType Directory -Force -Path "plugin-name\skills\skill-name\examples"
New-Item -ItemType Directory -Force -Path "plugin-name\skills\skill-name\scripts"
New-Item -ItemType File -Force -Path "plugin-name\skills\skill-name\SKILL.md"
```

On macOS/Linux:

```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

Create only the directories actually needed. Delete any example files or directories not required for the skill.

### Step 4 — Write SKILL.md

#### 4a. Frontmatter

Use third-person format with specific trigger phrases:

```yaml
---
name: skill-name
description: This skill should be used when the user asks to "specific phrase 1", "specific phrase 2", "specific phrase 3". Include exact phrases users would say that should trigger this skill. Be concrete and specific.
version: 0.1.0
---
```

**Good description:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks", or mentions hook events (PreToolUse, PostToolUse, Stop).
```

**Bad description (do not do this):**
```yaml
description: Use this skill when working with hooks.        # Wrong person, vague
description: Load when user needs hook help.                # Not third person
description: Provides hook guidance.                        # No trigger phrases
```

#### 4b. Body — Writing Style

Write the entire skill using **imperative/infinitive form** (verb-first), not second person:

**Correct:**
```
To create a hook, define the event type.
Configure the MCP server with authentication.
Validate settings before use.
```

**Incorrect:**
```
You should create a hook by defining the event type.
You need to configure the MCP server.
You must validate settings before use.
```

#### 4c. Body — Content

Answer these questions in the body:

1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used? (Also in frontmatter description with specific triggers)
3. In practice, how should Claude use the skill? Reference all bundled resources so Claude knows they exist.

#### 4d. Keep SKILL.md Lean

Target 1,500–2,000 words for the body (max 5,000). Move detailed content to references:

| Content Type | Destination |
|--------------|-------------|
| Detailed patterns | a `patterns.md` file in the references folder |
| Advanced techniques | an `advanced.md` file in the references folder |
| Migration guides | a `migration.md` file in the references folder |
| API references | an `api-reference.md` file in the references folder |

If reference files are large (>10k words), include grep search patterns in SKILL.md so Claude can search efficiently.

#### 4e. Reference Bundled Resources in SKILL.md

```markdown
## Additional Resources

### Reference Files
- List every bundled file that actually exists (this skill ships `references/skill-creator-original.md`)
- For a skill you are authoring, name the real files you added — do not invent placeholders

### Example Files
- **`examples/example-script.sh`** — Working, runnable example (only if that file exists)

### Scripts
- Name each real helper in the scripts folder (only if that file exists)
```

### Step 5 — Validate and Test

1. **Check structure**: Skill directory is at `plugin-name/skills/skill-name/`
2. **Validate SKILL.md**: Has YAML frontmatter with `name` and `description`
3. **Check trigger phrases**: Description includes specific user queries in third person
4. **Verify writing style**: Body uses imperative/infinitive form, not second person
5. **Test progressive disclosure**: SKILL.md is lean (1,500–2,000 words), detailed content in references/
6. **Check references**: All referenced files actually exist
7. **Validate examples**: Examples are complete and correct
8. **Test scripts**: Scripts are executable and work correctly

Test by installing the plugin locally:

```powershell
# Windows (PowerShell)
cc --plugin-dir C:\path\to\plugin
```

```bash
# macOS/Linux
cc --plugin-dir /path/to/plugin
```

Then ask questions that should trigger the skill and verify it loads correctly.

### Step 6 — Iterate

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

**Common improvements:**
- Strengthen trigger phrases in description
- Move long sections from SKILL.md to references/
- Add missing examples or scripts
- Clarify ambiguous instructions
- Add edge case handling

## Pitfalls

### Pitfall 1: Weak Trigger Description

**Bad:**
```yaml
description: Provides guidance for working with hooks.
```
Vague, no specific trigger phrases, not third person.

**Good:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events. Provides comprehensive hooks API guidance.
```
Third person, specific phrases, concrete scenarios.

### Pitfall 2: Too Much in SKILL.md

**Bad:** Single 8,000-word SKILL.md with everything — bloats context every time the skill loads.

**Good:** 1,800-word SKILL.md with companion files in the references folder for patterns and advanced techniques — progressive disclosure, detailed content loaded only when needed.

### Pitfall 3: Second-Person Writing

**Bad:**
```markdown
You should start by reading the configuration file.
You need to validate the input.
You can use the grep tool to search.
```

**Good:**
```markdown
Start by reading the configuration file.
Validate the input before processing.
Use the grep tool to search for patterns.
```

### Pitfall 4: Missing Resource References

**Bad:** SKILL.md has core content but never mentions `references/` or `examples/` — Claude doesn't know they exist.

**Good:** SKILL.md includes an "Additional Resources" section listing every bundled file with a one-line description.

### Pitfall 5: Duplicated Information

**Bad:** Same schema documented in both SKILL.md and a schema file in the references folder.

**Good:** SKILL.md has a brief pointer; the full schema lives only in that companion file.

### Pitfall 6: Creating Unneeded Directories

**Bad:** Creating `examples/`, `scripts/`, and `assets/` directories that remain empty.

**Good:** Create only the directories that will contain actual files.

## Verification

### Structure Check (PowerShell)

```powershell
# Verify SKILL.md exists
Test-Path "plugin-name\skills\skill-name\SKILL.md"

# Verify frontmatter has name and description
Select-String -Path "plugin-name\skills\skill-name\SKILL.md" -Pattern "^name:"
Select-String -Path "plugin-name\skills\skill-name\SKILL.md" -Pattern "^description:"

# Count words in body (approximate)
(Get-Content "plugin-name\skills\skill-name\SKILL.md" -Raw).Split().Count
```

### Structure Check (Bash)

```bash
# Verify SKILL.md exists
test -f plugin-name/skills/skill-name/SKILL.md && echo "OK"

# Verify frontmatter
head -5 plugin-name/skills/skill-name/SKILL.md

# Word count
wc -w plugin-name/skills/skill-name/SKILL.md
```

### Validation Checklist

**Structure:**
- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] Frontmatter has `name` and `description` fields
- [ ] Markdown body is present and substantial
- [ ] All referenced files actually exist

**Description Quality:**
- [ ] Uses third person ("This skill should be used when...")
- [ ] Includes specific trigger phrases users would say
- [ ] Lists concrete scenarios ("create X", "configure Y")
- [ ] Not vague or generic

**Content Quality:**
- [ ] Body uses imperative/infinitive form (no second person)
- [ ] Body is 1,500–2,000 words (max 5,000)
- [ ] Detailed content moved to references/
- [ ] Examples are complete and working
- [ ] Scripts are executable and documented

**Progressive Disclosure:**
- [ ] Core concepts in SKILL.md
- [ ] Detailed docs in references/
- [ ] Working code in examples/
- [ ] Utilities in scripts/
- [ ] SKILL.md references all bundled resources

**Testing:**
- [ ] Skill triggers on expected user queries
- [ ] Content is helpful for intended tasks
- [ ] No duplicated information across files
- [ ] References load when needed

## Examples

### Minimal Skill

```
skill-name/
└── SKILL.md
```
Good for: Simple knowledge, no complex resources needed.

### Standard Skill (Recommended)

```
skill-name/
├── SKILL.md
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```
Good for: Most plugin skills with detailed documentation.

### Complete Skill

```
skill-name/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
├── examples/
│   ├── example1.sh
│   └── example2.json
└── scripts/
    └── validate.sh
```
Good for: Complex domains with validation utilities.

### Reference Study: Plugin-Dev Skills

Study these skills as examples of best practices:

| Skill | Word Count | References | Examples | Scripts | Strengths |
|-------|-----------|------------|----------|---------|-----------|
| `hook-development` | 1,651 | 3 | 3 | 3 | Excellent trigger phrases, progressive disclosure |
| `agent-development` | 1,438 | Yes | Yes | — | AI-assisted creation, focused body |
| `plugin-settings` | — | Yes | — | Yes | Real implementations, parsing scripts |

## Related Skills

- `../hook-development/` — Progressive disclosure, utilities
- `../agent-development/` — AI-assisted creation, references
- `../mcp-integration/` — Comprehensive references
- `../plugin-settings/` — Real-world examples
- `../command-development/` — Clear critical concepts
- `../plugin-structure/` — Good organization

## Additional Resources

### Reference Files

Load `references/skill-creator-original.md` when the full original skill-creator methodology is needed — it contains the complete canonical workflow that informed this skill's structure.
