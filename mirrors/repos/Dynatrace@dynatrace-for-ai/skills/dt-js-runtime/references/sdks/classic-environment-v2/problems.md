# `problemsClient`

Query problems and manage problem comments. Import:

```ts
import { problemsClient } from "@dynatrace-sdk/client-classic-environment-v2";
```

| Method | Purpose |
|---|---|
| `getProblems` | Query problems (filterable, paginated). |
| `getProblem` | Get one problem by id. |
| `closeProblem` | Close a problem. |
| `getComments` | List comments on a problem. |
| `getComment` | Get one comment. |
| `createComment` | Add a comment to a problem. |
| `updateComment` | Update a comment. |
| `deleteComment` | Delete a comment. |
