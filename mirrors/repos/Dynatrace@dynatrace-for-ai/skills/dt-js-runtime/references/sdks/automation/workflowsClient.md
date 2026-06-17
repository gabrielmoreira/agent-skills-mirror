# `workflowsClient`

Workflow lifecycle, templates, execution, and history. Import:

```ts
import { workflowsClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createWorkflow` | `Workflow` | `automation:workflows:write` | Create a workflow and set usages. |
| `getWorkflow` | `Workflow` | `automation:workflows:read` | Get a workflow by `id`. |
| `getWorkflows` | `WorkflowList` | `automation:workflows:read` | List workflows (filter by owner type, etc.). |
| `updateWorkflow` | `Workflow` | `automation:workflows:write` | Replace a workflow by `id`. |
| `patchWorkflow` | `Workflow` | `automation:workflows:write` | Partially update a workflow. |
| `deleteWorkflow` | — | `automation:workflows:write` | Delete a workflow by `id`. |
| `duplicateWorkflow` | `Workflow` | `automation:workflows:write` | Duplicate a workflow. |
| `runWorkflow` | `Execution` | `automation:workflows:run` | Create an Execution for the workflow (`body.input`, `body.params`). |
| `getWorkflowActions` | actions | `automation:workflows:read` | List actions used by a workflow. |
| `getWorkflowTask` / `getWorkflowTasks` | `Task` / `Tasks` | `automation:workflows:read` | Get one / all tasks of a workflow. |
| `exportWorkflow` | `WorkflowExport` | `automation:workflows:read` | Export a workflow definition. |
| `exportWorkflowTemplate` | `WorkflowTemplate` | `automation:workflows:read` | Export a workflow as a template. |
| `getWorkflowHistoryRecord` / `getWorkflowHistoryRecords` | history | `automation:workflows:read` | Get one / list change-history records. |
| `exportWorkflowHistoryRecord` | `Workflow` | `automation:workflows:read` | Export a historical version. |
| `exportWorkflowHistoryRecordTemplate` | `WorkflowTemplate` | `automation:workflows:read` | Export a historical version as a template. |
| `restoreWorkflowHistoryRecord` | `Workflow` | `automation:workflows:write` | Restore a historical version. |
| `resetWorkflowThrottles` | `WorkflowThrottlesResetStatus` | `automation:workflows:write` | Reset a workflow's throttles. |

## Example

```ts
import { workflowsClient } from "@dynatrace-sdk/client-automation";

const wf = await workflowsClient.createWorkflow({ body: { title: "My workflow" } });
const execution = await workflowsClient.runWorkflow({ id: wf.id, body: { input: {}, params: {} } });
```
