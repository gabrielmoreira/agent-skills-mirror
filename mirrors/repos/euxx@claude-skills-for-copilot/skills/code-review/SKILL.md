---
name: code-review
description: Multi-agent code review for local changes, files, or directories. Detects bugs, security issues, and conventions-file violations (AGENTS.md/CLAUDE.md/GEMINI.md).
argument-hint: "[file, directory, or git diff]"
user-invocable: true
---

# Code Review

Provide a code review for the given code changes (e.g. local changes, a file, or a directory).

## Steps

Make a todo list first, then follow these steps precisely:

### 1. Gather context

- Use a sub-agent to list file paths of relevant conventions files in this priority order: AGENTS.md, then CLAUDE.md, then GEMINI.md. Include the root file (if one exists), plus files in directories whose files were changed.
- Use a sub-agent to scan the code changes and return a summary of the change.

### 2. Parallel review

Launch 5 parallel sub-agents to independently review the change. Each agent returns a list of issues with the reason flagged (e.g. conventions-file adherence, bug, historical context):

- **Agent 1 — Conventions-file compliance**: Audit changes against AGENTS.md or similar conventions files (CLAUDE.md, GEMINI.md), using priority order AGENTS.md -> CLAUDE.md -> GEMINI.md. Note that these files are guidance for AI while writing code; not all instructions apply during code review.
- **Agent 2 — Bug scan**: Shallow scan for obvious bugs, focusing only on the changed lines. Prioritize large bugs; ignore nitpicks and likely false positives.
- **Agent 3 — Git history**: Read git blame and history of modified code to identify bugs in light of historical context.
- **Agent 4 — Code comments**: Read comments in modified files and verify the changes comply with any guidance in those comments.
- **Agent 5 — Security & quality**: Look for security issues and code quality problems that would directly impact functionality.

### 3. Confidence scoring

For each issue found in step 2, launch a parallel sub-agent to score it from 0–100 (give this rubric to each agent verbatim):

- **0** — Not confident at all. False positive that doesn't stand up to light scrutiny, or a pre-existing issue.
- **25** — Somewhat confident. Might be real, but unverified. If stylistic, not explicitly called out in the applicable conventions file.
- **50** — Moderately confident. Verified as real, but may be a nitpick or rare in practice. Not very important relative to the rest of the change.
- **75** — Highly confident. Double-checked; very likely a real issue that will be hit in practice. Important and directly impacts functionality, or directly mentioned in the applicable conventions file.
- **100** — Absolutely certain. Confirmed real issue that will happen frequently. Evidence directly confirms it.

For issues flagged due to conventions files, double-check that the applicable conventions file actually calls out that issue specifically.

### 4. Filter and output

- Discard issues scoring below 80.
- If no issues remain, output that no issues were found.
- Output the review directly to the user following the output format below.

## False Positives

Treat the following as false positives in steps 2 and 3:

- Pre-existing issues
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues a linter, typechecker, or compiler would catch (missing imports, type errors, formatting). Assume these run separately in CI.
- General code quality issues (lack of test coverage, poor documentation), unless explicitly required in a conventions file
- Issues called out in a conventions file but explicitly silenced in code (e.g. a lint-ignore comment)
- Intentional functionality changes directly related to the broader change
- Real issues on lines the user did not modify

## Notes

- Do not attempt to build or typecheck the app — these run separately in CI.
- Cite and link each issue. If referring to a conventions file, you must link it.

## Output Format

### With issues found

```
### Code review

Found N issues:

1. <brief description> (conventions file says "<...>")

   <link to file and line range>

2. <brief description> (some/other conventions file says "<...>")

   <link to file and line range>

3. <brief description> (bug due to <file and snippet>)

   <link to file and line range>
```

### No issues found

```
### Code review

No issues found. Checked for bugs and conventions-file compliance.
```
