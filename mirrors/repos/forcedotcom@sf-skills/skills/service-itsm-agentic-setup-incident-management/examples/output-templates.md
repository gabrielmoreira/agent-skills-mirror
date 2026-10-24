# Output Templates — service-itsm-agentic-setup-incident-management

Emit one of these text blocks at the corresponding step in the workflow. Show every feature the master
switch enables; render each row's `Status` from the actual tracked state (`Not done`, `In progress`,
`Done`) — never hard-code it.

## Feature menu (Behavior step 3)

```text
Incident Management Setup (via service-itsm-agentic-setup-incident-management)

Here are the features available for Incident Management. Select one or more to configure:

┌────┬───────────────────────────────┬──────────────────────────────────────────────────┬──────────┐
│ #  │ Feature                       │ Description                                      │ Status   │
├────┼───────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ P  │ Incident Preferences          │ The six setup toggles (validations, auto-close,  │ Not done │
│    │                               │ triage, Einstein, group restriction, rich text)  │          │
├────┴───────────────────────────────┴──────────────────────────────────────────────────┴──────────┤
│ Set Up the Basics                                                                                │
├────┬───────────────────────────────┬──────────────────────────────────────────────────┬──────────┤
│ 1  │ Incident Persona PSG          │ Manage User Access: give a user the Incident     │ Not done │
│    │                               │ Fulfiller or Manager persona (bundle + licenses) │          │
│ 2  │ Priority Matrix               │ Configure Rules for Automatic Incident Priority: │ Not done │
│    │                               │ the Impact × Urgency grid that sets Priority     │          │
│ 3  │ SLA & Milestones              │ Define SLAs to Prioritize Incidents: turn on SLA │ Not done │
│    │                               │ Management, then a predefined or custom policy   │          │
├────┴───────────────────────────────┴──────────────────────────────────────────────────┴──────────┤
│ Unlock Advanced Functionality                                                                    │
├────┬───────────────────────────────┬──────────────────────────────────────────────────┬──────────┤
│ 4  │ Incident Dashboards           │ Deploy the Incident Manager and/or Fulfiller     │ Not done │
│    │                               │ dashboards, and dashboards on the Home page      │          │
│ 5  │ Email-to-Incident             │ Report Incidents from Emails: email settings +   │ Not done │
│    │                               │ routing addresses                                │          │
│ 6  │ Major Incident Management     │ Review and Manage Major Incident Configuration:  │ Not done │
│    │                               │ approval group + the two MIM preferences         │          │
│    │                               │ (auto-create problem, auto-close child)          │          │
│ 7  │ Broadcast Communications      │ Set Up Broadcast Communication for Major         │ Not done │
│    │                               │ Incidents: turn on, then sender access, channels │          │
│    │                               │ (Email/In-app/Slack/Teams), objects              │          │
│ 8  │ Manage Incidents with AI      │ Auto-triage, Einstein assignment, and AI-drafted │ Not done │
│    │                               │ incidents from chat or voice transcripts         │          │
│ 9  │ Service Management Privilege  │ Escalation level, privilege records + employee   │ Not done │
│    │                               │ assignments, behind Enable Privilege Assignment  │          │
│ 10 │ Audit Tracking                │ Turn on field history tracking for the Incident  │ Not done │
│    │                               │ fields you choose (who changed what, and when)   │          │
└────┴───────────────────────────────┴──────────────────────────────────────────────────┴──────────┘

Reply with the numbers of the features you want to set up (one or more, e.g. `1,3`; `P` for Incident Preferences).
```

## Post-feature progress (Behavior step 5)

Example after the Incident Preferences feature completes (others still `Not done`):

```text
Incident Preferences — configured successfully
(via service-itsm-agentic-setup-incident-management)

┌────┬───────────────────────────────┬──────────┐
│ #  │ Feature                       │ Status   │
├────┼───────────────────────────────┼──────────┤
│ P  │ Incident Preferences          │ Done     │
│ 1  │ Incident Persona PSG          │ Not done │
│ 2  │ Priority Matrix               │ Not done │
│ 3  │ SLA & Milestones              │ Not done │
│ 4  │ Incident Dashboards           │ Not done │
│ 5  │ Email-to-Incident             │ Not done │
│ 6  │ Major Incident Management     │ Not done │
│ 7  │ Broadcast Communications      │ Not done │
│ 8  │ Manage Incidents with AI      │ Not done │
│ 9  │ Service Management Privilege  │ Not done │
│ 10 │ Audit Tracking                │ Not done │
└────┴───────────────────────────────┴──────────┘

Say a number (or `P`) to configure the next feature, or `done` to finish.
```

## Completion summary (Behavior step 6)

The completion summary fires either (a) after every feature completes, or (b) when the user says they are
finished — even if some features are still `Not done`. When rendering:

- Substitute each feature's row with its actual tracked status: `Done`, `In progress`, or `Not done`.
- Choose the header line based on whether every feature is `Done`:
  - All features `Done` → `Incident Management Setup — Complete`
  - Any feature still `Not done` or `In progress` → `Incident Management Setup — Finished`
- Choose the closing line based on state:
  - All `Done` → `Your Incident Management features are configured.`
  - Otherwise → `You have finished the features you selected. The remaining features can be resumed later by re-invoking this orchestrator.`

Example — user finished after configuring three features:

```text
Incident Management Setup — Finished
(via service-itsm-agentic-setup-incident-management)

┌───────────────────────────────┬──────────┐
│ Feature                       │ Status   │
├───────────────────────────────┼──────────┤
│ Incident Preferences          │ Done     │
│ Incident Persona PSG          │ Not done │
│ Priority Matrix               │ Not done │
│ SLA & Milestones              │ Done     │
│ Incident Dashboards           │ Not done │
│ Email-to-Incident             │ Not done │
│ Major Incident Management     │ Done     │
│ Broadcast Communications      │ Not done │
│ Manage Incidents with AI      │ Not done │
│ Service Management Privilege  │ Not done │
│ Audit Tracking                │ Not done │
└───────────────────────────────┴──────────┘

You have finished the features you selected. The remaining features can be resumed later by re-invoking this orchestrator.
```
