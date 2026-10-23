# OMH Agent Contract

This file is the repo-local operating contract for coding agents working on
oh-my-hermes, including Codex, Claude Code, Hermes runtime/handoff paths, and
generic executor profiles.

## Product Direction

Read `docs/DIRECTION.md` before changing architecture, workflow behavior,
wrapper contracts, generated skill guidance, or coding delegation semantics.

OMH is a Hermes-native wrapper orchestration layer. Keep Hermes responsible for
chat intake, clarification, source-backed research, planning, and status
narration. Keep main coding work delegated to the selected coding owner through
explicit prepared handoffs and observed evidence. Do not make Codex the implicit
default in product language, docs, schemas, prompts, or reports when Claude
Code, Hermes runtime/handoff paths, or generic executor profiles are also valid
owners.

When developing OMH itself, treat Codex, Claude Code, and Hermes
runtime/handoff paths as first-class product surfaces. User-facing runtime
selection may choose one coding owner for a task, but OMH feature design,
contracts, docs, setup, memory recall, and status/reporting changes should
consider all three surfaces unless a change is explicitly scoped to one
executor. If support differs, document the difference as a capability boundary
instead of silently optimizing for Codex.

Do not turn OMH into a hidden Hermes runtime patch, transport bot, network
service, LLM router, or secret coding executor. The one sanctioned execution
surface is the explicit opt-in fanout dispatch bridge described under
Implementation Boundaries — operator-invoked, local-only, fully observed,
never hidden and never a default. The one sanctioned network call OMH makes is
the `omh_jev_ask` tool, also described there — user-requested per turn, never a
default. The `show-reel` toolkit's opt-in provider scripts reach a provider
only when the user runs them with their own key; OMH never runs them. The OMH TUI that bare `omh` opens is a terminal frontend over Hermes'
own gateway, not an execution surface; its boundary is stated there too.

## Command Audience

Treat natural-language Hermes chat as the normal product surface. Most people
should only need to run `omh setup`, `omh update`, and `omh doctor` directly.
Removal or unusual repair commands are exceptional maintenance paths, not the
day-to-day OMH workflow.

Commands under `omh chat`, `omh coding`, `omh runtime`, `omh memory`, `omh
loop`, `omh goal`, `omh harness`, `omh capabilities`, `omh release`, `omh
state`, and similar control-plane groups primarily exist for Hermes Agent,
wrappers, coding agents, automations, and maintainers. Public docs may show
those commands as integration or operator references, but must label the
audience explicitly and must not make normal users memorize or run them to get
value. Describe the human action as an intent or outcome, such as asking Hermes
to prepare coding work, while keeping the backend command in the agent-facing
reference.

## Delivery Grain

One user goal should normally produce one PR.

Plan, explain, and report delivery at the full user-goal completion grain. Do
not frame a recommendation as "the first PR", "initial PR", "first slice", or a
similarly partial unit unless the user explicitly asks for phased delivery or an
independent release/rollback boundary forces a split. When implementation must
be split, state the complete target capability first, then explain the concrete
split reason and the remaining capability gap.

Use multiple focused commits inside the same goal PR when useful. Planning docs,
tests, implementation, code-review fixes, CI fixes, and small follow-up docs
belong in the same PR when they serve the same user goal.

Do not split review feedback or small follow-up fixes into new PRs merely
because a previous commit already exists. Split only when the next change is a
different user-facing goal, has independent release or rollback value, would
make the current PR too risky to review, is blocked by an external decision, or
the user explicitly asks for separate PRs.

When the user asks to merge, finish review fixes in the current PR first, rerun
verification, wait for required checks, then merge if authority is clear.

## Pull Request Reports

PR descriptions must read like a useful feature report, not a terse changelog.
When a coding agent opens a PR for this project, use the repository PR template
and fill every relevant section with concrete, reviewable detail.

Every PR body should explain:

- What capability, workflow, command, or contract changed.
- Why the change exists, including the user problem, product gap, or operational
  failure that motivated it.
- What the user or operator can do after the change that they could not do
  before.
- How the implementation works at the boundary level: important modules,
  commands, generated files, persisted state, or wrapper contracts touched.
- What verification was actually observed, including CI, targeted tests,
  generated-output checks, dry-runs, or manual Hermes/TUI gaps.
- What risks, rollout notes, compatibility concerns, or follow-up work remain.

Avoid one-line summaries such as "update docs" or "fix setup" when the PR
changes user-facing behavior. Prefer a short narrative plus bullets that make
the feature's origin, behavior, and evidence obvious to a reviewer reading the
PR without the chat history.

## Implementation Boundaries

- No LLM, API, Discord, Slack, GitHub, or network calls inside core `omh`
  features unless the user explicitly approves a scoped integration.
- The approved scoped integration under that clause is the fanout dispatch
  bridge (`omh coding fanout dispatch`, 2026-07 owner approval, plus its
  `omh coding run` single-run entry that builds and dispatches a one-unit
  contract through the same engine in one call): an explicit operator command
  that spawns LOCAL agent CLIs (the CLIs make their own network calls; omh
  still makes none) in per-unit worktrees against a frozen `fanout_contract/v2`,
  recording every spawn and exit as observed journal evidence. It never runs
  by default, never merges branches, never persists raw prompts under `.omh`,
  and never executes anything outside an explicit `dispatch`/`run` invocation
  -- running one against an explicitly-named owner is itself the required
  opt-in. Bridge dispatch is a separate axis from chat prompt-handoff
  semantics: chat-prepared handoffs remain prompt-only for prompt-only
  profiles.
- The approved Hermes-native child boundary (`omh coding hermes-child dispatch`,
  2026-08 owner approval) is a second explicit operator/maintainer surface for
  one isolated local Hermes single-query process (`hermes chat --query-file -`,
  the one Hermes transport that reads a prompt from stdin). It requires
  `--confirm-dispatch`, accepts prompts only through stdin/files, enforces a
  depth-one recursion limit and safe-mode file tools, records authenticated
  `routing_observation/v1` evidence, and never runs automatically. This
  boundary supports observed Hermes execution and the explicit benchmark
  controller; it does not make core OMH a provider client or hidden runtime.
- `omh coding paired-run dispatch` may reuse that same Hermes-child boundary
  for explicitly confirmed evaluation cells. The operator supplies one
  digest-matching task file per frozen task, the repository/revision, and the
  provider; OMH passes task bytes over child stdin, creates detached per-cell
  worktrees under an atomically unique invocation-owned parent, verifies
  signed evaluation bindings, removes only paths reserved by that invocation,
  and persists no task body. This is a front door to the approved child boundary,
  not a third subprocess authority. Executors without a receipt-capable
  adapter are refused without substitution; caller-injected adapters remain
  the executor-neutral extension seam.
- `omh coding fanout dispatch --final-review` may also compose that existing
  child boundary after dispatcher-observed integration GREEN. It requires the
  explicit flag, a clean integrated worktree/tree revision, and named Hermes
  provider/model settings; four read-only lenses run in disposable,
  write-denied detached worktrees under fixed concurrency, parse only a closed
  verdict token, and cannot merge or mutate the integrated checkout.
- `omh coding fanout dispatch --diagnostics` may spawn only the closed local
  diagnostic command set after producer verification GREEN. The default
  adapter discovers supported binaries from `PATH`, passes no shell text or
  user-selected executable, materializes detached fixed-revision worktrees,
  strips messages and absolute paths, redacts the child environment, caps
  concurrency/time/output, always reaps the provider's complete process tree,
  and removes every temporary worktree. No provider is installed or started
  unless the operator types the flag. On Windows the provider starts suspended,
  enters a kill-on-close Job Object, and resumes only after ownership succeeds;
  clean evidence requires the Job Object to report zero active processes.
- The approved scoped network integration (2026-09-23 owner approval) is the
  `omh_jev_ask` plugin tool: it POSTs typed questions to Jev with the user's
  own key and returns probabilities. It runs only when the person's own
  message for that turn names Jev (a per-turn marker `pre_llm_call` records;
  otherwise the tool returns `consent_not_observed` and opens no socket), and
  only when a route resolves — `TYPESAFE_API_KEY`, or `OPENROUTER_API_KEY`
  plus `{"openrouter_route": true}` in `<omh_home>/jev/settings.json`, which
  OMH never writes. Stdlib only, HTTPS only, a fixed two-host route table, no
  redirects, bounded bodies, no retry after a sent request times out. It
  persists no key, `state`, question text, or reply; one metadata-only ledger
  row per ask. `src/plugin_bundle/omh/jev_ask_client.py` is the only
  in-process network client in `src/` and only `tools/jev_ask_tool.py` may
  import it. Third-party Jev plugins are still never called, and `omh doctor`
  still reads no credential value.
- Opt-in show-reel provider scripts (owner approval, PR for show-reel
  upstream parity): `src/skills/show_reel_toolkit/scripts/eleven.py` and
  `narrate.py` (ElevenLabs TTS/STT/SFX/music by spawning `curl`, key from
  `ELEVENLABS_API_KEY` only and passed on curl's stdin) and
  `codex_ref_image.sh` (the user's signed-in codex CLI) ship as inert package
  data. Only the user runs them, with their own credential; without it they
  exit 2 and send nothing. OMH core, install, update, routing and doctor never
  import or execute them; `eleven.py` is in INVARIANT 1's
  `PROCESS_SPAWN_ALLOWLIST` and the companion-nonexecution tests cover both
  Python scripts.
- The OMH TUI is the frontend bare `omh` opens. `omh` runs the user's own
  `hermes --tui` with `HERMES_TUI_DIR` pointing at OMH's packaged frontend, so
  Hermes' launcher still resolves the profile, resume target, working
  directory and session ownership, then starts OMH's frontend in place of its
  own. That frontend spawns one child at a time, Hermes' `tui_gateway`, with
  the interpreter, import path and environment the launcher handed it, and
  speaks the gateway's stdio JSON-RPC. When that child exits on its own with
  a failure (never after a normal exit, after the person quits, or for a
  gateway another runtime owns), it spawns it again the same way and resumes
  the session that was open (`session.resume`), at most 3 times in 60 s, as
  Hermes' own TUI does: the open question and those waiting behind it close
  unanswered, a turn that was running is reported lost and never sent again,
  and past that limit it exits as it would without recovery, naming
  `hermes --tui`. It relays only what the person types; on its
  own it reads Hermes' settings and command catalog as a session opens
  and, at a fresh start, `session.list` to name the last session under
  the banner, and, beyond opening and closing sessions
  (`client.capabilities`, `session.create`, `session.resume`,
  `session.close`), sends only what this bullet names below, plus
  `session.history` again when Hermes refuses a rewind; when no turn runs,
  a steer Hermes refused as an ordinary prompt; and, at once, the decline
  frame for a request it cannot show (a vault unlock or save-login prompt,
  a terminal, preview or window read, a preview action, a tour, a display
  sudo install, a clarify with no question in it, or a method it does not
  know). It never
  answers an approval, clarify, sudo, or secret request on its own, apart
  from declining at once a request it cannot show (listed above): Esc or
  Ctrl+C declines, an approval decline is an explicit deny and then
  interrupts the running turn (`session.interrupt`, only while a turn runs;
  every deny the person gives an approval does, `d`, `n` and Enter on deny
  too, except the tell row's below), allowing a command takes the arrows
  and then Enter, and a request the gateway withdraws (its own timeout, an
  interrupt) closes without an answer.
  Hermes' `always` choice is offered only when the request lists it and is
  sent, like any allow, only on the person's arrows and then Enter; saving
  it as a permanent allow (`command_allowlist`) is Hermes' doing, and like
  allow this session for one session it stops Hermes asking about commands
  that match. An approval's last row, "no, and tell Hermes what to do
  instead", sends the explicit deny at once, interrupts nothing, and then
  opens the composer for what the person tells Hermes instead; Esc there
  sends nothing more.
  Leaving a session (`/new`, a switch) declines that session's open requests
  and says so in the new transcript. Shift+Tab is the one key that changes
  what Hermes asks; the approval answers above change it only for the
  commands they match. Shift+Tab may turn on Hermes' per-session yolo, the
  switch it sets in Hermes' own TUI, which stops Hermes from sending approval
  requests for that session; the TUI still answers none, because Hermes then
  sends none. It does this only on the person's keypress, with a `config.set`
  that names the session and an explicit value and never a `scope`, so it
  never writes the global `approvals.mode` and never sets the switch for the
  gateway process. Leaving a session it turned yolo on for, or whose yolo
  call is still unanswered (`/new`, a switch, `/quit`, any exit), it first
  sends that session an explicit off, since Hermes keeps yolo through
  `session.close` for a session a messaging gateway started. The mode is
  shown on the info line under the composer (which stays while a list the
  person picks from hides the composer) only once Hermes confirms it
  for that session; when turning it on, an answer that confirms anything else
  is a failure, followed by an explicit off, and accept is shown again if
  Hermes does not confirm that off either; and `session.info` corrects
  what is shown, so yolo that Hermes reports for its own reasons is shown
  too, except that one saying approvals are on within 2 seconds of a
  confirmed on is held until the next, keeping accept shown. Ctrl+T and
  `/effort` set that session's reasoning effort through the same
  session-scoped call. A pick in the `/model` picker (bare `/model`,
  listed from `model.options`) is sent as Hermes' own `/model <name>
  --provider <slug> --session` through `slash.exec`, so it switches
  that session only, and a name or slug that could read as a flag is
  left out of the list. `/cost` and `/permissions` run Hermes' `/usage`
  and `/approvals`; the latter shows or sets Hermes' persistent
  approval mode, as typed. Plan mode is the frontend's own flag, also
  turned on with Shift+Tab: while it is on, a prompt the person types goes to
  Hermes as `/plan <text>`. While Hermes has approvals off on its own (an off
  it confirmed did not end them, or they were off without the TUI turning
  them on), Shift+Tab sends nothing and turns only plan mode on and off. A
  steer (Ctrl+Enter, `/steer`, or what the person sends from the composer
  the tell row opened) sends into the running turn only text the person
  typed and sent that way, and the tell row's text goes as an ordinary
  prompt once the turn has ended; the TUI never steers on its own, and a
  queued prompt is never turned into a steer. A steer Hermes does
  not take waits in the TUI's own queue for the running turn to
  end, whatever the busy mode, so it never interrupts that turn.
  A steer Hermes does not answer within 120 s goes back to the
  composer and is never re-sent. Its look is the rail and kind colours the
  owner picked on 2026-10-22: each transcript block on a `┃` rail with no
  fill (grey for the person's prompt, the skin's accent for a reply, a
  call's state colour for the call), a call's state in its mark's glyph and
  colour as the dag view draws it (running blue `○`, done green `●`, failed
  red `✗`), its name in its tool family's hue at 4.5:1 on dark and light,
  consecutive skill loads and tool-detail reads folded into one row, and the
  composer between two full-width rules with no side edges; none of it
  changes what the TUI sends or answers. The subagent views (the agent view under
  the info line, always expanded while there are agents, as the owner asked
  on 2026-10-21; the list Down opens on its rows; one agent's log) read with
  `subagent.tail` only, the tail of the log
  the person opened. In a dag run the agent view is a folding tree, as the
  owner asked on 2026-10-22: a header row per node (a fold triangle, its
  state glyph, its label, then category, model:effort, status and tokens),
  under an open node its child's latest call and latest line (thinking,
  Hermes' progress line or its reply), running and failed nodes open, layers
  set apart by blank rows, folded to fit the view's cap before a count row
  cuts it; Down gives the tree the keys (the arrows and Space fold), and a new
  turn keeps the open run's lanes in the roster. Two keys in the agent list,
  and in the tree on the highlighted node's child, act on that
  agent, and only on the person's keypress: `x` interrupts it
  (`subagent.interrupt`) once a second `x` confirms, and `s` steers it
  (`subagent.steer`) with text the person then types and sends; the TUI
  never interrupts, steers or answers for a subagent on its own. A line the
  person sends that starts with `!` is their own shell command: the TUI
  sends it with `shell.exec`, which Hermes runs outside the model's context
  under its own 30 s limit and dangerous-command refusals, shows what it
  printed and its exit code when that is not 0 or nothing was
  printed, and sends nothing else that way: only a line whose
  leading `!` the composer showed (a collapsed paste whose text
  starts with `!` goes to the model), never a refused steer or
  a queued prompt that happens to start with `!`. A rewind (Esc
  Esc on an empty composer, `/rewind`) cuts the session's history before
  the prompt the person picked, and only when they send the prompt that
  replaces it (`prompt.submit` with `truncate_before_row_id` and
  `confirm_truncate`). Mouse reporting is on in one state only, the agent
  list open, and off in every other and on every exit. A plain left click
  on an agent opens its log, one on the list's `main` row leaves the list,
  and every other report does nothing. A report that starts while
  reporting is on, or within 0.5 s after it goes off, types nothing if it
  arrives whole within 0.8 s of its first byte. If 300 ms pass after that
  byte without the next, the byte is read as Esc, and the rest is dropped
  only if it arrives within 0.5 s after that. One that starts later and is
  split right after its first or second byte is read as keys. It never
  attaches to a session another runtime
  owns: when the launcher sets `HERMES_TUI_GATEWAY_URL`, it exits and names
  `hermes`. It writes no transcript, attachment, secret or server-request
  frame to disk or to a log, and prompt text in one place only: each line
  the person sends from the composer is appended to Hermes' own input
  history, `$HERMES_HOME/.hermes_history`, the file `hermes --tui` reads and
  writes, in its format (`+`-prefixed lines under a `#` timestamp line). It
  only appends there (opened `O_APPEND` and `O_NOFOLLOW`, created mode
  0600), reads at most the file's last 1 MiB and only when it is a regular
  file (no symlink or FIFO), and never writes an answer to
  a question Hermes asked or masked input there. The other files it writes
  are metadata: the launcher's active-session file (the session id), and
  what OMH's own HUD reader and model-chain picker already write under the
  OMH home (the HUD fan-out cache and its lock, and
  the chains `/omh-model` saves), and an empty fallback marker at the path
  `omh` named, which `omh` removes. The frontend opens no socket and makes no
  network call, strips the sidecar and attach URLs from the gateway's
  environment, and reaps the gateway when it exits, SIGTERM and SIGHUP
  included. Ctrl+Z stops the process group, Hermes' gateway with it, as
  Hermes' own CLI's Ctrl+Z does, and fg continues both. OMH itself still makes no
  LLM call; every model call, and every other network call the gateway makes,
  is Hermes'. This is a foreground terminal the person launched, not a
  background runtime, a transport bot, or a third process bridge.
- No Hermes core patching.
- Runtime artifacts are local, deterministic, schema-versioned, and
  metadata-only by default.
- Preserve prepared versus observed boundaries. `prepared_not_observed` is not
  execution, review, CI, merge-readiness, or merge evidence.
- Wrapper sessions own chat continuity and plan decisions only. Linked runtime
  runs own handoff, dispatch, execution, verification, review, CI, and merge
  evidence.
- Coding delegation and memory recall should be executor-neutral by default:
  name the selected owner (`codex`, `claude-code`, `hermes`, runtime profile, or
  generic executor) and only use Codex-specific wording for Codex-only lifecycle
  features.
- Project memory lives under `.omh/memory/` as reviewed OMH-local prepared
  context. Keep candidates separate from approved records, preserve
  review-first defaults, and never present recall packs as execution, review,
  CI, merge, or Hermes internal-memory evidence.
- Generated skills come from catalog data. Prefer updating
  `src/skills/catalog.py` and regenerating docs over hand-editing generated
  output.

## Coding Style

- Keep code, docs, commit messages, and PR text in English.
- Reply to Korean user messages in Korean. Use polite Korean by default; do not
  use banmal, casual endings, or overly familiar phrasing unless the user
  explicitly requests that tone.
- For Korean explanations, prefer concrete, human-readable wording that names
  what exists, what is missing, and the exact complete target behavior. Avoid
  vague process labels or "small first PR" framing when the user asked to reason
  at the whole-capability level.
- Prefer small, explicit Python functions and data structures over clever
  string parsing.
- Keep public claims conservative and test-backed.
- Avoid adding dependencies unless the user explicitly approves the dependency
  and its packaging story.
- Keep routing changes inside the existing normalization helpers
  (`normalized_phrase`, `routing_tokens`, and `contains_cue_phrase`) rather
  than adding raw substring checks.
- Ship routing and policy changes with both positive-intervention and
  negative-control cases. The source corpora are
  `ROUTING_INTERVENTION_CASES` and `ROUTING_PRECISION_CASES`.
- Treat exact-count fixtures as contracts. Update affected assertions in the
  same change, but do not copy mutable counts or source line numbers into
  prose. When a rebase conflicts on those counts, re-derive them from the
  producer instead of choosing a side: upstream's baseline moved and your
  delta still has to land on top of it.

## Generated Artifact Discipline

Keep source files and generated projections together in the same change:

- `src/skills/catalog.py` and `src/skills/render.py` produce
  `skills/*/SKILL.md`, `skills/*/references/*.md`, and `docs/WORKFLOWS.md`.
- `src/skills/show_reel_toolkit/` plus the closed registry in
  `src/skills/show_reel_support.py` produce `skills/omh-show-reel/toolkit/**`
  and `agent-skills/omh-show-reel/toolkit/**` as non-executed text support.
  `python tools/render_skill_pack.py --write` regenerates the tap pack;
  `--check` checks its declared files. `--refresh-provenance` with `--write`
  refreshes the canonical toolkit provenance after an audited source edit.
- Canonical domain toolkit resources and definition-owned closed support
  factories feed `builtin_skill_support_templates()` for geospatial analysis,
  biomedical evidence and molecular docking. `tools/render_skill_pack.py --write`
  projects these inert files to `skills/omh-<canonical-id>/toolkit/**`.
  The domain provenance files are producer-validated, not written by the
  show-reel-specific `--refresh-provenance` flag.
- `agent_skill_files()` and `agent_skills_manifest()` produce the one portable
  inventory `agent-skills/.omh-agent-skills-manifest.json`; `docs agent-skills`
  regenerates that tree and its six host adapters. Never embed copied digest
  inventories in the adapters.
- `roles_reference_markdown()` in `src/catalogs/roles.py` produces
  `docs/ROLES.md`.
- The demo case engine produces
  `examples/use-cases/g1-g10-demo-cards.json`.
- `capability_family_projection()` in `src/capabilities/families.py` produces
  `src/plugin_bundle/omh/tools/capability_families.json`.
- `skill_shortlist_projection()` in `src/routing/skill_shortlist_sidecar.py`
  produces `src/plugin_bundle/omh/tools/skill_shortlist.json`.

Never hand-edit those generated files. Change the source, regenerate every
affected projection, and commit source plus generated output together. The
repository checks are byte-exact; a one-character drift is a failure.

## CodeGraph

This repository is initialized for external CodeGraph (`@colbymchenry/codegraph`).
See `docs/CODEGRAPH.md` for setup, rebuild, query, and agent-usage details. The
local index lives under `.codegraph/`; commit only `.codegraph/.gitignore`, not
the machine-local SQLite database or daemon files.

Use CodeGraph as a project navigation aid before broad code exploration:

```sh
npx @colbymchenry/codegraph status .
npx @colbymchenry/codegraph query <symbol-or-text>
npx @colbymchenry/codegraph explore <area-or-task>
npx @colbymchenry/codegraph impact <symbol>
```

If the index is missing or stale, refresh it with:

```sh
npx @colbymchenry/codegraph init .
npx @colbymchenry/codegraph sync .
```

CodeGraph output is prepared local code-intelligence context only. It is not
execution, review, CI, merge-readiness, or merge evidence.

## Verification

Use the smallest check that proves the claim, then broaden when the touched
surface is shared.

Typical gates:

```sh
PYTHONPATH=tests uv run python -m unittest tests/test_cli.py -v
PYTHONPATH=tests uv run python -m unittest tests/test_router_content.py -v
PYTHONPATH=tests uv run python -m unittest discover -s tests -v
uv run python -m compileall -q src tests
uv run python -m omh.cli docs workflows --check
uv run python -m omh.cli docs roles --check
uv run python -m omh.cli docs claims --check --json
uv run python -m omh.cli docs navigation --check
uv run python -m omh.cli docs capability-families --check
uv run python -m omh.cli docs skill-shortlist --check
uv run python -m omh.cli docs ulw-inventory --check
uv run python -m omh.cli docs ulw-site --check
uv run python -m omh.cli docs chain-table --check
uv run --group lint ruff check src tests
git diff --check
```

Always set `PYTHONPATH=tests` for unittest because shared test helpers live at
the tests root. Run the smallest test that proves the claim first, then broaden
for shared surfaces and run the full suite before claiming completion.

For direction, docs, generated skill, wrapper contract, lifecycle, or runtime
artifact changes, add or update tests that lock the public contract.

### Reporting Our Own Numbers

A rate OMH computes about itself is a claim, so it carries what it divided.
Every percentage in a payload names the buckets its numerator summed, what its
denominator counted, and every observation class excluded before either count
was taken — `src/quality/reported_rate.py` is that shape, and
`reported_rate_shape_errors()` is what checks it. Two specific traps:

- **An empty denominator is not 0%.** `max(1, count)` in a divisor turns a
  corpus with nothing in it into a confident zero, which claims that every case
  was measured and every case failed. Report `percent: null` with basis
  `no_observations` instead, and let an unmeasured rate fail its target rather
  than pass it.
- **A composed numerator says so.** When a rate sums more than one outcome
  bucket, name them in the payload, not only in a text formatter — every
  non-human consumer reads the JSON.

The same rule governs prose: a headline number in a commit, PR, or report names
the arm, the corpus, the selection rule, and the committed artifact it came
from. A number without those is `prepared_not_observed`, not a result.

## Repository Maintenance Procedures

Three maintainer procedures are written down as executor-neutral procedures.
Any coding agent runs them the same way — Codex, Claude Code, a Hermes
handoff, or a generic executor profile. The two sweeps are manual and default
to a dry run; none of the three runs in CI.

| Procedure | File | What it does |
| --- | --- | --- |
| Triage sweep | `docs/TRIAGE-SWEEP.md` | Labels issues and PRs that have no `area/` label, deriving a PR's areas from its changed files against `.github/labels.yml` |
| Review sweep | `docs/REVIEW-SWEEP.md` | Reviews PRs carrying no review at their current head commit, against `REVIEW.md` |
| Model onboarding | `docs/MODEL-ONBOARDING.md` | Moves a new model generation or sibling through recognition, research, calibration, both routing lanes, pricing, machine placement, gates, and the measurement close |

When asked to triage, label, review the backlog, or onboard a model, read the
matching file and follow it rather than improvising. Each states its own
allowlist, dry-run default, and boundaries.

Supporting contracts:

- `REVIEW.md` — what counts as a blocking finding in this repository. Nothing
  loads it automatically; a reviewer is expected to read it.
- `.github/labels.yml` — the label manifest and the path globs that map a
  changed file to an `area/` label. It is the entire allowlist; never apply or
  create a label that is not in it.

`.claude/skills/triage-sweep/` and `.claude/skills/review-sweep/` exist only so
Claude Code can reach these as slash commands. They hold no rules of their own
and defer to the two files above, which stay the single source of truth.

## Git And Commits

Name a branch by the kind of change, not by the executor that makes it:
`feature/<topic>` for a new or extended capability, `fix/<topic>` for a
defect, and `omh/<topic>` for everything else (docs, release, maintenance,
measurement). Codex, Claude Code, Hermes, and a generic executor all use the
same three prefixes; `codex/`, `claude/`, `agent/`, and `hermes/` are no longer
used for new branches. Branches that already exist keep their names.
Before editing files for a coding task, create or switch to a dedicated
task branch unless the current branch is already clearly dedicated to that exact
user goal. Do this before the first implementation edit so the work does not mix
with unrelated branch history or user changes.

Every commit must include DCO signoff and the local Lore-style trailers used by
this repository:

```text
Constraint: <external constraint that shaped the decision>
Rejected: <alternative considered> | <reason>
Confidence: <low|medium|high>
Scope-risk: <narrow|moderate|broad>
Directive: <forward-looking warning>
Tested: <what was verified>
Not-tested: <known gaps>
Signed-off-by: <name> <email>
```

Never revert user changes or unrelated untracked files. If an unrelated file is
dirty, leave it alone and report it.
