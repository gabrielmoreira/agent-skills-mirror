# `webhookHandlersClient`

Manage webhook handlers. Import:

```ts
import { webhookHandlersClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `writeWebhookHandler` | `WebhookHandler` | `automation:workflows:write` | Create/update a webhook handler. |
| `getWebhookHandler` | `WebhookHandler` | `automation:workflows:read` | Get a webhook handler by `id`. |
| `getWebhookHandlers` | `WebhookHandlerList` | `automation:workflows:read` | List webhook handlers. |
| `deleteWebhookHandler` | — | `automation:workflows:write` | Delete a webhook handler. |
