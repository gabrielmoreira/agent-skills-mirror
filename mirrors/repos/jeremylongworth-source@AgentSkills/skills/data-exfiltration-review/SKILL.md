---
name: data-exfiltration-review
description: Review agent skills for data exfiltration risk. Use when Codex is asked to inspect a skill for unauthorized file reads, secret access, network sends, hidden output channels, logging leaks, or inappropriate data movement.
license: MIT
---

# Data Exfiltration Review

## Core Workflow

1. Identify what data the skill can access directly or through scripts, MCP
   tools, host permissions, examples, or references.
2. Identify sinks: network calls, external APIs, logs, generated files, shell
   output, issue comments, customer messages, and copied reports.
3. Check for hidden or unnecessary data movement, broad globbing, credential
   reads, encoded payloads, or unexplained uploads.
4. Verify the workflow uses least privilege and only accesses data needed for
   the user-requested artifact.
5. Recommend removals, redaction, allowlists, read-only defaults, and approval
   gates.
6. Report residual risk and safe-use conditions.

## Safety Rules

- Do not inspect or print secrets unless the user explicitly asks for a secrets
  audit and a safe handling path exists.
- Do not approve outbound network behavior without a clear purpose.
- Do not allow skills to collect broad local data unrelated to the task.

## Deliverable Shape

For exfiltration reviews, provide:

- Data sources
- Data sinks
- Unnecessary or hidden data movement
- Secrets and sensitive data concerns
- Least-privilege recommendations
- Approval conditions
- Pass/warn/fail/block recommendation

## References

- Read `references/data-exfiltration-review-checklist.md` when reviewing data
  access, output, logs, scripts, or network behavior.
