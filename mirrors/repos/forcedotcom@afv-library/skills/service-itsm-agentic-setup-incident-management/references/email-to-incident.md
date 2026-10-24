# Feature: Email-to-Incident (delegated to the `EmailToIncident` SOR)

How the orchestrator runs the **Email-to-Incident** feature, which turns incoming email into Incidents. The
`EmailToIncident` SOR's own steps and guidance decide *how*; the orchestrator runs them itself under its
**SOR hand-off protocol** and owns every user-facing gate. This file adds what is specific to
Email-to-Incident.

1. `discover` the SOR by intent (e.g. "email to incident settings routing address") and `describe` the id
   `discover` returns (`EmailToIncident`).
2. **Settings.** Read them (`get-email-to-incident-setting`) and ask which to change. Turning on
   Email-to-Incident itself (`enableEmailToIncident`) **can't be undone** — say so before asking. The save
   (`save-email-to-incident-setting`) replaces the whole settings map: send back every field the read
   returned (the set differs by release), changing only what the user chose, and on releases that have
   them, the draft-email, sender-error-notification, and signature settings each need Email-to-Incident on.
   Validate any choice-list value against the SOR's value-set reads. Confirm the full before → after
   change, save, and read back with `verify-save-setting`.
3. **Routing addresses — only if the user wants them.** List the existing addresses
   (`get-all-routing-addresses`) and the assignable queues (`get-incident-queue-ids`, the only source for
   the assignee), then create or update one with the user's routing name, email address, and default
   Urgency and Impact (the org's picklist values). An update replaces the whole row, so send every field.
   Read each change back with its `verify-*-routing-address` step. A delete is **irreversible** — confirm
   it explicitly. Re-sending an address's verification email sends a real email: do it only on an explicit
   request.
