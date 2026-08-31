# NTM Robot Mode

Use this file when you need the deeper, structured automation side of NTM.

## Contents

- [Output Formats](#output-formats) — `--robot-format`, env fallbacks, verbosity
- [Start Here](#start-here) — discovery, capabilities, schema
- [Canonical Operator Loop](#canonical-operator-loop)
- [Attention Feed](#attention-feed) — snapshot, events, digest, wait, overlay
  - [Attention Profiles](#attention-profiles)
  - [Wait Conditions](#wait-conditions)
- [Core Robot Actions](#core-robot-actions) — send, ack, tail, inspect
  - [Safe Restart Pattern](#safe-restart-pattern)
  - [Assignment and Routing](#assignment-and-routing)
  - [Context and Health](#context-and-health)
  - [Files, Replay, Support](#files-replay-support)
- [Beads, Mail, and CASS](#beads-mail-and-cass)
- [Human-Friendly Robot Views](#human-friendly-robot-views)
- [Robot Flag Navigation Index](#robot-flag-navigation-index) — grouped by purpose
  - [Discovery / docs](#discovery--docs)
  - [State / snapshots / formats](#state--snapshots--formats)
  - [Events / attention](#events--attention)
  - [Pane inspect / tail / watch](#pane-inspect--tail--watch)
  - [Activity / health / diagnose](#activity--health--diagnose)
  - [Control / mutate](#control--mutate)
  - [Sessions / spawn / controller](#sessions--spawn--controller)
  - [Assign / route / distribute](#assign--route--distribute)
  - [Work / beads / bv](#work--beads--bv)
  - [Pipeline](#pipeline)
  - [Mail / coordination](#mail--coordination)
  - [CASS](#cass)
  - [Ensemble / modes](#ensemble--modes)
  - [Monitor / tools / bundle](#monitor--tools--bundle)
  - [Palette / recipes / setup / profile](#palette--recipes--setup--profile)
  - [Integrations](#integrations)

---

## Output Formats

| Flag | Meaning |
| --- | --- |
| `--robot-format=json` | Full JSON output |
| `--robot-format=toon` | More token-efficient structured output (prefer when context is tight) |
| `--robot-format=auto` | Auto-select current default |

Env fallbacks honored (in order): `NTM_ROBOT_FORMAT`, `NTM_OUTPUT_FORMAT`, `TOON_DEFAULT_FORMAT`.

Note: `--robot-output-format` is a **deprecated** alias — always use `--robot-format`.

Verbosity: `--robot-verbosity=terse|default|debug` (env `NTM_ROBOT_VERBOSITY`).

## Start Here

```bash
ntm --robot-help
ntm --robot-capabilities                 # machine-discoverable API schema (prefer this over --help)
ntm --robot-docs=quickstart              # topics: quickstart | commands | examples | exit-codes
ntm --robot-schema=all                   # JSON Schema for every robot response type
ntm --robot-status
ntm --robot-snapshot
ntm --robot-plan
ntm --robot-dashboard
ntm --robot-markdown --md-compact
ntm --robot-terse
```

`--robot-capabilities` is the canonical schema/discovery surface. Prefer it over
parsing human help text. `--robot-schema=all` lets you validate parsed responses.

## Response and Freshness Contract

Robot output is meant to be parsed mechanically:

- Treat `success=false` plus `error_code` as the control signal; do not scrape prose.
- Required list fields should be present as empty arrays when checked-and-empty.
- Optional fields are omitted when irrelevant; do not expect `null`.
- `timestamp`, `schema_version`, and `output_format` are part of the envelope on
  the newer surfaces.
- For derived views, read `sources` / `degraded_sources` warnings before acting.

Decision rule:

| Source status | Operator posture |
| --- | --- |
| fresh / healthy | Safe to act on the derived recommendation |
| stale but available | Act only if low-risk; annotate the stale source |
| degraded / unavailable | Prefer non-mutating previews; fall back to native tools (`br`, `bv`, mail MCP) |
| contradictory sources | Re-bootstrap with `--robot-snapshot`, then inspect the native source |

Do not turn a degraded source into a hard stop by default. NTM is designed to remain
useful when CASS, Agent Mail, or BV are partially unavailable, but mutating commands
should be held to a higher proof threshold.

## Canonical Operator Loop

```text
1. Bootstrap with ntm --robot-snapshot
2. Read latest cursor / attention summary
3. Tend with ntm --robot-attention or ntm --robot-wait
4. Act with ntm --robot-send, ntm send, ntm assign, ntm mail, or ntm locks
5. Repeat

If the cursor expires, re-run --robot-snapshot.
```

## Attention Feed

| Command | Purpose |
| --- | --- |
| `--robot-snapshot` | Bootstrap unified state plus attention summary and cursor handoff |
| `--robot-events` | Raw replay since a cursor |
| `--robot-digest` | Non-blocking attention-feed summary |
| `--robot-attention` | Wait-then-digest tending command |
| `--robot-overlay` | Human handoff / overlay actuator |
| `--robot-wait` | Wait for pane or attention conditions |

Example flow:

```bash
ntm --robot-snapshot
ntm --robot-events --since-cursor=42 --events-limit=50 --events-category=agent
ntm --robot-digest --profile=minimal
ntm --robot-attention --attention-cursor=42
ntm --robot-overlay=myproject --overlay-no-wait
```

### Attention Profiles

| Profile | Flag | Behavior |
| --- | --- | --- |
| `operator` | `--profile=operator` | Default operator-focused blend |
| `debug` | `--profile=debug` | Full verbosity |
| `minimal` | `--profile=minimal` | Only the most urgent items |
| `alerts` | `--profile=alerts` | Alert-centric view |

Explicit filters override profile defaults.

### Wait Conditions

Flag: `--wait-until` (alias `--condition`). Canonical set from `--robot-capabilities`:

Pane-oriented:

- `idle`
- `complete`
- `generating`
- `healthy`
- `stalled`
- `rate_limited` — fires when a pane **becomes** rate-limited
- `rate_limit_lifted` — returns once **all** target panes are clear of the wall (do not confuse with `rate_limited`)
- `agent_ready` — CLI booted and responsive after relaunch/respawn (replaces fixed post-boot sleeps)

Attention-oriented:

- `attention`
- `action_required`
- `mail_pending`
- `mail_ack_required`
- `context_hot`
- `reservation_conflict`
- `file_conflict`
- `session_changed`
- `pane_changed`

**Deliberately unsupported:** `bead_orphaned`. NTM refuses to emit this because abandonment
cannot be proven from observable pane/session state alone — emitting it would invent
conclusions from insufficient data. Do not try to wait on it; the command will reject.

Example:

```bash
ntm --robot-wait=myproject --wait-until=idle --timeout=5m
ntm --robot-wait=myproject --wait-until=action_required --attention-cursor=42
ntm --robot-wait=myproject --wait-until=mail_pending --attention-cursor=42
ntm --robot-wait=myproject --wait-until=reservation_conflict --attention-cursor=42
ntm --robot-wait=myproject --wait-until=agent_ready --panes=2 --timeout=90s
ntm --robot-wait=myproject --wait-until=idle --wait-id=tend-17   # durable cross-process handle
ntm --robot-wait-cancel=tend-17                                  # cancel that wait from anywhere (no pkill)
```

## Core Robot Actions

```bash
# Send and watch for response (--message is an accepted alias of --msg)
ntm --robot-send=myproject --panes=2 --msg="Fix auth" --type=claude
ntm --robot-send=myproject --panes=2 --msg-file=- --clear-input < prompt.md   # stdin payload; owned composer-clear ritual
ntm --robot-send=myproject --panes=2 --msg="..." --verify-render   # bounded before/after capture; requires rendered delivery evidence
ntm --robot-send=myproject --panes=2 --msg="deploy" --op-id=deploy-42   # durable idempotent send: identical retries replay the recorded outcome; conflicting reuse → IDEMPOTENCY_CONFLICT; not with --track
ntm --robot-send-receipt=deploy-42                                      # query that op's per-target admission receipts later
# Definite bare-shell agent panes are refused with PANE_AGENT_DEAD + restart guidance.
ntm --robot-ack=myproject --timeout=30s                 # --ack-timeout/--ack-poll are deprecated aliases

# Inspect without retiling
ntm --robot-tail=myproject --panes=2 --lines=50
ntm --robot-tail=myproject --panes=2 --lines=50 --fresh  # direct live capture (capture_provenance:"fresh") for post-action truth
ntm --robot-inspect-pane=myproject --inspect-index=2
ntm --robot-inspect-session=myproject
ntm --robot-inspect-agent=myproject:2
ntm --robot-inspect-work=br-123
ntm --robot-inspect-coordination=<agent>
ntm --robot-inspect-quota=<provider>/<account>
ntm --robot-inspect-incident=<incident-id>
```

### Safe Restart Pattern

Raw `--robot-interrupt` is honest but blunt. Prefer the polite-probe-then-act pair:

```bash
# 1. Probe first
ntm --robot-is-working=myproject --panes=2,3        # structured working/idle state (indicator_basis, pane_pid, agent_cli_dead, agent_uptime_seconds)
ntm --robot-probe=myproject --panes=2                # responsiveness probe (numeric pane indices ONLY — %N/W.P rejected; bare index = whole window on multi-window, read pane_ref)
ntm --robot-probe=myproject --panes=2 --probe-method=wake_ping   # structured rate-limit liveness in one call
ntm --robot-diagnose=myproject                       # comprehensive health + recommendations

# 2. Act with smart defaults that refuse to interrupt working agents
ntm --robot-smart-restart=myproject --panes=2        # safe — checks --robot-is-working first
ntm --robot-restart-pane=myproject --panes=2 --type=claude --dry-run
#    restart-pane: failed prompt delivery → success:false + PROMPT_SEND_FAILED; compare
#    pane_shell_pids before/after (unchanged shell PID = that pane's restart FAILED);
#    --restart-model / --restart-agent-args override the relaunch

# 2b. Graceful lifecycle ladder when a full restart is too blunt
ntm --robot-exit-cli=myproject --panes=2 --relaunch  # verified double-Ctrl+C graceful CLI exit (+ optional relaunch)
ntm --robot-kill-agent=myproject --panes=2           # SIGTERM→SIGKILL the agent process tree; shell and pane survive
ntm --robot-kill-pane=myproject --panes=2            # remove the pane itself; session and siblings survive (explicit --panes required)

# 3. Only use raw interrupt when you've decided to override
ntm --robot-interrupt=myproject --panes=2 --msg="Stop and reconsider."
```

### Assignment and Routing

```bash
ntm --robot-assign=myproject --strategy=dependency
ntm --robot-bulk-assign=myproject --from-bv           # one-shot: assign bv top picks to idle agents
ntm --robot-route=myproject --strategy=sticky   # least-loaded, first-available, round-robin, round-robin-available, random, sticky, explicit
```

### Context and Health

```bash
ntm --robot-context=myproject                         # context-window usage per agent (anticipate rotation)
ntm --robot-agent-health=myproject
ntm --robot-health=myproject                          # bare --robot-health = project-wide rollup
ntm --robot-health-oauth=myproject                    # includes per-provider `pools` rollup + rotate/route recommendation
ntm --robot-health-restart-stuck=myproject            # skips blocked/rate-limited panes with typed reasons (restart cannot fix those)
ntm --robot-monitor=myproject --interval=30s
ntm --robot-metrics=myproject --metrics-period=1h
```

### Files, Replay, Support

```bash
ntm --robot-files=myproject --files-window=6h
ntm --robot-replay=myproject --replay-id=<id>
ntm --robot-support-bundle=myproject
ntm --robot-save=myproject
ntm --robot-restore=/path/to/snapshot.json
```

## Beads, Mail, and CASS

```bash
ntm --robot-beads-list --beads-status=open
ntm --robot-bead-show=br-123
ntm --robot-bead-claim=br-123 --bead-assignee=agent1
ntm --robot-bead-create --bead-title="..." --bead-type=task --bead-priority=2
ntm --robot-bead-close=br-123 --bead-close-reason="Completed"
ntm --robot-watch-bead=myproject                   # stream bead activity for a session

ntm --robot-mail                                    # machine-readable mail digest
ntm --robot-mail-check --mail-project=myproject --urgent-only
ntm --robot-context-inject=myproject                # inject mail + work context into panes

ntm --robot-cass-status
ntm --robot-cass-search="authentication error"
ntm --robot-cass-insights
ntm --robot-cass-context=<task-description>
```

Graph-aware triage (wraps bv):

```bash
ntm --robot-triage --triage-limit=10
ntm --robot-plan
ntm --robot-graph
ntm --robot-forecast=all
ntm --robot-impact=<path>
ntm --robot-search=<query>
ntm --robot-label-health
ntm --robot-label-flow
ntm --robot-label-attention
ntm --robot-file-beads=<path>      ntm --robot-file-hotspots      ntm --robot-file-relations=<path>
```

These are useful when a script or agent needs structured access to work state,
coordination state, or past-session search.

## Human-Friendly Robot Views

When JSON is too heavy but you still need automation-friendly output:

```bash
ntm --robot-markdown
ntm --robot-markdown --md-compact
ntm --robot-terse
```

Use `--robot-terse` for operator summaries. Use `--robot-markdown` when a human
or another model benefits from lower-token tables instead of raw JSON.

## Robot Flag Navigation Index

Grouped by purpose. Treat this as a navigation index, then query
`ntm --robot-capabilities` for the current flags, parameters, and examples.

### Discovery / docs

- `--robot-help`
- `--robot-status`
- `--robot-version` (plain `ntm --version` since v1.23; `-V` shorthand since v1.29)
- `--robot-capabilities`
- `--robot-docs=<topic>` — `quickstart|commands|examples|exit-codes`
- `--robot-schema=<type>` — `all` dumps every schema
- `--robot-default-prompts`

### State / snapshots / formats

- `--robot-snapshot`
- `--robot-terse`
- `--robot-markdown` / `--md-compact`
- `--robot-dashboard`
- `--robot-format=json|toon|auto`
- `--robot-output-format` (DEPRECATED)
- `--robot-verbosity=terse|default|debug`
- `--robot-limit N` / `--robot-offset N`
- Pagination scope is exact and machine-checkable (v1.25+): every list-shaped
  schema type is flagged `paginated: true/false` with a reason, exposed per
  surface by `--robot-capabilities` (`paginated`/`paginated_reason`, plus a
  `pagination_contract_violations` self-check that is empty on healthy builds).
  The offset-paginated CLI surfaces are `list`, `history`, `audit show/search`,
  `checkpoint list`, `approve list`; other list surfaces use cursor/limit
  truncation. Critical arrays are always `[]`, never `null` — an encoder
  invariant on every envelope, success and failure alike.

### Events / attention

- `--robot-events --since-cursor=N --events-limit=M`
- `--robot-attention`
- `--robot-digest`
- `--robot-alerts`
- `--robot-dismiss-alert=<id>`
- `--robot-overlay`

### Pane inspect / tail / watch

- `--robot-tail=<session> --panes=N,M --lines=L [--fresh]`
- `--robot-pane-address=<session>` — canonical base-index-immune addressing cards
- `--robot-dialogs=<session>` — classify in-pane dialogs (trust_prompt, rate_limit_options, …)
- `--robot-watch-bead=<session>`
- `--robot-errors=<session>`
- `--robot-inspect-pane=<session> --inspect-index=N --inspect-lines=L --inspect-code`
- `--robot-inspect-session=<session>`
- `--robot-inspect-agent=<session:pane>`
- `--robot-inspect-work=<bead-id>`
- `--robot-inspect-coordination=<agent>`
- `--robot-inspect-quota=<provider/acct>`
- `--robot-inspect-incident=<id>`

### Activity / health / diagnose

- `--robot-activity=<session>` — agents include `output_sequence {epoch, sequence}`: sequence advances only on real pane-content change (flat across ticks = no new output); same signal enriches status agents
- `--robot-is-working=<session> --panes=N,M`
- `--robot-agent-health=<session>`
- `--robot-health[=<session>]` — bare form = project-wide
- `--robot-health-oauth=<session>`
- `--robot-health-restart-stuck=<session> --stuck-threshold=<dur>` — declines blocked (interactive-gate) and rate-limited panes with typed skip reasons: a restart cannot answer a gate or lift a rate limit
- `--robot-diagnose=<session> [--diagnose-fix]`
- `--robot-context=<session>`
- `--robot-logs=<session>`

### Control / mutate

- `--robot-send=<session> --panes=N --msg="..."` (or `--msg-file=-` for stdin; `--message` aliases `--msg`; `--clear-input`; `--verify-render` for rendered-delivery evidence; `--op-id=<id>` for durable idempotent sends, incompatible with `--track`; `--with-memory` prepends top CM rules as a compact project-rules block within `[memory] send_budget_tokens` — enrichment only, an unavailable cm records a skip on the envelope and still sends; `--with-cass` / `--no-cass` toggle send-time CASS session-context injection per `[cass.context]`, same degrade-gracefully contract)
- `--robot-send-receipt=<op-id>` — replay a prior `--op-id` send's per-target admission receipts
- `--robot-ack=<session> --timeout=30s`
- `--robot-interrupt=<session> --panes=N --msg="..."`
- `--robot-smart-restart=<session> --panes=N [--force] [--hard-kill]`
- `--robot-restart-pane=<session> --type=claude --panes=N --dry-run [--restart-model=<m[@effort]>] [--restart-agent-args=...]`
- `--robot-exit-cli=<session> --panes=N [--relaunch]` — verified graceful CLI exit
- `--robot-kill-agent=<session> --panes=N [--relaunch]` — kill agent tree; shell survives
- `--robot-kill-pane=<session> --panes=N` — remove pane; session survives
- `--robot-answer-dialog=<session> --panes=N --choice=<decline|extra-usage|dismiss|option-K>`
- `--robot-incident-resolve=<id> [--incident-note=...]`
- `--robot-probe=<session> --panes=N [--probe-method=wake_ping]`
- `--robot-save=<session>`
- `--robot-restore=<path>`
- `--robot-switch-account=<provider[:acct]>`

### Sessions / spawn / controller

- `--robot-spawn=<session> --spawn-cc=N ...` — with `--spawn-assign-work`, `--strategy` picks the work-pairing strategy: `top-n` (default), `diverse`, `dependency-aware`, `skill-matched` (v1.29: routes through the agent capability matrix with per-assignment `assign_reason` rationale)
- `--robot-controller-spawn=<session>`
- `--robot-agent-names=<session>`

### Assign / route / distribute

- `--robot-assign=<session> --strategy=<s>` — `simple` (default; honest name for the historical sequential pairing), `balanced`, `speed`, `quality`, `dependency` run the real planner and carry its `confidence`
- `--robot-bulk-assign=<session> --from-bv`
- `--robot-route=<session> --strategy=<s> [--last-agent=%N]` — `--last-agent` anchors rotation across stateless invocations

### Work / beads / bv

- `--robot-plan`
- `--robot-graph`
- `--robot-triage --triage-limit=N`
- `--robot-suggest`
- `--robot-forecast=<id|all>`
- `--robot-impact=<path>`
- `--robot-search=<query>`
- `--robot-label-attention`
- `--robot-label-flow`
- `--robot-label-health`
- `--robot-file-beads=<path>`
- `--robot-file-hotspots`
- `--robot-file-relations=<path>`
- `--robot-beads-list`
- `--robot-bead-claim=<id> --bead-assignee=<a>`
- `--robot-bead-create --bead-title=<t> --bead-type=<t> --bead-priority=<n>`
- `--robot-bead-show=<id>`
- `--robot-bead-close=<id> --bead-close-reason=<r>`

### Pipeline

- `--robot-pipeline-run=<file> --pipeline-session=<s>` (run)
- `--robot-pipeline=<run-id>` (**status**)
- `--robot-pipeline-list`
- `--robot-pipeline-cancel=<run-id>`

### Mail / coordination

- `--robot-mail`
- `--robot-mail-check --mail-project=<project> [filters]`
- `--robot-context-inject=<session>`

### CASS

- `--robot-cass-status`
- `--robot-cass-search=<q>`
- `--robot-cass-insights`
- `--robot-cass-context=<task>`

### Ensemble / modes

- `--robot-ensemble-modes`
- `--robot-ensemble-presets`
- `--robot-ensemble=<session>`
- `--robot-ensemble-spawn=<session> --preset=<name> --question=<text>`
- `--robot-ensemble-suggest=<question>`
- `--robot-ensemble-stop=<session>`

### Monitor / tools / bundle

- `--robot-monitor=<session> --interval=30s`
- `--robot-support-bundle=<session>`
- `--robot-files[=<session>] --files-window=<dur>` — bare form = project-wide
- `--robot-metrics[=<session>] --metrics-period=<dur>` — bare form = project-wide
- `--robot-replay=<session> --replay-id=<id>`
- `--robot-diff=<session> --since=<dur>`
- `--robot-summary=<session> --since=<dur>`
- `--robot-history=<session>`
- `--robot-tokens`
- `--robot-wait=<session> --wait-until=<cond> [--wait-id=<handle>]`
- `--robot-wait-cancel=<wait-id>` — cancel a durable wait from any process

### Palette / recipes / setup / profile

- `--robot-palette`
- `--robot-recipes`
- `--robot-setup` / `--robot-acfs-status`
- `--robot-profile-list` / `--robot-profile-show=<name>`

### Integrations

See `INTEGRATIONS.md` for DCG, SLB, CAAM, RCH, RANO, quota, ru, giil, JFP, MS, XF.
