# List connected orgs (Operation A)

Shows the orgs that can receive a deploy: the **DX Inspector environments** stored in the source org. The same lookup resolves a target the user names (alias, URL, org id, or name) for Deploy and Connect.

The targets are the DX Inspector environments, **not** the orgs authorized on this machine. Never build the list from `sf org list` or local aliases: an org can be authorized locally yet not connected, and the reverse.

## 1. Run the resolver

```bash
bash scripts/resolve-environment.sh <source-org-alias> [identifier]
```

`<source-org-alias>` is the alias the user named, else the default org from `sf org display --json`. Pass `identifier` exactly as the user gave it. It accepts:

| The user gives | Example |
|---|---|
| Environment name | `MySandbox` |
| Local `sf` alias | `my-sandbox` |
| Org URL (My Domain, setup, or lightning host) | `https://mydomain--mysandbox.sandbox.my.salesforce.com` |
| Org id (15 or 18 characters) | `00D5g000001AbCd` |

The script runs `SELECT Id, Name, NamedCredential, OrgType, IsExpired, OrgUrl, OrgIdentifier FROM DevopsEnvironment ORDER BY Name` and prints one JSON document:

- `source`: `alias`, `username`, `orgId`, `instanceUrl` of the source org.
- `environments[]`: each row with `state` of `selectable`, `expired`, or `unauthenticated`.
- With an identifier: `matchStatus`, `matches[]`, `match`, and `sourceMatched`.

The Lifecycle Center org's own row is never returned (see `hub-org.md`).

## 2. If the script fails

It exits `1` and prints one reason on stderr. Say only what the reason supports:

| Script says | Tell the user | Then |
|---|---|---|
| `DevOps Center not enabled or no access` | "DX Inspector isn't enabled for this org or user, so there are no environments to list or deploy to. An admin needs to enable it." | Stop. Do not run another query, do not fall back to `sf org list`, and do not offer a deploy. |
| `query failed, not an enablement problem` | The error in plain words (often an expired session). | Tell them to reconnect the source org (in Builder Central use the Reconnect prompt; running the CLI locally, `sf org login web --alias <alias>`), then try again. Never say DX Inspector is disabled. |
| `unexpected query result` | The environment lookup returned something unreadable. | Report that and stop. Do not guess a list. |
| `cannot read source org` | The source org is not authorized on this machine. | Ask which org they build in. If it is not authorized, reconnect it the same way as above, then start again. |
| `jq required` | `jq` is missing from the environment. | Report it and stop. |

## 3. Read the match (only when an identifier was passed)

**First check `sourceMatched`.** If it is `true`, the identifier is the source org (this also covers a row with `isSource: true`): say it cannot be its own deploy target and ask for a different org. Ignore `matchStatus` in that case.

| `matchStatus` | Do |
|---|---|
| `matched` and `state` is `selectable` | Use that row. Confirm it back with name, URL, and org id. |
| `matched` and `state` is `unauthenticated` | Connect never finished. Offer to finish it (`connect-org.md`, repair path). |
| `matched` and `state` is `expired` | Retired or replaced by an environment swap. Not deployable and not repairable: pick another or connect a new one. |
| `ambiguous` | Show `matches` and ask which one. |
| `not-connected` | Not in DX Inspector. Offer to connect it (`connect-org.md`). If the identifier was an alias, URL, or org id, carry it into the connect flow so only the missing inputs are asked. |
| `none-requested` | No target named: show the list (section 4). |

When the identifier is an alias that is not connected, `sf org display --target-org <alias> --json` gives its URL, which sets the `orgType` by the host table in `connect-org.md`. Use the alias as the suggested environment name (letters only) and still ask the user to confirm the type if the host does not decide it.

## 4. Show the list

A numbered table with the columns `#`, `Name`, `Type`, `URL`, `Org id`, `Status`:

- One row per entry in `environments[]`, then the **source org** as the last row. A row with `isSource: true` is the source org: show it once, as that last row, never as a selectable environment.
- Always include the `Org id` column. Write `—` for any empty cell.
- The source org's `Type` is always `—`: `source` carries no org type, so never infer one.
- Never show row ids or credential names.
- If several rows share a name, tell them apart by URL.

| Row | Status column |
|---|---|
| `state = selectable` | Selectable |
| `state = expired` | Retired or replaced |
| `state = unauthenticated` | Not authenticated |
| The source org | `<alias> (current org, source)`. It is the source, so it is **not** a deploy target. If the user picks it, explain that and ask for another. |

Example:

| # | Name | Type | URL | Org id | Status |
|---|---|---|---|---|---|
| 1 | MySandbox | Sandbox | mydomain--mysandbox.sandbox.my.salesforce.com | 00D5g000001AbCd | Selectable |
| 2 | OldSandbox | Sandbox | mydomain--old.sandbox.my.salesforce.com | — | Retired or replaced |
| 3 | my-alias *(current org, source)* | — | mydomain.my.salesforce.com | 00D5g000001XyZw | — |

End the list with exactly this sentence and nothing after it:

> Want to deploy to an org that isn't listed? I can help you connect a new one.

Do not add any other offer, summary, or follow-up.

| Situation | Reply instead of the table |
|---|---|
| No environments | "No environments are connected to DX Inspector in `<source-org-alias>` yet." Then the closing sentence. |
| Every environment is expired or unauthenticated | "None of the connected environments can accept a deploy right now: <names and reasons>." Then the closing sentence. |

## 5. Current-org details

When the user asks about the current org itself, answer from `source`: alias, username, URL, and org id. Add nothing else.

## Carrying a chosen row forward

For Deploy, take `id` → `targetEnvironmentId` and `namedCredential` → `namedCredential` from the **same** row. The API rejects a mismatched pair. Never deploy to a row whose `state` is not `selectable`.
