# `schedulingRulesClient`

Manage scheduling rules (date/offset rules used by schedules). Import:

```ts
import { schedulingRulesClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createRule` | `Rule` | `automation:workflows:write` | Create a scheduling rule. |
| `getRule` | `Rule` | `automation:workflows:read` | Get a rule by `id`. |
| `getRules` | `PaginatedRuleList` | `automation:workflows:read` | List rules. |
| `updateRule` | `Rule` | `automation:workflows:write` | Replace a rule. |
| `patchRule` | `Rule` | `automation:workflows:write` | Partially update a rule. |
| `deleteRule` | — | `automation:workflows:write` | Delete a rule. |
| `duplicateRule` | `Rule` | `automation:workflows:write` | Duplicate a rule. |
| `previewRule` | `RulePreviewResponse` | `automation:workflows:read` | Preview the dates a rule would produce. |
| `getRuleHistoryRecord` / `getRuleHistoryRecords` | history | `automation:workflows:read` | Get one / list rule history. |
| `restoreRuleHistoryRecord` | `Rule` | `automation:workflows:write` | Restore a historical rule version. |
