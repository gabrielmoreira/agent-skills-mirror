---
name: github-issue-creator
description: "Turns pasted errors, screenshots, voice notes, and rough tickets into dated GitHub issue markdown covering environment, numbered repro, expected vs actual, evidence, and severity. Trigger when the user asks to file, create, or log a GitHub issue from unstructured bug input. Do not use for feature RFCs, design docs, or pull-request writeups."
version: 1.0.1
risk: unknown
source: community
date_added: "2026-02-27"
---

## Overview

Transform messy, unstructured input—pasted error logs, voice dictation, screenshots, support notes—into clean, actionable GitHub issue markdown files. Each issue includes a one-line summary, environment, numbered reproduction steps, expected vs. actual behavior, error details, visual evidence references, severity-rated impact, and additional context.

## When to Use

Use this skill when the user provides unstructured bug input and wants a structured GitHub issue. Trigger keywords and signals:

- Pasted stack traces, error messages, or HTTP status codes
- Voice dictation describing a bug ("so I was trying to… and it just failed")
- Screenshots or GIFs of a failure
- Support tickets, Slack threads, or rough notes needing triage
- Explicit requests: "create an issue", "file a bug", "log this on GitHub", "write up this bug"

Do **not** use this skill for feature requests, RFCs, or design docs—only bug/defect reports.

## Prerequisites

1. A local repo root where the `/issues/` directory will be created or already exists.
2. On Windows host (PowerShell), the repo root is typically `~\agent-skills\library\github-issue-creator` or the active project folder.
3. If the user references a screenshot or GIF, confirm the file path or attachment name before referencing it inline.
4. If required inputs are missing (product/service, at least one repro step, or expected behavior), stop and ask for clarification.

## Procedure

### 1. Gather and parse raw input

1. Collect all raw material from the user: error text, voice dictation transcript, screenshot paths, conversation context.
2. Extract facts buried in casual language. Voice notes often contain the real sequence of events behind informal phrasing.
3. Infer missing context from conversation or memory only when the user explicitly references it ("same project", "the dashboard", "that error from before"). Otherwise, use placeholders.

### 2. Determine environment and impact

1. Identify **Product/Service**, **Region/Version**, and **Browser/OS** from the input or conversation context.
2. If unknown, insert `[UNKNOWN]` or `[REGION]` placeholders—never fabricate.
3. Assign severity using the rubric below.

### 3. Assign severity

| Severity | Criteria |
|----------|----------|
| **Critical** | Service down, data loss, security issue |
| **High** | Major feature broken, no workaround |
| **Medium** | Feature impaired, workaround exists |
| **Low** | Minor inconvenience, cosmetic |

### 4. Write the issue file

1. Create the `/issues/` directory at the repo root if it does not exist.
   ```powershell
   New-Item -ItemType Directory -Path ".\issues" -Force
   ```
2. Name the file using the convention `YYYY-MM-DD-short-description.md`.
   ```powershell
   $date = Get-Date -Format "yyyy-MM-dd"
   $slug = "agent-deployment-silent-failure"
   New-Item -ItemType File -Path ".\issues\$date-$slug.md" -Force
   ```
3. Write the issue using the exact output template below.

### 5. Output Template

```markdown
## Summary
[One-line description of the issue]

## Environment
- **Product/Service**:
- **Region/Version**:
- **Browser/OS**: (if relevant)

## Reproduction Steps
1. [Step]
2. [Step]
3. [Step]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Details
```
[Error message/code if applicable]
```

## Visual Evidence
[Reference to attached screenshots/GIFs]

## Impact
[Severity: Critical/High/Medium/Low + brief explanation]

## Additional Context
[Any other relevant details]
```

### 6. Placeholder sensitive data

Replace any potentially sensitive values with bracketed placeholders:

- `[PROJECT_NAME]`
- `[USER_ID]`
- `[API_KEY]`
- `[TENANT_ID]`
- `[EMAIL]`

Never include live secrets, tokens, or credentials in the issue file.

### 7. Reference attachments inline

For screenshots or GIFs, reference them inline using the format:

```
![Description](path/or/attachment/name.png)
```

If the file path is unknown, write `[See attached: filename.png]` and flag it for the user to attach manually.

## Examples

### Example A — Voice dictation input

**Input**:
> so I was trying to deploy the agent and it just failed silently no error nothing the workflow ran but then poof gone from the list had to refresh and try again three times

**Output file**: `issues/2026-02-27-agent-deployment-silent-failure.md`

```markdown
## Summary
Agent deployment fails silently - no error displayed, agent disappears from list

## Environment
- **Product/Service**: Azure AI Foundry
- **Region/Version**: westus2

## Reproduction Steps
1. Navigate to agent deployment
2. Configure and deploy agent
3. Observe workflow completes
4. Check agent list

## Expected Behavior
Agent appears in list with deployment status, errors shown if deployment fails

## Actual Behavior
Agent disappears from list. No error message. Requires page refresh and retry.

## Impact
**High** - Blocks agent deployment workflow, no feedback on failure cause

## Additional Context
Required 3 retry attempts before successful deployment
```

### Example B — Error paste input

**Input**:
> Error: PERMISSION_DENIED when publishing to Teams channel. Code: 403. Was working yesterday.

**Output file**: `issues/2026-02-27-teams-publish-permission-denied.md`

```markdown
## Summary
403 PERMISSION_DENIED error when publishing to Teams channel

## Environment
- **Product/Service**: Copilot Studio → Teams integration
- **Region/Version**: [REGION]

## Reproduction Steps
1. Configure agent for Teams channel
2. Attempt to publish

## Expected Behavior
Agent publishes successfully to Teams channel

## Actual Behavior
Returns `PERMISSION_DENIED` with code 403

## Error Details
```
Error: PERMISSION_DENIED
Code: 403
```

## Impact
**High** - Blocks Teams integration, regression from previous working state

## Additional Context
Was working yesterday - possible permission/config change or service regression
```

## Pitfalls

1. **Fabricating environment details**: Never invent region, version, or browser/OS. Use `[UNKNOWN]` placeholders and ask the user.
2. **Missing repro steps**: If the input does not contain enough detail for at least 2 numbered repro steps, stop and ask the user for clarification.
3. **Including live secrets**: Error logs sometimes contain API keys, tokens, or connection strings. Always scrub these to `[REDACTED]` or the appropriate placeholder before writing the file.
4. **Vague severity**: Do not default to "Medium" when unsure. Map severity strictly to the rubric. If impact is unclear, ask the user.
5. **Wrong file location**: Issues must go in `/issues/` at the repo root, not in a subfolder or the user's home directory. On Windows, confirm the working directory with `Get-Location` before writing.
6. **Inconsistent naming**: Always use `YYYY-MM-DD-short-description.md`. Do not use spaces or uppercase in the slug portion.
7. **Over-writing existing issues**: Use `New-Item` without `-Force` on the file if you want to avoid clobbering; check first with `Test-Path`.
8. **Treating output as validated**: The generated issue is a draft. It does not substitute for environment-specific validation, testing, or expert review.

## Verification

After writing the issue file, verify:

1. **File exists and is named correctly**:
   ```powershell
   Get-ChildItem .\issues\*.md | Select-Object Name
   ```
   Confirm the filename matches `YYYY-MM-DD-short-description.md`.

2. **All required sections are present**:
   ```powershell
   $content = Get-Content ".\issues\YYYY-MM-DD-short-description.md" -Raw
   $sections = @("## Summary","## Environment","## Reproduction Steps","## Expected Behavior","## Actual Behavior","## Error Details","## Visual Evidence","## Impact","## Additional Context")
   foreach ($s in $sections) { if ($content -notmatch [regex]::Escape($s)) { Write-Host "MISSING: $s" } }
   ```

3. **No live secrets leaked**:
   ```powershell
   $content = Get-Content ".\issues\YYYY-MM-DD-short-description.md" -Raw
   if ($content -match '(?i)(sk-[a-z0-9]{20,}|Bearer\s+[A-Za-z0-9\.\-_]+|password\s*[:=]\s*\S+)') { Write-Host "WARNING: Possible secret detected" }
   ```

4. **Repro steps are numbered**: Confirm at least 2 numbered items exist under `## Reproduction Steps`.

5. **Severity is set**: Confirm the Impact section contains one of `Critical`, `High`, `Medium`, or `Low`.

## Related skills

- **github-pr-template**: For structuring pull request descriptions once a fix is ready.
- **bug-triage-labeler**: For assigning labels and priority after issue creation.
