# `schedulesClient`

Preview schedules and look up calendar reference data. Import:

```ts
import { schedulesClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `previewSchedule` | `SchedulePreviewResponse` | `automation:workflows:read` | Preview the trigger times a schedule would produce. |
| `getCountries` | `CountryList` | `automation:workflows:read` | List countries (for holiday calendars). |
| `getHolidayCalendar` | `HolidayCalendarList` | `automation:workflows:read` | Get holidays for a country/calendar. |
| `getTimezones` | timezones | `automation:workflows:read` | List supported timezones. |
