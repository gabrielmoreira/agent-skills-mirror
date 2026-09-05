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
never hidden and never a default.

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
  one isolated local `hermes --oneshot` process. It requires
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
  prose.

## Generated Artifact Discipline

Keep source files and generated projections together in the same change:

- `src/skills/catalog.py` and `src/skills/render.py` produce
  `skills/*/SKILL.md`, `skills/*/references/*.md`, and `docs/WORKFLOWS.md`.
- `roles_reference_markdown()` in `src/catalogs/roles.py` produces
  `docs/ROLES.md`.
- The demo case engine produces
  `examples/use-cases/g1-g10-demo-cards.json`.
- `capability_family_projection()` in `src/capabilities/families.py` produces
  `src/plugin_bundle/omh/tools/capability_families.json`.

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
uv run python -m omh.cli docs capability-families --check
uv run python -m omh.cli docs ulw-inventory --check
uv run python -m omh.cli docs ulw-site --check
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

Use executor-appropriate branch names. `codex/` is fine for Codex-authored work,
but use neutral or matching prefixes such as `agent/`, `claude/`, or `hermes/`
when Claude Code, Hermes, or a generic executor owns the coding work.
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
