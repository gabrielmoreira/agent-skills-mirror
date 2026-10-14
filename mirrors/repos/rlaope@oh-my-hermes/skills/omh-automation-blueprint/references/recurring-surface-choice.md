# Choosing Among Heartbeat, Loop, Goal, and Cron

"Keep doing this for me" has four answers in OMH, and they differ in exactly
one thing: what ends them. Decide that first; the stop condition, retry policy,
and delivery target all follow from it.

## The four

| Surface | Ends when | Runs between occurrences | Recommend when |
| --- | --- | --- | --- |
| Cron (`scheduled_ops_blueprint`) | the operator removes the schedule | nothing | the request names a cadence - "every morning", "nightly", "each Monday" |
| Heartbeat (`heartbeat_watch`) | never; the user withdraws it | a liveness check only | the request watches a condition with no cadence and no end state |
| Loop (`loop_start`) | a named verification signal passes | work driven by the last iteration | the request improves something inside a bounded arena |
| Goal (`native_goal`) | a stated stop criterion is met | work driven toward that criterion | the request already states the condition that finishes it |

Two distinctions carry most of the decisions. A cadence answers *when*, so a
request that names one is never a loop, even when the work inside each
occurrence is iterative. And a heartbeat reports without changing anything: the
moment the request asks for something to be fixed between observations, it is a
loop or a goal.

## Each recommendation names the three it beat

A recommendation that does not say why the other three lost is a default, not a
choice, and a user cannot correct a default they cannot see. State each
rejection in the request's own terms - "not a schedule, because no cadence was
named" is checkable, "a heartbeat fits better" is not.

`assess_loopability` emits this as `recurring_surface_comparison`, one reason
per pair, and refuses a recurring recommendation that carries no stop
condition.

## Stop condition

Every recommendation carries one, and it is a condition, never a duration.
"Until the tests pass" is a stop condition; "for two weeks" is an end date,
which belongs in the schedule rather than in the stop rule. A heartbeat's stop
condition is the delivery of a change, not a completion - say that rather than
leaving the field blank, because a blank field reads as "runs forever by
design" when it usually means nobody decided.

## Retry policy

Retry belongs to the surface, not to the task. Name five things before
activation:

- **Overlap** - a prior occurrence is still running when the next is due: skip,
  queue, or run concurrently.
- **Missed run** - the host was down through a window: run once late, or drop it
  and continue at the next occurrence.
- **Retry** - whether a failed occurrence runs again, how often, and whether the
  wait between attempts is bounded.
- **Backfill** - whether each missed window is replayed, and how many at most.
- **Failure pause** - how many consecutive failures pause the surface, and
  whether resuming needs a human.

A loop and a goal answer these differently from a cron: an iteration that fails
its verification is information the next iteration uses, so a loop's "failure"
is usually not a retry at all. Say which reading applies.

### What Hermes cron already decides

On Hermes cron most of these are scheduler behavior, not settings, and none of
them is set per job. Say for each decision what the scheduler does and which
postures it cannot honour, so nobody is asked to choose a policy that will be
ignored:

| Decision | What Hermes cron does | What that means for the posture |
| --- | --- | --- |
| Overlap | Keeps one run of a job in flight; a fire that comes due while the last run is still going is skipped. | `skip_when_running` is what happens. `queue_after_running` and `allow_concurrent` are not honoured. |
| Missed run | A recurring fire the scheduler reaches late still runs, once, and a backlog of misses collapses into that one run. Some builds also read a global `cron.catch_up_missed` switch that drops a fire later than the catch-up window instead. | `run_once_when_late` is native. `skip_missed_window` exists only as that global switch, where the build has it. |
| Retry | No general retry; a failed run waits for its next occurrence. Where the installed Hermes ships `cron/unreachable_retry.py`, a recurring job's fire that failed on a transient network or DNS error before any model call is re-run up to three times within about an hour, unless the next scheduled occurrence comes first; the failure notice waits meanwhile, `cron.retry_unreachable: false` turns it off, and an `unreachable_retry` entry on the job record means one is pending. | `no_retry` describes every other failure. `retry_bounded` is not honoured outside that narrow case. |
| Backfill | None; missed windows are never replayed one by one. One extra run is `cronjob_manage` action `run`, which fires at once in the background, or `hermes cron run`, which runs it on the scheduler's next tick. | `no_backfill` is native. `backfill_bounded_window` means the user asking for each of those runs. |
| Failure pause | No automatic pause. After several failures in a row (`cron.failure_nudge_threshold`, default 3, one value for every job) the failure notice suggests pausing; the pause is `cronjob_manage` action `pause` or `hermes cron pause`. `failure_deliver` sends failure notices somewhere other than `deliver`. | `pause_after_consecutive_failures` holds only when someone acts on that notice. |

## Delivery target

Name the destination, the silence rule, and what a no-change occurrence does.
The silence rule is the one people skip: a daily digest that sends when nothing
changed trains its reader to ignore it, and one that never sends is
indistinguishable from a broken schedule. Choose one and write it down - report
only on change, or report every occurrence with an explicit no-change line.

In Hermes cron the destination is the job's `deliver`: `origin` is the
conversation the job was set up from, a bare platform name such as `slack`
sends to the home channel configured for it, and `platform:chat_id` names one
chat. Report
only on change becomes the prompt's last instruction - a final reply of
`[SILENT]` alone sends nothing - and `continuity` lets each run see its own
previous output, which "changed since last time" needs. A `monitor` source (a
URL, or a script whose output is deterministic) skips the model entirely when
nothing changed; it is the user's source, never one OMH writes.

## The native blueprint

Hermes calls a scheduled skill an Automation Blueprint: a skill whose
frontmatter carries `metadata.hermes.blueprint`. A
`prepared_native_blueprint/v1` record prepares that block and an equivalent
cron call. They reach Hermes by different routes and do not carry the same
things:

- The block: `schedule` (required), `deliver`, `prompt`, and `no_agent`, taken
  from the prepared intents. Hermes reads it only from a skill's frontmatter,
  and a job made from it preloads that one skill and carries no `continuity`,
  so a report-on-change job made this way needs
  `hermes cron edit <job_id> --continuity` afterwards, or a `monitor` source.
- The cron call, used when
  `cronjob_manage` is in your tool list or tool_search finds it,
  and otherwise handed to the user as the equivalent
  `hermes cron create "<schedule>" "<prompt>" --deliver <target> --skill <name> --continuity`
  command: the same values as a `cronjob_manage` `create`, plus the
  `skills` the context chain names and `continuity` when only changes are
  reported.
- A model pin is the user's to set: the block's own `model` and `provider`
  keys, `hermes cron create` or `hermes cron edit` with `--model` and
  `--provider`, or, where `cronjob_manage` offers `pinned`, `pinned=true`
  only on the user's explicit request, which pins the current main model.
  `cronjob_manage` takes no `model` or `provider` argument, and the
  prepared call never pins. `enabled_toolsets` is left unset, which keeps
  every default tool; the agent may narrow it when the job is created.
- `needs_confirmation` names the fields still open, `prompt` included while
  the silence rule is unsettled or the request ran past the stored preview.
  The stored prompt is a bounded preview of the request, not a
  self-contained cron prompt: while `prompt` is open, write the full prompt
  from the request in the conversation when the job is created. Hermes
  parses the schedule when the job is created, so confirm it in one of Hermes' forms first - an interval such as
  `every 2h`, a day and time such as `weekdays at 9am`, or a cron expression.

Activation is never OMH's, and it happens in one of four ways, each started
by the person or by Hermes: `/blueprint` for one of Hermes' own catalog
automations, which asks for the values and creates the job; accepting the
Suggested Cron Job that `/suggestions` lists after a blueprint skill is
installed from the hub, which is never scheduled until accepted; a
`cronjob_manage` `create` the user asked for in the conversation; or a
`hermes cron create` the user runs. Preparing a blueprint is not that request.

## After activation

Status comes from Hermes, never from the blueprint:

- `cronjob_manage` action `list` - the job's `state`, `last_status`,
  `last_run_at`, and `next_run_at`, plus a warning when the gateway that fires
  jobs is not running, in which case the job is saved but will not run.
- `hermes cron runs <job_id>` - the attempts Hermes recorded.
- `hermes cron incidents` - failures grouped by job and error. `detected` and
  `alerted` are open; `hermes cron incidents ack <id>` closes one.

An occurrence of a saved recurring intent links to a Hermes run only through
that run's own reference.

## Boundary

A recommended surface, its stop condition, its retry policy, and its delivery
target are a prepared native blueprint. OMH starts, skips, queues, retries, and
backfills nothing, and creates no cron job; a policy decision is not proof the
runtime honoured it, and a saved recurring intent stays paused until an
approved runtime surface records an occurrence against that exact intent
revision.
