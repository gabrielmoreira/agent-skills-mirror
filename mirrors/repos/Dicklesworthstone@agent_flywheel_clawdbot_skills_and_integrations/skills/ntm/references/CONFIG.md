# NTM Configuration and Project Resolution

Use this file when `spawn`, `quick`, templates, or project-local overrides behave
in surprising ways.

## Project Resolution

`ntm spawn <name>` expects NTM to resolve `<name>` to a project directory.

```bash
ntm config get projects_base
ntm quick myproject --template=go
```

If the repo is elsewhere, make it resolvable from `projects_base` or use the repo's
preferred layout.

Labels extend the session name as:

```text
project--frontend
project--backend
```

That means:

```bash
ntm quick myproject --label frontend
ntm spawn myproject --label frontend --cc=2
ntm add myproject --label frontend --cc=1
```

## Useful Config Commands

```bash
ntm config init
ntm config show
ntm config path                     # print resolved config file path
ntm config diff                     # show deltas from defaults
ntm config get projects_base
ntm config set projects-base <path> # convenience shortcut (note: dashes, not underscores)
ntm config validate
ntm config edit
ntm config reset --confirm          # destructive; requires confirmation
ntm config project init [--force]   # seed a .ntm/ tree in the current project
```

## Config Sections That Move Around

- Restart/monitoring settings live under `[resilience]` (`auto_restart`, `max_restarts`,
  `restart_delay_seconds`, `health_check_seconds`, `crash_threshold`). The old `[health]`
  section no longer exists.
- Rotation auto-trigger is `[rotation] auto_trigger`. The coordinator's
  context-rotation trigger is `[rotation] usage_percent_threshold` (default `0`
  = off; transcript-sourced usage only, safety gates re-checked at fire time).
- CAAM auto-failover is `[integrations.caam] auto_failover` (default off, and
  doubly opt-in: `failover_providers` must also be non-empty).
- CM send-time rule injection is `[memory] send_injection` (default off;
  per-call `--with-memory` works regardless), with `send_max_rules` and
  `send_budget_tokens`.
- `ntm bugs watch` push routing is `[bugs] push_routing` (opt-in).
- The coordinator mail nudge (v1.28, default off) is `[coordinator] mail_nudge`,
  with `nudge_cooldown_seconds` and `nudge_message` — idle panes with unread
  Agent Mail get a composer-verified "check your inbox" nudge; never into a
  working pane, fail-closed for undetectable agent types.
- Every bv subprocess is bounded by `[integrations.bv] timeout_seconds`
  (default 30) / env `NTM_BV_TIMEOUT` (v1.28) — `BV_*` env vars you set reach
  the child, so `BV_NO_CACHE=1` wrappers work without hacks.
- Send-time CASS context injection is `[cass.context]` (`enabled`,
  `max_sessions`, `lookback_days`, `max_tokens`, `min_relevance`,
  `skip_if_context_above`, `prefer_same_project`); per-call `--with-cass` /
  `--no-cass` override it on both send surfaces.
- Per-pane Claude credential isolation is opt-in via `[agents] claude_isolate_credentials`
  plus `claude_token_file` — the token is passed by reference, never typed into the pane.
- `ntm coordinator enable/disable <feature>` persists the flag into the **global**
  `~/.config/ntm/config.toml` by default (not project `.ntm/config.toml`), preserving
  comments; a running coordinator daemon does not pick it up — restart it.

## Removed / Deprecated Config Keys Fail The Loader

NTM has been deleting reader-less config knobs in staged batches. As of
v1.29.0, **two whole batches of formerly-valid keys are hard strict-loader
errors** — a config that still sets one refuses to load, listing every
offending key with its disposition:

> **Automatic cleanup (v1.29.2+): run `ntm config migrate`.** It surgically
> deletes every removed/deprecated key from the config file (timestamped
> backup written first; comments and all live keys byte-preserved; emptied
> tables removed; `--dry-run` and `--json` supported). All these keys were
> provable no-ops, so behavior cannot change. v1.29.2 also collapses the
> startup warning to one line and keeps `ntm shell`/completion output
> byte-clean, so new terminal panes never see a warning wall.

- Removed in v1.26.0, error since v1.27.0: `tmux.palette_key`, extra
  `integrations.caam.*` leaves, all `[integrations.caut]` and
  `[integrations.proxy]`, `integrations.process_triage.on_stuck`,
  `integrations.rano.persist_history`/`.history_days`,
  `integrations.xf.{bin_path,archive_path,default_mode}`
  (`integrations.xf.enabled` stays live), `[rotation.dashboard]`,
  `[swarm.limit_patterns]`, `[swarm.marching_orders]`,
  `[retry.{scheduler,completion,db,assign}]`,
  `memory.include_anti_patterns`/`.include_history`.
- Deprecated in v1.28.0, error since v1.29.0 (128 keys): the whole
  `[accounts]` section, all `[scanner.*]` except `scanner.ubs_path`, the
  `[spawn_pacing]` rate/backoff/headroom subset, the `[cass]` dead subset
  (`[cass]` core + `[cass.context]` stay live), several integrations leaves
  (`caam.{enabled,auto_rotate,providers}`, `rano.{binary_path,providers}`,
  `process_triage.binary_path`, most `rch.*`), the `[checkpoints]` auto
  subset, `[tmux.activity_indicators]`,
  `robot.output.{pretty,timestamps,compress}`, `rotation.prefer_restart`,
  `rotation.accounts.priority`, and seven singles.

None of these ever had an effect — the fix is always to **delete the key**
(the load error and `ntm doctor` both name each one; doctor scans leniently,
which is useful precisely when the strict loader refuses to start). Never
paste config snippets from pre-v1.26 docs into a current config.

## User-Level Assets

Common user-level locations:

- `~/.config/ntm/config.toml`
- `~/.config/ntm/recipes.toml`
- `~/.config/ntm/workflows/`
- `~/.config/ntm/personas.toml`
- `~/.config/ntm/templates/`
- `~/.ntm/policy.yaml`

## Project-Level Assets

Project-local assets usually live under `.ntm/` and override user defaults where appropriate.

Common examples:

- `.ntm/workflows/`
- `.ntm/pipelines/`
- `.ntm/templates/`
- `.ntm/personas.toml`
- `.ntm/recipes.toml`
- `.ntm/checkpoints/`

These matter because session templates, prompt templates, workflows, pipelines, and
persona definitions are often project-specific rather than globally shared.
