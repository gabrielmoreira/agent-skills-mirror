---
name: jira-sync
description: "Bulk sync all epics and stories from the local backlog to JIRA. Use when the user says 'sync to JIRA', 'push everything to JIRA', or 'create all JIRA tickets'."
---

# JIRA — Bulk Sync

## Goal

Create all epics and stories from the local backlog in JIRA in one operation. Idempotent: skips items that already have a `jira_key` in the backlog.

---

## Prerequisite Check

Verify `integrations.jira` in config. If missing: "Run `jira-connect` first."

Load backlog from `{planning_artifacts}/epics-stories/{project_name}-backlog.md`.

---

## Step 1: Inventory

Show what will be synced:

```
Sync Preview:
─────────────────────────────
Epics to create:   {n} (skipping {m} already synced)
Stories to create: {n} (skipping {m} already synced)
─────────────────────────────
This will create {total} JIRA issues.
```

⏸️ **STOP** — ask: "Proceed with sync?"

---

## Step 2: Create Epics First

For each epic WITHOUT a `jira_key`:
1. Create using the same curl command as `jira-create-epic`
2. Write returned JIRA key back to backlog
3. Show progress: `✅ E-001 → {JIRA-KEY}`

---

## Step 3: Create Stories

For each story WITHOUT a `jira_key`:
1. Identify its parent epic's JIRA key
2. Create story using the same curl command as `jira-create-story`
3. Link to epic
4. Write returned JIRA key back to story file and backlog
5. Show progress: `✅ S-001 → {JIRA-KEY}`

---

## Step 4: Summary

```
Sync Complete
─────────────────────────────
Epics created:   {n}
Stories created: {n}
Skipped (existing): {n}
Errors: {n}
─────────────────────────────
View board: {jira_url}/projects/{project_key}/boards
```

If any errors, list them with the raw error message.
