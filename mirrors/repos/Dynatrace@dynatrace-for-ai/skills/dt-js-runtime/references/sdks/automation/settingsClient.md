# `settingsClient`

Automation settings, service users, and permissions. Import:

```ts
import { settingsClient } from "@dynatrace-sdk/client-automation";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getSettings` | `GetSettingsResponse` | `automation:workflows:read` | Get automation settings (incl. available scopes). |
| `getUserSettings` | `UserSettings` | `automation:workflows:read` | Get the calling user's settings. |
| `getUserPermissions` | permissions | `automation:workflows:read` | Get the calling user's permissions. |
| `getServiceUsers` | `GetServiceUsersResponse` | `automation:workflows:read` | List service users available to automation. |
| `updateAuthorizations` | — | `automation:workflows:write` | Update authorizations/scopes. |
