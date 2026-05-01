---
description: 'Use when starting any new work item, feature, fix, or investigation — when a developer says "start a new issue", "begin new work", "I want to work on X", "create a new requirement", "work on feature", "fix the issue", "investigate the problem". Confirms the primary branch, offers to use current branch or create a new one from the latest primary, then starts the discussion phase. Required before writing any code.'
agent: 'Discuss'
---
# Start Issue — Branch First, Then Define

> **Note**: This prompt uses git CLI commands. If terminal access is unavailable, use VS Code's built-in Git panel (Source Control view) to check current branch, switch branches, and create new branches manually, then proceed with the Discuss phase.

Before any requirements discussion or code, we set up the right workspace.

**Issue description**: ${input:issue-description:What are you building? (e.g., "add rate limiting to login endpoint")}
**Issue ID**: ${input:issue-id:Issue ID (e.g., ISSUE-042)}

---

## Step 1 — Confirm Primary Branch

Run:
```bash
git branch -a
```

Then check `.github/copilot-instructions.md` for a line that looks like:
```
Primary branch: <branch-name>
```

**If the primary branch IS already recorded** in `copilot-instructions.md` → note it and skip to Step 2.

**If the primary branch is NOT recorded yet**, ask the developer:

> "What is your team's primary branch? This is the branch everyone creates feature branches from (common choices: `main`, `dev`, `develop`, `staging`).
> Whatever you say will be stored in `.github/copilot-instructions.md` so you won't be asked again."

Wait for the developer's answer, then append the following line to the `## Conventions` section of `.github/copilot-instructions.md`:

```
Primary branch: <answer>
```

> ✅ Primary branch confirmed. Stored for future sessions.

---

## Step 2 — Check Current Branch

Run:
```bash
git branch --show-current
```

Show the developer the current branch, then ask:

> "You are currently on `<current-branch>`.
>
> How do you want to proceed?
>
> **A) Stay on `<current-branch>`** — continue work here (use this if you're already on the right feature branch)
>
> **B) Create a new branch from `<primary-branch>`** — pull the latest from `<primary-branch>` and create a fresh `issue/<issue-id>-<slug>` branch (recommended for new work)"

Wait for the developer to choose **A** or **B**.

---

## Step 3A — (If developer chose A) Stay on current branch

Announce:
> "✅ Staying on `<current-branch>`. Skipping branch creation."

Skip to Step 4.

---

## Step 3B — (If developer chose B) Create a new branch from primary

Pull the latest from the primary branch:
```bash
git checkout <primary-branch>
git pull origin <primary-branch>
```

Create and switch to a new feature branch:
```bash
git checkout -b issue/${input:issue-id}-${input:issue-slug:Short slug (e.g., login-rate-limiting)}
```

Confirm the branch:
```bash
git branch --show-current
```

Expected output: `issue/ISSUE-042-login-rate-limiting`

> ✅ New branch created from the latest `<primary-branch>`.

---

## Step 4 — Verify Clean Baseline

```bash
npm test
```

> **If tests fail:** Report the failures. Ask the developer: "Existing tests are failing on this branch. Should we fix them before starting, or is this expected?"
> **Do NOT proceed** with new work on a red baseline without explicit developer approval.

> **If tests pass (or no tests exist):** Announce: "✅ Baseline is clean. Ready to define requirements."

---

## Step 5 — Begin Requirements Discussion

Now that we have an isolated branch with a clean baseline, begin the Discuss phase.

Ask: "Tell me about what you want to build with **${input:issue-description}**."

Create the Issue doc at: `docs/issues/${input:issue-id}-${input:issue-slug}.md`

Use the issue template at `docs/templates/issue-template.md` as the starting structure.

---

## Step 6 — Switch to the Discuss Agent

Branch confirmed. Issue doc initialized. Baseline verified.

> ✅ **Your next step**: In the Copilot Chat panel, **select the `Discuss` agent** and describe what you want to build. The Discuss agent will guide you through defining requirements before any code is written.
