# `appEngineRegistryAppsClient`

Install, query, and run-search AppEngine apps. Import:

```ts
import { appEngineRegistryAppsClient } from "@dynatrace-sdk/client-app-engine-registry";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getApps` | `AppInfoList` | `app-engine:apps:read` | List installed apps. |
| `getApp` | `AppInfo` | `app-engine:apps:read` | Get one installed app by `id`. |
| `installApp` | `AppStub` | `app-engine:apps:install` | Install or update an app from a zipped app bundle (`body: Blob`). |
| `uninstallApp` | — | `app-engine:apps:delete` | Uninstall an app by `id`. |
| `searchActions` | `SearchAppActionList` | `app-engine:apps:run` | Search actions of installed apps by whitespace-separated terms (matched against app/action name & description; ≤ 256 chars). |

Install/uninstall are asynchronous — inspect the returned `status` / pending-operation fields.

## Example

```ts
import { appEngineRegistryAppsClient } from "@dynatrace-sdk/client-app-engine-registry";

const stub = await appEngineRegistryAppsClient.installApp({ body: new Blob() });
```
