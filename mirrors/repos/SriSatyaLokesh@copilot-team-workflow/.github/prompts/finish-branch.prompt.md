---
description: 'Use when implementation and verification are complete, before merging or closing out work — when a developer says "I\'m done", "ready to merge", "wrap up this branch", "create a PR", "finish this feature", or "clean up the branch". Presents 4 structured options: merge locally, create PR, keep branch, or discard. Tests must pass first.'
agent: 'Verify'
---
# Finish Branch — Verify, Then Decide

This is the final gate before merging or creating a PR.

**Issue doc**: ${input:issue-doc:Path to Issue doc (e.g., docs/issues/ISSUE-042-name.md)}

## Step 1 — Run the full test suite

```bash
npm test
```

> **If tests fail:** Show the failures. Say: "Tests must pass before finishing this branch. Fix the failures and run `/finish-branch` again."
> **Do NOT offer merge/PR options while tests are failing.**

## Step 2 — Run quality checks

```bash
npx tsc --noEmit
npm run lint
```

Report any errors found.

## Step 3 — Verify Issue requirements are met

Read `${input:issue-doc}` and check Phase 5 (Verify) findings.

For each Phase 1 requirement, confirm it is `✅ met`.

If any requirement is `❌ not met` or has no verification:
> "The following requirements are not yet verified: [list]. Fix these before finishing."

## Step 4 — Present the 4 options

Once everything is green, present exactly these options:

```
Implementation is complete. What would you like to do?

1. Merge to main locally — merge the feature branch into main now
2. Push and create a Pull Request — push branch and open PR on GitHub
3. Keep the branch as-is — I'll handle merging later
4. Discard this work — delete the branch and all commits

Which option?
```

## Step 5 — Execute the chosen option

### Option 1 — Merge locally
```bash
git checkout main
git pull
git merge issue/ISSUE-XXX-name
npm test
```
If merge tests pass: `git branch -d issue/ISSUE-XXX-name`

### Option 2 — Push and PR
```bash
git push -u origin issue/ISSUE-XXX-name
gh pr create --title "[Issue title]" --body "Closes ISSUE-XXX. See docs/issues/ISSUE-XXX-name.md for full details."
```

### Option 3 — Keep as-is
Report: "Branch `issue/ISSUE-XXX-name` preserved. Tests passing. Resume anytime with `/execute`."

### Option 4 — Discard
Ask for confirmation: "Type 'discard' to permanently delete branch `issue/ISSUE-XXX-name` and all commits."
Only then: `git checkout main && git branch -D issue/ISSUE-XXX-name`

## Mark Issue Complete

For Options 1 and 2, update the Issue doc frontmatter:
```
status: done
```
