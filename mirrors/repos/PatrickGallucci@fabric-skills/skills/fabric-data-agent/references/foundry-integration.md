# Integrating Fabric Data Agents with Azure AI Foundry

Connect a published Fabric Data Agent to Azure AI Foundry to build intelligent agents that leverage enterprise data through natural language queries. The Fabric tool enables Foundry agents to invoke Fabric Data Agents using identity passthrough (On-Behalf-Of) authorization.

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Fabric Data Agent | Created and **published** in the Fabric portal |
| Foundry Project | Azure AI Foundry project endpoint |
| Fabric Connection | Microsoft Fabric connection added to the Foundry project |
| Model Deployment | A model deployed in Foundry (recommend `gpt-4o-mini` for orchestration) |
| RBAC | Developers and end users need `Azure AI User` role |
| Data Access | At least `READ` on the Fabric Data Agent and its underlying data sources |
| Same Tenant | Fabric Data Agent and Foundry Agent must be in the same tenant |

**Important:** The Fabric data agent only supports user identity authentication. Service Principal Name (SPN) authentication is not supported.

## Environment Variables

Set these before running the API calls:

```bash
export AZURE_AI_FOUNDRY_PROJECT_ENDPOINT="<your-foundry-project-endpoint>"
export AGENT_TOKEN="<your-bearer-token>"
export API_VERSION="2025-05-15-preview"
export FABRIC_CONNECTION_ID="/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<ai-services>/projects/<project>/connections/<fabric-connection>"
export MODEL_DEPLOYMENT_NAME="<your-model-deployment>"
```

## Step 1: Create an Agent with Fabric Tool Enabled

```bash
curl --request POST \
  --url $AZURE_AI_FOUNDRY_PROJECT_ENDPOINT/assistants?api-version=$API_VERSION \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'$MODEL_DEPLOYMENT_NAME'",
    "name": "Fabric-Powered Agent",
    "instructions": "You are a helpful data analyst. For customer and product sales related data, please use the Fabric tool. Always provide clear, data-driven answers.",
    "tools": [
      {
        "type": "fabric_dataagent",
        "fabric_dataagent": {
          "connection_id": "'$FABRIC_CONNECTION_ID'"
        }
      }
    ]
  }'
```

**Tips for agent instructions:**
- Describe what data the Fabric tool can access so the model knows when to invoke it
- Use `tool_choice` parameter to force Fabric tool invocation on every run if needed
- The orchestration model (set in Foundry) is only used for agent reasoning — it does not impact which model Fabric uses for NL2SQL

## Step 2: Create a Thread

```bash
curl --request POST \
  --url $AZURE_AI_FOUNDRY_PROJECT_ENDPOINT/threads?api-version=$API_VERSION \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d ''
```

Save the returned `thread_id` for subsequent calls.

## Step 3: Add a User Question

```bash
curl --request POST \
  --url $AZURE_AI_FOUNDRY_PROJECT_ENDPOINT/threads/<thread_id>/messages?api-version=$API_VERSION \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "What were our top 5 products by revenue last quarter?"
  }'
```

## Step 4: Run the Thread

```bash
curl --request POST \
  --url $AZURE_AI_FOUNDRY_PROJECT_ENDPOINT/threads/<thread_id>/runs?api-version=$API_VERSION \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "<assistant_id>"
  }'
```

## Step 5: Check Run Status

```bash
curl --request GET \
  --url $AZURE_AI_FOUNDRY_PROJECT_ENDPOINT/threads/<thread_id>/runs/<run_id>?api-version=$API_VERSION \
  -H "Authorization: Bearer $AGENT_TOKEN"
```

Poll until `status` is `completed`.

## Step 6: Retrieve the Response

```bash
curl --request GET \
  --url $AZURE_AI_FOUNDRY_PROJECT_ENDPOINT/threads/<thread_id>/messages?api-version=$API_VERSION \
  -H "Authorization: Bearer $AGENT_TOKEN"
```

## PowerShell Equivalent

See [Invoke-FabricFoundryAgent.ps1](../scripts/Invoke-FabricFoundryAgent.ps1) for a PowerShell implementation of this workflow that handles authentication, polling, and response parsing.

## SDK Support

| SDK | Supported |
|-----|-----------|
| Python SDK | Yes |
| C# SDK | Not yet |
| JavaScript SDK | Not yet |
| REST API | Yes |

## Security Model

The integration uses Identity Passthrough (On-Behalf-Of) authorization. When a user sends a query through the Foundry agent, the Fabric tool uses the end user's identity to generate and execute queries. Users can only access data they already have permissions to view in Fabric.
