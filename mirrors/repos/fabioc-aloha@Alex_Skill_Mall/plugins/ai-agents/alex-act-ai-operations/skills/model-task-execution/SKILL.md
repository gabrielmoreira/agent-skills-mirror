---
name: model-task-execution
description: "Execute an approved model task plan through Microsoft Foundry, Hugging Face, or ElevenLabs and record provider evidence. Use after model-router emits a valid plan and the user wants to run it, monitor jobs, cancel work, download outputs, or apply an approved fallback."
lastReviewed: 2026-08-11
---

# Model Task Execution

Execute exactly what the user approved. A valid plan is necessary but not
sufficient: explicit user consent must appear in the current conversation.

## Preflight

1. Validate the plan against the model-task plan schema.
2. Compute a SHA-256 plan hash over canonical JSON and show it with the consent
   summary.
3. Confirm `consent.required` and `consent.status` match the operation.
4. Show provider, model, operation, transmitted inputs, retention evidence,
   cost estimate status, maximum approved cost, and fallbacks.
5. Check whether the selected provider/model requires a credential. If it does,
   verify only that provider-native login or the named host environment variable
   is available; never print or persist its value. If missing, stop and route
   to `setup-ai-operations`.
6. Ask for explicit user consent. Do not invoke a paid, externally visible,
   state-changing, or data-transmitting provider tool before approval.
7. Store the approved plan hash in memory for this execution only. Do not write
   credentials, raw secrets, or private inputs to an execution manifest.

## Material-Change Gate

Any change to the **provider, model, data boundary, or cost ceiling** invalidates
the plan hash and requires **renewed consent**. The same applies when a fallback
adds a new provider, transmits additional data, or changes output visibility.

## Dispatch

1. Mark the next step `approved`.
2. Invoke only the provider tool named in the step.
3. Capture the provider job ID, exact model/version, start time, and immediate
   response.
4. Poll status through the provider's own read operation. Do not submit a second
   job merely because the first is slow.
5. If the provider fails, stop and report the error. Apply only an already
   approved fallback whose plan hash still matches.
6. Download or attach outputs before provider retention removes them.
7. Mark the terminal status and capture duration, available usage/cost evidence,
   output identifiers, and any data-retention note.

## Cancellation

Cancellation is separately permitted when the user asks to stop active work or
when an approved maximum cost or duration guard fires. Use the provider's
cancellation tool and verify the terminal status.

## Execution Manifest

Return a sanitized manifest containing:

- Plan ID and approved plan hash
- Provider, model, operation, and provider job ID
- Start and completion timestamps
- Terminal status
- Actual usage or cost evidence when the provider returns it
- Output paths or provider URLs
- Fallbacks used
- Errors and cancellations

Never persist API keys, bearer tokens, raw private prompts, or uploaded file
contents.

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Treat plan creation as consent | Ask after showing the final plan. |
| Switch providers silently | Re-plan and obtain renewed consent. |
| Retry by creating a second paid job | Poll the existing job first. |
| Claim actual cost from an estimate | Label estimates and provider usage separately. |
| Record credentials for reproducibility | Record provider IDs and evidence, never secrets. |
| Ask for every API key before execution selection | Set up only the selected provider through native login, the host environment, or approved secret storage. |

## Would Revise If

Revise immediately if any paid or data-transmitting call occurs without
explicit consent. Revisit by **2026-11-11** if provider status models cannot be
represented without unsafe retries or if execution manifests omit load-bearing
provider evidence twice.
