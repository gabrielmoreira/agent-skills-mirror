# Publishing and Sharing

Troubleshoot issues with publishing, sharing, and consuming Fabric Data Agents.

## Publishing a Data Agent

### How Publishing Works

Publishing creates two versions of the data agent:

1. **Draft version** - Your working copy for continued refinement
2. **Published version** - The shared version colleagues interact with

### Steps to Publish

1. Test the agent across various questions to confirm accurate SQL/DAX/KQL generation.
2. Select **Publish** from the top toolbar.
3. Provide a detailed description of the agent's purpose and capabilities.
4. The description guides colleagues AND external AI orchestrators invoking the agent.

### Publishing Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Publish button grayed out | No data sources configured | Add at least one data source before publishing |
| Publish fails with error | Capacity throttled or unavailable | Retry after a few minutes; check capacity health |
| Published version outdated | Draft changes not republished | Click Publish again to update the published version |
| Description not visible | Description left empty | Re-publish with a detailed description |

## Sharing a Data Agent

### How Sharing Works

After publishing, share the agent so colleagues can ask questions against it.

### Share Permissions

| Permission Level | What It Allows |
|-----------------|---------------|
| Read | View and interact with the published agent (ask questions) |
| Share | Re-share the agent with others |
| Edit | Modify the agent's configuration, instructions, and examples |

### Sharing Steps

1. Navigate to the workspace containing the data agent.
2. Select the data agent item.
3. Click **Share** from the toolbar.
4. Add users or security groups and set the permission level.
5. Shared users can access the published version to ask questions.

### Sharing Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| User cannot see the agent | Not shared with them | Share the agent with Read permission |
| User gets access denied on queries | User lacks data source permissions | The user must have permissions on the underlying data sources too |
| Shared user sees no data | Data permissions are separate from agent permissions | Grant the user Read access to the underlying lakehouse/warehouse/model |
| Agent not showing in workspace | User doesn't have workspace access | Add user to workspace with at least Viewer role |

### Critical: Data Permissions Are Separate

Sharing the agent does NOT automatically grant access to the underlying data. Users need:

1. **Agent permission** - Read permission on the data agent item
2. **Data permission** - Appropriate access to each underlying data source

The agent executes queries using the **current user's credentials**, not the agent creator's. If the user cannot query the data directly, the agent cannot query it on their behalf.

## Consuming a Published Agent

### In-Product Experience

Published agents are consumed through the Fabric portal chat interface:

1. User navigates to the shared data agent.
2. Types a natural language question.
3. Agent processes the question and returns results.
4. User can view intermediate steps (generated queries) via the dropdown.

### Via Fabric Data Agent SDK

For programmatic access from Fabric notebooks:

```python
%pip install fabric-data-agent-sdk

from fabric_data_agent_sdk import DataAgentClient

client = DataAgentClient(agent_id="<agent-artifact-id>")
response = client.query("What were total sales last quarter?")
print(response)
```

### Via Azure AI Foundry Integration

Published agents expose an endpoint for integration:

- Endpoint format: `https://<environment>.fabric.microsoft.com/groups/<workspace_id>/aiskills/<artifact_id>`
- Extract `workspace-id` and `artifact-id` from this URL for Foundry connections
- Only user identity authentication is supported (SPN not supported)

## Reverting to a Previous Version

Select **Revert to published version** in the toolbar to discard draft changes and restore the currently published configuration.

## Version Management Best Practices

1. Test thoroughly with diverse questions before each publish
2. Document changes in the agent description
3. Use the SDK evaluation feature to benchmark accuracy before publishing
4. Collect feedback from shared users and incorporate into the draft
5. Re-publish periodically as you add more example queries and instructions
