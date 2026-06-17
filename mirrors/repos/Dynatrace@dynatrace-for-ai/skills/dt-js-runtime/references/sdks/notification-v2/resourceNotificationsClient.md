# `resourceNotificationsClient`

Manage resource notifications. Import:

```ts
import { resourceNotificationsClient } from "@dynatrace-sdk/client-notification-v2";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createResourceNotification` | `ResourceNotification` | `notification:notifications:write` | Create (`notificationType`, `resourceId`). |
| `getResourceNotification` | `ResourceNotification` | `notification:notifications:read` | Get one by `id`. |
| `getResourceNotifications` | `PaginatedResourceNotificationList` | `notification:notifications:read` | List (paginated/filterable). |
| `deleteResourceNotification` | — | `notification:notifications:write` | Delete by `id`. |
| `deleteResourceNotificationByTypeAndResource` | — | `notification:notifications:write` | Delete by `notificationType` + `resourceId`. |

## Example

```ts
import { resourceNotificationsClient } from "@dynatrace-sdk/client-notification-v2";

await resourceNotificationsClient.createResourceNotification({
  body: { notificationType: "...", resourceId: "..." },
});
```
