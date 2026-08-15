---
name: gen-catalog
description: "Indexes SKILL.md trees by reading name and description frontmatter, inferring categories, and emitting README marker tables, JSON, or standalone HTML. Use when generating or refreshing a skills catalog, README skills table, or skills-list embed. Not a /create-skill authoring or quality-refresh pass. Never invent missing YAML fields, nest one skill under another, or add Co-Authored-By on the optional catalog commit."
version: 1.0.1
---

## When to Use

Use this skill when the task is to auto-discover all skills in a directory and produce a structured catalog. Typical triggers:

- "Generate the skill catalog" / "update skills documentation"
- "List all skills" / "build a skills index"
- "Create a JSON or HTML catalog of available skills"
- "Refresh the README skills table"

The agent operates autonomously: **do NOT ask the user questions**. Clarify the goal from context, pick the right output format, execute, and verify.

## Prerequisites

- A skills directory containing one or more `*/SKILL.md` or `*/skill.md` files.
- Default skills directory: `~/.claude/skills/` (override if the user specifies a different path).
- Global commands directory: `~/.claude/commands/*.md` (checked for slash commands outside the skills directory).
- For README format: an existing `README.md` in the skills directory (created if absent).
- For `skills-list` update: a `skills-list/SKILL.md` file inside the skills directory (optional).
- Windows host is primary (PowerShell). Path separators in generated links use forward slashes for Markdown compatibility.

## Procedure

### Phase 1 — Discover All Skills

1. **Determine the skills directory.** If the user specifies a directory, use that. Otherwise default to `~/.claude/skills/`.

2. **Glob for skill files.** Search for all `*/SKILL.md` and `*/skill.md` files under the skills directory. Also check `~/.claude/commands/*.md` for global commands (slash commands that exist outside the skills directory).

3. **Parse YAML frontmatter** (between `---` delimiters) for each file found:
   - `name` — **required**
   - `description` — **required**
   - Any other frontmatter fields are preserved but not required.

4. **Auto-detect categories** by scanning each skill's instructions content. Do NOT use a fixed category list. Instead:
   - Extract keywords and themes from the instructions.
   - Group skills by their primary purpose. Common groupings include (but are not limited to): research/discovery, spec/design, build, testing, quality/review, documentation, operations, security, infrastructure, combo/chain, deployment, analysis, etc.
   - If a skill clearly chains other skills (e.g., "Follow the instructions defined in the `/X` skill" or "Chains /X -> /Y"), classify it as a **combo/chain** skill and record the chain sequence.
   - Use short lowercase labels for categories (e.g., `research`, `build`, `testing`, `docs`, `ops`, `combo`).
   - Generate human-readable display names from category labels (e.g., `research` → "Research & Discovery", `build` → "Build & Implement").

5. **Generate a markdown link** for each skill pointing to its SKILL.md file relative to the skills directory root:
   ```
   [`/name`](./name/SKILL.md)
   ```

### Phase 2 — Determine Output Format

Check if the user requested a specific output format. Supported formats:

| Format | Default? | Output file |
|--------|----------|-------------|
| `readme` | Yes | Markdown table injected into `README.md` |
| `json` | — | JSON array written to `skills-catalog.json` |
| `html` | — | Standalone HTML page written to `skills-catalog.html` |

If no format is specified, use **readme**.

#### README Format (default)

1. Read the existing `README.md` in the skills directory.
2. **Preserve everything above** `<!-- AUTO-GENERATED-SKILLS-TABLE-START -->`.
3. **Preserve everything below** `<!-- AUTO-GENERATED-SKILLS-TABLE-END -->`.
4. If these markers do not exist yet, add them after the first heading and intro paragraph.
5. Between the markers, generate:

```markdown
### Skills by Category
```

For each detected category (sorted alphabetically, with combo/chains last):

```markdown
#### [Category Display Name]

| Skill | Description |
|-------|-------------|
| [`/name`](./name/SKILL.md) | description |
```

For combo/chain skills, add a "Chain" column:

```markdown
| Skill | Chain | Description |
|-------|-------|-------------|
| [`/name`](./name/SKILL.md) | `/a` -> `/b` -> `/c` | description |
```

Also include global commands from `~/.claude/commands/` with a note:

```markdown
> Global commands (available in any project):

| Command | Description |
|---------|-------------|
| `/name` | description |
```

#### JSON Format

Write a JSON file with this structure:

```json
{
  "generated": "ISO-8601 timestamp",
  "skills_directory": "/path/to/skills",
  "categories": {
    "category-label": {
      "display_name": "Category Display Name",
      "skills": [
        {
          "name": "skill-name",
          "description": "...",
          "path": "relative/path/to/SKILL.md",
          "chain": ["/a", "/b"]
        }
      ]
    }
  },
  "global_commands": [
    { "name": "command-name", "description": "..." }
  ]
}
```

> The `chain` array is only included for combo/chain skills.

#### HTML Format

Generate a standalone HTML page with:
- Clean CSS styling (no external dependencies)
- Skills grouped by category in collapsible sections
- A search/filter input for skill names and descriptions
- Links to each skill's SKILL.md file

### Phase 3 — Update skills-list (README format only)

If outputting README format **and** `skills-list/SKILL.md` exists in the skills directory, update its embedded skills table:

1. Keep the YAML frontmatter intact.
2. Replace **only** the skills table content.
3. Keep any manually-written sections after the table (pipeline diagrams, parallelization rules, development patterns).

Generated table format:

```markdown
| Skill | Description |
|---|---|
| **name** | description |
```

Group by category with category headers.

### Phase 4 — Verify

1. Count total skills discovered.
2. Count skills in generated output.
3. Counts **must match**. If not, flag the discrepancy.
4. Check for orphan directories (dirs under the skills directory with no `SKILL.md`).
5. Check for skills referenced in combo chains that don't exist.

Report:

```markdown
## Catalog Generated
- Skills discovered: N
- Output format: [readme|json|html]
- Output updated: N skills
- Orphan directories: [list or "none"]
- Missing chain targets: [list or "none"]
```

### Phase 5 — Commit (optional)

If changes were made:

1. Stage the updated files.
2. Commit with message: `docs: auto-generate skills catalog (N skills)`
3. **Do NOT include Co-Authored-By lines.**
4. Push after committing.

### Self-Healing Validation (max 2 iterations)

After producing documentation, validate completeness:

1. Verify all required sections are present and non-empty.
2. Verify internal cross-references and links resolve correctly.
3. Verify no draft text remains (`{follow-up item}`, `[decision pending]`, `...`, `etc.`).
4. Verify code examples are syntactically valid.

**If validation fails:**
- Identify which sections are incomplete or contain placeholders.
- Re-generate only the deficient sections.
- Repeat up to **2 iterations**.

### Self-Evolution Telemetry

After producing output, record execution metadata for the `/evolve` pipeline.

1. Check if a project memory directory exists by looking for the project path in `~/.claude/projects/`.
2. If found, append to `skill-telemetry.md` in that memory directory.

Entry format:

```markdown
### /gen-catalog {{YYYY-MM-DD}}
- Outcome: {{SUCCESS | PARTIAL | FAILED}}
- Self-healed: {{yes what was healed | no}}
- Iterations used: {{N}} / {{N max}}
- Bottleneck: {{phase that struggled or "none"}}
- Suggestion: {{one-line improvement idea for /evolve, or "none"}}
```

> Only log if the memory directory exists. Skip silently if not found. Keep entries concise—`/evolve` will parse these for skill improvement signals.

## Pitfalls

- **Missing frontmatter fields.** A skill file without `name` or `description` in YAML frontmatter will break parsing. Skip it and report it as an orphan or malformed entry rather than crashing.
- **Marker drift in README.** If someone manually edits content between the `<!-- AUTO-GENERATED-SKILLS-TABLE-START -->` and `<!-- AUTO-GENERATED-SKILLS-TABLE-END -->` markers, it will be overwritten. Document this in the README intro.
- **Case sensitivity.** Both `SKILL.md` and `skill.md` are valid; glob for both to avoid missing skills on case-sensitive filesystems.
- **Orphan directories.** Directories without a `SKILL.md` are not errors but should be reported so the user can decide whether to clean up.
- **Broken chain references.** A combo skill referencing `/X` where `/X` does not exist must be flagged in the verification report, not silently dropped.
- **Co-Authored-By lines.** Never include them in the commit message. The commit message must be exactly: `docs: auto-generate skills catalog (N skills)`.
- **Telemetry directory.** Do not create `~/.claude/projects/` if it does not exist. Only append to an existing memory directory.
- **HTML external dependencies.** The HTML output must be fully standalone with inline CSS. No CDN links or external JS libraries.

## Verification

After running the full workflow, confirm:

1. **Skill count match:**
   ```powershell
   # Count discovered skill files
   (Get-ChildItem -Path ~/.claude/skills -Recurse -Filter "SKILL.md" | Measure-Object).Count
   (Get-ChildItem -Path ~/.claude/skills -Recurse -Filter "skill.md" | Measure-Object).Count
   ```
   The sum must equal the number of skills listed in the generated catalog.

2. **README markers present (readme format):**
   ```powershell
   Select-String -Path ~/.claude/skills/README.md -Pattern "AUTO-GENERATED-SKILLS-TABLE"
   ```
   Expected: two matches (START and END).

3. **JSON validity (json format):**
   ```powershell
   Get-Content ~/.claude/skills/skills-catalog.json | ConvertFrom-Json | Out-Null
   ```
   No errors means valid JSON.

4. **HTML opens in browser (html format):**
   ```powershell
   Test-Path ~/.claude/skills/skills-catalog.html
   ```
   Expected: `True`.

5. **Orphan directories reported.** The verification report must list any directory under the skills root that has no `SKILL.md` or `skill.md`.

6. **Missing chain targets reported.** The verification report must list any combo chain reference that points to a non-existent skill.

7. **No draft placeholders.** Search the generated output for `{follow-up item}`, `[decision pending]`, `...`, `etc.` — none should remain.

## Related Skills

- **skills-list** — If present in the skills directory, its embedded table is updated during README-format generation (Phase 3).
- **/evolve** — Consumes telemetry entries written by this skill's Self-Evolution Telemetry phase.
