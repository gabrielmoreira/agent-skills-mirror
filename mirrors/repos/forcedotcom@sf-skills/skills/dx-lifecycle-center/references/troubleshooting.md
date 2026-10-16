# Troubleshooting: DX Inspector org connection

Explain each problem to the user in plain language. Never echo raw JSON or tokens. Do not retry a failing call in a loop.

| Symptom | Likely cause | Fix |
|---|---|---|
| Deploy POST returns `TARGET_ORG_ENVIRONMENT_CREATION_FAILED:Invalid org type` | `orgType` is not valid | Use `PRODUCTION`, `SANDBOX`, or `ORGFARM`. `envName` must contain at least one letter. |
| Hub POST returns `400 namedCredentialType is not supported.` | Typo or wrong case in the type | Use one of `ORG_TO_ORG`, `ORG_TO_SANDBOX_ORG`, `ORG_TO_ORGFARM_ORG`. |
| POST returns 403 or "insufficient access" | User lacks DevOps API access in the dev org | Assign the DevOps Center permissions in the dev org. The user needs *Customize Application*. |
| POST succeeds but `redirectUrl` is empty | Setup or URL generation failed on the server; the errors were swallowed | **Hub:** check status; if the EC or NC exists, re-POST once. **Deploy:** the row already exists, so do not POST again (it would insert a second row). Get a fresh link with `GET /connect/devops/environment/<id>`, or delete the row (below) and start over. If it is still empty, tell the user setup failed server-side and stop. |
| Login page is `login.salesforce.com` but the target is a sandbox, or the reverse | Wrong `namedCredentialType` | **Deploy:** `DELETE /connect/devops/environment/<id>` (removes the NC, EC and row), then POST again with the correct `orgType`. **Hub:** delete the NC and EC in Setup, then re-run with the correct type. |
| OAuth page shows an error or loops back | The browser has no dev-org session, or the user denied access | Ask the user to sign in to the dev org in that browser, then give a fresh link (deploy: `GET /connect/devops/environment/<id>`; hub: re-run Step 1). Do not run `sf org open`. |
| EC principal still `NotConfigured` after the user says they're done | The login didn't finish, or a different Salesforce user completed it | The token is per user, so the same dev-org user must do the login. Give a fresh link (deploy: `GET /connect/devops/environment/<id>`; hub: re-run Step 1). |
| User can't use the credential | Missing **Access DevOps Center Named Credentials** (`AccessDevOpsCenterNamedCredentials`) | Assign that permission set to the user in the dev org. |
| Hub PATCH returns `404 Named credential does not exist` | POST never created the NC, or the name differs | Re-check the exact name (case-sensitive) and re-run Step 1. |
| Hub PATCH returns `DOCE_CONNECTION_UPDATE_FAILED` | The `userinfo` callout failed, usually because the OAuth token is missing or expired | Confirm the principal is `Configured`, then re-run Steps 1–4. The user's saved DX Inspector selections were cleared, so they must pick them again. |
| Deploy environment PATCH returns `TARGET_ORG_AUTHENTICATION_STATUS_CHECK_FAILED` (401/403), `TARGET_ORG_AUTHENTICATION_TIMEOUT` (408/504), or `TARGET_ORG_UNKNOWN_ERROR` (includes "Environment record not found" and "does not have a named credential") | The login is missing or expired, the callout timed out, or the id is wrong | Confirm the principal is `Configured` and the `id` is the POST's. Give a fresh link and PATCH once. Do not loop. |
| PATCH `calloutUrl` or `orgUrl` is still a login host | Unexpected `userinfo` response | Stop and report. Do not hand the NC to deploy. |
| Hub mode: `doceConnectionType` fails | The hub user lacks **DevOps Center User** | Assign the permission set in the Lifecycle Center org, then re-run the check. |
| Deploy: `TARGET_ORG_SESSION_EXPIRED` or `Bad_OAuth_Token` | The target refresh token was revoked or expired. A stale token is not visible in the environment list; it only shows at deploy time | Repair: fresh link from `GET /connect/devops/environment/<id>`, user logs in, PATCH once. |
| Environment shows `unauthenticated` (empty `OrgUrl` or `OrgIdentifier`) | The connect never finished: POST ran but login or PATCH did not | Same repair: fresh link, login, PATCH once. Do not POST again. |
| `Doce Hub Environment` row is missing from the environment list | By design: the resolver drops the hub row (credential `ALMDevOpsCenterHub`, empty `OrgUrl`) because it is the Lifecycle Center hub, not a deploy target | Nothing to repair. To deploy to that org, connect it as a deploy target with the Environment API. |
| Environment shows `expired` | `IsExpired` is set when an environment is retired or replaced by a swap; it is not an OAuth expiry | Do not repair it. Pick another environment or connect a new one. |

## Starting over

**Deploy target:** `DELETE /connect/devops/environment/<id>` (confirm with the user first). It removes the Named Credential, External Credential, and the `DevopsEnvironment` row. Do not delete credentials in Setup: that leaves an orphaned row that still looks selectable.

**Hub:** delete both the **Named Credential** and the **External Credential** named `ALMDevOpsCenterHub` in Setup → Named Credentials (and the External Credentials tab), and run the skill again.

For the hub, the **Remove DevOps Center Connection** option in DX Inspector does the same teardown.
