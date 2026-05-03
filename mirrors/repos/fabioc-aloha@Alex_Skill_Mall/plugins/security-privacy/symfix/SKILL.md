---
type: skill
lifecycle: stable
inheritance: inheritable
name: symfix
description: Classify and remediate CodeQL alerts with the SymFix workflow using staged changelog updates
tier: standard
applyTo: '**/*symfix*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# SymFix Workflow — Instructions

> Scope: Classify and remediate the requested CodeQL alert set with SymFix

## Required Inputs

- CodeQL job ID
- Alert information.

## Goal

Use SymFix to classify and remediate the requested alert set with the minimum safe repository diff.

## Tool naming note

SymFix runtimes may expose tool names that differ slightly from the labels used in this guide.

- If the exact tool name in this guide exists, use it.
- If the exact name does not exist, use the closest matching SymFix tool for the same action.
- Keep the action order from this guide unchanged even when the runtime uses different tool names.

## Pre-flight checks

Before Step 1, confirm all of the following:

- the SymFix MCP service is reachable
- the CodeQL job ID is available
- the staging directory parent location is writable
- the repository checkout for the selected mode is ready

## Workflow Steps

### Step 1: Staging directory creation

- Create a directory `symfix_staging_directory` in the user profile directory and use it as the staging directory.
- If the directory already exists, proceed to Step 2.

### Step 2: Get the list of CodeQL alerts to fix

- Use the SymFix tool `SymFixGetCodeQLAlerts` to get the list of CodeQL alerts.
- If you are not able to locate the alert, the job ID may be incorrect. Re-run input resolution to get the correct job ID.

### Step 3: Process each alert

For each alert in the list, follow these sub-steps in order:

1. Use the SymFix tool `SymFixUpdateAlert` to set up the code graph for the alert and update the alert line numbers.
2. Pass a changelog ranges list into `SymFixUpdateAlert`. For the first alert, use an empty list. For each subsequent alert, reuse the accumulated changelog ranges returned by earlier applied fixes.
3. Use the updated alert for every following sub-step.
4. Use the SymFix tool `SymFixGenerateAlertClassificationPrompt` to get the alert classification prompt. Follow the prompt instructions. Use the SymFix code navigation tools `GetContainingDefinition`, `GetDefinition`, `GetMethodCallers`, `GetMethodCallees`, `GetReferences`, and `GetImports` as needed.
5. Use the SymFix tool `SymFixValidateAlertClassificationResponse` to validate your response to the alert classification prompt.
6. If your analysis classifies the alert as a false positive, skip the remaining sub-steps for that alert and move to the next alert.
7. Use the SymFix tool `SymFixGenerateAlertFixPrompt` to get the fix generation prompt. Follow the prompt instructions.
8. Use the SymFix tool `SymFixValidateAndApplySearchReplaceChangelog` to validate and apply the SearchReplace changelog that is your response to the fix prompt. This tool takes the earlier changelog ranges list as input, updates it with the current fix, and returns the updated list.

## Expected per-alert outcome

For each alert, end the SymFix phase in exactly one of these states before moving on:

- `FIXED`
- `FALSE_POSITIVE`
- `FAILED`

Record the state for every alert so the final output can report exact per-alert results.

## Requirements

- Follow these steps exactly as provided.
- Do not skip any step.
- Do not perform unrelated analysis outside of the provided workflow.
- If any step fails, report the failure and stop further processing.
- Keep output chat messages to the minimum necessary to report progress and results.