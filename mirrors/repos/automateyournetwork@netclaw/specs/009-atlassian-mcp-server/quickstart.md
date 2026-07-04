# Quickstart: Atlassian MCP Server Integration

**Feature**: 009-atlassian-mcp-server
**Date**: 2026-03-27

## Prerequisites

1. An Atlassian instance (Cloud or Server/Data Center) with Jira and/or Confluence
2. Credentials: API token (Cloud) or Personal Access Token (Server/Data Center)
3. Python 3.10+ and uv installed on the AI assistant host
4. Network connectivity from the AI assistant host to the Atlassian instance

## Setup

### For Atlassian Cloud

#### 1. Generate an API Token

Go to: **https://id.atlassian.com/manage-profile/security/api-tokens → Create API token**

#### 2. Configure environment variables

```bash
# Jira Cloud
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"

# Confluence Cloud (same credentials, same domain)
export CONFLUENCE_URL="https://your-domain.atlassian.net/wiki"
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"
```

### For Server/Data Center

#### 1. Generate a Personal Access Token

In Jira: **Profile → Personal Access Tokens → Create token**

#### 2. Configure environment variables

```bash
# Jira Server/DC
export JIRA_URL="https://jira.example.com"
export JIRA_USERNAME="your-username"
export JIRA_API_TOKEN="your-personal-access-token"

# Confluence Server/DC (may be separate URL)
export CONFLUENCE_URL="https://confluence.example.com"
export CONFLUENCE_USERNAME="your-username"
export CONFLUENCE_API_TOKEN="your-personal-access-token"
```

### 3. Register in openclaw.json

Add to `config/openclaw.json` under `mcpServers`:

```json
{
  "atlassian-mcp": {
    "command": "uvx",
    "args": ["mcp-atlassian"],
    "env": {
      "JIRA_URL": "${JIRA_URL}",
      "JIRA_USERNAME": "${JIRA_USERNAME}",
      "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
      "CONFLUENCE_URL": "${CONFLUENCE_URL}",
      "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
      "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
    }
  }
}
```

### 4. Run the server (standalone test)

```bash
uvx mcp-atlassian
```

The server communicates via stdio. It will wait for JSON-RPC messages on stdin.

## Usage Examples

Once registered with an MCP client (Claude Desktop, OpenClaw, etc.):

**Jira:**
- "Show me open issues in project NET assigned to me"
- "Search Jira for issues with label 'outage' in project OPS"
- "Get details for issue NET-1234"
- "Create a Jira issue in project NET titled 'Router-01 BGP peer down' with priority Critical"
- "Transition issue NET-1234 to In Progress"
- "Add a comment to NET-1234: 'Root cause identified — BGP hold timer expired'"

**Confluence:**
- "Search Confluence for 'BGP runbook'"
- "Show me the page 'Network Architecture Overview' in space NET-DOCS"
- "Create a Confluence page in space NET-DOCS titled 'Incident Postmortem: Router-01 Outage'"
- "Update the page 'Router Maintenance Procedures' with new content"

## Available Tool Categories (72 tools)

| Category | Examples | Count |
|----------|----------|-------|
| Jira Issues | jira_search, jira_get_issue, jira_create_issue, jira_update_issue | ~20 |
| Jira Transitions | jira_get_transitions, jira_transition_issue | ~5 |
| Jira Comments | jira_add_comment, jira_get_comments | ~5 |
| Jira Projects | jira_get_projects, jira_get_project | ~5 |
| Jira Fields | jira_get_fields, jira_get_issue_types | ~5 |
| Confluence Pages | confluence_search, confluence_get_page, confluence_create_page, confluence_update_page | ~15 |
| Confluence Comments | confluence_add_comment, confluence_get_comments | ~5 |
| Confluence Spaces | confluence_get_spaces, confluence_get_space | ~5 |
| Cross-Product | jira_link_issue, jira_get_issue_links | ~7 |

## Verification

To verify the integration is working:

1. Ensure Jira API is accessible: `curl -u "email:token" "https://your-domain.atlassian.net/rest/api/3/myself"`
2. Ensure Confluence API is accessible: `curl -u "email:token" "https://your-domain.atlassian.net/wiki/rest/api/space?limit=1"`
3. Register in OpenClaw and issue a test query: "Show me my Jira issues"
4. Verify GAIT audit log records the interaction
