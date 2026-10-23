# Admission limits and recovery

How to add a REA-owned admission ceiling, budget, or deadline, and what a caller
does when one is hit. This is a design rule, not an inventory. Ceilings that
should become settings are tracked in
[#6176](https://github.com/morluto/rea/issues/6176). Naming honesty for limit
errors is [#5910](https://github.com/morluto/rea/issues/5910).

## Name a default, then a setting when operators need headroom

Put the number in a named constant with a unit. Do not leave it as a magic
number at the call site.

When a workload may need more room, add a setting whose unset value is that
constant. One module under
[`src/config/`](https://github.com/morluto/rea/blob/main/src/config) owns the
default, any floor, the maximum, the schema, the parser, and the recovery
text. Register that schema on `environmentSchema` in
[`environment.ts`](https://github.com/morluto/rea/blob/main/src/config/environment.ts).
`parseConfig` calls `parseEnvironment`. Doctor uses that same parser through
`nativeAnalysisConfigurationError`, so startup and `rea doctor` accept the
same values. Add the name to `SELECTED_REGISTRATION_SETTINGS` so `rea setup`
copies it into the client registration. Unset keeps today's behavior. An
invalid value is a `ConfigurationError` and projects as `configuration_invalid`.
Do not fall back to the default.

[`REA_REGEX_MATCHING_DEADLINE_MS`](https://github.com/morluto/rea/blob/main/src/config/regexMatchingDeadline.ts)
([#6267](https://github.com/morluto/rea/pull/6267)) is the reference. Default
5000 ms, floor 1 ms, maximum 2147483647 ms, because Node schedules a longer
`setTimeout` delay as 1 ms. Setup copies the setting. A hit says:

> The effective REA_REGEX_MATCHING_DEADLINE_MS value is 5000 ms (source default; default 5000 ms, floor 1 ms, maximum 2147483647 ms). Set REA_REGEX_MATCHING_DEADLINE_MS in the environment that starts REA to a positive decimal integer from 1 to 2147483647, then restart REA. The worker old-generation heap does not raise this deadline.

[`REA_MCP_MAX_RESPONSE_BYTES`](https://github.com/morluto/rea/blob/main/src/config/mcpResponseBudget.ts)
is the byte-budget shape: a decimal safe integer with a 10 MiB floor
(`MINIMUM_RESPONSE_BYTES`), the same shared schema, and no silent fallback. A
change needs a REA restart and a matching client receive buffer. It does not
raise REA's reserved string limit or Node's string ceiling. The setup
allowlist does not copy this setting. A new headroom setting should, following
the regex deadline.

A per-call budget is not an environment setting. JavaScript `max_heap_mb`
(CLI `--max-heap-mb`) is an integer from 128 to 16384 MiB, default 1024. It
applies on the next analysis, which starts a new worker, and does not restart
REA. It does not raise the parent result budget, transfer ceilings, or fixed
parser limits.

Host memory and `NODE_OPTIONS` do not raise a REA admission unless that
admission's recovery says so. The JavaScript parent result budget is one that
does: its recovery says to set `NODE_OPTIONS` (for example
`--max-old-space-size=<MiB>`) on the process that starts REA, then restart
that process. `max_heap_mb` does not raise it.

## Keep a fixed ceiling honest

If the ceiling must stay fixed, say so in the failure. Name the limit and the
effective value, say this release has no runtime override, and name what does
not raise it. Do not invent a setting.

JSON values stop at `MAX_JSON_DEPTH` (1000) in
[`jsonValue.ts`](https://github.com/morluto/rea/blob/main/src/domain/jsonValue.ts):
"JSON value exceeds maximum nesting depth of 1000. This release has no runtime
override."

## Recovery text

The string the caller sees includes:

- the limit or setting name
- the effective value and unit
- the source (`default` or `setting`)
- the default, the maximum, and the floor when the setting has one
- the next action, including where to set it ("in the environment that starts REA")
- whether a restart is required
- what the change does not raise

Invalid settings never take this path. They are `configuration_invalid`.
Doctor reports `runtime-configuration:<setting>` and says to correct it in the
shell or the MCP registration, then rerun.

## What agents do

Follow `remediation.action`. Change a request field or a `REA_*` setting only
when that text recommends the change. Restart only when it says the value is
read at startup. A sentence that a control does not raise the limit is not a
request to change it.

- Dropped MCP connection: retry the call once only when it is safe to repeat
  or known not to have started. If it may already have changed the target, or
  it fails again, tell the user and ask them to restart the MCP client. Do not
  start with `rea doctor`
  ([#6353](https://github.com/morluto/rea/pull/6353)).
- REA could not start its connection: retry once. If it fails again, tell the
  user and ask them to restart the MCP client, then run `rea doctor`. Do not
  retry a startup that returns the same unchanged result: tell the user REA
  could not start, ask them to restart the MCP client, then run `rea doctor`.
- Unexpected process-command failure: do not repeat the command. Tell the user
  to check the input files, then run `rea doctor`.
- `cleanup_incomplete`: the operation is not retryable. Retry that exact
  cleanup owner, named in `details.resources`, and wait until it confirms
  release before admitting new work on those resources
  ([#6357](https://github.com/morluto/rea/pull/6357)).
- `resource_constraint` for capacity, when `retryable` is true: wait for the
  active admission to finish, then retry within the reported limits. Do not
  restart REA to free the slot.
- `configuration_invalid`: correct the named setting in the environment that
  starts REA, then start REA again. Run `rea doctor` for the
  `runtime-configuration:` check. Re-run `rea setup` for that client when the
  setting is on the registration allowlist, then reconnect so the new process
  sees it.
- `invalid_request`: correct the reported fields from the current schema or
  CLI help. Do not repeat the unchanged call.

A restart is required for an environment setting and for a client still
running the previous registration. It is not the first step for a transient
MCP drop, a capacity wait, or retained cleanup.

## Tests

Lock the unset default, one accepted override, rejected floor, maximum, and
syntax, and the recovery sentence through `parseEnvironment` and `parseConfig`.
[`regexMatchingDeadline.test.ts`](https://github.com/morluto/rea/blob/main/src/config/regexMatchingDeadline.test.ts)
is the pattern. Project the failure and assert `configuration_invalid` for a
bad value and the recovery wording for a hit.
