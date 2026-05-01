# Workflow: Operations Agent Debugging

## Table of Contents

- [Definition Structure](#definition-structure)
- [Common Issues](#common-issues)
- [Validation Checklist](#validation-checklist)
- [Example Configuration](#example-configuration)

## Definition Structure

An Operations Agent requires a `Configurations.json` definition with this structure:

```json
{
  "configuration": {
    "goals": "<business goals - concise, action-oriented>",
    "instructions": "<imperative steps the agent follows>",
    "dataSources": { "<alias>": { "id": "<GUID>", "type": "KustoDatabase", "workspaceId": "<GUID>" } },
    "actions": { "<alias>": { "id": "<GUID>", "kind": "PowerAutomateAction", "displayName": "...", "description": "..." } },
    "recipient": "<optional email>"
  },
  "playbook": {},
  "shouldRun": true
}
```

**Required fields:** goals, instructions, dataSources (at least one), actions (at least one).

## Common Issues

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Agent not running | `shouldRun` is `false` | Set `shouldRun: true` in definition |
| No data source connected | Empty `dataSources` object | Add at least one KustoDatabase source |
| Actions never trigger | Empty `actions` object or wrong `kind` | Add PowerAutomateAction with valid GUID |
| Wrong data queried | Incorrect `workspaceId` or `id` | Verify GUIDs match actual Kusto database |
| Playbook errors | Invalid playbook structure | Use empty object `{}` until schema published |
| Unknown type value | Using unsupported data source type | Only `KustoDatabase` is currently supported |
| Unknown kind value | Using unsupported action kind | Only `PowerAutomateAction` is currently supported |
| Invalid GUID format | Malformed UUID strings | Ensure all GUIDs are valid UUIDs |

## Validation Checklist

- [ ] `shouldRun` is set to `true`
- [ ] `goals` contains concise, action-oriented business objectives
- [ ] `instructions` contains imperative procedural steps
- [ ] At least one data source exists with valid GUID, `type: "KustoDatabase"`, and valid workspaceId
- [ ] At least one action exists with valid GUID, `kind: "PowerAutomateAction"`, displayName, and description
- [ ] All GUIDs are valid UUIDs (format: 8-4-4-4-12 hex characters)
- [ ] Data source aliases and action aliases are unique within their objects
- [ ] `playbook` is an empty object `{}`
- [ ] Power Automate flow referenced by the action is active and accessible
- [ ] Kusto database referenced by the data source is online and accessible

## Example Configuration

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
