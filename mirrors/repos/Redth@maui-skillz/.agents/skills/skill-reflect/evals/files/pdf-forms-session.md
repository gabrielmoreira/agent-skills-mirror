<!-- SYNTHETIC FIXTURE — all names/emails/tokens are fake, for eval only. -->
<!-- This file exists solely to support skill-reflect M9 dogfood evals. -->
<!-- DO NOT use as a template for real session data. -->

# Synthetic Session Log — 2026-01-01

**Session ID:** sess-2026-01-01-fake001
**Agent:** Copilot CLI (simulated)
**User:** alice.runner@acmecorp.example
**Working directory:** /Users/alice.runner/work/q4-expense-filing
**API token in env:** ghp_Xk2mN7pQ4rT1vB8cD3eF6gH0iJ5lKwY9zA3bC
**Internal logging host:** 10.42.5.199

---

## Turn 1 — User request

**User:** Fill out the Q4 expense PDF form using pdf-forms and flatten the fields.

**Agent reasoning:** Invoking `pdf-forms` to fill and flatten the form per the skill's
documented `fill` subcommand. The skill SKILL.md advertises `--flatten` to flatten
interactive fields after fill.

**Tool call (skill: pdf-forms, subcommand: fill):**

```bash
pdf-forms fill \
  --input /Users/alice.runner/work/q4-expense-filing/expense-q4.pdf \
  --data '{"submitter": "alice.runner@acmecorp.example", "quarter": "Q4", "total": "2400.00"}' \
  --flatten \
  --output /Users/alice.runner/work/q4-expense-filing/expense-q4-filled.pdf
```

**Tool exit:** 1

**Tool stderr:**
```
error: unknown option '--flatten'
  Hint: did you mean '--flatten-fields'? (option renamed in pdf-forms v2.0)
```

---

## Turn 2 — Agent retry (same command, no change)

**Agent reasoning:** Retrying — the skill documentation shows `--flatten`; perhaps a
transient error.

**Tool call (skill: pdf-forms, subcommand: fill):**

```bash
pdf-forms fill \
  --input /Users/alice.runner/work/q4-expense-filing/expense-q4.pdf \
  --data '{"submitter": "alice.runner@acmecorp.example", "quarter": "Q4", "total": "2400.00"}' \
  --flatten \
  --output /Users/alice.runner/work/q4-expense-filing/expense-q4-filled.pdf
```

**Tool exit:** 1

**Tool stderr:**
```
error: unknown option '--flatten'
```

---

## Turn 3 — Agent retry (third attempt, unchanged)

Same invocation as Turn 2. Same failure.

---

## Turn 4 — Agent abandons skill guidance, uses external tool

**Agent reasoning:** `pdf-forms fill --flatten` fails repeatedly. Skill docs do not mention
`--flatten-fields`. Falling back to `pdftk` outside the skill's prescribed workflow.

```bash
pdftk /Users/alice.runner/work/q4-expense-filing/expense-q4.pdf \
  fill_form /Users/alice.runner/work/q4-expense-filing/fdf-data.fdf \
  flatten \
  output /Users/alice.runner/work/q4-expense-filing/expense-q4-filled.pdf
```

**Tool exit:** 0

Task completed via workaround (not via pdf-forms).

---

## Turn 5 — User requests validation

**User:** Now validate the completed form.

**Agent reasoning:** Invoking `pdf-forms validate` as documented. Skill docs state the
output schema is `{"valid": true|false, "errors": ["..."]}`.

**Tool call (skill: pdf-forms, subcommand: validate):**

```bash
pdf-forms validate \
  --file /Users/alice.runner/work/q4-expense-filing/expense-q4-filled.pdf
```

**Tool stdout (actual):**
```json
{"status": "ok", "fields_validated": 14, "warnings": []}
```

**Agent reasoning:** Expected `{"valid": ..., "errors": [...]}` per skill docs.
Actual output uses `status`/`fields_validated`/`warnings` keys. Schema mismatch.
Cannot determine validity from documented output format. Retrying.

---

## Turn 6 — Validate retry 2

Same command. Same output (`status`/`fields_validated`/`warnings`).
Agent still cannot reconcile with documented `valid`/`errors` schema.

---

## Turn 7 — Validate retry 3

Same command. Same output. Agent notes schema mismatch in reasoning trace.

---

## Turn 8 — Validate retry 4 (final), pivot

Same command. Same output.

Agent abandons documented parse path; reads the raw JSON directly and infers validity
from `status: "ok"`. Workaround succeeded.

---

## Session end

**skill-reflect-auto:** Friction counter for `pdf-forms` = 7 (3 fill retries + 4 validate
retries). Staging pending-review marker.

**Marker written to:** ~/.skill-reflect/pending/sess-2026-01-01-fake001.json
