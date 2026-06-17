# Notification v2 (`@dynatrace-sdk/client-notification-v2`)

> Env: ✅ Server runtime
> Status: current (replaces [notification-v1](../notification-v1/README.md))

Manage resource and event notifications via the Notification Service API.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `eventNotificationsClient` | `createEventNotification`, `getEventNotification(s)`, `updateEventNotification`, `patchEventNotification`, `deleteEventNotification` | Event-triggered notifications |
| `resourceNotificationsClient` | `createResourceNotification`, `getResourceNotification(s)`, `deleteResourceNotification`, `deleteResourceNotificationByTypeAndResource` | Resource-level notifications |

`EventTriggerConfig` supports three trigger types: DQL `EventQuery` (`EventQueryTriggerConfig`), Davis problem (`DavisProblemTriggerConfig`), Davis event (`DavisEventTriggerConfig`).

Full method/type detail: [eventNotificationsClient.md](eventNotificationsClient.md), [resourceNotificationsClient.md](resourceNotificationsClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Required scopes

- `notification:notifications:read` / `notification:notifications:write`.

## Example

```ts
import { eventNotificationsClient } from "@dynatrace-sdk/client-notification-v2";

const data = await eventNotificationsClient.createEventNotification({
  body: {
    resourceId: "...",
    notificationType: "...",
    triggerConfiguration: { type: "event", value: { query: "..." } },
  },
});
```

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-notification-v2/
