# `executionsClient`

Control and inspect workflow executions and task executions. Import:

```ts
import { executionsClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getExecution` | `Execution` | `automation:workflows:read` | Get an execution by `id`. |
| `getExecutions` | `PaginatedExecutionList` | `automation:workflows:read` | List executions. |
| `getExecutionActions` | actions | `automation:workflows:read` | Actions assigned to tasks in an execution. |
| `getExecutionLog` | log | `automation:workflows:read` | Execution log. |
| `getAllEventLogs` | `EventLogs` | `automation:workflows:read` | All event logs for an execution. |
| `getTransitions` | `TaskTransitions` | `automation:workflows:read` | Task transitions of an execution. |
| `getTaskExecution` | `TaskExecution` | `automation:workflows:read` | A task execution. |
| `getTaskExecutions` | `TaskExecutions` | `automation:workflows:read` | All task executions. |
| `getTaskExecutionInput` | `TaskExecutionInput` | `automation:workflows:read` | Resolved input of a task execution. |
| `getTaskExecutionResult` | result | `automation:workflows:read` | Result of a task execution. |
| `getTaskExecutionLog` | log | `automation:workflows:read` | Log of a task execution. |
| `cancelExecution` | — | `automation:workflows:run` | Cancel an active execution. |
| `cancelTaskExecution` | — | `automation:workflows:run` | Cancel a task execution (cancels the workflow). |
| `pauseExecution` | — | `automation:workflows:run` | Pause an execution. |
| `resumeExecution` | — | `automation:workflows:run` | Resume a paused execution. |

## Example

```ts
import { executionsClient } from "@dynatrace-sdk/client-automation";

const exec = await executionsClient.getExecution({ id: "..." });
const result = await executionsClient.getTaskExecutionResult({ executionId: "...", id: "..." });
```
