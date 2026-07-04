# Quickstart: GitLab MCP Server Integration

**Feature**: 008-gitlab-mcp-server
**Date**: 2026-03-27

## Prerequisites

1. A GitLab instance (gitlab.com or self-hosted) with accessible API
2. A GitLab Personal Access Token with appropriate scopes (`api` for full access, `read_api` for read-only)
3. Node.js 18+ installed on the AI assistant host
4. Network connectivity from the AI assistant host to the GitLab API endpoint

## Setup

### 1. Generate a GitLab Personal Access Token

In GitLab: **User Settings → Access Tokens → Add new token**

Select scopes:
- `read_api` — for read-only monitoring (US1, US2, US3)
- `api` — for full access including write operations (US4, US5)

### 2. Configure environment variables

```bash
export GITLAB_PERSONAL_ACCESS_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_API_URL="https://gitlab.com"              # Default for SaaS
# export GITLAB_API_URL="https://gitlab.example.com"    # For self-hosted
# export GITLAB_READ_ONLY_MODE="true"                   # Optional: restrict to read-only
```

### 3. Register in openclaw.json

Add to `config/openclaw.json` under `mcpServers`:

```json
{
  "gitlab-mcp": {
    "command": "npx",
    "args": ["-y", "@zereight/mcp-gitlab"],
    "env": {
      "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_PERSONAL_ACCESS_TOKEN}",
      "GITLAB_API_URL": "${GITLAB_API_URL:-https://gitlab.com}"
    }
  }
}
```

### 4. Run the server (standalone test)

```bash
npx -y @zereight/mcp-gitlab
```

The server communicates via stdio. It will wait for JSON-RPC messages on stdin.

## Usage Examples

Once registered with an MCP client (Claude Desktop, OpenClaw, etc.):

- "Show me open issues in project network-automation"
- "List merge requests awaiting review in network-configs"
- "Show pipelines for project infrastructure-deploy"
- "Get the job log for the deploy stage in pipeline #456"
- "Show the directory structure of project network-configs"
- "Create an issue in network-automation titled 'BGP peer flapping on router-01'"
- "What commits were in the last merge request for project network-configs?"
- "Search for projects containing 'network'"
- "List milestones for project network-automation"

## Available Tool Categories (98+ tools)

| Category | Examples | Count |
|----------|----------|-------|
| Issues | list_issues, get_issue, create_issue, update_issue | ~15 |
| Merge Requests | list_merge_requests, get_merge_request, create_merge_request, merge_merge_request | ~15 |
| Pipelines | list_pipelines, get_pipeline, get_pipeline_jobs, retry_pipeline, cancel_pipeline | ~12 |
| Repository | list_repository_tree, get_file_content, list_commits, compare_branches | ~10 |
| Projects | list_projects, get_project, search_projects | ~8 |
| Labels | list_labels, create_label, update_label, delete_label | ~5 |
| Milestones | list_milestones, create_milestone, update_milestone | ~5 |
| Releases | list_releases, get_release, create_release | ~5 |
| Wiki | list_wiki_pages, get_wiki_page, create_wiki_page | ~5 |
| Other | groups, members, snippets, branches, tags | ~18 |

## Verification

To verify the integration is working:

1. Ensure the GitLab API is accessible: `curl -H "PRIVATE-TOKEN: $GITLAB_PERSONAL_ACCESS_TOKEN" "$GITLAB_API_URL/api/v4/projects?per_page=1"`
2. Register in OpenClaw and issue a test query: "List my GitLab projects"
3. Verify GAIT audit log records the interaction
