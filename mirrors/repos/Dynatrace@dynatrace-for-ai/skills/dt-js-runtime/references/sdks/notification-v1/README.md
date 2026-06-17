# Notification v1 (`@dynatrace-sdk/client-notification`)

> Env: ✅ Server runtime
> Status: ⚠ **DEPRECATED** — use [notification-v2](../notification-v2/README.md) instead

Manage self-notifications via the Notification Service API. All methods are deprecated; migrate to v2.

## Clients & key methods

`selfNotificationsClient` — `createSelfNotification`, `getSelfNotification`, `getSelfNotifications`, `updateSelfNotification`, `patchSelfNotification`, `deleteSelfNotification`.

Trigger types: event query, Davis problem, Davis event.

Full method/type detail: [selfNotificationsClient.md](selfNotificationsClient.md) · [types.md](types.md).

## Required scopes

- `notification:self-notifications:read` / `notification:self-notifications:write`.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-notification/
