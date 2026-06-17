# `businessCalendarsClient`

Manage business calendars (working days/holidays referenced by schedules). Import:

```ts
import { businessCalendarsClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createBusinessCalendar` | `BusinessCalendarResponse` | `automation:workflows:write` | Create a business calendar. |
| `getBusinessCalendar` | `BusinessCalendarResponse` | `automation:workflows:read` | Get a calendar by `id`. |
| `getBusinessCalendars` | `PaginatedBusinessCalendarResponseList` | `automation:workflows:read` | List calendars. |
| `updateBusinessCalendar` | `BusinessCalendarResponse` | `automation:workflows:write` | Replace a calendar. |
| `patchBusinessCalendar` | `BusinessCalendarResponse` | `automation:workflows:write` | Partially update a calendar. |
| `deleteBusinessCalendar` | — | `automation:workflows:write` | Delete a calendar. |
| `duplicateBusinessCalendar` | `BusinessCalendarResponse` | `automation:workflows:write` | Duplicate a calendar. |
| `getBusinessCalendarHistoryRecord` / `getBusinessCalendarHistoryRecords` | history | `automation:workflows:read` | Get one / list calendar history. |
| `restoreBusinessCalendarHistoryRecord` | `BusinessCalendarResponse` | `automation:workflows:write` | Restore a historical version. |
