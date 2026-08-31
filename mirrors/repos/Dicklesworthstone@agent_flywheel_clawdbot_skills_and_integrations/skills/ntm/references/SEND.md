# `ntm send` — Exhaustive Flag Reference

## Contents

- [Default targeting behavior](#default-targeting-behavior)
- [Agent-type selectors (with `:variant` filter)](#agent-type-selectors-with-variant-filter)
- [Pane selectors](#pane-selectors) — `--pane`, `--panes`, `--all`, `--include-user`, `-s/--skip-first`, `--project`, `--tag`
- [Input sources](#input-sources) — `--file`, stdin, positional, priority order
- [Base prompt (prepended to every target)](#base-prompt-prepended-to-every-target)
- [`-c/--context` file-range injection](#-c--context-file-range-injection)
- [Templates and variables](#templates-and-variables) — `-t/--template`, `--var`
- [Smart routing (`--smart` + `--route`)](#smart-routing---smart----route)
- [Distribute mode (auto-distribute from bv triage)](#distribute-mode-auto-distribute-from-bv-triage)
- [Batch / broadcast](#batch--broadcast)
- [CASS duplicate-detection](#cass-duplicate-detection) — `--cass-check`, `--no-cass-check`, workarounds
- [Send-time CASS context injection](#send-time-cass-context-injection---with-cass----no-cass) — `--with-cass`, `--no-cass`
- [Shell quoting for prompt payloads](#shell-quoting-for-prompt-payloads-field-incident)
- [Canonical flag spellings per surface](#canonical-flag-spellings-per-surface-stop-guessing)
- [Prefix, suffix, hooks, dry-run](#prefix-suffix-hooks-dry-run)
- [Output shapes](#output-shapes)
- [Error matrix](#error-matrix)
- [Scenario catalog](#scenario-catalog) — 10 copy-ready recipes

---

Covers every flag registered in `/dp/ntm/internal/cli/send.go`. Source citations use
`send.go:line` shorthand; all paths are under `/dp/ntm/internal/cli/`.

## Default targeting behavior

With **no** target flags, `send` targets every agent pane and excludes every pane
typed as `user`. It does not assume that the user pane is first, so `--no-user`
sessions retain their first agent. Preview shell sends with `--dry-run` when pane
typing or session topology is uncertain.

- `--all` overrides type/tag filters but still targets agent panes only; the user
  pane stays excluded unless you add `--include-user` (deliberate shell input only).
- `-s/--skip-first` skips only the first pane in deterministic
  `(window_index, pane_index, pane_id)` order. It is not an all-user-pane exclusion
  mechanism — and since `--all` now excludes the user pane by itself, the old
  broadcast `--skip-first` recipes are obsolete.

## Agent-type selectors (with `:variant` filter)

Custom flags implemented by `sendTargetValue` (`send.go:297-341`). All three accept
`NoOptDefVal=true`, so bare `--cc` means "any Claude pane," while `--cc=opus` filters
by `tmux.Pane.Variant` exact equality.

| Flag | AgentType | Example | Notes |
|------|-----------|---------|-------|
| `--cc[=variant]` | `cc` (Claude) | `--cc=opus` | Variant is an open string, not pre-enumerated |
| `--cod[=variant]` | `cod` (Codex) | `--cod=gpt-5` | |
| `--agy[=variant]` | `agy` (Gemini via Antigravity CLI) | `--agy` | **Preferred Gemini provider** (NTM-pinned; the pin is `Gemini 3.7 Flash (High)` since v1.29.0 — was `Gemini 3.1 Pro (High)` before) |
| `--gmi[=variant]` | `gmi` (Gemini via the legacy Gemini CLI, retired 2026-06-18; still accepted for legacy panes) | `--gmi=pro` | Use `--agy` for Gemini today |

`--cc=false` is treated as a no-op. Selectors can be combined: `--cc --cod` sends
to all Claude + Codex panes. Explicit `--pane` / `--panes` selectors take
precedence over agent-type and tag filters; do not combine them when the intent is
an intersection.

## Pane selectors

| Flag | Type | Purpose | Source |
|------|------|---------|--------|
| `-p/--pane` | string | Exactly one `N`, `W.P`, or `%N` selector | `send.go:newSendCmd` |
| `--panes` | string | Strict CSV of `N`, `W.P`, and `%N` selectors | `send.go:parseShellPaneSelectors` |
| `--all` | bool | Override type/tag filters (agent panes only; user pane excluded) | `send.go:925` |
| `--include-user` | bool | Opt the user/control pane into a `--all` broadcast | `send.go:926` |
| `-s/--skip-first` | bool | Skip only the first returned pane (rarely needed now) | `send.go:928` |
| `--project` | string | Broadcast to all sessions sharing a `SessionBase` | `send.go:775` |
| `--tag` (repeatable) | []string | Match panes by tag (OR logic) | `send.go:735` |

The selector grammar matches robot send:

- `%N` is one exact tmux pane ID.
- `W.P` is one exact `window_index.pane_index` address.
- Bare `N` selects pane index `N` in a single-window session. In a multi-window
  session it selects window `N`; plural `--panes=N` may therefore select every pane
  in that window, while singular `--pane=N` fails if that window has more than one
  pane.

Every token must match. Missing or malformed selectors fail before hooks,
checkpoints, or pane actuation. Aliases that name the same physical pane are
deduplicated by tmux pane ID. Multi-window JSON, dry-run, history, hook, and pacing
surfaces emit canonical `W.P` references plus pane IDs where the schema provides
one.

### Conflicts

- `--pane` + `--panes` → `cannot use --pane and --panes together` (`send.go:658`).
- `--skip-first` + explicit `--pane` / `--panes` → rejected instead of silently
  ignoring `--skip-first`.
- `--skip-first` + `--smart` or `--distribute` → rejected as nonsensical.
- `--project` + specific session name → `cannot use --project with a specific session name` (`send.go:580`).

### `--all` vs `--project`

These are orthogonal axes.

- `--all` scope: **agent panes within one session**; add `--include-user` for the user pane.
- `--project` scope: **all sessions whose `SessionBase(name)` matches**, iterates each session and applies the intra-session pane filter independently.

You can combine them: `ntm send --project myproject --all "x"` → every agent pane of every session variant (add `--include-user` to hit each session's user pane too).

## Input sources

Resolved by `getPromptContent` (`send.go:851-891`) in priority order. First match wins.

| Priority | Source | Flag | Source-label in JSON |
|----------|--------|------|----------------------|
| 1 | File | `-f/--file` (`-` = stdin) | `file:<path>` |
| 2 | Stdin | (pipe; only when no args) | `stdin` |
| 3 | Positional args | (joined with spaces) | `args` |

- `--file=-` reads the prompt from stdin explicitly, keeping payloads off the
  scanned command line (robot twin: `--msg-file=-`; >10MB rejected).
- Empty file errors at `send.go:862`.
- Empty stdin with no prefix errors at `send.go:878`.
- `--prefix` / `--suffix` (`send.go:730-731`) wrap file or stdin content; **ignored for positional args** (`send.go:889`).

## Base prompt (prepended to every target)

- `--base-prompt <string>` (`send.go:763`).
- `--base-prompt-file <path>` (`send.go:764`).
- Config fallbacks: `cfg.Send.BasePrompt`, `cfg.Send.BasePromptFile` (`send.go:594-595`).

Resolution precedence: flag string > flag file > config string > config file (`send.go:597`).

## `-c/--context` file-range injection

Repeatable `StringArray` (`send.go:732`). Parsed by `prompt.ParseFileSpec` (`send.go:698`).

Syntax (documented at `send.go:539`):

| Form | Meaning |
|------|---------|
| `path` | Whole file |
| `path:10-50` | Lines 10–50 inclusive |
| `path:10-` | Line 10 through end |
| `path:-50` | Start through line 50 |

Multiple `-c` accumulate in order. `prompt.InjectFiles` (`send.go:705`) prepends them to
the final prompt with file headers + code fences.

```bash
ntm send myproject --cc \
  -c internal/auth/service.go:1-80 \
  -c internal/auth/middleware.go \
  "Review these handlers side by side and propose a unification."
```

## Templates and variables

- `-t/--template <name>` (`send.go:733`): loads named template via the template loader.
- `--var key=value` repeatable (`send.go:734`).

Templates are resolved from project `.ntm/templates/` then user `~/.config/ntm/templates/`
(enumerate with `ntm template list`).

Template engine supports:

- `{{variable}}` substitution
- `{{#var}}...{{/var}}` conditional blocks (non-empty → include)
- `{{file}}` auto-bound to `--file` content

When `-t` is given the input path flows through `runSendWithTemplate` (`send.go:686`).

```bash
ntm send myproject --cc \
  -t fix \
  --var issue="nil pointer deref in JWT validator" \
  --var severity="P0" \
  --file internal/auth/service.go
```

## Smart routing (`--smart` + `--route`)

| Flag | Default | Source |
|------|---------|--------|
| `--smart` | false | `send.go:738` |
| `--route <strategy>` | `""` | `send.go:739` |

Strategies (validated at dispatch; the `--help` text still lists a stale set): `least-loaded`,
`first-available`, `round-robin`, `round-robin-available`, `random`, `sticky`, `explicit`.
`affinity` is **rejected** (`invalid routing strategy`).

Decision returned in `SendResult.RoutedTo *SendRoutingResult` (`send.go:172-179`) with
`{PaneIndex, AgentType, Strategy, Reason, Score}`.

Routing state is durable and keyed by `(session, filter)` (v1.27): `sticky`
and `round-robin` persist per-session cursors across invocations
(pane-anchored — vanished panes are skipped, not double-served), `random` is
genuinely random, and dry runs never advance persisted cursors. Filter-key
canonicalization through the agent-type alias resolver and
kill-clears-routing-state landed one release later (v1.28).

## Distribute mode (auto-distribute from bv triage)

| Flag | Default | Source |
|------|---------|--------|
| `--distribute` | false | `send.go:952` |
| `--dist-strategy` | `simple` | `send.go:953` |
| `--dist-limit N` | 0 (one per idle agent) | `send.go:954` |
| `--dist-auto` | false (skip confirmation) | `send.go:955` |

Valid `--dist-strategy`: `simple` (historical sequential pairing — the honest
default name since v1.25), `balanced`, `speed`, `quality`, `dependency`. The
non-simple strategies run the real graph-aware planner and produce genuinely
different assignments; envelopes carry the planner's `confidence` and report
`"strategy": "simple"` when you never pass the flag.

`--dist-auto` + `--dry-run` is rejected (`send.go:806`). Use one or the other.

## Batch / broadcast

| Flag | Default | Source |
|------|---------|--------|
| `--batch <file>` | `""` | `send.go:767` |
| `--delay <dur>` | `""` (parsed by `time.ParseDuration`) | `send.go:768` |
| `--confirm-each` | false | `send.go:769` |
| `--stop-on-error` | false | `send.go:770` |
| `--broadcast` | false | `send.go:771` |
| `--agent <idx>` | -1 (round-robin) | `send.go:772` |
| `--randomize` | false | `send.go:756` |
| `--seed <int64>` | 0 (time-based) | `send.go:757` |
| `--priority-order` | false | `send.go:760` |

Batch file format: one prompt per line, or `---` separated blocks (`send.go:767`).

Randomization uses xorshift64 Fisher-Yates (`send.go:424-441`). Seed 0 uses
`time.Now().UnixNano()` and the chosen value is returned as `SeedUsed` in the JSON
result so you can reproduce.

> `--confirm-each` in batch mode **blocks on stdin** per prompt, and without a TTY it
> now errors up front instead of hanging. In automation or cron, omit it.

## CASS duplicate-detection

Default ON. CASS (Cross Agent Session Search) queries past sessions for prompts similar
to what you're about to send and asks for confirmation if one is found. Without a TTY
the confirm no longer blocks: the send proceeds with a stderr warning.

| Flag | Default | Source |
|------|---------|--------|
| `--cass-check` | true | `send.go:748` |
| `--no-cass-check` | false | `send.go:749` |
| `--cass-similarity <float>` | 0.7 | `send.go:750` |
| `--cass-check-days N` | 7 | `send.go:751` |
| `--loop-mode` | false | `send.go:952` |

In practice this blocks repeat-sends in tending loops. Ways to bypass:

1. **Per-call (recommended in scripts):** `ntm send ... --no-cass-check`.
2. **Structural (recommended for automation):** `ntm --robot-send=<session>` is non-interactive and never prompts (`--no-cass-check` is also accepted there).
3. **Tending loops:** `--loop-mode` is the sanctioned dedup exemption for repeated orchestration nudges (replaces the old rotating-suffix trick).
4. **Recovery wrappers:** `--force-non-interactive` bypasses the CASS confirm class only; destructive/ambiguous confirm classes still fail closed.

## Send-time CASS context injection (`--with-cass` / `--no-cass`)

Since v1.25 both send surfaces (`ntm send` and `--robot-send`) can inject
relevant past-session CASS context above the prompt:

| Flag | Effect |
|------|--------|
| `--with-cass` | Inject relevant CASS session context before sending; degrades gracefully (a missing/wedged cass records a skip and still sends) |
| `--no-cass` | Disable injection for this send, overriding `[cass.context] enabled=true` |

Config: `[cass.context]` `enabled` / `max_sessions` / `lookback_days` /
`max_tokens` / `min_relevance` / `skip_if_context_above` / `prefer_same_project`.
Injected context is redacted and framed as data-not-instructions. Do not
confuse with `--with-memory` (CM rules) or `--cass-check`/`--no-cass-check`
(duplicate detection) — three independent mechanisms.

## Shell quoting for prompt payloads (field incident)

Backticks and `$(...)` inside a **double-quoted** `--msg`/positional prompt are
executed by YOUR shell before ntm ever sees them — a prompt describing
`` `rm -rf target` `` in double quotes runs it locally. Rules:

- Single-quote every literal prompt payload: `--msg='...'`.
- For anything multi-line or containing quotes/backticks/`$`, use
  `--msg-file=-` (robot) or `--file` (shell send) and pipe the payload in —
  this also keeps the text off the scanned command line so dcg-style filters
  can't mistake message content for executable commands (see AP-52).
- Never interpolate untrusted pane output into a double-quoted dispatch.

## Canonical flag spellings per surface (stop guessing)

The most common `INVALID_FLAG` class in fleet history is agents guessing
`--message`, `--session`, `--pane`, or `--project-dir` on the wrong surface.
The real spellings:

| Surface | Session | Message | Pane targeting |
|---|---|---|---|
| `ntm send` | positional: `ntm send <session>` | positional text, or `-f/--file` (`-` = stdin) — there is **no `--msg`** here | `--pane` (one) or `--panes` (CSV), `--cc/--cod/--agy` |
| `ntm --robot-send` | flag value: `--robot-send=<session>` — **no `--session`** | `--msg` (`--message` accepted alias since v1.23) or `--msg-file` | `--panes` (CSV), or singular `--pane` for exactly one pane (also valid with `--robot-history`) |
| `ntm --robot-tail` | `--robot-tail=<session>` | — | `--panes`, `--lines`, `--fresh` |
| `ntm --robot-pipeline-run` (also `--robot-tokens`/`--robot-alerts`/`--robot-palette`) | `--session=<s>` (the only robot surfaces that DO use `--session`) | — | — |
| `ntm --robot-probe` | `--robot-probe=<session>` | — | `--panes` = numeric window-local indices ONLY |

There is no `--project-dir` anywhere — project resolution goes through
`projects_base`/`NTM_PROJECTS_BASE`. Unknown flags fail loudly with
`INVALID_FLAG` plus a did-you-mean `hint`; read the hint instead of retrying
blind.

Delivery mechanics (v1.29): sends go through tmux `load-buffer` + `paste-buffer -d`,
and buffer names are collision-proof across processes (`ntm-<pid>-<nanos>-<seq>`),
so concurrent ntm processes sharing one tmux server cannot delete each other's
in-flight paste buffers. All session `-t` targets are pinned with tmux's
exact-match `=` sigil, so a send to `foo` can never prefix-resolve into `foo_bar`.

## Prefix, suffix, hooks, dry-run

| Flag | Purpose | Source |
|------|---------|--------|
| `--prefix <str>` | Prepend to prompt (file/stdin sources only) | `send.go:730` |
| `--suffix <str>` | Append to prompt (file/stdin sources only) | `send.go:731` |
| `--clear-input` | Clear residual composer text (per-agent Escape/C-u ritual, verified) before typing; recommended after interrupts on codex panes | `send.go:927` |
| `--no-hooks` | Disable PreSend/PostSend hook chain | `send.go:752` |
| `--dry-run` | Emit `SendDryRunResult` without sending | `send.go:753` |

## Output shapes

### Normal send (`SendResult`, `send.go:49-64`)

```json
{
  "success": true,
  "session": "myproject",
  "targets": ["1.0"],
  "delivered": 1,
  "failed": 0,
  "routed_to": { "pane_index": 0, "pane": "1.0", "pane_id": "%7", "agent_type": "cc", "strategy": "least-loaded", "reason": "idle for 34s", "score": 0.92 },
  "randomized": false,
  "seed_used": 0,
  "error_code": ""
}
```

### Dry-run (`SendDryRunResult`, `send.go:75-88`)

```json
{
  "would_send": [
    { "pane": "1.0", "pane_id": "%7", "agent": "cc_1", "prompt": "...", "prompt_preview": "...", "source": "file:task.md", "priority": 0 }
  ]
}
```

## Error matrix

| Condition | Message |
|-----------|---------|
| `--pane` + `--panes` | `cannot use --pane and --panes together` |
| Malformed selector | `invalid pane selector ...: expected N, W.P, or %N` |
| Selector matches nothing | `pane selector ... not found; available: ...` |
| Singular selector matches multiple panes | `pane selector ... matched N panes ...; use explicit W.P or %N` |
| `--skip-first` + `--pane` / `--panes` | Rejected as incompatible |
| `--skip-first` + `--smart` / `--distribute` | Rejected as incompatible |
| `--batch` + `--pane` / `--panes` | Rejected; use batch `--agent` |
| `--project` + session arg | `cannot use --project with a specific session name` |
| No session + no `--project` | `session name required (or use --project)` |
| `--project` with zero matches | `no sessions found for project %q` |
| Empty file or stdin with no prefix | `prompt content is empty` |
| `--dist-auto` + `--dry-run` | Rejected as incompatible |
| Agent pane's CLI exited to a bare shell | `PANE_AGENT_DEAD` + restart guidance (also on `--robot-send`) |
| Composer still holds text after `--clear-input` | `COMPOSER_NOT_CLEARED`; inspect with `--robot-tail` before resending |

## Scenario catalog

### 1. One-shot message to all Claude agents

```bash
ntm send myproject --cc "Summarize current blockers in three bullets."
```

### 2. Target two specific panes with a file prompt

```bash
ntm send myproject --panes=0.2,%7 --file prompts/refactor.md
```

### 3. File-range context injection for code review

```bash
ntm send myproject --cc=opus \
  -c internal/auth/jwt.go:40-120 \
  -c internal/auth/middleware.go:1-60 \
  --prefix "Context: we're hardening JWT validation." \
  "Review and propose concrete fixes."
```

### 4. Smart-routing a new task to the least-loaded agent

```bash
ntm send myproject --smart --route=least-loaded \
  "Take the next ready authentication bead and implement."
```

### 5. Distribute bv triage across idle agents

```bash
ntm send myproject --distribute --dist-strategy=dependency --dist-auto
```

### 6. Scripted batch with deterministic ordering

```bash
ntm send myproject --batch prompts.txt --delay=30s --seed=42 --stop-on-error
```

### 7. Cross-session broadcast to every label variant

```bash
ntm send --project myproject \
  "Sync to main and report any conflicts you encounter."
```

### 8. Non-interactive send from an automation loop

```bash
ntm --robot-send=myproject --panes=2 \
    --msg="Checkpoint and continue with the current plan." \
    --type=cc
# --message is an accepted alias of --msg. For crash-safe loops, add
# --op-id=<stable-id>: identical retries replay the recorded outcome instead of
# re-sending (conflicting reuse → IDEMPOTENCY_CONFLICT; not with --track), and
# `ntm --robot-send-receipt=<op-id>` re-queries the per-target receipts.
# For repeated `ntm send` nudges in a tending loop, use --loop-mode instead of
# mutating the message each pass.
# --with-memory prepends the top CM (cass-memory) rules as a compact
# project-rules block within [memory] send_budget_tokens; enrichment only —
# a missing or wedged cm records a skip on the envelope and still sends
# ([memory] send_injection=true makes it the robot-send default).
```

### 9. Template + variables + file

```bash
ntm send myproject --cc \
  -t fix --var issue="nil deref" --file internal/auth/jwt.go
```

### 10. Bypass CASS dedup for a retry

```bash
ntm send myproject --pane=2 --no-cass-check "Please retry; previous send was rejected."
```
