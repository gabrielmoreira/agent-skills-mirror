---
name: configuring-test-provider
description: "Configures an available test provider (e.g. Apex Unit Tests, Code Analyzer, Flow Tests, Provar) on a DevOps Center pipeline via the Connect API, after explicit user confirmation, so the provider's test suites become available for assignment to pipeline stages. Takes a pipelineId and a testProviderId. Use this skill when a provider is available on the pipeline but not yet configured and the user wants to enable it. TRIGGER when: the user wants to configure, enable, set up, or add a test provider on a pipeline, or wants a not-yet-configured provider's suites to become available. DO NOT TRIGGER when: re-syncing an already-configured provider to pick up new suites (use syncing-test-providers), or assigning existing suites to a stage (use managing-suite-assignments)."
metadata:
  version: "1.0"
  minApiVersion: "67.0"
---

# Configuring a Test Provider

Configures an available test provider on a DevOps Center pipeline, making its test suites available for assignment to pipeline stages.

**Confirmation required:** Yes — explicit confirmation before the provider is configured.

## Prerequisites

Load `checking-devops-prerequisites` first — Prerequisites 1–4 (org login, Agentforce DX plugin, DevOps Center org auth, pipeline identified). Prerequisite 5 (stage) is **not** required: providers are configured at the pipeline level, not the stage level.

| Variable | Source |
|---|---|
| `doce-org-alias` | Established in Prerequisite 1 |
| `pipelineId` | Identified in Prerequisite 4 (pipeline selection) |
| `testProviderId` | Resolved by fetching the pipeline's test providers (below) |

---

## Step 1 — Fetch test providers to resolve the provider ID

Get all test providers for the pipeline so you can resolve the `testProviderId` and confirm which providers are still available to configure:

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

- **Only an Available provider can be configured.** If the pipeline has no available providers, report that and stop — do NOT fabricate a provider or ID.

### If the named provider is already Configured

Do **not** present the confirmation gate and do **not** POST to the configure endpoint (Steps 2–3) — that would create a duplicate `DevopsPipelineTestProvider`. Instead:

1. State plainly that the provider is already configured, including its synced suite count and last-sync time if returned (e.g. *"Flow Tests is already configured on `<pipelineName>` with 3 suites synced (last sync 2026-06-23)."*).
2. Diagnose the user's actual goal and redirect **by name**:
   - If the user says the provider's **suites don't appear when assigning tests to a stage**, this is a **stage-assignment gap, not a provider-configuration gap** — the suites already exist at the pipeline level; they just need to be linked to the stage. Redirect to **`managing-suite-assignments`**.
   - If the user expects **newly created suites** that aren't yet synced, redirect to **`syncing-test-providers`** (re-sync via `POST /connect/devops/sync`) to pull them in.
3. Do not loop back to configuring — finish cleanly after the explanation and redirect.

## Step 2 — Confirmation gate

**Required — do not call the API before the user confirms.**

> "I'll configure `<testProviderName>` on the `<pipelineName>` pipeline. This will make its suites available for assignment to stages. Confirm?"

Do not proceed until the user gives an affirmative response.

## Step 3 — Configure the provider

On confirmation, call the configure endpoint with the provider ID:

```bash
sf api request rest \
  "/services/data/v67.0/connect/devops/pipeline/<pipelineId>/testProvider" \
  --method POST \
  --body '{"testProviderId": "<testProviderId>"}' \
  --target-org <doce-org-alias>
```

## On success

> "Provider `<testProviderName>` is now configured on the `<pipelineName>` pipeline. Its suites are available for assignment to stages."

Newly configured suites can then be assigned to stages with `managing-suite-assignments`.

---

## Critical gotcha

This `POST .../pipeline/<pipelineId>/testProvider` endpoint **creates a new provider configuration record** (`DevopsPipelineTestProvider`). Use it ONLY to configure a provider for the first time. To re-sync an already-configured provider for new suites, use `syncing-test-providers` (`POST /connect/devops/sync`) — calling this configure endpoint on an already-configured provider produces **duplicate** `DevopsPipelineTestProvider` records.

## Error Handling

Never expose raw API error messages, stack traces, or JSON payloads to the user. Map response status codes to plain-language messages:

| Status | User-facing message |
|---|---|
| 400 | "The request was invalid. Check that the provider ID and pipeline ID are correct." |
| 403 | "You don't have permission to configure test providers on this pipeline." |
| 404 | "The pipeline or test provider was not found." |
| 409 | "That provider appears to already be configured on this pipeline. To pick up new suites, re-sync it instead." |
| 500 | "A server error occurred. Try again in a few minutes." |

---

## Related skills

- **`checking-devops-prerequisites`** — loaded first to establish org and pipeline context.
- **`syncing-test-providers`** — once a provider is configured, use this to re-sync it later and pull in newly added suites.
- **`managing-suite-assignments`** — after configuring a provider, use this to assign or map its suites to a pipeline stage.
- **`recommending-devops-tests`** — to recommend which of the newly available suites to run.
