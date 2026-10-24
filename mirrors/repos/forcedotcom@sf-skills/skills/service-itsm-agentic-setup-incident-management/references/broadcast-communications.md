# Feature: Broadcast Communications (delegated to the `service-itsm-broadcast-communications-setup` SOR)

How the orchestrator runs the **Broadcast Communications** feature over the
`service-itsm-broadcast-communications-setup` SOR — never the Service-Foundation `IncidentManagement`
look-alike's broadcast toggles. The SOR's own steps and guidance decide *how*; the orchestrator runs them
itself under its **SOR hand-off protocol** and owns every user-facing gate. This file adds what is specific
to Broadcast Communications.

1. `discover` the SOR by intent (e.g. "set up ITSM broadcast communications") and `describe` the id
   `discover` returns. Its own prerequisite checks fall under protocol step 2.
2. **Phase 1 — turn it on, before asking about anything else.** Read the feature (`get-feature-status`).
   Already on → Phase 2 with no question. Non-empty `enableBlockedReasons` or `dependencyStatuses` → name
   the unmet prerequisite in plain language and stop. Otherwise say it's off and that turning it on **can't
   be undone** (Salesforce Go has no way to turn it off), get an explicit yes, run `enable-feature`, and
   require `verify-enabled` to read it on. Never turn the feature off, even when asked — offer to turn off a
   channel or object, or to revoke sender access, instead.
3. **Phase 2 — configure only what the user picks** (`AskUserQuestion`, multi-select; never everything by
   default): **sender access** for the users they name (resolve each name, username, or email to exactly
   one user, or ask; the license goes on before the *Broadcast Communication Sender* permission set, a
   duplicate is success, and only that permission set is ever assigned), **channels** (Email, In-app,
   Slack, Microsoft Teams — Slack delivers only with a connected Slack org), and **objects** (Incident,
   Change Request). For each: read, skip it if already set, confirm, write, and read back.
4. This is setup only — it sends no broadcast.
