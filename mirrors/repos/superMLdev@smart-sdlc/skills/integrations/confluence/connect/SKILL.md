---
name: confluence-connect
description: "Set up and verify Confluence integration. Use when the user says 'connect to Confluence', 'set up Confluence', or 'configure Confluence'."
---

# Confluence — Connect and Verify

## Goal

Validate Confluence connectivity and store working credentials so push-doc and sync operations work without re-prompting.

Supports two connection modes:
- **REST API** — direct HTTP calls using email + API token
- **MCP Server** — uses the Atlassian MCP server (same server as JIRA if already configured)

---

## Security Check First

Confirm `_superml/config.yml` is in `.gitignore` before proceeding (same check as `jira-connect`).

---

## Step 1: Choose Connection Mode

Check `_superml/config.yml` for `jira.connection_mode`. If JIRA is already configured in MCP mode, suggest using the same MCP server:

> "JIRA is configured to use MCP Server. Would you like Confluence to use the same MCP server? (recommended — same Atlassian credentials)
> 1. Yes, use the same MCP server
> 2. No, use REST API for Confluence"

If JIRA is not configured, ask:

> "How would you like to connect to Confluence?
> 1. **REST API** — email + API token, direct HTTP calls
> 2. **MCP Server** — Atlassian Remote MCP Server or a self-hosted MCP package"

---

## Path A: REST API Connection

### A1: Collect Confluence Details

Ask:
1. **Confluence base URL**: e.g., `https://yourorg.atlassian.net/wiki`
2. **Space key**: e.g., `ENG` or `PROD` — the key of the space to publish docs to
3. **Email** (if not already in JIRA config, re-use it)
4. **API token** (same Atlassian token as JIRA — share if already configured)

### A2: Verify Connectivity

```bash
curl -s \
  "{confluence_url}/rest/api/space/{space_key}" \
  -u "{email}:{api_token}" \
  -H "Accept: application/json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('✅ Connected to space:', d['name'])
print('Space key:', d['key'])
"
```

If fails, list available spaces:
```bash
curl -s \
  "{confluence_url}/rest/api/space?type=global&limit=20" \
  -u "{email}:{api_token}" \
  -H "Accept: application/json" | python3 -c "
import sys, json
results = json.load(sys.stdin)['results']
[print(s['key'], '-', s['name']) for s in results]
"
```

⏸️ **STOP** — connectivity must succeed before saving.

### A3: Set Parent Page (Optional)

Ask: "Should published docs go under a specific parent page? (enter page title or leave blank for space root)"

If provided, find the page ID:
```bash
curl -s \
  "{confluence_url}/rest/api/content?title={encoded_title}&spaceKey={space_key}" \
  -u "{email}:{api_token}" \
  -H "Accept: application/json" | python3 -c "
import sys, json
results = json.load(sys.stdin)['results']
print('Page ID:', results[0]['id']) if results else print('Page not found')
"
```

### A4: Save to Config

Update `{project-root}/_superml/config.yml` under the `confluence:` key:

```yaml
confluence:
  enabled: true
  connection_mode: rest
  base_url: "{confluence_url}"
  space_key: "{space_key}"
  root_page_id: "{page_id_or_empty}"
  email: "{email}"
  api_token: "{api_token}"
  prd_page_parent: "Requirements"
  architecture_page_parent: "Architecture"
  stories_page_parent: "Stories"
```

---

## Path B: MCP Server Connection

If JIRA is already configured in MCP mode, the same server handles Confluence — no additional setup needed beyond confirming the space key.

### B1: Get the Space Key

Ask: "What is your Confluence space key? (e.g. `ENG`, `PROJ`, `DOCS`)"

Test via MCP:
> "In a Copilot chat, type: `@atlassian list Confluence spaces`
> Confirm your space key appears in the list."

### B2: Set Parent Page (Optional)

Ask: "Should published docs go under a specific parent page title? (leave blank for space root)"

### B3: Save to Config

```yaml
confluence:
  enabled: true
  connection_mode: mcp
  space_key: "{space_key}"
  root_page_title: "{parent_page_title_or_empty}"
  mcp_server:
    name: "atlassian"    # matches the server key in .vscode/mcp.json
  prd_page_parent: "Requirements"
  architecture_page_parent: "Architecture"
  stories_page_parent: "Stories"
```

---

## Completion

Show summary appropriate to the connection mode:

**REST mode:**
> "✅ Confluence connected (REST API).
> Space: {space_name} ({space_key}) — {confluence_url}"

**MCP mode:**
> "✅ Confluence connected (MCP Server: atlassian).
> Space: {space_key}"

Either way:
> "Available skills:
> - `confluence-push-doc` — push any planning artifact as a Confluence page
> - `confluence-sync` — keep docs in sync with local changes
>
> Skills will automatically use your configured connection mode."
