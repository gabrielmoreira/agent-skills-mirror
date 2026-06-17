# Automation (`@dynatrace-sdk/client-automation`)

> Env: ✅ Server runtime
> Status: current

Manage and execute workflows via the AutomationEngine API. For helpers used *inside* a workflow's Run JavaScript action, see [automation-utils](../automation-utils/README.md).

## Clients & key methods

| Client | Purpose |
|---|---|
| `workflowsClient` | Workflow CRUD + `runWorkflow` |
| `executionsClient` | Monitor / pause / resume / cancel executions |
| `schedulingRulesClient` | Scheduling rules (cron / recurrence) + previews |
| `businessCalendarsClient` | Business calendars & holidays |
| `eventTriggersClient` | Davis problem/event triggers |
| `webhookHandlersClient` | Webhook handlers |
| `schedulesClient` | Timezones, holiday calendars |

Full method/type detail (per client): [workflowsClient.md](workflowsClient.md), [executionsClient.md](executionsClient.md), [schedulingRulesClient.md](schedulingRulesClient.md), [businessCalendarsClient.md](businessCalendarsClient.md), [schedulesClient.md](schedulesClient.md), [settingsClient.md](settingsClient.md), [eventTriggersClient.md](eventTriggersClient.md), [actionExecutionsClient.md](actionExecutionsClient.md), [actionsSampleResultClient.md](actionsSampleResultClient.md), [webhookHandlersClient.md](webhookHandlersClient.md), [versionClient.md](versionClient.md) · [types.md](types.md).

## Required scopes

- `automation:workflows:read` (reads: get/export/list/preview), `automation:workflows:write` (mutations: create/update/patch/delete/duplicate/restore), `automation:workflows:run` (execution control: run/cancel/pause/resume); admin ops also need `automation:workflows:admin`.

## Example

```ts
import { workflowsClient } from "@dynatrace-sdk/client-automation";

const execution = await workflowsClient.runWorkflow({
  id: "workflow-uuid",
  body: { input: {}, params: {} },
});
```

## Notes

- Several methods are deprecated (flagged in the official docs).

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-automation/
