---
name: confluence-sync
description: "Push a Smart SDLC document to a Confluence page, creating or updating it. Use when the user says 'sync to Confluence', 'publish to Confluence', or 'update the Confluence page'."
---

# Confluence — Sync Document

## Goal

Push a Smart SDLC artifact (PRD, architecture doc, sprint plan, etc.) to a Confluence page. Creates the page if it doesn't exist; updates it if it does.

---

## Prerequisite Check

Check `integrations.confluence` in `_superml/config.yml`. If missing: "Run `confluence-connect` first."

---

## Step 1: Identify the Document

Ask:
1. Which document are you syncing? (PRD, architecture, sprint plan, retrospective, etc.)
2. Do you have a target Confluence page URL or page ID? (Optional — will create new if not provided)

Load the document file.

---

## Step 2: Convert to Confluence Format

Convert Markdown to Confluence Storage Format (XHTML):
- Headers: `## ` → `<h2>...</h2>`
- Bold: `**text**` → `<strong>text</strong>`
- Code blocks: ` ```lang ``` ` → `<ac:structured-macro ac:name="code">...`
- Tables: Markdown table → Confluence table XHTML
- Checkboxes: `- [x]` → ✅ `- [ ]` → ○

---

## Step 3: Check If Page Exists

If a page ID was provided:
```bash
curl -u {email}:{api_token} \
  "https://{domain}.atlassian.net/wiki/rest/api/content/{page_id}" \
  | jq '.id, .version.number, .title'
```

If no page ID, search by title:
```bash
curl -u {email}:{api_token} \
  "https://{domain}.atlassian.net/wiki/rest/api/content?title={title}&spaceKey={space}" \
  | jq '.results[0].id, .results[0].version.number'
```

---

## Step 4A: Create New Page

If page does not exist:
```bash
curl -X POST -u {email}:{api_token} \
  -H "Content-Type: application/json" \
  "https://{domain}.atlassian.net/wiki/rest/api/content" \
  -d '{
    "type": "page",
    "title": "{title}",
    "space": {"key": "{space_key}"},
    "ancestors": [{"id": "{parent_page_id}"}],
    "body": {"storage": {"value": "{xhtml_content}", "representation": "storage"}}
  }'
```

---

## Step 4B: Update Existing Page

```bash
curl -X PUT -u {email}:{api_token} \
  -H "Content-Type: application/json" \
  "https://{domain}.atlassian.net/wiki/rest/api/content/{page_id}" \
  -d '{
    "version": {"number": {next_version}},
    "title": "{title}",
    "type": "page",
    "body": {"storage": {"value": "{xhtml_content}", "representation": "storage"}}
  }'
```

---

## Step 5: Update Config

Log the sync in `_superml/config.yml`:
```yaml
integrations:
  confluence:
    last_sync:
      document: "{doc_type}"
      page_id: "{page_id}"
      page_url: "{page_url}"
      synced_at: "{timestamp}"
```

---

## Done

> ✅ Synced to Confluence: {page_url}
