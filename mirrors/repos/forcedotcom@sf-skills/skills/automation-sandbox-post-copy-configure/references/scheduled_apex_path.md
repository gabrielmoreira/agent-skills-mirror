# Step F — Scheduled Apex (anonymous Apex route)

`ScheduledApex` entries in the post-copy config target the `CronTrigger`
sobject, which is **read-only** in the Tooling API — there is no
compound `Metadata` field, so Steps A–E (describe → SOQL → GET+PATCH)
cannot apply. Instead this route runs anonymous Apex
`System.schedule(...)` via `sf apex run` and verifies via a
`CronTrigger` SOQL read-back.

## Fields shape

Every `ScheduledApex` entry must carry these three keys under `Fields`:

| Key | Meaning |
|-----|---------|
| `ApexClassName` | Bare Apex identifier of the class that implements `Schedulable`. |
| `CronExpression` | Salesforce cron expression (6- or 7-field). |
| `JobName` | Human-readable job name. Appears in Setup > Scheduled Jobs; equals `CronTrigger.CronJobDetail.Name` post-schedule. |

If any of the three is missing, mark the entry `API_NOT_IDENTIFIED` and
skip. Never fabricate one from the others.

## Prerequisites

The Apex `Schedulable` class named by `ApexClassName` must already exist
on the target sandbox. Sandbox refresh copies class metadata from source
to target, so this is normally satisfied on a fresh refresh — the reason
scheduled *jobs* need re-creation is that `CronTrigger` records (runtime
state) don't copy, not that the classes don't.

If the class is genuinely missing, F-3 (`sf apex run`) fails at compile
with `Variable does not exist: <ApexClassName>` — the outcome becomes
`FAILED` and the customer follows the Cross-Skill Integration row on
`platform-metadata-deploy` to deploy the class before re-running this
skill.

## F-1 — Pre-flight AMBIGUOUS check

`System.schedule` throws `AlreadyScheduledException` if a job with the
same name already exists. Query first to avoid that path — and per skill
policy, do NOT auto-abort an existing job; surface it as `AMBIGUOUS` so
the customer decides.

`JobName` is human-readable and may legitimately contain an apostrophe
(e.g. `Owner's nightly job`). Never inline it into the SOQL literal
directly — escape it via the deterministic helper first, which also
rejects the same characters `scripts/build-scheduled-apex.mjs` rejects
(newlines/backslashes), so an input that passes F-1 will also pass F-2:

```bash
JOB_NAME_LITERAL=$(node scripts/soql-escape-job-name.mjs "<Fields.JobName>") || {
  # Non-zero exit → outcome FAILED with stderr in Follow-ups; skip F-2/F-3/F-4.
  exit 1
}
SOQL="SELECT Id FROM CronTrigger WHERE CronJobDetail.Name = '$JOB_NAME_LITERAL'"
sf data query --json --query "$SOQL" > /tmp/entry-<Slug>-cron.json
COUNT=$(jq -r '.result.totalSize' /tmp/entry-<Slug>-cron.json)
```

Outcomes:

- `COUNT == 0` → proceed to F-2.
- `COUNT >= 1` → outcome `AMBIGUOUS`. Add a Follow-ups bullet listing
  the entry's `Fields.JobName` and every returned `CronTrigger.Id`.
  Do not attempt to schedule.

In dry-run, still run F-1 — it is a read.

## F-2 — Build the anonymous Apex snippet

Never author the snippet from memory — Apex string escaping is a common
foot-gun. Use the deterministic builder:

```bash
node scripts/build-scheduled-apex.mjs \
  "<Fields.JobName>" \
  "<Fields.CronExpression>" \
  "<Fields.ApexClassName>" \
  assets/scheduled_apex_template.apex \
  > /tmp/entry-<Slug>.apex
```

The script:

- Verifies `CronExpression` is 6- or 7-field whitespace-separated.
- Verifies `ApexClassName` matches `^[A-Za-z_][A-Za-z0-9_]*$`.
- Rejects newlines and backslashes in any input (would either break the
  string literal or enable Apex injection).
- Single-quote-escapes `JobName` and `CronExpression` for embedding in
  the Apex single-quoted string.
- Writes the substituted `.apex` snippet to stdout.

Non-zero exit → outcome `FAILED` with stderr in Follow-ups.

## F-3 — Execute the snippet

```bash
sf apex run --file /tmp/entry-<Slug>.apex --json \
  > /tmp/entry-<Slug>-apex.json
```

Classify from the JSON response:

| `.result.compiled` | `.result.success` | Outcome | Follow-ups body |
|--------------------|-------------------|---------|-----------------|
| `false` | (any)   | `FAILED` | `.result.compileProblem`, `.result.line`, `.result.column` |
| `true`  | `false` | `FAILED` | `.result.exceptionMessage`, `.result.exceptionStackTrace` |
| `true`  | `true`  | proceed to F-4 | — |

Skip F-3 entirely in dry-run and record `DRY_RUN`.

## F-4 — Verify the job scheduled

Reuse `$JOB_NAME_LITERAL` from F-1 — it is the same JobName, already
SOQL-escaped and validated:

```bash
SOQL="SELECT Id, State, NextFireTime, CronExpression FROM CronTrigger WHERE CronJobDetail.Name = '$JOB_NAME_LITERAL'"
sf data query --json --query "$SOQL" > /tmp/entry-<Slug>-verify.json
```

Outcomes:

- 0 rows → `FAILED_VERIFY` (apex reported success but no CronTrigger
  materialized — usually a permission or platform limits issue).
- ≥1 row where `.CronExpression == '<Fields.CronExpression>'` → `SUCCESS`.
- ≥1 row with a different `CronExpression` → `FAILED_VERIFY` (something
  else claimed the name after F-1 saw it clear).

Skip F-4 entirely in dry-run (nothing to verify).

## Summary shape for a Step F entry

Reuse the phase table from the canonical output shape:

- `Sobject` column reads `CronTrigger`.
- `Describe` column reads `—` (no describe probe on this route).
- "Planned request" / "Request executed" is the anonymous Apex snippet
  path (`/tmp/entry-<Slug>.apex`) and its contents inline, not a PATCH
  path/body.
- `HTTP` column reads `—` (no direct HTTP status; `sf apex run` bundles
  compile+execute into one response).

## Dry-run recap

| Sub-step | Dry-run behavior |
|----------|------------------|
| F-1 SOQL pre-flight | run (read) |
| F-2 snippet build (writes to `/tmp` only) | run |
| F-3 `sf apex run` | SKIP → record `DRY_RUN` |
| F-4 verify SOQL | SKIP (nothing to verify) |

The "Planned request" printed in the dry-run summary for a Step F entry
is the full contents of the built `.apex` snippet, so the customer can
audit exactly what would have executed.
