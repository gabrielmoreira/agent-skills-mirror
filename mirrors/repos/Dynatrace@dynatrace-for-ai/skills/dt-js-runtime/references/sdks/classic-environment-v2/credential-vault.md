# `credentialVaultClient`

Stored credentials (certificates, tokens, username/password) — commonly used to authenticate external `fetch` calls. Import:

```ts
import { credentialVaultClient } from "@dynatrace-sdk/client-classic-environment-v2";
```

| Method | Returns | Purpose |
|---|---|---|
| `createCredentials` | created credentials | Create a credentials entry. |
| `listCredentials` | credentials list | List credentials (filter by `type`). |
| `getCredentials` | credentials | Get credentials metadata by id. |
| `getCredentialsDetails` | credentials details | Get full credentials details by id (username/password, token, certificate). |
| `getCredentialsDetailsList` | details list | Get details for multiple credentials. |
| `updateCredentials` | — | Update a credentials entry. |
| `removeCredentials` | — | Delete a credentials entry. |

Scopes: credential-vault read/write scopes (see canonical page per method).

## Example — credential vault for external fetch

```ts
import { credentialVaultClient } from "@dynatrace-sdk/client-classic-environment-v2";

const creds = await credentialVaultClient.getCredentialsDetails({ id: "CREDENTIALS_VAULT-..." });
const auth = `Basic ${btoa(`${creds.username}:${creds.password}`)}`;
const res = await fetch("https://api.example.com/...", { headers: { Authorization: auth } });
```

See [../../fetch.md](../../fetch.md) for the full external-fetch pattern.
