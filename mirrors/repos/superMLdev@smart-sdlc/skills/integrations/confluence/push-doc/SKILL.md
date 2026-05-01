---
name: confluence-push-doc
description: "Push a planning artifact to Confluence as a formatted page. Use when the user says 'push to Confluence', 'publish this doc', or 'sync to Confluence'."
---

# Confluence — Push Document

## Goal

Publish or update a local planning artifact (PRD, architecture doc, backlog, etc.) as a Confluence page with proper formatting and version metadata.

---

## Prerequisite Check

Check `integrations.confluence` in config. If missing: "Run `confluence-connect` first."

---

## Step 1: Select Document

Ask: "Which document do you want to push?"

| # | Document | Path |
|---|----------|------|
| 1 | PRD | `{planning_artifacts}/prd/` |
| 2 | Architecture | `{planning_artifacts}/architecture/` |
| 3 | Backlog | `{planning_artifacts}/epics-stories/` |
| 4 | Product Brief | `{planning_artifacts}/briefs/` |
| 5 | Sprint Plan | `{implementation_artifacts}/sprints/` |
| 6 | Other (specify path) | |

---

## Step 2: Check if Page Already Exists

```bash
curl -s \
  "{confluence_url}/rest/api/content?title={encoded_title}&spaceKey={space_key}" \
  -u "{email}:{api_token}" \
  -H "Accept: application/json" | python3 -c "
import sys, json
results = json.load(sys.stdin)['results']
if results:
    print('EXISTS', results[0]['id'], results[0]['version']['number'])
else:
    print('NEW')
"
```

---

## Step 3: Convert Markdown to Confluence Storage Format

Convert key markdown patterns:
- `## Heading` → `<h2>Heading</h2>`
- Markdown tables → `<table>` format
- Code blocks → `<ac:structured-macro ac:name="code">`
- Mermaid diagrams → render as a code block with note "Diagram source — render with Mermaid"
- `**bold**` → `<strong>bold</strong>`

Build the body as Confluence Storage Format XML.

---

## Step 4: Create or Update Page

**Create new page:**
```bash
curl -s -X POST \
  "{confluence_url}/rest/api/content" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "page",
    "title": "{page_title}",
    "space": { "key": "{space_key}" },
    "ancestors": [{ "id": "{parent_page_id}" }],
    "body": {
      "storage": {
        "value": "{escaped_html_content}",
        "representation": "storage"
      }
    }
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('Created:', d.get('id'), d.get('_links',{}).get('webui',''))"
```

**Update existing page** (increment version):
```bash
curl -s -X PUT \
  "{confluence_url}/rest/api/content/{page_id}" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "version": { "number": {current_version + 1} },
    "title": "{page_title}",
    "type": "page",
    "body": {
      "storage": {
        "value": "{escaped_html_content}",
        "representation": "storage"
      }
    }
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('Updated to version:', d['version']['number'])"
```

---

## Step 5: Update Local Frontmatter

Add to the local document's frontmatter:
```yaml
confluence_page_id: "{page_id}"
confluence_url: "{confluence_url}/wiki{webui_path}"
confluence_version: {version_number}
last_synced: {date}
```

---

## Completion

> "✅ Published to Confluence: [{page_title}]({confluence_page_url})
> Version: {version}
>
> The `prd_version` label is embedded in the page metadata so stories generated from this version can trace back to it."
