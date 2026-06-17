# `actionExecutionsClient`

Read action executions. Import:

```ts
import { actionExecutionsClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getActionExecution` | `ActionExecution` | `automation:workflows:read` | Get an action execution by `id`. |
| `getActionExecutionLog` | log | `automation:workflows:read` | Get the log of an action execution. |
