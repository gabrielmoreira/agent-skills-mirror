# External Integration

Troubleshoot issues integrating Fabric Data Agents with Azure AI Foundry, Microsoft Copilot Studio, Microsoft Teams, and other external systems.

## Azure AI Foundry Integration

### Prerequisites

1. A published Fabric data agent with a valid endpoint
2. An Azure AI Foundry project with an agent configured
3. User identity authentication (SPN is NOT supported)

### How It Works

1. Build and **publish** a Fabric data agent in the Fabric portal.
2. Extract the endpoint URL: `https://<environment>.fabric.microsoft.com/groups/<workspace_id>/aiskills/<artifact_id>`
3. In Azure AI Foundry, add the Microsoft Fabric tool to your agent.
4. Create a connection using the `workspace-id` and `artifact-id` from the endpoint.
5. When a user queries the Foundry agent, it determines whether to invoke the Fabric tool.
6. The Fabric tool uses the end user's identity (On-Behalf-Of) for data access.

### Connection Setup

1. In the Foundry portal, navigate to your agent's **Setup** pane → scroll to **Knowledge** → **Add**.
2. Select **Microsoft Fabric** (only one per agent).
3. Click to add a new connection.
4. Enter the `workspace-id` and `artifact-id` extracted from the published endpoint URL.
5. Check **is secret** for both values.

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Fabric tool not invoked | Agent instructions don't mention Fabric | Update Foundry agent instructions to describe when to use Fabric (e.g., "for customer and product sales data, use the Fabric tool") |
| Connection fails | Agent not published | Verify the data agent is published (not just draft) in Fabric |
| Wrong workspace/artifact ID | Miscopied from endpoint URL | Re-extract IDs from the endpoint URL format |
| SPN authentication error | Service principal used | SPN is not supported; only user identity authentication works |
| Orchestration model too large | Using oversized model for routing | Use a smaller model like gpt-4o-mini for Foundry agent orchestration |
| Fabric tool never selected | Tool choice not forced | Use `tool_choice` parameter in SDK/API to force Fabric tool invocation |

### Important Notes

- The Foundry agent's selected model is used ONLY for orchestration and response generation, NOT for NL2SQL within the Fabric data agent.
- The Fabric data agent uses its own internal LLM for query generation (cannot be changed).
- Recommend using `gpt-4o-mini` or similar smaller model for the Foundry agent.
- Only one Fabric tool can be added per Foundry agent.

## REST API Integration

### Operations Agent Definition

For programmatic agent management via the Fabric REST API, the definition uses a `Configurations.json` payload:

```json
{
  "configuration": {
    "goals": "<business goals>",
    "instructions": "<agent instructions>",
    "dataSources": {
      "primaryKusto": {
        "id": "11111111-2222-3333-4444-555555555555",
        "type": "KustoDatabase",
        "workspaceId": "66666666-7777-8888-9999-aaaaaaaaaaaa"
      }
    },
    "actions": {
      "notifyFlow": {
        "id": "bbbbbbbb-cccc-dddd-eeee-ffffffffffff",
        "kind": "PowerAutomateAction",
        "displayName": "PowerAutomateAlert",
        "description": "A PowerAutomate action to send out alert",
        "parameters": [
          { "name": "Severity", "description": "Alert severity level" }
        ]
      }
    },
    "recipient": "user@contoso.com"
  },
  "playbook": {},
  "shouldRun": true
}
```

### REST API Validation Rules

| Rule | Detail |
|------|--------|
| All GUIDs must be valid UUIDs | Use proper GUID format for all ID fields |
| Playbook is reserved | Provide an empty object `{}` until schema is extended |
| Data source type values | Currently only `KustoDatabase` is supported for operations agents |
| Action kind values | Currently only `PowerAutomateAction` is supported |
| Keys must be unique | Data source and action aliases must be unique within their objects |
| At least one data source + action | Provide both for a meaningful agent |
| Goals: concise, action-oriented | Use clear business objective statements |
| Instructions: imperative steps | Use step-by-step procedural language |

### Common REST API Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| 400 Bad Request | Invalid GUID format | Validate all ID fields are proper UUIDs |
| Unknown type value rejected | Using unsupported data source type | Only `KustoDatabase` is supported currently |
| Unknown kind value rejected | Using unsupported action kind | Only `PowerAutomateAction` is supported currently |
| Definition fails validation | Missing required fields | Ensure goals, instructions, dataSources, and actions are all present |

## Fabric CLI Integration

For command-line management of Fabric items including data agents:

```bash
# Install
pip install ms-fabric-cli

# Login
fab auth login

# Use interactive browser login for user identity
# Service principal login is available for automation scenarios
```

## Python SDK Integration

For notebook-based programmatic access:

```python
%pip install fabric-data-agent-sdk

# Create, manage, and evaluate data agents programmatically
# SDK works exclusively within Microsoft Fabric notebooks
# Not supported for local execution
```

### SDK Prerequisites
- Python >= 3.10
- Must run within a Fabric notebook (not local)
- Dependencies installed automatically via pip

## Security Model

All external integrations follow Identity Passthrough (On-Behalf-Of):

1. External system authenticates the end user.
2. User's identity is passed to the Fabric data agent.
3. Agent queries data using the user's permissions.
4. Users can only access data they are authorized to view.

This means:
- No service principal passthrough for data queries
- Each user sees only data they have permissions for
- Data access follows existing Fabric RBAC and row-level security
