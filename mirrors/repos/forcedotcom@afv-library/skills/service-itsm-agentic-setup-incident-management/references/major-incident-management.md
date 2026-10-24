# Feature: Major Incident Management (delegated to the `MIM` SOR)

How the orchestrator runs the **Major Incident Management** feature: the major-incident approval group and
the two MIM preferences, on top of base Incident Management. The `MIM` SOR's own steps and guidance decide
*how* — the approver license, the approvers group, group validation, the designation, and the two valid
preference names; the orchestrator runs them itself under its **SOR hand-off protocol** and owns every
user-facing gate. This file adds what is specific to MIM.

1. `discover` the SOR by intent (e.g. "set up the major incident management approval group") and
   `describe` the id `discover` returns (`MIM`). Its IT Service Enablement and Incident Management gates
   fall under protocol step 2.
2. **MIM must already be active.** Run the SOR's probe (`get-mim-setup-page-org-preference`) first. If it
   doesn't return a boolean, stop and say Salesforce provisions MIM — nothing here can turn it on.
3. Ask only what's missing (`AskUserQuestion`): the approval group, the preferences, or both; which public
   group approves (the `MajorIncidentApprovers` group or an existing public group the user names — if they
   name a person, offer to put them in a public group); and, for a preference, which one and on or off
   (never infer the direction).
4. **Approval group.** Read the current designation (`verify-approval-group`). Query for the
   `MajorIncidentApprovers` group (`verify-approvers-public-group`) and reuse it if it exists; create it
   only when none does. License and add only the members who still need it. Then run `validate-group-users`
   on that exact group — it changes nothing, so it needs no confirmation of its own — and designate only
   when it returns true. If it returns false, say the group isn't valid yet (every member needs the Major
   Incident Manager license, and the group can't be empty) and offer to license the members or pick another
   group.
5. Confirm the full plan before any write — the licenses to assign (each uses a seat), the group changes,
   the designation or reassignment, and each preference with its direction — and that this org is modified
   (explicit confirmation for production). Read every write back through its verify step.
6. Report with the block below, only what read-back confirmed, omitting the parts the user didn't choose.
   In plain language: no Major Incident Manager license on the org means it lacks the MIM add-on; a full
   license means a seat must free up first; a `403` means an admin with ITSM setup access must do it.

```text
Major Incident Management

  Approvers licensed (N) ............ Licensed N | M already held
  Approvers group ................... Created | Reused · N members added
  Approval group designated ......... <group> | Already designated | Reassigned
  Preferences ....................... Auto-create problem: on/off · Auto-close child incidents: on/off
```
