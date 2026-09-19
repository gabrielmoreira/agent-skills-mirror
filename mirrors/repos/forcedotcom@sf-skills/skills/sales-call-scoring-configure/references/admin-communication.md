# Admin Communication Guidelines — Full Spec

**CRITICAL**: The `sales-call-scoring-configure` skill serves admin users, not developers. These 13 rules govern every chat response, script invocation, and error surfacing in this skill. The parent SKILL.md holds only the summary; the rationale for each rule lives here.

## Table of contents

- [Rule 1 — Run all bash commands in background](#rule-1--run-all-bash-commands-in-background)
- [Rule 2 — Monitor progress without showing commands](#rule-2--monitor-progress-without-showing-commands)
- [Rule 3 — Investigate errors silently](#rule-3--investigate-errors-silently)
- [Rule 4 — Narrate in plain language](#rule-4--narrate-in-plain-language)
- [Rule 5 — Hide technical details](#rule-5--hide-technical-details)
- [Rule 6 — Speak admin language, not entity language](#rule-6--speak-admin-language-not-entity-language)
- [Rule 7 — Report the outcome, not the steps](#rule-7--report-the-outcome-not-the-steps)
- [Rule 8 — Don't speculate about internals](#rule-8--dont-speculate-about-internals)
- [Rule 9 — Check exit codes](#rule-9--check-exit-codes)
- [Rule 10 — On failure, surface the SOAP fault text](#rule-10--on-failure-surface-the-soap-fault-text)
- [Rule 11 — Idempotency is silent](#rule-11--idempotency-is-silent)
- [Rule 12 — Chain automatically, don't hand the baton back](#rule-12--chain-automatically-dont-hand-the-baton-back)
- [Rule 13 — Ask OOTB-vs-custom once, on first-time competency setup](#rule-13--ask-ootb-vs-custom-once-on-first-time-competency-setup)

## Rule 1 — Run all bash commands in background

Every bash invocation MUST use `run_in_background: true`. Includes the enable script, competency CRUD scripts, and any log-tailing for progress monitoring.

## Rule 2 — Monitor progress without showing commands

You can tail script output to provide progress updates, but keep tails in background. Parse the output and show only friendly updates like "Call Coaching enabled" or "6 competencies installed". Never show the script name, curl command, jq parsing, or raw script output.

## Rule 3 — Investigate errors silently

When something fails, do your diagnosis (check state, retry queries, fix auth) in background without narrating each step. Only surface the conclusion and action: "The org isn't ready yet — Einstein GenAI needs to be turned on first. Doing that now..." NOT "The --json output has embedded control chars, jq is failing, let me try show-access-token instead..."

## Rule 4 — Narrate in plain language

Say "Turning on Call Coaching..." NOT "Running enable-call-scoring.sh Phase 4 SOAP updateMetadata".

## Rule 5 — Hide technical details

No record Ids (`1nA...`), DeveloperNames (`CCH_...`), `SourceCompetencyTemplate` enum values, HTTP codes, character counts, SOAP responses, curl commands, jq parsing, script paths, or phase numbers — unless the admin asks to debug or share with support.

**Exception:** the S9 `verify-ootb-competencies.sh` markdown table surfaces evaluation criteria (the actual prompt body values) to the admin by design — that's the "here's what got configured" moment. See `competency-crud.md` §S9 for the rationale.

## Rule 6 — Speak admin language, not entity language

"Call Coaching", "Coaching Competency", "active/inactive". Never say `EnablementCompetencyDef`, `IsActive`, `enableECICallScoring`, `EvaluationInstructions`, `SourceCompetencyTemplate` in the primary message.

Same S9 exception applies — the verify table's column labels ("Competency", "Evaluation Instructions") are admin-readable English, and the values shown are the prompt bodies themselves (which are content the admin needs to see, not entity metadata).

## Rule 7 — Report the outcome, not the steps

"3 competencies installed" not "ran install-ootb, parsed 6 records, filtered by template, POSTed each".

## Rule 8 — Don't speculate about internals

If a state disagrees with what you expected, translate it into an admin-visible outcome ("Executive Vision Alignment is currently inactive — do you want to reactivate it?"), not a meta-analysis about which query returned what.

## Rule 9 — Check exit codes

Always parse success/failure and translate technical errors to admin-friendly messages ("The org's on the wrong sales-cloud arm for this skill — needs ECI").

## Rule 10 — On failure, surface the SOAP fault text

So the admin can share it with support if needed. Redact session tokens (the `soap.sh` library does this).

## Rule 11 — Idempotency is silent

If the feature is already on or a competency is already installed, say so briefly and move on — do not re-run the write.

## Rule 12 — Chain automatically, don't hand the baton back

When `enable-call-scoring.sh` exits 0 it prints a `Next: <script>` hint (State 3 → competency setup, State 4 → `list-competencies.sh`, fresh enable → same as State 3). Run that next script yourself, in the same turn, without telling the admin to run it and without asking permission to continue — the admin should never need to manually invoke a script in this skill.

**Exception: the State 3 "Next" hint is not a green light to install the OOTB set unasked.** First-time competency setup requires the OOTB-vs-custom choice below (rule #13) — that's the one checkpoint in this skill where Claude asks before writing.

## Rule 13 — Ask OOTB-vs-custom once, on first-time competency setup

When state detection lands on State 3 (Call Coaching enabled, zero competencies) and the admin's intent is "set up competencies" / "install competencies" / an unqualified continuation of the enable flow (not an explicit "install the OOTB set" or "create a custom competency" ask), run `install-ootb-competencies.sh --list` to render the 6-competency table, show it to the admin, and ask whether they want the OOTB set installed as-is or want to build custom competencies instead (S5).

If the admin's original request already named OOTB or custom explicitly, skip the question and proceed — this checkpoint exists for the ambiguous "set this up for me" case, not to re-litigate an explicit ask.
