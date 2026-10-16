# Simple Deploy Request Body

> **Scope:** the skill sends metadata only. `datachanges` is documented here for reference but is deferred; do not send it from this skill yet.

Source of truth: `ISimpleDeployResource` / `SimpleDeployInputRepresentation` (Connect) and the cliaas `validator/schema.ts`. Connect forwards `requestBody` to cliaas unchanged, so cliaas validation errors surface as a 400.

## Envelope (Connect input)

| Field | Type | Notes |
|---|---|---|
| `namedCredential` | string | `DevopsEnvironment.NamedCredential`. Must be bound to `targetEnvironmentId`. |
| `targetEnvironmentId` | string | `DevopsEnvironment.Id`. Scopes validate and quick-deploy tracking. |
| `requestBody` | object | The deploy payload below. |
| `headerTargetInstanceURL`, `headerTargetAccessToken` | string | Raw-token alternative to `namedCredential`. **Do not use from this skill.** |
| `components` | array | Deprecated and ignored. Do not send. |

## `requestBody`

| Field | Type | Notes |
|---|---|---|
| `changes[]` | `{fullName, type, operation}` | All three required and non-blank. `operation` is `add`, `modify`, or `delete`. Map anything else (dependency, manual, manifest) to `modify`. |
| `datachanges` | object (deferred) | `{ "objectsList": { "<ObjectApiName>": { "fields": [{"name": "..."}], ... } } }`. Each object needs at least one field. |
| `isCheckDeploy` | boolean | `true` = validate only (alias `checkOnly`). Default `false`. |
| `testOptions` | `{level, tests[]}` | `level`: `NoTestRun`, `RunSpecifiedTests`, `RunLocalTests` (default), `RunAllTestsInOrg`. `tests` must list the tests for `RunSpecifiedTests`; send an empty array otherwise. Legacy `testLevel` + `tests` also accepted. |
| `isQuickDeploy` | boolean | `true` = deploy a prior validation. Default `false`. |
| `checkDeployIdentifier` | string | `0Af` id (15 or 18 chars). Required with `isQuickDeploy`. |
| `metadataLookups` | map<string,string> | Optional. |

### `datachanges.objectsList.<Object>` entry

`fields[]` (required, `{name, ...}`), plus optional `relatedObjects`, `duplicateCheck` (field names for dedupe), `recordIds`, `filters`, `formats`, `numRecords`, `externalIdField` (upsert/match key, for example `External_Account_Id__c`). Unknown keys pass through. Remove duplicate fields by `name` before sending.

## Mode matrix

| Mode | `changes` | `datachanges` | `testOptions` | Other |
|---|---|---|---|---|
| deploy | required (this skill) | deferred | optional | The API itself allows data-only; this skill sends metadata. |
| validate | **required** | ignored (stripped, remembered for quick deploy) | optional | `isCheckDeploy: true`. |
| quickDeploy | **forbidden** | forbidden | **forbidden** | `isQuickDeploy: true` + `checkDeployIdentifier`. |

Test level default: Production targets need tests to complete a deploy, so use `RunLocalTests`; sandbox and scratch-like targets use `NoTestRun`. An explicit user choice always wins.

## Examples

Metadata deploy:

```json
{
  "namedCredential": "QA_Sandbox_1PJSB...",
  "targetEnvironmentId": "1QeSB0000004T3R0AU",
  "requestBody": {
    "changes": [
      {"fullName": "AccountService", "type": "ApexClass", "operation": "modify"},
      {"fullName": "Account.Tier__c", "type": "CustomField", "operation": "add"}
    ],
    "testOptions": {"level": "NoTestRun", "tests": []}
  }
}
```

Validate only:

```json
{ "namedCredential": "Prod", "targetEnvironmentId": "1Qe...",
  "requestBody": { "isCheckDeploy": true,
    "changes": [{"fullName": "AccountService", "type": "ApexClass", "operation": "modify"}],
    "testOptions": {"level": "RunLocalTests", "tests": []} } }
```

Quick deploy:

```json
{ "namedCredential": "Prod", "targetEnvironmentId": "1Qe...",
  "requestBody": { "isQuickDeploy": true, "checkDeployIdentifier": "0AfXXXXXXXXXXXXXXX" } }
```
