# Quickstart: Jenkins MCP Server Integration

**Feature**: 007-jenkins-mcp-server
**Date**: 2026-03-27

## Prerequisites

1. A running Jenkins instance (v2.533 or later)
2. The Jenkins MCP Server plugin installed (v0.158 or later) — install from Jenkins Plugin Manager
3. A Jenkins API token generated for your user account
4. Network connectivity from the AI assistant host to the Jenkins HTTPS endpoint

## Setup

### 1. Install the Jenkins MCP Server Plugin

In Jenkins: **Manage Jenkins → Plugins → Available Plugins → search "MCP Server" → Install**

No additional plugin configuration is needed — the MCP endpoints are available immediately after installation.

### 2. Generate a Jenkins API Token

In Jenkins: **User menu → Configure → API Token → Add new Token → Generate**

Copy the generated token — it will not be shown again.

### 3. Configure environment variables

```bash
export JENKINS_URL="https://your-jenkins-host:8443"
export JENKINS_USERNAME="your-username"
export JENKINS_API_TOKEN="your-api-token"

# Generate the Base64 auth string
export JENKINS_AUTH_BASE64=$(echo -n "${JENKINS_USERNAME}:${JENKINS_API_TOKEN}" | base64)
```

### 4. Register in openclaw.json

Add to `config/openclaw.json` under `mcpServers`:

```json
{
  "jenkins-mcp": {
    "url": "${JENKINS_URL}/mcp-server/mcp",
    "headers": {
      "Authorization": "Basic ${JENKINS_AUTH_BASE64}"
    },
    "env": {
      "JENKINS_URL": "${JENKINS_URL}",
      "JENKINS_AUTH_BASE64": "${JENKINS_AUTH_BASE64}"
    }
  }
}
```

### 5. Verify the connection

Once registered with an MCP client (Claude Desktop, OpenClaw, etc.):

```
"Check Jenkins health and tell me who I'm authenticated as"
```

This invokes `getStatus` and `whoAmI` to confirm connectivity and permissions.

## Usage Examples

Once registered with an MCP client:

- "Show me all Jenkins jobs"
- "What is the status of the last build for deploy-network-config?"
- "Trigger a build for job backup-routers with parameter SITE=datacenter1"
- "Show me the build log for deploy-network-config build #42"
- "Search the build log for 'ERROR' or 'FATAL'"
- "What commits were in the last build of deploy-network-config?"
- "Find all jobs that use the repository git@github.com:org/network-configs.git"

## Available Tools (16)

| Category | Tool | Description |
|----------|------|-------------|
| Jobs | getJob | Get job details by full name |
| Jobs | getJobs | List all jobs with pagination |
| Jobs | triggerBuild | Trigger a build (with optional parameters) |
| Jobs | getQueueItem | Check queue item status |
| Builds | getBuild | Get build details |
| Builds | updateBuild | Update build display name or keep flag |
| Builds | getBuildLog | Retrieve build console output |
| Builds | searchBuildLog | Search log by regex pattern |
| SCM | getJobScm | Get job SCM configuration |
| SCM | getBuildScm | Get build SCM details |
| SCM | getBuildChangeSets | Get commits for a build |
| SCM | findJobsWithScmUrl | Find jobs by repository URL |
| System | whoAmI | Get authenticated user info |
| System | getStatus | Get Jenkins health status |
| Pipeline | getPipelineRuns | Get pipeline run history |
| Pipeline | getPipelineRunLog | Get pipeline run log |

## Verification

To verify the integration is working:

1. Ensure the Jenkins MCP plugin is installed: visit `https://your-jenkins-host/mcp-server/mcp` — should return an MCP protocol response
2. Test Basic Auth: `curl -u "username:api_token" https://your-jenkins-host/mcp-server/mcp`
3. Register in OpenClaw and issue a test query via your MCP client
4. Verify GAIT audit log records the interaction
