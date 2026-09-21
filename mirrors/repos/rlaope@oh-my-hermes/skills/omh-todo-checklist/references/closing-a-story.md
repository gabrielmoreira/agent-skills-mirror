# Closing A Story

The last phase of a code story - `X. Close` in the `code-story` plan
template. Open this when the work is finished and somebody is about to say so.

Closing is two acts, and conflating them is the failure this page exists to
prevent.

**Landing the change happens outside OMH.** OMH makes no network calls, so it
neither merges anything nor watches anything merge. Whether the change landed
is observed evidence somebody else supplies.

**Reporting the close is what this page governs.** Say what the record says,
and say what the record could not say. A report that does the second well and
lets a reader infer the first has claimed a merge nobody observed.

## The record a close may read

| Source | Held where | Read these | What it supplies |
| --- | --- | --- | --- |
| Plan record (`omh_todo/v1` item) | durable record, read with `omh runtime todo show` | `state`, `phase`, `blocked_reason` | what was done, which stage it belonged to, and what was skipped with its reason |
| Verification gate (`verification-gate`) | this session only | `observed_check_results/v1`, `claim_verdict/v1` | which command actually ran, its exit status, and which checks are missing or failed |
| Review (`code-review`) | this session only | `ranked findings per axis` | what a reader misses unless someone tells them |
| QA (`ultraqa`) | this session only | `pass/fail evidence` | what nobody thought of the first time |

One of those four outlives the session: the plan record, at
`$OMH_HOME/runtime/todos/<session key>.json`, read with `omh runtime todo show`.
The other three - Verification gate, Review and QA - are declared outputs: OMH asks a
model to produce them and stores none of them, so they are in this
conversation or they are gone. Whether that changes is a product question
filed separately.

So a close judgement that reads records reads the plan record and nothing
else today. If a verdict, a finding, or a QA result is still in context, cite
it as a declared output of this session and say so, because the next reader
cannot go back to it.

## What `done` means here, and what it does not

Three inferences a close report must not make.

**Every item `done` does not mean every item was worked.** It means every item
was DECLARED done, by a writer who may simply not have done it. OMH observes
declarations; no record can see the difference, and a close report that reads
`done` as delivery has invented the evidence between them.

**A phase `done` carrying a `blocked_reason` was skipped on purpose.** The
template refuses a stamped plan that DROPS a phase, so a phase this change did
not need is still on the list, marked `done`, with a reason saying why it
produced nothing. Report those as skipped and quote the reason; folding them
into the delivered phases turns the template's one enforceable guarantee into
a longer list of things that look shipped.

**No `blocked_reason` anywhere means nothing was RECORDED as blocked.** It is
not evidence that nothing was blocked. An empty field and an unwritten field
read identically here.

## The report

Five parts. The first and the last are the ones usually missing.

1. **Basis.** Which of these the report rests on, before any content:

   - `entries_observed`
   - `sources_read_no_entries`
   - `session_sources_lost`
   - `plan_record_absent`
   - `unknown_or_missing`

   Only `sources_read_no_entries` is a statement about the change. The rest
   are statements about what could be read, and saying which is the difference
   between a close and a confident silence.

2. **Phase by phase, in the list's own order.** Quote `phase`, `state`, and
   `blocked_reason` rather than paraphrasing them, and do not sort. On an
   ordinary plan `phase` is a free-text label the store never ranks, and an
   item may carry none at all, so stored order is the only order there is. A
   `code-story` plan does have a delivery order -- its labels are
   numbered, and a stamped plan that first names them out of sequence is
   refused -- but stored order already is that order. Reading the list as it
   stands is right either way; re-deriving an order is not.

3. **What was not delivered.** Every item not `done`, plus every `done` item
   carrying a `blocked_reason`. A plan closed with items still open is an
   ordinary outcome and says so; a plan closed by ticking them is not.

4. **Landing, observed or absent.** Name the artifact somebody actually saw -
   a merge commit, a CI conclusion, a pull-request state - and who saw it. A
   prepared handoff is `prepared_not_observed` and is not a landing.

5. **What could not be read, per source.** Read-and-empty and could-not-read
   are different answers, and only the first is about the change.

The record bounds parts 2 and 3 before you start: at most 20 items,
200 characters of text each, and a record written by another session is
unlinked after 24 hours. A close attempted the next day may find no plan at
all, which is `plan_record_absent` and never "nothing was blocked".

## What closing may not do

- **Do not tick the remaining items to finish the list.** A state written at
  close time is a fresh declaration that the outcome happened, and it outlives
  the session in a way the conversation does not. An open item reported as
  open costs a sentence; an open item marked `done` is a false record.
- **Do not issue a verdict here.** PASS, HOLD, and BLOCK over build, lint,
  typecheck, tests, docs and CI belong to `verification-gate`, which runs
  before this phase rather than inside it. A close report restating one of its
  verdicts has not re-proved it.
- **Do not let the deep guide, the ELI5 pass, or the quiz stand in for the
  close.** Those are `wiki`'s three handover artifacts and they are retained
  knowledge, not a report of what the plan says.

## Boundary

A close report is prepared narration over a metadata-only record. It is not
execution, verification, review, CI, merge-readiness, or merge evidence, and
issuing one neither lands a change nor makes a declaration into a result.
