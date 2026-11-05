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

- Use a sub-agent to list file paths of relevant conventions files in this priority order: AGENTS.md, then CLAUDE.md, then GEMINI.md. Include the repository root and all ancestor directories of changed files, including the changed files' own directories.
- Use a sub-agent to scan the code changes and return a summary of the change.
- Give every review and validation agent the user's requested scope and the change summary. Include the PR title and description when provided as context.

### 2. Parallel review

Launch 4 parallel sub-agents to independently review the change. Each agent returns a list of issues with the reason flagged (e.g. conventions-file adherence, bug):

- **Agents 1 and 2 - Conventions-file compliance**: Independently audit changes against AGENTS.md or similar conventions files (CLAUDE.md, GEMINI.md), using priority order AGENTS.md -> CLAUDE.md -> GEMINI.md. Apply each file only to its directory and descendants, respecting more specific instructions. Quote the exact applicable rule for each violation; not all writing instructions apply during code review.
- **Agent 3 - Diff-focused bug scan**: Scan the changed lines for significant, demonstrable bugs. Avoid nitpicks, speculative concerns, and findings that cannot be validated from the diff alone.
- **Agent 4 - Logic and security**: Look for incorrect logic and concrete security problems introduced by the changed code. Read surrounding context when needed to verify the behavior.

Prioritize actionable findings with clear evidence and actual impact. For input- or state-dependent bugs, identify the concrete trigger and resulting failure. Do not report subjective improvements or general quality concerns.

### 3. Independent validation

For each candidate issue, launch an independent validation sub-agent. Give it the scope, change summary, issue description, and relevant conventions-file paths.

- Check the actual code and surrounding context to confirm the failure and its trigger.
- Check whether the behavior is pre-existing or an intentional part of the requested change.
- For conventions-file findings, verify both the exact rule and its directory scope.
- Return whether the issue is confirmed, with supporting evidence. Discard issues that cannot be validated with high confidence.

### 4. Filter and output

- Discard unvalidated issues and deduplicate reports of the same underlying problem.
- If no issues remain, output that no issues were found.
- Output the review directly to the user following the output format below.
- Keep output in chat. Posting GitHub comments requires an explicit user request and tools available in the target environment.

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
