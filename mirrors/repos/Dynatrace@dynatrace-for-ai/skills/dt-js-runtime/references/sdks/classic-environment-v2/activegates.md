# ActiveGate clients

Inspect ActiveGates, groups, and manage auto-update config/jobs. Import from `@dynatrace-sdk/client-classic-environment-v2`.

## `activeGatesClient`

| Method | Purpose |
|---|---|
| `getAllActiveGates` | List ActiveGates (filterable by module, OS, type, version, …). |
| `getOneActiveGateById` | Get a single ActiveGate by id. |

## `activeGatesActiveGateGroupsClient`

| Method | Purpose |
|---|---|
| `getActiveGateGroups` | List ActiveGate groups. |

## `activeGatesAutoUpdateConfigurationClient`

| Method | Purpose |
|---|---|
| `getGlobalAutoUpdateConfigForTenant` | Get tenant-global auto-update config. |
| `putGlobalAutoUpdateConfigForTenant` | Update tenant-global auto-update config. |
| `validateGlobalAutoUpdateConfigForTenant` | Validate tenant-global config. |
| `getAutoUpdateConfigById` | Get per-ActiveGate auto-update config. |
| `putAutoUpdateConfigById` | Update per-ActiveGate config. |
| `validateAutoUpdateConfigById` | Validate per-ActiveGate config. |

## `activeGatesAutoUpdateJobsClient`

| Method | Purpose |
|---|---|
| `getAllUpdateJobList` | List all auto-update jobs. |
| `getUpdateJobListByAgId` | List update jobs for an ActiveGate. |
| `getUpdateJobByJobIdForAg` | Get one update job. |
| `createUpdateJobForAg` | Create an update job. |
| `validateUpdateJobForAg` | Validate an update job. |
| `deleteUpdateJobByJobIdForAg` | Delete an update job. |
