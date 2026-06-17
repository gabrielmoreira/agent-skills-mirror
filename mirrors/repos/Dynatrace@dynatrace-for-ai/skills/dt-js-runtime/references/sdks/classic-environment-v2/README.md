# Classic Environment v2 (`@dynatrace-sdk/client-classic-environment-v2`)

> Env: ✅ Server runtime
> Status: current (supersedes v1 — see [classic-environment-v1](../classic-environment-v1/README.md) for not-yet-migrated resources)

Client for the Dynatrace Environment API v2: settings, tokens, ActiveGates, events, audit logs, and the **credential vault**.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `settingsObjectsClient` | `getSettingsObjects`, `postSettingsObjects`, `putSettingsObjectByObjectId`, `deleteSettingsObjectByObjectId` | Read/write settings objects (paginated — see Notes) |
| `credentialVaultClient` | `getCredentialsDetails`, `getCredentials`, `postCredentials` | Stored credentials (certificates, tokens, username/password) |
| `accessTokensApiTokensClient` | `getApiTokens`, `postApiToken` | API token CRUD |
| `activeGatesClient` | `getAllActiveGates` | List/inspect ActiveGates |
| `eventsClient` / `businessEventsClient` | `createEvent`, `ingest` | Custom & CloudEvent business-event ingestion |
| `auditLogsClient` | `getLogs` | Environment activity log |
| `attacksClient` | `getAttacks` | Security attack queries |

## Full detail by domain (34 clients)

This SDK exposes **34 clients**, grouped by domain into the files below (each client is its own section). Exact per-method OAuth scopes are on the canonical page; the general pattern is `<area>:<resource>:read|write` (e.g. `settings:objects:read`, credential-vault scopes, `entities:read`, `metrics:read`/`:write`, `events:ingest`, `slo:read`/`:write`, `securityProblems:read`).

| File | Clients |
|---|---|
| [access-tokens.md](access-tokens.md) | `accessTokensApiTokensClient`, `accessTokensActiveGateTokensClient`, `accessTokensAgentTokensClient`, `accessTokensTenantTokensClient` |
| [activegates.md](activegates.md) | `activeGatesClient`, `activeGatesActiveGateGroupsClient`, `activeGatesAutoUpdateConfigurationClient`, `activeGatesAutoUpdateJobsClient` |
| [credential-vault.md](credential-vault.md) | `credentialVaultClient` |
| [settings.md](settings.md) | `settingsObjectsClient`, `settingsSchemasClient`, `settingsManagementZonesClient` |
| [events.md](events.md) | `eventsClient`, `businessEventsClient` |
| [logs.md](logs.md) | `logsClient` |
| [metrics.md](metrics.md) | `metricsClient`, `metricsUnitsClient` |
| [entities.md](entities.md) | `monitoredEntitiesClient`, `monitoredEntitiesCustomTagsClient`, `monitoredEntitiesMonitoringStateClient` |
| [problems.md](problems.md) | `problemsClient` |
| [security.md](security.md) | `securityProblemsClient`, `attacksClient`, `davisSecurityAdvisorClient` |
| [synthetic.md](synthetic.md) | `syntheticLocationsNodesAndConfigurationClient`, `syntheticNetworkAvailabilityMonitorsClient`, `syntheticOnDemandMonitorExecutionsClient`, `syntheticHttpMonitorExecutionsClient` |
| [slo.md](slo.md) | `serviceLevelObjectivesClient` |
| [network-zones.md](network-zones.md) | `networkZonesClient` |
| [extensions.md](extensions.md) | `extensions_2_0Client` |
| [audit-logs.md](audit-logs.md) | `auditLogsClient` |
| [releases-and-rum.md](releases-and-rum.md) | `releasesClient`, `rumManualInsertionTagsClient` |
| [types.md](types.md) | Types + enums (large) |

## Required scopes

- Per-operation, e.g. `settings:objects:read` / `settings:objects:write`, `environment:roles:manage-settings`, credential-vault scopes. Each method's docs list the exact scope.

## Example — credential vault for an external fetch

```ts
import { credentialVaultClient } from "@dynatrace-sdk/client-classic-environment-v2";

const creds = await credentialVaultClient.getCredentialsDetails({ id: "CREDENTIALS_VAULT-..." });
const auth = `Basic ${btoa(`${creds.username}:${creds.password}`)}`;
```

See [fetch.md](../../fetch.md) for the full external-fetch pattern.

## Notes — `settingsObjectsClient` pagination gotcha

When a response has a `nextPageKey`, pass it as the **sole** parameter — omit `schemaIds`, `fields`, `pageSize`, and everything else. Mixing `nextPageKey` with any other param causes `400: Constraints violated`.

```ts
const items = [];
let nextPageKey;
do {
  const page = await settingsObjectsClient.getSettingsObjects(
    nextPageKey
      ? { nextPageKey }
      : { schemaIds: "builtin:my-schema", fields: "scope,value", pageSize: 500 }
  );
  items.push(...(page.items ?? []));
  nextPageKey = page.nextPageKey;
} while (nextPageKey);
```

The spread trick `{ schemaIds: "...", ...(nextPageKey ? { nextPageKey } : {}) }` looks equivalent but sends **both** params on page 2 — the API rejects it. The same rule applies to other paginated settings clients (e.g. app-settings).

- Business-event ingestion: 5 MiB max payload per request.
- Early-adopter/preview operations may change incompatibly; new enum values may appear without a version bump — handle unknown values gracefully.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-classic-environment-v2/
