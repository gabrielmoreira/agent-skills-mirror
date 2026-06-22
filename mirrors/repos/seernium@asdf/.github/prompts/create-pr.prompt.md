---
mode: agent
description: Generate a complete PR description, changelog entry, and migration guide from the current branch.
---

Invoke the `pr-author` agent to:
1. Run `git diff main --stat` and read the key changed files to understand what and why.
2. Generate a structured PR description (summary, changes, testing, breaking changes, migration steps).
3. Write a Conventional Commits changelog entry.
4. Explicitly flag any breaking changes: API shape, schema migrations, env var changes, auth behavior.
5. Include the PR checklist with `pnpm tsc --noEmit`, lint, test, and security reviewer sign-off items.

Branch/context: ${input:current branch changes}
