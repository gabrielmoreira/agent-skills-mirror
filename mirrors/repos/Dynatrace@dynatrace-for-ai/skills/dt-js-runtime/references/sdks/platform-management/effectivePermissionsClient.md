# `effectivePermissionsClient`

Import:

```ts
import { effectivePermissionsClient } from "@dynatrace-sdk/client-platform-management-service";
```

| Method | Returns | Purpose |
|---|---|---|
| `resolveEffectivePermissions` | `EffectivePermissions` | Resolve whether an identity holds a set of permissions in a context. Body is a `ResolutionRequest` (`permissionContext` + `permissions` as `SinglePermissionRequest[]`). |

## Example

```ts
import { effectivePermissionsClient } from "@dynatrace-sdk/client-platform-management-service";

const result = await effectivePermissionsClient.resolveEffectivePermissions({
  body: { /* ResolutionRequest */ },
});
```
