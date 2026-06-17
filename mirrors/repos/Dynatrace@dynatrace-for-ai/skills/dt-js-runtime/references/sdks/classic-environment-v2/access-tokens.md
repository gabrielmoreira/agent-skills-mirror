# Access-token clients

Manage API tokens, ActiveGate tokens, agent tokens, and tenant token rotation. Import from `@dynatrace-sdk/client-classic-environment-v2`.

## `accessTokensApiTokensClient`

| Method | Purpose |
|---|---|
| `createApiToken` | Create an API token (with scopes). |
| `listApiTokens` | List API tokens. |
| `getApiToken` | Get an API token by id. |
| `lookupApiToken` | Look up the token metadata for a token secret. |
| `updateApiToken` | Update an API token. |
| `deleteApiToken` | Delete an API token. |

## `accessTokensActiveGateTokensClient`

| Method | Purpose |
|---|---|
| `createToken` | Create an ActiveGate token. |
| `listTokens` | List ActiveGate tokens. |
| `getToken` | Get an ActiveGate token by id. |
| `revokeToken` | Revoke an ActiveGate token. |

## `accessTokensAgentTokensClient`

| Method | Purpose |
|---|---|
| `getAgentConnectionToken` | Get the agent connection token. |

## `accessTokensTenantTokensClient`

| Method | Purpose |
|---|---|
| `startRotation` | Start tenant token rotation. |
| `finishRotation` | Finish tenant token rotation. |
| `cancelRotation` | Cancel tenant token rotation. |
