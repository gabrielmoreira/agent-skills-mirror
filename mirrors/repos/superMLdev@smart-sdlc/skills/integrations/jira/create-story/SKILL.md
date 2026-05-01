---
name: jira-create-story
description: "Create a single story ticket in JIRA from a local story file. Use when the user says 'create this story in JIRA' or 'push story to JIRA'."
---

# JIRA — Create Story

## Goal

Create one JIRA story ticket from a local story file. Embed the returned JIRA key in the local story for branch naming, conflict detection, and PR linking.

---

## Prerequisite Check

Check config for `integrations.jira`. If missing:
> "Run `jira-connect` first."

Check that the epic for this story already exists in JIRA (`jira_epic_key` field in backlog). If not:
> "The parent epic {E-ID} hasn't been created in JIRA yet. Create it first with `jira-create-epic`."

---

## Step 1: Identify Story

Ask: "Which story should I create?" (accept S-ID, title, or JIRA key)

Load story from `{implementation_artifacts}/stories/` or from the backlog.

Show:
```
Story: S-{id} — {title}
Epic: E-{id} (JIRA: {epic_jira_key})
Points: {n}
ACs: {count}
```

⏸️ **STOP** — confirm.

---

## Step 2: Format Acceptance Criteria

Convert local ACs to JIRA description format:

```bash
# Build ACs text for JIRA
ACS="{
  AC-1: {criteria text}
  AC-2: {criteria text}
  AC-3: {criteria text}
}"
```

---

## Step 3: Create in JIRA

```bash
curl -s -X POST \
  "{jira_url}/rest/api/3/issue" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": { "key": "{project_key}" },
      "issuetype": { "name": "Story" },
      "summary": "{story_title}",
      "description": {
        "type": "doc", "version": 1,
        "content": [
          { "type": "paragraph", "content": [{ "type": "text", "text": "User Story: {user_story}" }] },
          { "type": "paragraph", "content": [{ "type": "text", "text": "Acceptance Criteria:\n{acs}" }] }
        ]
      },
      "story_points": {story_points},
      "labels": ["superml", "prd-v{prd_version}"],
      "priority": { "name": "{priority}" }
    }
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('key','ERROR'))"
```

---

## Step 4: Link to Epic

```bash
curl -s -X POST \
  "{jira_url}/rest/api/3/issue/{story_key}/remotelink" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{"object": {"url": "{jira_url}/browse/{epic_key}", "title": "Epic: {epic_name}"}}'
```

---

## Step 5: Update Local Story File

Add to story frontmatter:
```yaml
jira_key: "{STORY-KEY}"
jira_url: "{jira_url}/browse/{STORY-KEY}"
jira_epic_key: "{EPIC-KEY}"
```

---

## Completion

> "✅ Story created: [{STORY-KEY}]({jira_url}/browse/{STORY-KEY})
>
> When you start implementing, run `jira-conflict-detect` first to verify this story isn't already claimed."
