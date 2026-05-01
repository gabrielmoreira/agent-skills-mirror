---
id: user_experience
name: User Experience
---

# User Experience

Evaluates whether the plugin's purpose is obvious, provides feedback during operation,
and delivers a smooth experience from start to finish.

## What to look for

- **Clear entry point** — Is it obvious how to invoke the plugin? What words trigger it?
- **Purpose clarity** — Can a new user understand what the plugin does in 10 seconds?
- **Progress feedback** — Does the agent communicate what it's doing during long operations?
- **Smart defaults** — Does it work out of the box without extensive configuration?
- **Output quality** — Is the final output well-formatted, useful, and actionable?
- **Error messages** — When things fail, are error messages helpful and actionable?

## Scoring rubric

| Score | Criteria |
|-------|----------|
| **5** | Trigger phrases documented in SKILL.md. Works with zero configuration. Provides progress updates during multi-step operations. Output is structured (tables, lists) and actionable. |
| **4** | Entry point is clear. Works with ≤1 setup step. Output is formatted and useful. |
| **3** | User can figure out how to use it from the README, but trigger phrases are undocumented. Output is functional but unformatted. |
| **2** | Entry point unclear — user must read source code to understand invocation. Output is a raw dump. |
| **1** | Cannot determine how to invoke the plugin without contacting the author. |

## What a 5 looks like

- Trigger phrases documented: "Use when user says 'validate links', 'check docs'"
- Progress updates: "Scanning 47 files... Found 3 issues... Generating report..."
- Smart defaults: works in current directory, no flags required
- Clean output: table/list format, not raw dumps

## Scoring examples

### Score 5 — deep-review

```markdown
## Usage
/deep-review                    # Review uncommitted local changes
/deep-review <PR-ID>            # Review a pull request
/deep-review <commit>           # Review a specific commit
/deep-review <file1> <file2>    # Review specific files
```

Why it scores 5: Entry points are immediately obvious with multiple invocation
patterns. Works with zero configuration (defaults to uncommitted changes).
Output is structured with per-agent findings and synthesized verdict.

### Score 3 — hello-skills

```markdown
description: Greets the user with a friendly, personalized message.
  Use when the user wants a greeting or says hello.
```

Why it scores 3: User can figure out it triggers on "hello", but trigger
phrases are only in YAML frontmatter. No progress feedback. Output format
(ASCII art) is mentioned but not demonstrated.
