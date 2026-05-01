---
name: jira-connect
description: "Set up and verify JIRA integration. Use when the user says 'connect to JIRA', 'set up JIRA', or 'configure JIRA'."
---

# JIRA — Connect and Verify

## Goal

Validate JIRA connectivity and store working credentials in `_superml/config.yml` so all other JIRA skills work without re-prompting.

Supports two connection modes:
- **REST API** — direct HTTP calls using email + API token (Atlassian Cloud or Server)
- **MCP Server** — uses an Atlassian MCP server; AI uses tool calls instead of curl

---

## Important: Credential Security

Credentials go in `{project-root}/_superml/config.yml` which **must** be in `.gitignore`.

Before proceeding, verify:
```bash
cat {project-root}/.gitignore | grep _superml
```

If not present, add it:
```bash
echo "_superml/config.yml" >> {project-root}/.gitignore
```

⏸️ **STOP** — confirm `.gitignore` is updated before collecting any credentials.

---

## Step 1: Choose Connection Mode

Ask the user:

> "How would you like to connect to JIRA?
>
> 1. **REST API** — email + API token, direct HTTP calls (works everywhere)
> 2. **MCP Server** — Atlassian Remote MCP Server or a self-hosted MCP package; AI uses MCP tool calls natively
>
> Which would you like to use? (1 or 2)"

Proceed to the matching path below.

---

## Path A: REST API Connection

### A1: Collect JIRA Details

Ask the user:
1. **JIRA base URL**: e.g., `https://yourorg.atlassian.net`
2. **JIRA project key**: e.g., `PROJ` (the prefix on all tickets)
3. **Your JIRA email**: the email on the Atlassian account
4. **API token**: Generate at https://id.atlassian.com/manage-profile/security/api-tokens

### A2: Test Connectivity

Run the following to verify the credentials work:

```bash
curl -s -u "{email}:{api_token}" \
  "{jira_url}/rest/api/3/project/{project_key}" \
  -H "Accept: application/json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ Connected to:', d['name'])"
```

If the command fails, show the error and suggest:
- API token may be expired → generate a new one at https://id.atlassian.com/manage-profile/security/api-tokens
- Project key may be wrong → list projects to find the right key
- URL may be missing or wrong

List available projects if key is unknown:
```bash
curl -s -u "{email}:{api_token}" \
  "{jira_url}/rest/api/3/project/search" \
  -H "Accept: application/json" | python3 -c "import sys,json; [print(p['key'], '-', p['name']) for p in json.load(sys.stdin)['values']]"
```

⏸️ **STOP** — connectivity must succeed before saving.

### A3: Save to Config

Update `{project-root}/_superml/config.yml` under the `jira:` key:

```yaml
jira:
  enabled: true
  connection_mode: rest
  base_url: "{jira_url}"
  project_key: "{project_key}"
  email: "{email}"
  api_token: "{api_token}"
  epic_issue_type: "Epic"
  story_issue_type: "Story"
  task_issue_type: "Task"
  board_id: ""
  default_assignee: ""
```

---

## Path B: MCP Server Connection

MCP Server mode means Copilot uses MCP tool calls to interact with JIRA — no curl commands, no API tokens stored locally (auth is handled by the MCP server).

### B1: Choose MCP Server Type

Ask:

> "Which Atlassian MCP server would you like to use?
>
> 1. **Atlassian Remote MCP** — official cloud-hosted server at `mcp.atlassian.com` (Atlassian Cloud only, OAuth-based)
> 2. **npm package** — self-hosted, runs locally (e.g., `@sooperset/mcp-atlassian` — supports Cloud and Server)
> 3. **Custom URL** — a company-hosted MCP endpoint
>
> Which? (1, 2, or 3)"

### B2: Configure the MCP Server

**If option 1 (Atlassian Remote MCP):**

Guide the user to:
1. Go to https://developer.atlassian.com/cloud/jira/platform/mcp-server/ and follow the OAuth setup
2. Copy the MCP endpoint URL provided (format: `https://mcp.atlassian.com/...`)
3. In VS Code settings or `.vscode/mcp.json`, add:

```json
{
  "servers": {
    "atlassian": {
      "url": "{mcp_endpoint_url}"
    }
  }
}
```

**If option 2 (npm package — `@sooperset/mcp-atlassian`):**

Install and configure:
```bash
# Verify Node.js is available
node --version
```

Add to `.vscode/mcp.json` (create if absent):
```json
{
  "servers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@sooperset/mcp-atlassian"],
      "env": {
        "JIRA_URL": "{jira_url}",
        "JIRA_USERNAME": "{email}",
        "JIRA_API_TOKEN": "{api_token}"
      }
    }
  }
}
```

⚠️ **Security**: `.vscode/mcp.json` contains credentials — add it to `.gitignore`:
```bash
echo ".vscode/mcp.json" >> {project-root}/.gitignore
```

**If option 3 (Custom URL):**

Ask for:
1. MCP server URL
2. Authentication header name and value (if any)

Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "atlassian": {
      "url": "{custom_mcp_url}",
      "headers": {
        "{auth_header_name}": "{auth_header_value}"
      }
    }
  }
}
```

### B3: Verify MCP Connection

Ask the user to run a quick test using the MCP tools:

> "In a new Copilot chat, type: `@atlassian list my JIRA projects`
> If the MCP server responds with your projects, the connection is working."

⏸️ **STOP** — confirm the MCP test succeeded before saving.

### B4: Save to Config

Update `{project-root}/_superml/config.yml`:

```yaml
jira:
  enabled: true
  connection_mode: mcp
  project_key: "{project_key}"
  mcp_server:
    type: "{atlassian_remote | npm_package | custom}"
    name: "atlassian"    # matches the server key in .vscode/mcp.json
  epic_issue_type: "Epic"
  story_issue_type: "Story"
  task_issue_type: "Task"
  board_id: ""
  default_assignee: ""
```

Note: No `base_url`, `email`, or `api_token` are stored — those are managed by the MCP server configuration.

---

## Step 4: Confirm

Show a summary appropriate to the connection mode:

**REST mode:**
> "✅ JIRA connected (REST API).
> Project: {project_name} ({project_key}) — {jira_url}

**MCP mode:**
> "✅ JIRA connected (MCP Server: {type}).
> Project key: {project_key}
> MCP server: `{name}` in `.vscode/mcp.json`

Either way, the available JIRA skills are the same:
> - `jira-create-epic` — create epics from your planning artifacts
> - `jira-create-story` — create individual stories
> - `jira-sync` — bulk sync all epics and stories
> - `jira-conflict-detect` — check if a story is already claimed
>
> Skills will automatically use your configured connection mode."
