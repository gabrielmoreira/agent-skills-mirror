# Feature: Service Management Privilege (delegated to the `ServiceMgmtPrivilegeSetup` SOR)

How the orchestrator runs the **Service Management Privilege** feature — ITSM privilege escalation: the
*Enable Privilege Assignment* toggle, the org-wide escalation level, the privilege definitions, and bulk
employee assignments. The `ServiceMgmtPrivilegeSetup` SOR's own steps and guidance decide *how* — the
toggle's place in the order, the privilege fields, Tag-first handling, and which writes can be read back;
the orchestrator runs them itself under its **SOR hand-off protocol** and owns every user-facing gate. This
file adds what is specific to this feature.

1. `discover` the SOR by intent (e.g. "set up ITSM service management privilege escalation") and `describe`
   the id `discover` returns (`ServiceMgmtPrivilegeSetup`). Its IT Service Enablement check falls under
   protocol step 2. No other public API covers this feature: a `404` or a `discover` miss means it isn't
   served on this org — say so and stop; never look for another route.
2. Ask which part the user wants (`AskUserQuestion`): the escalation level, the privileges, or employee
   assignments. Read the toggle (`check-privilege-assignment-enabled`) first. If it reads off, turn it on —
   it's reversible — with the user's yes, before any escalation-level or privilege step, as the SOR orders
   it; if they decline, stop.
3. For a new privilege, ask its tag, access level, and description (the SOR sets the rest). If the tag isn't
   on the Tag field yet (the SOR's `new-tag-needed` choice), the user adds it in Object Manager after their
   explicit OK — never dispatch `add-privilege-tag-value`. For assignments, ask the privilege and exactly
   which employees to add or remove.
4. Confirm the full plan before any write — the toggle, the escalation value, each privilege change, and the
   employees to add and remove — and that this org is modified (explicit confirmation for production). A
   privilege delete is **irreversible**: confirm it on its own, and never delete to test.
5. Read every write back: the toggle and the escalation level through their verify steps, and each
   privilege create, update, or delete by re-listing the privileges (`get-service-privileges`). Employee
   assignments have no read-back: report them as applied, never as verified. A `403` means an admin with
   ITSM setup access (and, from API 68.0, Customize Application) must make the change.

```text
Service Management Privilege
  Enable Privilege Assignment ....... On | Off | Enabled now
  Escalation level .................. <value> | Unchanged
  Privileges ........................ Created/Updated/Deleted <name> | N configured
  Employee assignments .............. Applied: +N / -M (not read-back verifiable)
```

Report only what read-back confirmed, and omit the lines the user didn't choose. The persona PSGs, the
Major Incident Manager license, and Problem / Change Management are outside this feature.
