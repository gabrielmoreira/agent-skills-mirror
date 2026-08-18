# Governed Completion

Use this path when an executor has stopped but the run remains open, a
WorkThread needs attention, or a human escalation or waiver must be handled.

## Interpret The State

For governed runs, executor success is not completion. A GitHub-backed run that
ships a pull request remains open until provider webhook evidence confirms that
the pull request exists, the complete current-head check rollup was fetched, and
every observed check passes. Empty or truncated check results remain pending.
Explicit repository completion policies still take precedence. Runs that ship no
pull request retain executor-success semantics.

Inspect before acting:

```bash
opentag status --run <run_id>
opentag status --work-thread <work_thread_id>
opentag status --attention
opentag completion escalations --run <run_id>
```

Distinguish pending provider evidence from failed checks, a human escalation,
an expired obligation, and a delivery problem. An executor-reported pull
request URL can identify the target, but it is not provider proof.

## Human Actions

Use the CLI help for the required actor and reason fields:

```bash
opentag completion acknowledge --help
opentag completion resolve --help
opentag completion waive --help
```

- Acknowledge records that an attributed human saw an escalation; it does not
  resolve the blocking decision.
- Resolve records one bounded, attributed decision. Resume work through a new
  source-thread task rather than pretending the old executor is still running.
- Waive only selected current gates under explicit human authority, with the
  real actor, policy scope, reason, and optional expiry. Do not fabricate provider evidence.
  Do not use a waiver to rewrite observed GitHub state.

If checks appear stale, verify GitHub webhook delivery, repository binding, the
current pull-request head, and the observed check rollup before changing any
completion policy. Change `defaultGitHubCompletion` to `compat` only when the
user explicitly chooses legacy executor-success behavior.
