# Feature: Incident Persona PSG (delegated to the `service-itsm-incident-persona-assign` SOR)

How the orchestrator runs the **Incident Persona PSG** feature: giving one user the **Incident Fulfiller**
or **Incident Manager** persona — its permission set group (PSG) plus the permission-set licenses its
member sets need. The `service-itsm-incident-persona-assign` SOR's own steps and guidance decide *how* —
the PSG lookup, the user and license resolution, licenses before the PSG, and the read-back; the
orchestrator runs them itself under its **SOR hand-off protocol** and owns every user-facing gate. This file
adds what is specific to the personas.

1. `discover` the SOR by intent (e.g. "assign the Incident Fulfiller or Incident Manager persona to a
   user") and `describe` the id `discover` returns (`service-itsm-incident-persona-assign`).
2. Find the personas (`resolve-incident-persona-psgs`). If neither PSG exists, stop and report that the
   incident personas aren't provisioned on this org. Don't follow the hand-off that step names for this
   case: Behavior step 2 already confirmed Incident Management is on, and turning it on doesn't prove the
   PSGs exist.
3. Unless the user named one, ask which persona (`AskUserQuestion`, multi-select), offering only the PSGs
   that exist — Fulfiller works incidents, Manager runs the process. Never auto-select, and never offer the
   Major Incident Manager PSG (that approver license is part of **Major Incident Management**). Resolve the
   user to exactly one active user (`resolve-target-user`, or `resolve-current-user` for "me"); on zero or
   several matches, ask.
4. For each chosen PSG, separately: resolve its backing licenses, check what the user already has, and check
   seats only on the licenses still missing — a license the user already holds needs no free seat. If the
   PSG has no member sets, say so and stop that persona. Confirm the exact grants and that this org is
   modified (each license uses a seat; explicit confirmation for production), then run
   `assign-backing-psl`, `assign-persona-psg`, and `verify-persona-assignment`.
5. Report with the block below — one `Persona:` block per PSG — only what read-back confirmed. If the PSG's
   status still reads `Updating`, the grant is in place and its permissions are settling: say so rather than
   failing it. An access error that isn't a duplicate means an admin must make the assignment.

```text
Incident Management Persona Assignment
User:    <name> (<username>)
Persona: <Incident Fulfiller | Incident Manager>

  Persona bundle .................... Assigned | Already had it
  Backing licenses (N) .............. Assigned N | M already held
  Effective permissions ............. Active | Recalculating (settles shortly)
```

This feature only assigns the two standard persona PSGs — it never creates, edits, or recalculates a PSG,
and it assigns no other permission set.
