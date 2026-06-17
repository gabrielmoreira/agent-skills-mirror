# `usersAndGroupsClient`

Query users, groups, and service users at an organizational level. Import:

```ts
import { usersAndGroupsClient } from "@dynatrace-sdk/client-iam";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getActiveUserFromOrganizationalLevel` | `RestUserPublic` | `iam:users:read` | Get one active user by `uuid` at a level (`levelType`, `levelId`). |
| `getActiveUsersForOrganizationalLevel` | `RestUserPublicListResponse` | `iam:users:read` | List active users at a level; filter by `partialString` and/or `uuid` (at least one required); ordered by name then surname. |
| `getActiveUsersForOrganizationalLevelPost` | `RestUserPublicListResponse` | `iam:users:read` | Same as above but POST — provide a body list of UUIDs and/or `partialString`. |
| `getAvailableServiceUsers` | `SearchResult` | `iam:service-users:use` | List service users at a level usable by the execution user (environment queries run in account context). |
| `getVisibleGroupsForAccount` | `RestGroupPublicListResponse` | `iam:groups:read` | List visible groups at a level; filter by `partialGroupName` and/or `uuid` (at least one required). |
| `getVisibleGroupsForAccountPost` | `RestGroupPublicListResponse` | `iam:groups:read` | Same as above but POST — provide body with `groupUuids` list and/or `partialGroupName`. |

## Example

```ts
import { usersAndGroupsClient } from "@dynatrace-sdk/client-iam";

const users = await usersAndGroupsClient.getActiveUsersForOrganizationalLevel({
  levelType: "account",
  levelId: "...",
  partialString: "jane",
});
```
