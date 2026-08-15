---
name: github-actions-debugger
description: "Maps a failed GitHub Actions run onto the matching `.github/workflows` job and step, then emits a unified YAML diff for secrets env maps, deprecated action majors, runner/runtime skew, cache keys, flaky timeouts, or permissions. Use when CI is red, a step points at the wrong cause, or a deprecated action/runtime must be upgraded. Not for greenfield pipeline design, local git without an Actions run, or merging a pull request."
version: 1.0.1
category: devops
risk: safe
source: community
source_type: community
date_added: "2026-06-25"
tags: [github-actions, ci-cd, devops, debugging, workflows]
tools: [claude, cursor, gemini, antigravity]
---

## When to Use
- Use when a GitHub Actions workflow fails unexpectedly and the error log is long, obscure, or misleading.
- Use when debugging dependency mismatch errors, missing secrets, caching issues, or runner environment problems in CI.
- Use to optimize slow pipelines by identifying bottlenecks in workflow steps.
- Use to update and modernize deprecated actions or workflow syntax.

## Prerequisites
- Access to the failing GitHub Actions run log (exported as a raw text file or pasted directly).
- Access to the workflow definition file (`.github/workflows/*.yml`).
- **CRITICAL SAFETY REQUIREMENT:** All sensitive credentials, secrets, tokens, private keys, and internal system paths must be redacted from the logs before pasting or uploading them.

## Procedure
1. **Log Ingestion & Redaction:** Request the raw GitHub Actions log. Verify that no live secrets (e.g., `YOUR_KEY`, tokens) are present. If unmasked secrets are found, halt and request redaction.
2. **Context Mapping:** Open the corresponding `.github/workflows/*.yml` file. Locate the failing job and step identified in the log.
3. **Root Cause Analysis:** Analyze the error message against the workflow definition. Check for:
   - Missing `env:` mappings for secrets (e.g., `DEPLOY_API_KEY: ${{ secrets.DEPLOY_API_KEY }}`).
   - Deprecated action versions (e.g., `actions/checkout@v2`).
   - OS or runtime version mismatches (e.g., Node.js 16 vs 20).
   - Flaky tests, timeout limits, or syntax errors in bash scripts within `run:` blocks.
4. **Resolution Proposal:** Output a unified diff showing the exact changes needed in the `.yml` file or underlying scripts to resolve the issue.

## Pitfalls
- **Ignoring Transient Failures:** Mistaking temporary network dropouts or registry downtime (e.g., npm or pip install errors) for actual code or configuration bugs. Always check if a rerun succeeds before attempting heavy changes.
- **Hardcoding Tokens:** Fixing authentication errors by hardcoding secrets or API tokens directly into the YAML files instead of utilizing GitHub Secrets (`${{ secrets.SECRET_NAME }}`).
- **Overlooking Caching Side Effects:** Forgetting that outdated cache keys can keep corrupt dependencies loaded. If dependency installation is failing, try running a job with actions caching bypassed.
- **Deprecated Runtimes:** Many failures are caused by deprecated runtime versions (e.g., Node.js 16) in older third-party actions. Always recommend upgrading to the latest major versions (e.g., `v4`).
- **Insufficient Permissions:** Ensure the workflow has the correct `permissions:` block if it's attempting to write to the repository, packages, or deploy environments.

## Verification
- **Dry-Run Mode:** When recommending modifications to bash script steps inside workflows, suggest adding flags like `--dry-run` or staging execution to prevent unintended side effects in downstream environments during debugging.
- **Reproducibility Check:** If a test fails in CI but passes locally, investigate environment differences such as timezone, headless browser state, memory limits, or parallel execution race conditions.
- **Execution Validation:** The skill cannot execute the GitHub action itself to test the fix. Validation requires pushing the proposed fix to the repository and triggering a workflow run to confirm the pipeline passes.
