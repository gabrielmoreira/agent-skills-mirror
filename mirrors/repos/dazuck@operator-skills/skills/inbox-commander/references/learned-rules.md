# Learned Rules

This file is auto-updated when user overrides classifications. Load at start of each triage run.

## Override Patterns

Format: `[DATE] [Original Tier] → [User Action] | Pattern: [what to match] | New Rule: [how to classify]`

<!--
Example entries (will be added by the skill during runs):

- [2026-01-14] Tier 3 HIGH → User archived | Pattern: from:*@srsacquiom.com, subject:"shareholder" | New Rule: Tier 1 auto-archive (informational notices)
- [2026-01-14] Tier 1 auto-archive → User escalated | Pattern: from:*@vercel.com, subject:"invoice" | New Rule: Tier 3 (invoices ≠ receipts)
-->

## Sender Reclassifications

<!--
Senders moved between tiers based on user behavior:

- [DATE] newsletters@example.com: Tier 2 → Tier 4 (user never reads, suggest unsubscribe)
- [DATE] important@partner.com: Tier 3 MEDIUM → Tier 3 HIGH (user always responds quickly)
-->

## Notes

- Patterns here override defaults in classification-rules.md
- Review periodically and promote stable patterns to classification-rules.md
- Delete entries that were one-off corrections
