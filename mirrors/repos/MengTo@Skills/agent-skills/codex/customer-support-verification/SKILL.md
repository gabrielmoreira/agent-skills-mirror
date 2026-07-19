---
name: customer-support-verification
description: Verify customer support work against the applicable runbook, draft-safety, evidence, mutation, and commit-scope requirements. Use after every Gmail/customer support triage, billing/cancellation/refund/account/access investigation, support handoff, or draft-review task before the final response; also use when the user asks to verify support work against a runbook, checklist, skill, or requirements.
---

# Customer Support Verification

## Overview

Use this skill as the final gate for support work. It turns the user's support rules into an explicit verification report before the agent says the task is done.

## Required Inputs

Collect these before verifying:

- The applicable support `RUNBOOK.md` or user-provided support requirements.
- Any product-specific `AGENTS.md`, support runbook, or billing/access runbook that was used.
- The customer request, Gmail thread/draft ids, and current draft body when present.
- The evidence gathered from local docs/source/admin/read-only data.
- A list of every external action taken, including Gmail, Stripe, Firebase, Supabase, browser, deploy, or commit actions.
- For any subscription refund, the verified subscription id, proof that it was canceled before the refund, the post-cancellation read-back, and the refund/charge/PaymentIntent read-back. If no payment was collected, record that no refund was created and verify the subscription plus any open invoice or retry were resolved instead.
- The hourly unresolved follow-up status: created, blocked, or not applicable, plus the planned question/content. It must ask the request owner whether the case is resolved, summarize what the customer wants, and say what the request owner should do next.
- The duplicate-thread check: searches performed by customer, Gmail thread id, draft id, latest message id, and issue; the canonical thread id; and any stale duplicate thread ids that were archived/closed.

If any input is missing, mark the related check `UNKNOWN`, explain why, and do not treat the task as fully verified.

## Verification Checklist

Evaluate each item as `PASS`, `FAIL`, or `UNKNOWN`.

1. Runbook loaded: The applicable support `RUNBOOK.md` or user-provided support requirements were read or already active in the current context.
2. Product routing: The product/account owner was identified from trusted local/source/admin evidence, or the uncertainty was kept explicit.
3. Original and draft shown: The handoff includes the customer original or safe summary, the current Gmail draft body, and the recommended response or "no revision needed".
4. Draft safety: No email was sent, archived, deleted, marked read, or externally changed unless the user explicitly approved that action.
5. Untrusted email handling: Email links, inline images, attachments, and customer claims were not treated as trusted evidence.
6. Mutation safety: No Stripe, Firebase, Supabase, account, subscription, invoice, refund, deploy, or billing mutation was performed without explicit approval.
7. Refund cancellation order: Every subscription refund canceled the verified subscription first, read back the canceled subscription state, then created the refund and read back the refund, charge, PaymentIntent, profile, and subscription. Never leave a subscription active after refunding it. If Stripe collected $0, do not create a fake refund; verify cancellation and void or otherwise stop any open invoice or retry instead.
8. Evidence over promise: Customer-facing wording does not promise cancellation, refund, no charge, access repair, deletion, or future prevention until verified by trusted systems and, when needed, read-back.
9. Source/admin surfaces: The handoff names the exact docs/source/admin surfaces checked and the exact surfaces still needing verification.
10. Draft recommendation freshness: If new evidence makes the existing draft stale, the handoff says it needs revision and provides safe replacement wording.
11. Hourly unresolved follow-up: A recurring hourly follow-up was created, or a blocker was stated. It must proactively ask the request owner whether the case is resolved, summarize what the customer wants, say what the request owner should do next, and continue every hour until the request owner confirms the case is resolved.
12. Duplicate-thread hygiene: Existing Codex support threads were searched before creating or linking a handoff. A single canonical thread remains for the same unresolved customer issue, and stale duplicate threads were archived/closed or the blocker was stated.
13. Browser rule: If browser work was needed, the workspace's approved browser policy was followed.
14. Commit discipline: If files were changed, only narrow task files were staged/committed and final commit scope was checked. If no git repo or no changes exist, state that clearly.
15. Final answer readiness: The final response includes a concise verification summary with any `FAIL` or `UNKNOWN` items surfaced, not hidden.

## Failure Handling

- If an item is `FAIL`, fix the work before finalizing whenever possible.
- If a `FAIL` cannot be fixed without user approval or missing access, stop and report the blocker.
- If an item is `UNKNOWN`, say what evidence would turn it into `PASS`.
- Never downgrade `FAIL` to `UNKNOWN` just because the result is inconvenient.
- If a subscription refund was created before verified cancellation, mark the task `FAIL` and resolve the still-active subscription before treating the support case as complete.

## Output Format

Use a compact table or bullets:

```text
Verification against support requirements:
- PASS: Runbook loaded - checked RUNBOOK.md.
- PASS: Draft safety - draft remains unsent.
- PASS: Hourly unresolved follow-up - hourly check-in created until the request owner confirms resolved.
- UNKNOWN: Stripe-live invoice state - not checked because no approval for billing action/read pass.
- PASS: Commit discipline - committed only docs/support/example.md as abc1234.
```

End with the next approval gate when one remains, such as: `Needs user approval before Stripe action or sending the draft.`
