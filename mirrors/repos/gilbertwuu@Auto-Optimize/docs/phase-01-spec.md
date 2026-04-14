# Phase 1: requirement definition

## What to do

Turn a vague ask into **five** explicit elements (the first four are classic spec; **the fifth is a mandatory acceptance checklist**):

```
1. Feature list: what does the product do? (all features)
2. Tech stack: languages, frameworks, DB, etc.
3. Output shape: SPA? API? docs?
4. Quality bar: what “good enough” means (core paths work? error handling?)
5. Acceptance checklist: under what conditions can **anyone** say “this round can stop / ship”?
   - Each line should be **checkable**: scripts, grep, or a short manual test—prefer concrete checks.
   - **Forbidden** to fill the list with uncheckable fluff (“looks professional”); if subjective, define **how** to verify (e.g. compare to attached screenshot).
```

## Acceptance file on disk (default)

- Before phase 1 ends, create or update **`tracks/phase-01-acceptance.md`**.
- Use Markdown task lists for humans and scripts, e.g.:

```markdown
# Acceptance checklist (locked in phase 1)

> Inner loop must not silently delete items; scope changes go back to phase 1/2 with trace.

## Structure / machine-checkable

- [ ] Deliverable is single-file HTML with root `<html lang="...">`
- [ ] …

## Behavior / manual or scripted

- [ ] …
```

- **Gate**: feature list **non-empty**, and **`tracks/phase-01-acceptance.md` has at least one** `- [ ]` or `- [x]` line. Before phase 2 the list need not be all checked; **all checked** is required to finish a track in phase 3 and to ship in phase 4 (see `phase-03-inner.md`, `verifiability.md` R3).

## Example

User: “Build me an expense tracker.” After phase 1:

```
Features: add income/expense, monthly stats, filter by category
Stack: Next.js + SQLite + Tailwind
Output: single-page web app
Quality: core flows work, validated inputs, clean UI
Acceptance (excerpt; must land in tracks/phase-01-acceptance.md):
  - [ ] Page has form id="txn-form"
  - [ ] After submit, list shows a new row with matching amount
  - [ ] …
```

## Gate

Spec is written, feature list **non-empty**, and **`tracks/phase-01-acceptance.md` exists with at least one acceptance line**. Otherwise do not enter phase 2.
