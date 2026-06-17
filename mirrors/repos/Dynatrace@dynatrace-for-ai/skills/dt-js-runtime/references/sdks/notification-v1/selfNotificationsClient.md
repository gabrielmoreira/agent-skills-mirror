# `selfNotificationsClient`

> **DEPRECATED** — migrate to [notification-v2](../notification-v2/README.md).

Manage self-notifications. Import:

```ts
import { selfNotificationsClient } from "@dynatrace-sdk/client-notification";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createSelfNotification` | `SelfNotification` | `notification:self-notifications:write` | Create a self-notification. |
| `getSelfNotification` | `SelfNotification` | `notification:self-notifications:read` | Get one by id. |
| `getSelfNotifications` | `PaginatedSelfNotificationList` | `notification:self-notifications:read` | List self-notifications. |
| `updateSelfNotification` | `SelfNotification` | `notification:self-notifications:write` | Full update by id. |
| `patchSelfNotification` | `SelfNotification` | `notification:self-notifications:write` | Partial update by id. |
| `deleteSelfNotification` | — | `notification:self-notifications:write` | Delete by id. |
