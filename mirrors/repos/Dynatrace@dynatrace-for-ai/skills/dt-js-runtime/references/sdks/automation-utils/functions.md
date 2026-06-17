# Automation Utils — Functions

Import from `@dynatrace-sdk/automation-utils`.

| Function | Returns | Scope | Purpose |
|---|---|---|---|
| `execution(executionId?)` | `Promise<IExecution>` | `automation:workflows:read` | Current workflow execution details. Has `.event()` for trigger context and `.result(taskName)` for a task's result. Standard workflows only. |
| `actionExecution(actionExecutionId?)` | `Promise<…>` | `automation:workflows:read` | Current action execution details, incl. `loopItem` for loop iterations. Standard workflows only. |
| `result(taskName)` | `Promise<any>` | `automation:workflows:read` | Result of a predecessor task's execution in the current workflow. |
| `getExecutionLink()` | `string \| null` | — | Deep link to the current execution. |
| `getTaskExecutionLink()` | `string \| null` | — | Deep link to the current task execution. |
| `getWorkflowLink()` | `string \| null` | — | Deep link to the current workflow. |

## Examples

```ts
import { execution, result } from "@dynatrace-sdk/automation-utils";

const exe = await execution();
const eventContext = exe.event();
const prev = await result("predecessor_task_1");
```
