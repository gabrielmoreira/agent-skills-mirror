---
name: syncing-test-providers
description: "Re-syncs a configured DevOps Center test provider on a pipeline to pick up new test suites, via the Connect API sync endpoint, after explicit user confirmation. Takes a pipelineId and one or more testProviderIds and triggers an asynchronous re-sync so newly added suites become available for assignment. Use this skill when a test provider (e.g. Apex Unit Tests, Code Analyzer, Flow Tests, Provar) has had suites added since it was last configured and the user wants those suites to show up in DevOps Center. TRIGGER when: the user wants to re-sync a test provider, pull in new suites from a provider, refresh a provider's suite list, or says assigned suites are missing/out of date for a configured provider. DO NOT TRIGGER when: configuring a provider for the first time (that creates a new DevopsPipelineTestProvider configuration), or assigning/mapping existing suites to a stage (use managing-suite-assignments)."
metadata:
  version: "1.0"
  minApiVersion: "67.0"
---

# Syncing Test Providers

Re-syncs a configured test provider on a DevOps Center pipeline so that suites added to the provider since it was last configured become available for assignment to stages.

**Confirmation required:** Yes — explicit confirmation before the sync is triggered.

## Prerequisites

Load `checking-devops-prerequisites` first — Prerequisites 1–4 (org login, Agentforce DX plugin, DevOps Center org auth, pipeline identified). Prerequisite 5 (stage) is **not** required: providers are synced at the pipeline level, not the stage level.

| Variable | Source |
|---|---|
| `doce-org-alias` | Established in Prerequisite 1 |
| `pipelineId` | Identified in Prerequisite 4 (pipeline selection) |
| `testProviderId` | Resolved by fetching the pipeline's test providers (below) |

---

## Step 1 — Fetch test providers to resolve the provider ID

Get all test providers configured on the pipeline so you can resolve the `testProviderId` and confirm the provider name with the user:

```bash
sf api request rest \
  "/services/data/v67.0/connect/devopstesting/pipeline/<pipelineId>/testProviders?status=all" \
  --target-org <doce-org-alias>
```

Each provider entry includes `testProviderId`, `testProviderName`, and a status (Configured vs. Available). Present a short summary grouped by status:

```text
Test providers for <pipelineName>:

✓ Configured:
- Code Analyzer (63 suites)
- Apex Unit Tests (5 suites)

Available (not yet configured):
- Flow Tests
```

- **Only a Configured provider can be synced.** If the user names an *Available* (not-yet-configured) provider, explain it must be configured first — this skill does not configure providers.
- If the pipeline has no configured providers, report that and stop — do NOT fabricate a provider or ID.

## Step 2 — Confirmation gate

**Required — do not call the API before the user confirms.**

> "I'll re-sync `<testProviderName>` on the `<pipelineName>` pipeline to pick up any new suites. Confirm?"

Do not proceed until the user gives an affirmative response.

## Step 3 — Trigger the sync

On confirmation, call the sync endpoint with the provider ID(s) and pipeline ID:

```bash
sf api request rest \
  "/services/data/v67.0/connect/devops/sync" \
  --method POST \
  --body '{
    "testProviderIds": ["<testProviderId>"],
    "pipelineId": "<pipelineId>"
  }' \
  --target-org <doce-org-alias>
```

`testProviderIds` is a list — multiple configured providers can be synced in one call.

## On success

> "Provider `<testProviderName>` sync started. The operation is running asynchronously — new suites will be available shortly."

The sync runs asynchronously; newly synced suites can then be assigned to stages with `managing-suite-assignments`.

---

## Critical gotcha

**Do NOT use** `POST /connect/devops/pipeline/<pipelineId>/testProvider` to sync — that endpoint **creates a new provider configuration** and will result in duplicate `DevopsPipelineTestProvider` records. Sync only via `POST /connect/devops/sync`.

## Error Handling

Never expose raw API error messages, stack traces, or JSON payloads to the user. Map response status codes to plain-language messages:

| Status | User-facing message |
|---|---|
| 400 | "The sync request was invalid. Check that the provider ID and pipeline ID are correct." |
| 403 | "You don't have permission to sync test providers on this pipeline." |
| 404 | "The pipeline or test provider was not found." |
| 500 | "A server error occurred. Try again in a few minutes." |

---

## Related skills

- **`checking-devops-prerequisites`** — loaded first to establish org and pipeline context.
- **`configuring-test-provider`** — use to configure an available provider for the first time; this skill only re-syncs already-configured providers.
- **`managing-suite-assignments`** — after a sync surfaces new suites, use this to assign or map them to a pipeline stage.
- **`recommending-devops-tests`** — to recommend which of the newly synced suites to run.
