---
name: jira-conflict-detect
description: "Check if a story is already being worked on by another team member. Use before starting any story implementation."
---

# JIRA — Multi-Member Conflict Detection

## Goal

Perform a 3-layer conflict check before any team member claims a story. Prevents two developers from working on the same story simultaneously.

---

## Why 3 Layers?

A single check can be bypassed or stale. Three independent signals give high confidence:

| Layer | Signal | What It Catches |
|-------|--------|-----------------|
| 1 | JIRA ticket status + assignee | Story is formally In Progress or In Review |
| 2 | Git branch existence | Story branch was already created (even if JIRA not updated) |
| 3 | Confluence doc version lock | Story references a planning doc version that's been superseded |

---

## Activation

Ask: "Which story are you checking?" (accept S-ID, JIRA key, or title)

Load the story's JIRA key from local story file frontmatter.

---

## Layer 1: JIRA Status Check

```bash
curl -s \
  "{jira_url}/rest/api/3/issue/{JIRA-KEY}" \
  -u "{email}:{api_token}" \
  -H "Accept: application/json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
fields = d['fields']
status = fields['status']['name']
assignee = (fields.get('assignee') or {}).get('displayName', 'Unassigned')
print(f'Status: {status}')
print(f'Assignee: {assignee}')
"
```

**Conflict conditions:**
- Status is `In Progress` AND assignee is NOT the current user → 🔴 **CONFLICT**
- Status is `In Review` → 🟡 **WARNING** (story may be done, verify)
- Status is `Done` → 🔴 **CONFLICT** (story is complete, don't re-implement)
- Status is `To Do` or `Open` AND unassigned → ✅ **CLEAR**

---

## Layer 2: Git Branch Check

```bash
git fetch --all --quiet
git branch -a | grep -i "{JIRA-KEY}"
```

**Conflict conditions:**
- Branch exists remotely → 🔴 **CONFLICT** (someone created the branch already)
- Branch exists locally but not remotely → 🟡 **WARNING** (stale local branch from previous attempt)
- No branch found → ✅ **CLEAR**

---

## Layer 3: Confluence Version Consistency (if Confluence is configured)

Load the story's `prd_version` from frontmatter.

If Confluence integration is configured, check if the PRD page version on Confluence matches the local `prd_version` embedded in the story.

```bash
curl -s \
  "{confluence_url}/rest/api/content/{prd_page_id}?expand=version" \
  -u "{email}:{api_token}" \
  -H "Accept: application/json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Confluence PRD version:', d['version']['number'])
print('Story based on version:', '{local_prd_version}')
"
```

**Conflict conditions:**
- Confluence version > local story's prd_version → 🟡 **WARNING** (PRD was updated after stories were generated; stories may be stale)

---

## Conflict Report

Present a single consolidated verdict:

```
Conflict Check — {JIRA-KEY}: {story_title}
════════════════════════════════════════
Layer 1 — JIRA Status:    [✅ CLEAR | 🟡 WARNING | 🔴 CONFLICT]
  Status: {status}, Assignee: {assignee}

Layer 2 — Git Branch:     [✅ CLEAR | 🟡 WARNING | 🔴 CONFLICT]
  {branch found or not}

Layer 3 — Doc Version:    [✅ CLEAR | 🟡 WARNING | N/A]
  {version comparison}
════════════════════════════════════════
VERDICT: [✅ SAFE TO CLAIM | 🟡 PROCEED WITH CAUTION | 🔴 DO NOT PROCEED]
```

---

## If Conflict Detected

🔴 **DO NOT PROCEED.** Report:
> "Story {JIRA-KEY} appears to be actively worked on by **{assignee}** (status: {status}). Starting implementation risks merge conflicts and duplicate work. Recommended: sync with your team or pick a different story."

🟡 **Caution**:
> "There's a potential conflict signal. Review before claiming the story. If you're sure it's safe, you may proceed."

✅ **Clear**:
> "No conflicts detected. Safe to claim and implement. Shall I create the branch now? (`github-create-branch`)"
