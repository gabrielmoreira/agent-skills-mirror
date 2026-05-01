# Operations Agent Definition Schema

The Operations Agent definition (Configurations.json) is the programmatic structure used to create and manage data agent items via the Fabric REST API. This document details the schema and provides examples.

## Definition Parts

| Path | Type | Required | Description |
|------|------|----------|-------------|
| `Configurations.json` | OperationsAgentDefinition (JSON) | Yes | Root definition containing configuration (goals, instructions, data sources, actions), playbook, and run state |

## OperationsAgentDefinition

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `configuration` | OperationsAgentConfiguration | Yes | User-authored configuration: goals, instructions, data sources, and actions |
| `playbook` | Object | Yes | Playbook definition (reserved for future expansion). Provide an empty object `{}` if not authored |
| `shouldRun` | Boolean | Yes | Whether the agent should currently run (`true`) or stay stopped (`false`) |

## OperationsAgentConfiguration

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `goals` | String | Yes | Business goals for the agent to accomplish |
| `instructions` | String | Yes | Explicit instructions / procedures the agent should follow |
| `dataSources` | Object (dictionary of DataSource) | Yes | Map of user-chosen data source aliases to data source objects |
| `actions` | Object (dictionary of Action) | Yes | Map of user-chosen action aliases to action objects |
| `recipient` | String | No | Recipient of the operation |

**Notes:**
- The keys inside `dataSources` and `actions` are user-defined aliases (e.g., `primaryKusto`, `notifyFlow`)
- Provide at least one data source and one action for a meaningful agent
- Keys must be unique within their respective objects

## DataSource

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | String (GUID) | Yes | Unique identifier for the data source reference |
| `type` | String (enum) | Yes | Data source type. Currently only `KustoDatabase` is supported |
| `workspaceId` | String (GUID) | Yes | Workspace ID containing the data source |

## Action

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | String (GUID) | Yes | Unique identifier for the action reference |
| `displayName` | String | Yes | The display name for the action |
| `description` | String | Yes | The description for the action |
| `kind` | String (enum) | Yes | Action kind. Currently only `PowerAutomateAction` is supported |
| `parameters` | Parameter[] | No | Optional parameter metadata list |

## Parameter

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | String | Yes | Parameter name |
| `description` | String | No | Human-friendly description |

## JSON Skeleton

```json
{
  "configuration": {
    "goals": "<business goals>",
    "instructions": "<agent instructions>",
    "dataSources": {},
    "actions": {}
  },
  "playbook": {},
  "shouldRun": true
}
```

## Complete Example

```json
{
  "configuration": {
    "goals": "Reduce manual triage of operations logs.",
    "instructions": "Monitor Kusto database metrics and trigger flow on thresholds.",
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
    "recipient": "ops-team@contoso.com"
  },
  "playbook": {},
  "shouldRun": true
}
```

## Validation Rules

- All GUID strings must be valid UUIDs
- Provide an empty object `{}` for `playbook` until extended schema details are published
- Use concise, action-oriented statements in `goals` and imperative steps in `instructions`
- Keys under `dataSources` and `actions` should be unique within their respective objects
- Validation rejects unknown `type` and `kind` values — only use documented enum values

## REST API Operations

The Operations Agent definition is used with the standard Fabric item CRUD APIs:

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create Item | `POST /v1/workspaces/{workspaceId}/items` | POST |
| Get Item Definition | `GET /v1/workspaces/{workspaceId}/items/{itemId}/getDefinition` | POST |
| Update Item Definition | `POST /v1/workspaces/{workspaceId}/items/{itemId}/updateDefinition` | POST |
| Delete Item | `DELETE /v1/workspaces/{workspaceId}/items/{itemId}` | DELETE |
| List Items | `GET /v1/workspaces/{workspaceId}/items` | GET |

The definition payload is Base64-encoded when sent via the API. See the [PowerShell automation script](../scripts/New-FabricDataAgent.ps1) for a working example.
