# HTTP Fetch — Internal & External

How to make HTTP calls from the runtime. Quotas in [limits-and-restrictions.md](limits-and-restrictions.md); the `fetch` API itself is listed in [apis-and-modules.md](apis-and-modules.md).

## Internal Dynatrace API (relative path)

Call the platform's own APIs with a **relative path** — no host, no auth header. The runtime injects credentials automatically, and relative paths **bypass the outbound allowlist**.

```js
const res = await fetch("/platform/classic/environment-api/v2/settings/objects?...");
const data = await res.json();
```

Prefer the typed `@dynatrace-sdk/*` clients (see [sdk.md](sdk.md)) over hand-rolled relative fetches when a client exists.

## External URL with credential vault

For external hosts, pull secrets from the credential vault rather than hardcoding them:

```ts
import { credentialVaultClient } from "@dynatrace-sdk/client-classic-environment-v2";

const creds = await credentialVaultClient.getCredentialsDetails({ id: "CREDENTIALS_VAULT-..." });
const auth = `Basic ${btoa(`${creds.username}:${creds.password}`)}`;
const res = await fetch("https://api.example.com/...", { headers: { Authorization: auth } });
```

See [classic-environment-v2](sdks/classic-environment-v2/README.md) for the credential vault client.

## Outbound allowlist

The tenant controls which external hosts are reachable via the setting `builtin:dt-javascript-runtime.allowed-outbound-connections`. If an external `fetch` **silently fails**, the host is most likely not allowlisted.

Inspect the current allowlist:

```dtctl
dtctl get settings --schema "builtin:dt-javascript-runtime.allowed-outbound-connections" -o json
```

Only full-URL fetches are gated by the allowlist; relative `/platform/...` paths are not.
