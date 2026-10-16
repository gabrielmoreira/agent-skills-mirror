# Review Format — what the user sees (SKILL.md steps 7 and 10)

**When to load:** step 7, before filling any values. The layout is the same whether the skill was
chained from `nonprofit-volunteer-management-structure-generate` or started on its own.

## Three phases, always in this order

1. **Insert summary — once, up front, in plain language.** Open with one sentence saying what the
   run will write, e.g. *"We'll create 1 Volunteer Initiative, 3 Job Positions across 2 Locations,
   and a 30-shift schedule, and reuse 2 existing Locations."* Then: **Reuse** (each existing record
   as "Name · object", no Ids) and **New** (per object, with counts); one short paragraph on how the
   records fit together; the write order; and the origin-tag legend. Close with: *"Next we'll go
   through each object one at a time. You can change any record before it's written; when you
   confirm an object's table, those records are written and we move to the next object."*
2. **Per object, one at a time, in write order:** what it is, its field guide, its records table,
   and the modify prompt. Confirming the table is the yes to write it — no second confirmation.
   Write, read back, then move to the next object. Never show every object's tables up front.
3. **Final insert report — once, at the end.** One table of every record this run wrote or reused,
   and of any planned record that wasn't written.

## Origin tags (every records table)

Every value passed to `scripts/render-review-table.py` carries one of these. The table prints only
`reuse` and `needs-input`; the others are checked by the script but not shown, because the user
reviews every value the same way whatever its origin.

| Tag | Meaning |
|---|---|
| `given` | From the user or the plan |
| `default` | A safe default (e.g. Status `Upcoming`) |
| `generated` | The skill's proposed value — a suggestion, not something the user gave |
| `reuse` | A lookup to an existing record — the cell shows that record's Name |
| `new` | A lookup to a record created this run — the cell shows that record's Name |
| `needs-input` | A required value still missing — must be filled before the write |

Lookup cells show the referenced record's **Name**, never an Id. The Ids are written internally and
appear in the final report.

## Filling values — grounded only, consent per object

The fill mode (**Prefill everything** or **Generate together**) decides how much is filled at
once, not whether values may be invented. Either mode fills only: `given` values, safe `default`s,
and honest `generated` proposals.

- **Proposable:** a recommended or optional field with a safe default or an honest best guess.
  Propose it, tagged `generated`; the user edits if they disagree.
- **Must-ask (never invented):** values only the user knows — Location Type, an Address's street,
  city, state, postal code and country, a Job Position Title the user hasn't given — and any
  `Description` with no real context. They stay `needs-input` (or blank, for an optional
  Description) and are asked at their own object.

**"Just make one up" covers only the object under review.** When you move to the next object,
must-ask fields reset to `needs-input` and you ask again. Values made up at the user's request are
tagged `generated`, and the review says plainly that they were made up on request (the table
doesn't show that tag, so say it in the message).

## Per-object block

- **Header:** `‹Object› — ‹i› of ‹N› objects (‹n› new)`, e.g. `Job Positions — 3 of 7 objects (3 new)`.
- **What this is:** 1–2 sentences on what the object is for in this program.
- **Field guide** — one row per **field**, not per record. Columns **Field · Type · What it does ·
  Recommendation**.
  - **Field:** the label (an admin-renamed label from the description wins).
  - **Type:** the type an admin sees in Setup: Text, Text Area, Date, Time, Date/Time, Number,
    Checkbox, Picklist, Auto Number, Formula, `Lookup → ‹object›`. Never merge two different types
    (Text Area ≠ Text, Time ≠ Date).
  - **What it does:** the field's `Meaning` from `references/field-guide.md`, verbatim. The
    `Policy` column there is internal and never shown.
  - **Recommendation:** tier 1 → required, tier 2 → recommended, tier 3 → optional; a required
    custom field → `required · custom`. List every field you'll fill and every schema-required
    field. Tier 4 and 5 fields are hidden and named in a trailing `Not set (system-managed): …` line.
- **Records table** — one row per **record**. **Always render it with
  `scripts/render-review-table.py`; never type the table by hand.** Hand-typed rows put values under
  the wrong column when records' fields arrive in different orders. Pass the object's records as
  JSON (field → value + origin tag) and show the script's output as-is. The script fixes the column
  order (Record, then fields in field-guide tier order, then lookups last), uses labels as headers,
  shows required fields as `needs-input` when empty, leaves out optional fields no record uses,
  drops the Name column when the row label already shows it, moves a value that's the same on
  every row into one `Same on every row: …` line above the table, and groups identical rows behind
  "show all N". Spec in the script's docstring.
  - **Shifts:** one record per **series**, not per shift. The record's `label` names the series
    (`Saturdays 9:00–12:00 · 3 Oct → 19 Dec 2026 · 12 shifts`); Start Date holds the pattern
    (`every Saturday from 3 Oct 2026`), End Date `same day` (or `next day` for an overnight shift),
    and the other fields their shared values. Pass a `title` that counts shifts
    (`Records to insert — 12 Job Position Shifts (1 series)`).
  - **More than 10 series:** one row per **schedule** instead — series that share days, times and
    dates (e.g. the same season at every site) are one row. The Job Position cell names the group
    (`16 job positions · 4 roles × 4 sites`), and a value that differs within the group is spelled
    out in its cell (`by role: Site Lead 1 · Check-in 10 · Planter none`). The `title` counts both
    (`Records to insert — 2,304 Job Position Shifts (48 series, 3 schedules)`). Offer "show all
    series" for the per-series table.
- **Modify prompt:** invite edits, apply them, re-render with the script, and ask again.

One table per object; never mix two objects' fields.

---

## Template — insert summary and one per-object block

`{…}` is a per-run value; `‹…›` comes from `references/field-guide.md` or the script.

```text
Insert summary   (only the objects in this run; omit a line with nothing to show)
Reusing: {Name · object}, …
Creating: {object} ({count}) · {object} ({count}) · …     (in write order)
How it fits: {1–2 sentences tying this run's records together}
Order: {write order for exactly the objects above}
Lookups show Names; Ids are in the final report.

▶ {Object} — {i} of {N} objects ({n} new)
What this is: {1–2 sentences}

Field guide
| Field          | Type                         | What it does                 | Recommendation                         |
| ‹field label›  | ‹type, e.g. Lookup → Location› | ‹Meaning from field-guide.md› | ‹required / recommended / optional›   |
Not set (system-managed): ‹tier 4 and 5 fields›

‹output of scripts/render-review-table.py for this object›

Anything to change? e.g. "‹field› = ‹value› for all", "row 2 ‹field› → ‹value›". Otherwise reply "insert".
```

---

## Final insert report

```text
Insert complete — {total} records across {k} objects
| Object   | Record (Name)  | Id                   | Result        |
| {object} | {record Name}  | {record Id}          | created       |
| {object} | {record Name}  | {record Id}          | reused        |
| {object} | {series label} | {first Id}–{last Id} | {n} created   |
| {object} | {record Name}  | —                    | not created — {reason} |
Planned {p} · Created {c} · Reused {r} · Not created {x}
```

A shift or time-slot series is one row with its count and Id range. If a write failed part-way, the
records that were created stay — list them as `created`, list the rest as `not created` with the
error, and say what the user can do next. Nothing is undone. For a shift series, state the dates it
covers and that later shifts are added in a later run.
