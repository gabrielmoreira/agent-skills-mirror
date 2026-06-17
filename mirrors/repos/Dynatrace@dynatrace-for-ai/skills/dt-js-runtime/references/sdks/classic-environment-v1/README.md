# Classic Environment v1 (`@dynatrace-sdk/client-classic-environment-v1`)

> Env: ✅ Server runtime
> Status: current (many resources superseded by [classic-environment-v2](../classic-environment-v2/README.md))

Client for the Dynatrace Classic Environment API v1: OneAgent/ActiveGate deployment, synthetic monitors, RUM JavaScript, and user-session queries (USQL).

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `clusterConfigClient` / `clusterVersionClient` | `getClusterVersion` | Cluster identity & version |
| `deploymentClient` | `downloadLatestAgentInstaller` | OneAgent/ActiveGate/BOSH/Lambda installer downloads |
| `oneAgentOnAHostClient` | host agent status & config | OneAgent-on-host info |
| `syntheticMonitorsClient` | CRUD | Synthetic monitor management |
| `rumJavaScriptTagManagementClient` | RUM tag delivery | RUM JS tag |
| `rumUserSessionsClient` | USQL execution | User-session query language |

Full method/type detail (per client): [deployment.md](deployment.md), [oneagent-on-host.md](oneagent-on-host.md), [rum-javascript-tags.md](rum-javascript-tags.md), [rum-user-sessions.md](rum-user-sessions.md), [synthetic.md](synthetic.md), [cluster.md](cluster.md) · [types.md](types.md).

## Required scopes

- Various `environment-api:*` scopes plus specific viewer/management permissions per operation.

## Example

```ts
import { deploymentClient } from "@dynatrace-sdk/client-classic-environment-v1";

const installer = await deploymentClient.downloadLatestAgentInstaller({
  osType: "windows",
  installerType: "default",
});
```

## Notes

- Prefer v2 where a resource exists there.
- Early-adopter/preview operations may change incompatibly; new enum constants may be added without a version bump.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-classic-environment-v1/
