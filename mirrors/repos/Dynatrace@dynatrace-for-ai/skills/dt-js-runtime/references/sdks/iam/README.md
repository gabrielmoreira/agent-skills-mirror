# Identity & Access Management (`@dynatrace-sdk/client-iam`)

> Env: ✅ Server runtime
> Status: current

Query users, groups, and service users across organizational levels.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `usersAndGroupsClient` | `getActiveUserFromOrganizationalLevel`, `getActiveUsersForOrganizationalLevel`, `getActiveUsersForOrganizationalLevelPost` | Active users |
| `usersAndGroupsClient` | `getAvailableServiceUsers` | Service users usable by the execution user |
| `usersAndGroupsClient` | `getVisibleGroupsForAccount`, `getVisibleGroupsForAccountPost` | Visible groups |

Types: `RestUserPublic`, `RestGroupPublic`, `ServiceUserDto`; responses include pagination (`nextPageKey`, `totalCount`).

Full method/type detail: [usersAndGroupsClient.md](usersAndGroupsClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Concepts

- Queries are scoped to an **organizational level** via `levelType` + `levelId` (e.g. account or environment). Authorization is based on the calling user's assignment to the account associated with that level; for environment level the user must be assigned to the account the environment belongs to (no explicit env permissions needed).
- Read-only SDK — view users/groups/service users; no user/group mutation here.

## Required scopes

- `iam:users:read` / `iam:groups:read`.

## Notes

- Filter strings: min 3, max 320 chars.
- Throttling applies; responses include retry information.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-iam/
