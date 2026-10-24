# Feature: Audit Tracking (delegated to the `FieldHistoryTracking` SOR)

How the orchestrator runs the **Audit Tracking** feature — field history on the Incident fields the user
chooses — over Salesforce's **Field History Tracking SOR**. This file re-derives none of the SOR's steps —
the SOR's own steps and guidance decide *how*. The orchestrator runs them under its **SOR hand-off
protocol** and owns the user-facing gates:

1. `discover` the SOR by intent (e.g. "field history tracking") and `describe` the id `discover` returns
   (`FieldHistoryTracking`). Judge availability by what the calls return, not by a step's `status` label —
   a step labelled `proposed` may still be served. A `discover` miss or a `401`/`403`/`404` means the
   surface isn't available to this user or org: surface it and stop.
2. Use the Incident fields the user already named, or ask which fields to track if the choice is missing
   or ambiguous, plus anything else `describe` says it needs. If the user chooses no fields, leave the
   feature `Not done` and stop; do not treat an empty choice as already configured.
3. Through the SOR, check Setup access, read Incident with `get-single-entity-data-with-metadata`, and get
   its per-object tracked-field limit. Use the returned tracking flag, field labels, `canBeTracked` values,
   current tracked set, and `fieldEnumOrId` keys to resolve the user's choices; do not guess field keys.
4. The save replaces the object's whole tracked-field set, so send the **union** of what's already tracked
   and the chosen fields using their returned keys, with Incident's object-level tracking flag on — never
   drop an already-tracked field unless the user asks. If a chosen field can't be tracked, or the union
   would exceed the limit, say so plainly; never untrack another field to make room. Report it as done
   with no write only if the nonempty chosen set is already tracked **and** Incident's object-level tracking
   is on. If the fields are selected but that flag is off, the change still needs a save.
5. Show the exact final tracked-field list by field label (disambiguate matching labels) in either case.
   Before any save, also show that object-level tracking will be enabled and get an explicit yes
   (`AskUserQuestion`) for that plan; when the user already named the fields, this confirms the selection.
6. After any save, read Incident's tracked fields back through the SOR. Mark the feature `Done` only when
   the live read (for the no-write case) or post-save read-back shows Incident's object-level tracking on,
   the chosen fields tracked, and no field dropped that the user didn't ask to drop — a save response alone
   is not proof.

## Rules

- ALWAYS keep every already-tracked Incident field in the save unless the user asked to stop tracking it,
  confirm the exact final field list before the save, and verify by read-back before marking it `Done` (or
  verify the already-configured state by live read with no write) — the SOR asks the user nothing itself

## Before marking it `Done`

- [ ] A live metadata read resolved the fields and complete labeled set; any save kept every
      already-tracked field the user didn't ask to drop, was confirmed before it ran, and was verified by
      read-back; a no-write `Done` also had Incident's object-level tracking confirmed on
