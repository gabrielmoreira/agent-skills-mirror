---
name: conventions-improver
description: Audit and improve project conventions files (AGENTS.md, CLAUDE.md, GEMINI.md). Scans for all conventions files, evaluates quality against a scoring rubric, outputs a quality report, then makes targeted improvements with user approval. Use when asked to check, audit, update, or improve AGENTS.md or similar files.
argument-hint: "[path or leave blank to scan entire workspace]"
user-invocable: true
---

# Conventions File Improver

Audit, evaluate, and improve project conventions files (AGENTS.md, CLAUDE.md, GEMINI.md) to ensure AI agents have optimal project context.

**This skill can write to conventions files.** After presenting a quality report and getting user approval, it applies targeted improvements.

## Workflow

### Phase 1: Discovery

Find all conventions files in the repository using this priority order: AGENTS.md, then CLAUDE.md, then GEMINI.md.

Search for files named `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` at the root and in any subdirectories.

**File Types & Locations:**

| Type             | Location                                    | Purpose                                   |
| ---------------- | ------------------------------------------- | ----------------------------------------- |
| Project root     | `./AGENTS.md` (or `CLAUDE.md`, `GEMINI.md`) | Primary project context, shared with team |
| Package-specific | `./packages/*/AGENTS.md`                    | Module-level context in monorepos         |
| Subdirectory     | Any nested location                         | Feature/domain-specific context           |

**Note:** AI agents auto-discover conventions files in parent directories, so monorepo setups work automatically.

### Phase 2: Quality Assessment

For each conventions file found, evaluate it against the following scoring rubric (total: 100 points):

#### Scoring Criteria

**1. Commands/Workflows (20 points)**

- 20: All essential commands documented with context (build, test, lint, deploy, dev)
- 15: Most commands present, some missing context
- 10: Basic commands only, no workflow
- 5: Few commands, many missing
- 0: No commands documented

**2. Architecture Clarity (20 points)**

- 20: Clear codebase map — key directories explained, module relationships, entry points, data flow
- 15: Good structure overview, minor gaps
- 10: Basic directory listing only
- 5: Vague or incomplete
- 0: No architecture info

**3. Non-Obvious Patterns (15 points)**

- 15: Gotchas and quirks captured — known issues, workarounds, edge cases, "why we do it this way"
- 10: Some patterns documented
- 5: Minimal pattern documentation
- 0: No patterns or gotchas

**4. Conciseness (15 points)**

- 15: Dense, valuable content — no filler, no obvious info, no redundancy
- 10: Mostly concise, some padding
- 5: Verbose in places
- 0: Mostly filler or restates obvious code

**5. Currency (15 points)**

- 15: Reflects current codebase — commands work, file references accurate, tech stack current
- 10: Mostly current, minor staleness
- 5: Several outdated references
- 0: Severely outdated

**6. Actionability (15 points)**

- 15: Instructions are executable — commands can be copy-pasted, steps concrete, paths real
- 10: Mostly actionable
- 5: Some vague instructions
- 0: Vague or theoretical

**Grade thresholds:** A (90–100), B (70–89), C (50–69), D (30–49), F (0–29)

**Assessment process:** Read the file completely, cross-reference with actual codebase (verify commands, check if referenced files exist, test architecture descriptions), score each criterion, then list specific issues and propose concrete improvements.

**Red flags to note:**

- Commands that would fail (wrong paths, missing deps)
- References to deleted files/folders
- Copy-paste from templates without customization
- "TODO" items never completed
- Duplicate info across multiple conventions files

### Phase 3: Quality Report Output

**Always output the quality report before making any updates.**

```
## Conventions File Quality Report

### Summary
- Files found: X
- Average score: X/100
- Files needing update: X

### File-by-File Assessment

#### 1. ./AGENTS.md (Project Root)
**Score: XX/100 (Grade: X)**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Commands/workflows | X/20 | ... |
| Architecture clarity | X/20 | ... |
| Non-obvious patterns | X/15 | ... |
| Conciseness | X/15 | ... |
| Currency | X/15 | ... |
| Actionability | X/15 | ... |

**Issues:**
- [List specific problems]

**Recommended additions:**
- [List what should be added]
```

### Phase 4: Targeted Updates

After outputting the quality report, ask for user confirmation before updating.

**Update principles — only add information that genuinely helps future AI sessions:**

What TO add:

- Commands or workflows discovered during analysis
- Gotchas or non-obvious patterns found in code
- Package relationships that weren't clear
- Testing approaches that work
- Configuration quirks or environment-specific knowledge

What NOT to add:

- Obvious info restatable from code (e.g., "UserService handles users")
- Generic best practices already covered everywhere
- One-off bug fixes unlikely to recur
- Verbose explanations — prefer one-liners

**Diff format for each change** — show file path, a `Why:` explanation, and a unified diff:

```
### Update: ./AGENTS.md

**Why:** Build command was missing, causing confusion about how to run the project.

+## Commands
+
+| Command | Description |
+|---------|-------------|
+| `npm run dev` | Start development server |
+| `npm test` | Run test suite |
```

### Phase 5: Apply Updates

After user approval, apply changes using file editing tools. Preserve existing content structure.

## Recommended File Structure

Use only the sections relevant to the project. Typical sections:

- **Commands** — table of build/test/lint/dev commands
- **Architecture** — directory tree with `# purpose` annotations
- **Key Files** — list of entry points and important config paths
- **Code Style** — project-specific conventions (not generic advice)
- **Environment** — required env vars and setup steps
- **Testing** — test commands and patterns
- **Gotchas** — non-obvious issues, ordering dependencies, common mistakes

## What Makes a Great Conventions File

**Key principles:**

- Concise and human-readable — one line per concept when possible
- Actionable commands that can be copy-pasted
- Project-specific patterns, not generic advice
- Non-obvious gotchas and warnings

**Validation checklist before finalizing any update:**

- Each addition is project-specific
- No generic advice or obvious info
- Commands are tested and work
- File paths are accurate
- Would a new AI session find this helpful?
- Is this the most concise way to express the info?
