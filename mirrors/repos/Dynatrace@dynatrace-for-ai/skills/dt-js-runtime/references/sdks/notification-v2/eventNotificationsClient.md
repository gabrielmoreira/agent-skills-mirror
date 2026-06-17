# `eventNotificationsClient`

Manage event-triggered notifications. Import:

```ts
import { eventNotificationsClient } from "@dynatrace-sdk/client-notification-v2";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createEventNotification` | `EventNotification` | `notification:notifications:write` | Create an event notification (`resourceId`, `notificationType`, `triggerConfiguration`). |
| `getEventNotification` | `EventNotification` | `notification:notifications:read` | Get one by `id`. |
| `getEventNotifications` | `PaginatedEventNotificationList` | `notification:notifications:read` | List (paginated/filterable). |
| `updateEventNotification` | `EventNotification` | `notification:notifications:write` | Full update by `id`. |
| `patchEventNotification` | `EventNotification` | `notification:notifications:write` | Partial update by `id`. |
| `deleteEventNotification` | — | `notification:notifications:write` | Delete by `id`. |

## Example

```ts
import { eventNotificationsClient } from "@dynatrace-sdk/client-notification-v2";

await eventNotificationsClient.createEventNotification({
  body: {
    resourceId: "...",
    notificationType: "...",
    triggerConfiguration: { type: "event", value: { query: "..." } },
  },
});
```
