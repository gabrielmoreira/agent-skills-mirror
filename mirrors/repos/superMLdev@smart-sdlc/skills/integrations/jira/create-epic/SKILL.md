---
name: jira-create-epic
description: "Create an epic in JIRA from a planning artifact. Use when the user says 'create this epic in JIRA' or 'push epic to JIRA'."
---

# JIRA — Create Epic

## Goal

Create a single epic in JIRA from the local backlog. Embed the returned JIRA key into the local epic record for future story linking.

---

## Prerequisite Check

Check `{project-root}/_superml/config.yml` for `integrations.jira`. If missing, say:
> "JIRA is not configured. Run `jira-connect` first."

---

## Step 1: Identify Epic

Ask: "Which epic should I create in JIRA?" (accept E-ID or epic name)

Load epic from `{planning_artifacts}/epics-stories/{project_name}-backlog.md`.

Show summary:
```
Epic: E-{id} — {name}
Goal: {goal}
Stories: {n} planned
PRD Version: {version}
```

⏸️ **STOP** — confirm before creating.

---

## Step 2: Create in JIRA

Load credentials from config. Run:

```bash
curl -s -X POST \
  "{jira_url}/rest/api/3/issue" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": { "key": "{project_key}" },
      "issuetype": { "name": "Epic" },
      "summary": "{epic_name}",
      "description": {
        "type": "doc", "version": 1,
        "content": [{
          "type": "paragraph",
          "content": [{ "type": "text", "text": "{epic_goal}" }]
        }]
      },
      "labels": ["superml", "prd-v{prd_version}"]
    }
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('Created:', d.get('key','ERROR'), d.get('self',''))"
```

---

## Step 3: Embed JIRA Key in Local Epic

Update the epic in the backlog file, adding:
```markdown
**JIRA Epic Key:** {JIRA-KEY}
**JIRA URL:** {jira_url}/browse/{JIRA-KEY}
```

---

## Completion

> "✅ Epic created in JIRA: [{JIRA-KEY}]({jira_url}/browse/{JIRA-KEY})
>
> Ready to create stories for this epic? Use `jira-create-story` and reference epic key **{JIRA-KEY}**."
