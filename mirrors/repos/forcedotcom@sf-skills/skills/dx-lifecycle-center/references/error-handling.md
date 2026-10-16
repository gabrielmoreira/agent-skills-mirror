# Simple Deploy Error Handling

Connect errors arrive as `CODE:message`. Read the code, explain the cause in plain language, state the fix, and stop. Never retry in a loop and never fabricate a `requestId` or result.

| Code / symptom | Cause | Fix |
|---|---|---|
| 403 / no access | User lacks `userHasDevopsSimpleDeployApiAccess`. | Ask an admin for DX Inspector deploy access. |
| `TARGET_ORG_NAMED_CREDENTIAL_NOT_AUTHENTICATED` | Named credential exists but OAuth was never completed. | Complete the OAuth flow for the environment (`connect-org.md`), then retry. |
| `TARGET_ORG_SESSION_EXPIRED` | Credential returned 401 or 403. | Reconnect the target org (`connect-org.md`), then retry. |
| `DEPLOY_TARGET_ORG_CONNECTION_FAILED` with `Bad_OAuth_Token` | The environment's stored OAuth token is stale or revoked (seen live). | Reconnect that environment (`connect-org.md`); try another environment only if the user asks. |
| `DEPLOY_TARGET_ORG_CONNECTION_FAILED` with an HTML error page | The target org is gone or unreachable (for example an expired scratch org; seen live). The message carries a full HTML page. | Say the target org is unreachable or expired. Do not paste the HTML. |
| `DEPLOY_TARGET_ORG_CONNECTION_FAILED` | Credential service or target unreachable, or "Target environment does not match the named credential". | Re-resolve the pair from the same `DevopsEnvironment` row (`list-orgs.md`). |
| `VALIDATION_REQUIRES_METADATA` | Validate run with no `changes`. | Add at least one metadata component. |
| `QUICK_DEPLOY_NOT_AVAILABLE` / `QUICK_DEPLOY_NOT_DEPLOYABLE` | No successful, still-valid validation for this target. | Re-run validate, then quick deploy the new `0Af` id. |
| `QUICK_DEPLOY_ALREADY_DONE` / `QUICK_DEPLOY_ALREADY_IN_PROGRESS` | The validation was already used or is running. | Check status of the earlier request instead. |
| `QUICK_DEPLOY_VALIDATE_ONLY_MUTUALLY_EXCLUSIVE` | Both `isCheckDeploy` and `isQuickDeploy` set. | Send only one. |
| `VALIDATE_QUICK_DEPLOY_FEATURE_NOT_ENABLED` | Validate/quick deploy kill switch is closed. | Use a plain deploy, or ask the platform team. |
| 400 with a Zod message | cliaas schema rule (see `request-body.md`): blank `fullName`/`type`/`operation`, bad `testOptions`, `changes` with quick deploy, bad `0Af` id. | Fix the named field and resubmit once. |
| `DEPLOY_UNKNOWN_ERROR` | Unexpected server error. | Report the message; do not retry blindly. |
| Status `FAILED` (or `DevopsRequestInfo` `ERROR`) | Deploy ran and failed. | Show the failed `step` and the reason: `errorDetail` (component and test failures, coverage shortfall) when present, else `activityMessage`. Details in `deploy.md`, Step 7. |
| Status `NOT_FOUND` | Unknown id, or older than ~2 days. | Confirm the id; resubmit only if the user asks. |
