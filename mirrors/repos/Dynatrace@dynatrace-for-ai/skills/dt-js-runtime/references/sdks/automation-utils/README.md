# Automation Utils (`@dynatrace-sdk/automation-utils`)

> Env: ✅ Server runtime (inside workflow **Run JavaScript** actions)
> Status: current

Helper functions for accessing AutomationEngine context from within a Run JavaScript action. For full workflow management see [automation](../automation/README.md).

## Key exports

| Export | Purpose |
|---|---|
| `execution()` | Current workflow execution; returns an `IExecution` with helper methods |
| `actionExecution()` | Current action execution details (e.g. loop items) |
| `result(taskName)` | Result of a predecessor task by name |
| `getWorkflowLink()` / `getExecutionLink()` / `getTaskExecutionLink()` | Deep-link URLs |
| Constants | `executionId`, `workflowId`, `taskName`, `actionExecutionId` |

`IExecution` adds `event()` (trigger event payload as key-value) and `result(taskId)`.

Full detail: [functions.md](functions.md) (per-function signatures + examples) · [constants.md](constants.md) · [types.md](types.md) (`IExecution`).

## Required scopes

- `automation:workflows:read` for most operations.

## Example

```ts
import { execution, result } from "@dynatrace-sdk/automation-utils";

const exec = await execution();
const prev = await result("fetch_data");
```

## Notes

- Available for **standard** workflows only — simple workflows return 404.

Canonical reference: https://developer.dynatrace.com/develop/sdks/automation-utils/
