# Feature: Incident Preferences (delegated to the `IncidentMgmt` SOR)

How the orchestrator runs the **Incident Preferences** feature: the six per-feature toggles on the ITSM
Incident Management setup page. The `IncidentMgmt` SOR's own steps and guidance decide *how* — the six
preference names and labels, the two one-way ones, and the read-back; the orchestrator runs them itself
under its **SOR hand-off protocol** and owns every user-facing gate. This file adds what is specific to the
preferences.

1. `discover` the SOR by intent (e.g. "configure ITSM incident management preferences: automatically triage
   incidents, assign incidents with Einstein") and `describe` the id `discover` returns (`IncidentMgmt`) —
   never the Service-Foundation `IncidentManagement` look-alike, whose toggles are broadcast channels.
2. Behavior step 2 already ran this SOR's IT Service Enablement and Incident Management steps, so start at
   its preference flow: read (`getOrgPref_1`), change (`updateOrgPref_2`), read back
   (`verify-update-org-pref`). Never run its `disable-itsm-incident-feature` /
   `verify-itsm-incident-feature-disabled` steps (the master switch is not part of this feature) or
   `delegate-email-to-incident` (that is the **Email-to-Incident** feature).
3. Read all six and show them with the block below, flagging the two one-way ones. Ask which to change and
   in which direction (`AskUserQuestion`) — never infer the direction from the current state, and never
   offer to turn a one-way preference off. Skip any already in the requested state.
4. Confirm the exact change and that this org is modified (explicit confirmation for production). For
   *Restrict Assigned Group to Regular Groups* or *Enable Rich Text for Incident Descriptions*, the
   confirmation must say it can't be undone. Write each chosen preference and read each back; mark the
   feature `Done` only when every read-back matches.
5. In plain language: a failed enable of *Restrict Assigned Group…* means the org already has incidents, so
   it can't be turned on now — don't retry. If *Automatically Triage Incidents* or *Assign Incidents with
   Einstein* can't be read or turned on, the org lacks that switch's license (*IT Services: Agentforce
   Features for Employees* for triage, *IT Services: Einstein Features* for Einstein assignment): say so,
   skip it, and carry on with the others.
6. *Automatically Triage Incidents* and *Assign Incidents with Einstein* are also two of the three switches
   of the **Manage Incidents with AI** feature — the same org preferences — so one set in either feature
   reads as already set in the other. That feature's third switch, *Report Incidents from Chat or Voice
   Using AI*, is not one of the six.

```text
  Default Field Validations for Incidents ...... On | Off
  Automatically Close Child Incidents .......... On | Off
  Automatically Triage Incidents ............... On | Off
  Assign Incidents with Einstein ............... On | Off
  Restrict Assigned Group to Regular Groups .... On | Off  (one-way)
  Enable Rich Text for Incident Descriptions ... On | Off  (one-way)

Changed: <label> Off → On (SUCCEEDED | ALREADY-ON | FAILED)
```
