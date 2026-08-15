---
name: create-skill
description: "Authors Cursor Agent Skills: SKILL.md frontmatter, third-person descriptions, progressive disclosure, and ~/.cursor/skills or .cursor/skills layout. Use when the user asks to create a skill, write a SKILL.md, or design skill structure and triggers. Not for AGENTS.md/CLAUDE.md (agents-md), Claude Code plugin skill packs (skill-development), hermes-agent in-repo skills, or general markdown docs."
version: 1.0.1
---

# Creating Cursor Agent Skills

This skill teaches you how to author production-grade Agent Skills for Cursor. A skill is a directory containing a `SKILL.md` file (plus optional references and scripts) that instructs the agent on a specialized workflow: PR reviews, commit message formatting, database schema queries, PDF processing, etc.

## When to Use

Use this skill when the user:

- Asks to **create** a new skill or write a `SKILL.md`
- Wants to know the **structure**, **frontmatter**, or **directory layout** of a skill
- Asks about **progressive disclosure**, reference files, or `scripts/` usage
- Wants to **improve** or **refactor** an existing skill
- Mentions `.cursor/skills/`, `~/.cursor/skills/`, or agent-skills library

Do NOT use this skill for general markdown authoring or documentation that is not a Cursor skill.

## Prerequisites

- Cursor editor with agent mode
- Write access to either `~/.cursor/skills/` (personal) or `.cursor/skills/` (project)
- Optional: Python or shell runtime if the skill will include utility scripts

## Procedure

### Phase 1 — Discovery

Gather the following from the user before writing anything:

1. **Purpose and scope**: What specific task or workflow does this skill cover?
2. **Target location**: Personal (`~/.cursor/skills/`) or project (`.cursor/skills/`)?
3. **Trigger scenarios**: When should the agent automatically apply this skill?
4. **Key domain knowledge**: What specialized info does the agent need that it wouldn't already know?
5. **Output format preferences**: Specific templates, formats, or styles required?
6. **Existing patterns**: Existing examples or conventions to follow?

If the `AskQuestion` tool is available, use it for structured gathering:

```
Example AskQuestion usage:
- "Where should this skill be stored?" with options like ["Personal (~/.cursor/skills/)", "Project (.cursor/skills/)"]
- "Should this skill include executable scripts?" with options like ["Yes", "No"]
```

If `AskQuestion` is not available, ask conversationally.

**Verbatim text rule**: If the user includes exact wording to use in the skill, respect it and use it **verbatim** in `SKILL.md` (same words, same order). Do not paraphrase, soften, or expand their copy, and do not add unrequested headings or commentary around it.

**Inferring from context**: If previous conversation context exists, infer the skill from what was discussed. You can create skills based on workflows, patterns, or domain knowledge that emerged in the conversation.

### Phase 2 — Design

1. Draft the skill name: lowercase letters, numbers, hyphens only; max 64 chars. Match the folder name exactly.
2. Write a specific, third-person description (see § Writing Effective Descriptions).
3. Outline the main sections needed.
4. Identify whether supporting files (`reference.md`, `examples.md`) or utility scripts (`scripts/`) are needed.

### Phase 3 — Implementation

#### Directory Layout

Example layout for a skill you are authoring. Names such as validate.py are illustrative — this pack does not ship those helpers.

```
skill-name/
├── SKILL.md              # Required - main instructions
├── reference.md          # Optional - detailed documentation
├── examples.md           # Optional - usage examples
└── scripts/              # Optional - utility scripts
    ├── validate.py
    └── helper.sh
```

#### Storage Locations

| Type | Path | Scope |
|------|------|-------|
| Personal | `~/.cursor/skills/skill-name/` | Available across all your projects |
| Project | `.cursor/skills/skill-name/` | Shared with anyone using the repository |

**HARD RULE — Never create skills in `~/.cursor/skills-cursor/`.** This directory is reserved for Cursor's internal built-in skills and is managed automatically by the system.

#### SKILL.md Structure

Every skill requires a `SKILL.md` file with YAML frontmatter and a markdown body:

```markdown
---
name: your-skill-name
description: Brief description of what this skill does and when to use it
disable-model-invocation: true
---

# Your Skill Name

## Instructions
Clear, step-by-step guidance for the agent.

## Examples
Concrete examples of using this skill.
```

**Default `disable-model-invocation: true`** so the skill only loads when named explicitly. Omit it only when the agent should auto-invoke from ambient context.

#### Required Metadata Fields

| Field | Requirements | Purpose |
|-------|--------------|---------|
| `name` | Max 64 chars, lowercase letters/numbers/hyphens only | Unique identifier for the skill |
| `description` | Max 1024 chars, non-empty | Helps agent decide when to apply the skill |

#### Writing Effective Descriptions

The description is **critical** for skill discovery — the agent uses it to decide when to apply your skill.

1. **Write in third person** (the description is injected into the system prompt):
   - ✅ Good: "Processes Excel files and generates reports"
   - ❌ Avoid: "I can help you process Excel files"
   - ❌ Avoid: "You can use this to process Excel files"

2. **Be specific and include trigger terms**:
   - ✅ Good: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
   - ❌ Vague: "Helps with documents"

3. **Include both WHAT and WHEN**:
   - WHAT: What the skill does (specific capabilities)
   - WHEN: When the agent should use it (trigger scenarios)

Description examples:

```yaml
# PDF Processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Excel Analysis
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.

# Git Commit Helper
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.

# Code Review
description: Review code for quality, security, and best practices following team standards. Use when reviewing pull requests, code changes, or when the user asks for a code review.
```

#### Core Authoring Principles

**1. Concise is key.** The context window is shared with conversation history, other skills, and requests. Every token competes for space. Default assumption: the agent is already very smart. Only add context it doesn't already have.

Challenge each piece of information:
- "Does the agent really need this explanation?"
- "Can I assume the agent knows this?"
- "Does this paragraph justify its token cost?"

Good (concise):
```markdown
## Extract PDF text

Use pdfplumber for text extraction:

\`\`\`python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
\`\`\`
```

Bad (verbose):
```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases well...
```

**2. Keep SKILL.md under 500 lines.** For optimal performance, the main `SKILL.md` should be concise. Use progressive disclosure for detailed content.

**3. Progressive disclosure.** Put essential information in `SKILL.md`; detailed reference material in separate files that the agent reads only when needed.

```markdown
# PDF Processing

## Quick start
[Essential instructions here]

## Additional resources
- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

**Keep references one level deep** — link directly from `SKILL.md` to reference files. Deeply nested references may result in partial reads.

**When to load reference files**: Tell the agent explicitly when to read each file. Example:
- "Read `reference.md` when you need complete API details beyond the quick start."
- "Read `examples.md` when output quality depends on seeing worked examples."
- "Execute a helper named validate.py in a scripts directory after generating output to verify correctness."

**4. Set appropriate degrees of freedom.** Match specificity to the task's fragility:

| Freedom Level | When to Use | Example |
|---------------|-------------|---------|
| **High** (text instructions) | Multiple valid approaches, context-dependent | Code review guidelines |
| **Medium** (pseudocode/templates) | Preferred pattern with acceptable variation | Report generation |
| **Low** (specific scripts) | Fragile operations, consistency critical | Database migrations |

#### Common Patterns

**Template Pattern** — provide output format templates:

```markdown
## Report structure

Use this template:

\`\`\`markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
\`\`\`
```

**Examples Pattern** — for skills where output quality depends on seeing examples:

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
\`\`\`
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
\`\`\`

**Example 2:**
Input: Fixed bug where dates displayed incorrectly
Output:
\`\`\`
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
\`\`\`
```

**Workflow Pattern** — break complex operations into clear steps with checklists:

```markdown
## Form filling workflow

Copy this checklist and track progress:

\`\`\`
Task Progress:
- [ ] Step 1: Analyze the form
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output
\`\`\`

**Step 1: Analyze the form**
Run a helper named analyze_form.py in a scripts directory, for example: \`python analyze_form.py input.pdf\`
...
```

**Conditional Workflow Pattern** — guide through decision points:

```markdown
## Document modification workflow

1. Determine the modification type:

   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   ...
```

**Feedback Loop Pattern** — for quality-critical tasks, implement validation loops:

```markdown
## Document editing process

1. Make your edits
2. **Validate immediately** with a helper named validate.py in a scripts directory, for example: \`python validate.py output/\`
3. If validation fails:
   - Review the error message
   - Fix the issues
   - Run validation again
4. **Only proceed when validation passes**
```

#### Utility Scripts

Pre-made scripts offer advantages over generated code:
- More reliable than generated code
- Save tokens (no code in context)
- Save time (no code generation)
- Ensure consistency across uses

```markdown
## Utility scripts

**analyze_form.py**: Extract all form fields from PDF (example name for a helper in a scripts directory of the skill you are authoring — this pack does not ship it)
\`\`\`bash
python analyze_form.py input.pdf > fields.json
\`\`\`

**validate.py**: Check for errors (example name for a helper in a scripts directory of the skill you are authoring — this pack does not ship it)
\`\`\`bash
python validate.py fields.json
# Returns: "OK" or lists conflicts
\`\`\`
```

Make clear whether the agent should **execute** the script (most common) or **read** it as reference.

### Phase 4 — Verification

1. Verify the `SKILL.md` is under 500 lines.
2. Check that the description is specific and includes trigger terms.
3. Ensure consistent terminology throughout.
4. Verify all file references are one level deep.
5. Test that the skill can be discovered and applied.

## Pitfalls

### 1. Windows-Style Paths
- ✅ Use forward slashes in skill-relative paths (for example a helper named helper.py in a scripts directory)
- ❌ Avoid backslashes in those paths

> **Windows host note**: Even on a Windows primary host (PowerShell), skill file paths inside `SKILL.md` must use forward slashes for cross-platform compatibility.

### 2. Too Many Options
```markdown
# Bad - confusing
"You can use pypdf, or pdfplumber, or PyMuPDF, or..."

# Good - provide a default with escape hatch
"Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
```

### 3. Time-Sensitive Information
```markdown
# Bad - will become outdated
"If you're doing this before August 2025, use the old API."

# Good - use an "old patterns" section
## Current method
Use the v2 API endpoint.

## Old patterns (deprecated)
<details>
<summary>Legacy v1 API</summary>
...
</details>
```

### 4. Inconsistent Terminology
Choose one term and use it throughout:
- ✅ Always "API endpoint" (not mixing "URL", "route", "path")
- ✅ Always "field" (not mixing "box", "element", "control")

### 5. Vague Skill Names
- ✅ Good: `processing-pdfs`, `analyzing-spreadsheets`
- ❌ Avoid: `helper`, `utils`, `tools`

### 6. Writing in `~/.cursor/skills-cursor/`
**Never** create skills in `~/.cursor/skills-cursor/`. This directory is reserved for Cursor's internal built-in skills and is managed automatically by the system.

### 7. Deeply Nested References
Keep references one level deep. Link directly from `SKILL.md` to reference files. Deeply nested references may result in partial reads.

### 8. Over-Explaining What the Agent Already Knows
The agent is already very smart. Only add context it doesn't already have. Challenge each paragraph: "Does this justify its token cost?"

## Verification

Before finalizing a skill, verify:

### Core Quality
- [ ] Description is specific and includes key terms
- [ ] Description includes both WHAT and WHEN
- [ ] Written in third person
- [ ] SKILL.md body is under 500 lines
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract

### Structure
- [ ] File references are one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps
- [ ] No time-sensitive information

### If Including Scripts
- [ ] Scripts solve problems rather than punt
- [ ] Required packages are documented
- [ ] Error handling is explicit and helpful
- [ ] No Windows-style paths

### Quick Checks
```powershell
# Count lines in SKILL.md (PowerShell, Windows host)
(Get-Content .\SKILL.md | Measure-Object -Line).Lines

# Verify frontmatter starts with ---
Get-Content .\SKILL.md -TotalCount 1
# Expected output: ---

# Verify name matches folder name
$dir = (Get-Item .).Name
$name = (Get-Content .\SKILL.md -Raw | Select-String '(?m)^name:\s*(.+)$').Matches.Groups[1].Value
"$dir vs $name"
# Expected: folder name and name field match exactly
```

## Examples

### Complete Example: `code-review` Skill

**Directory structure:**
```
code-review/
├── SKILL.md
├── STANDARDS.md
└── examples.md
```

**SKILL.md:**
```markdown
---
name: code-review
description: Review code for quality, security, and maintainability following team standards. Use when reviewing pull requests, examining code changes, or when the user asks for a code review.
---

# Code Review

## Quick Start

When reviewing code:

1. Check for correctness and potential bugs
2. Verify security best practices
3. Assess code readability and maintainability
4. Ensure tests are adequate

## Review Checklist

- [ ] Logic is correct and handles edge cases
- [ ] No security vulnerabilities (SQL injection, XSS, etc.)
- [ ] Code follows project style conventions
- [ ] Functions are appropriately sized and focused
- [ ] Error handling is comprehensive
- [ ] Tests cover the changes

## Providing Feedback

Format feedback as:
- 🔴 **Critical**: Must fix before merge
- 🟡 **Suggestion**: Consider improving
- 🟢 **Nice to have**: Optional enhancement

## Additional Resources

- For detailed coding standards, see [STANDARDS.md](STANDARDS.md)
- For example reviews, see [examples.md](examples.md)
```

## Related Skills

- Skills that reference `scripts/` directories should document when to execute vs. read each script.
- Skills using progressive disclosure should explicitly tell the agent when to load each reference file.
