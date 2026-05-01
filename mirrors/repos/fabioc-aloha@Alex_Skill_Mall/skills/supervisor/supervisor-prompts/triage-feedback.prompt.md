---
description: "Supervisor: Triage an item in feedback/inbox/ — categorize, deduplicate, route, and record"
mode: agent
lastReviewed: 2026-04-30
---

# /triage-feedback

Run the [feedback-triage](../skills/feedback-triage/SKILL.md) skill on items in `feedback/inbox/`.

If the user names a specific item, triage that one. Otherwise, sweep all unprocessed items in `feedback/inbox/`.

For each item:

1. Categorize (`bug` / `friction` / `feature-request` / `success` / `framework`)
2. Deduplicate against `feedback/inbox/` and `decisions/` from the last 90 days
3. Assign severity (`critical` / `high` / `medium` / `low`)
4. Route (Edition fix / Mall change / AlexMaster escalation)
5. Record in `decisions/curation-log.md` with M/S classification

For items routed to **Edition fix**, draft the PR description but do not open the PR yet — the user reviews first.

For items routed to **AlexMaster escalation**, write the escalation stub but do not transmit yet.

Always run the trimmed [act-pass](../instructions/act-pass.instructions.md). Triage is medium-stakes when it determines whether something escalates.
