---
description: 'Start Phase 1 — define requirements for an existing feature branch Issue. Requires /start-issue to have been run first (feature branch must exist).'
agent: 'Discuss'
---
# Phase 1 — Define Requirements

**Issue doc path**: ${input:issue-doc:Path to Issue doc (e.g., docs/issues/ISSUE-042-name.md)}

## Step 1 — Confirm you are on a feature branch (not main)

```bash
git branch --show-current
```

> If output is `main` or `master`: **STOP**.
> Say: *"You must run `/start-issue` first to create your branch. Come back to `/discuss` once you are on an issue branch."*
>
> If on a feature branch (e.g. `issue/ISSUE-042-login-rate-limiting`): ✅ Continue.

## Step 2 — Read or create the Issue doc

If the file `${input:issue-doc}` doesn't exist yet:
- Ask the developer for the Issue ID and a short slug
- Create it from: [docs/templates/ISSUE-template.md](../../docs/templates/ISSUE-template.md)

If it exists: read Phase 1 to understand what's already captured.

## Step 3 — Hand off to Discuss agent

Now begin the structured requirements discussion following the 6-step checklist:

1. Check project context (recent commits, existing docs)
2. Ask clarifying questions ONE AT A TIME (max 5)
3. Propose 2-3 approaches with trade-offs
4. Present a design and get explicit approval
5. Write Phase 1 of the Issue doc (requirements + acceptance criteria + out-of-scope)
6. Hand off to Research agent automatically
