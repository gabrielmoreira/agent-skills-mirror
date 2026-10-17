# Commit through the DevOps Center API

Request, response and polling were verified live (dev org + Core hub, work item `WI-000001`, status In Progress). Error codes, no-access preflight behaviour and git-path sync behaviour come from source, not live tests. Use this when the user supplies a dev org alias and the changes are already deployed in that org.

## Contents

- Orgs involved
- Preflight
- Request
- Response and errors
- Polling
- Confirming on the hub
- Differences from the git path
- Known limits

## Orgs involved

| Org | Role | Used for |
|-----|------|----------|
| Dev org | Holds the metadata; where DX Inspector runs | `doceConnectionType`, `commitChanges`, `DevopsRequestInfo` polling |
| Hub org | Holds projects, work items, component lists | `sf devops work-item list`, status checks, confirming the commit |

The dev org reaches the hub server-side through the `ALMDevOpsCenterHub` named credential. The CLI cannot use that credential, so the hub needs its own `sf` login (`--target-org <hub-alias>`).

## Preflight

```bash
sf api request rest "/services/data/v67.0/connect/devops/doceConnectionType" --target-org <dev-org>
```

The commit API is used at `v67.0`; the commands are not tied to the skill's `minApiVersion`. Treat a non-zero exit or an error body as failure for every `sf api request rest` call here (the no-access case was not tested live).

- 2xx with `{"isCore": true, "isManagedPackage": false}` — Core hub; proceed. This call itself goes through the hub named credential, so success is evidence the credential works.
- A failed call (no DX Inspector access, endpoint missing) — fall back to the git path.
- `isCore` not `true`, or `isManagedPackage: true` — this reference covers the Core path only; use the git path.
- Optional: `sf data query --target-org <dev-org> -q "SELECT DeveloperName FROM NamedCredential WHERE DeveloperName = 'ALMDevOpsCenterHub'"`.

## Request

`POST /services/data/v67.0/connect/devops/commitChanges` on the **dev org**. The REST body is the input object itself. Wrapping it in `{"commitChanges": {...}}` fails with `JSON_PARSER_ERROR: Unrecognized field "commitChanges"`.

```json
{
  "isCommitCore": "true",
  "workItemId": "<hub work item id>",
  "projectId": "<hub project id>",
  "workItemName": "WI-000001",
  "workItemLink": "<url of the work item in the hub>",
  "commitMessage": "<message>",
  "changes": [
    {"fullName": "MyClass", "type": "ApexClass", "operation": "modify"}
  ]
}
```

- `isCommitCore` is the **string** `"true"`. The Core path needs it together with a non-empty `workItemId`.
- `operation` is `add`, `modify` or `delete`.
- Rebuild the request body for **every** commit. Write it to a temp file (`mktemp`) and delete it afterwards, so a later `git add` cannot pick it up.
- Do not send `dataChanges` or `vcsRepo` (data deployment and the Managed Package path are out of scope).

```bash
BODY=$(mktemp)   # write the JSON above to "$BODY"; rm "$BODY" when done
sf api request rest "/services/data/v67.0/connect/devops/commitChanges" \
  --method POST --body @"$BODY" --target-org <dev-org>
```

Pass the file with the `@` prefix (`--body @<file>`); without it the CLI treats the path as the literal body.

## Response and errors

Success: `{"reqId": "<uuid>", "status": "SUCCESS"}` — this means the request was accepted, not that the commit finished.

Request-level failures (e.g. `JSON_PARSER_ERROR` from a malformed body) come back as real HTTP errors: surface them and stop. Business failures are returned as HTTP 200 with `status: "ERROR"` and `reqId` holding `CODE:message`. Codes seen in source: `WORKITEM_NEVERED`, `VCS_NOT_AUTHENTICATED`, `COMMIT_API_FAILURE_CORE`, `COMMIT_API_FAILURE_CLIAAS`, `COMMIT_PAYLOAD_ERROR_*`, `COMMIT_DATA_VALIDATION_ERROR`, `COMMIT_FAILED`. Always check `status`, not the exit code alone.

Server-side preconditions: work item not closed (`WORKITEM_NEVERED`); status New, In Progress, In Review or Ready to Promote; the VCS connection is authenticated.

## Polling

There is no status resource. Query the dev org:

```bash
sf data query --target-org <dev-org> --json \
  -q "SELECT Status, Message, ErrorDetails, RequestCompletionDate FROM DevopsRequestInfo WHERE RequestToken = '<reqId>'"
```

- Terminal `Status` values: `SUCCESS` (not `COMPLETED`) and `ERROR`. A loop that waits for `COMPLETED` never exits.
- The commit observed took about 10 seconds. Poll every 10 seconds, deadline 12 minutes.
- `IN_PROGRESS` comes first; `RequestToken` equals the POST `reqId`.
- At the deadline the request is stuck (worker timeout is 10 minutes and the status can stay in progress). Report it and do not retry automatically; a retry is a new request that could race the stuck one.
- `Message`/`ErrorDetails` carry the failure text when `Status` is `ERROR`.

## Confirming on the hub

```bash
sf data query --target-org <hub-org> --json \
  -q "SELECT Name, CommitReference, CreatedDate FROM WorkItemComponentList WHERE WorkItemId = '<id>' ORDER BY CreatedDate"
```

A new row with a `CommitReference` hash confirms the commit was recorded. A new row with a null `CommitReference` (seen with unchanged components) means the request succeeded but nothing new was committed; report "nothing to commit", not a successful commit. An In Progress work item stays In Progress; a New one is expected to move to In Progress (not tested live).

## Differences from the git path

| | Git path | API path |
|---|---|---|
| Committed content | Files on local disk | Components named in `changes`, retrieved from the dev org |
| Orgs | Hub only | Dev org for the commit, hub for lookup and confirmation |
| Author | The user's git identity | `DevOps Center <noreply@salesforce.com>` |
| Branch | Work item `branch` field | The work item name (`WI-000001`); the live test could not distinguish this from `branch` |
| Hub records | Created when the hub's external-commit sync picks the push up (only for In Progress, In Review, Ready to Promote) | Created immediately |
| Result tracking | git exit codes | `reqId` plus `DevopsRequestInfo` |

## Known limits

- No rebase before push: a concurrent push to the same branch can make the commit fail as non-fast-forward.
- An empty change set can finish `SUCCESS` with nothing committed.
- A failed attempt can leave an orphaned component list on the hub.
