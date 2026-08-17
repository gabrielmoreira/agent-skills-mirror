# CLAUDE.md

Practical Claude Code guidance for this repo. Product direction, delivery
grain, PR report style, evidence boundaries, and commit trailers are defined in
`AGENTS.md` and `docs/DIRECTION.md` — read those first; this file does not
repeat them. `CONTEXT.md` is the glossary for the OMH ↔ Hermes Agent boundary
(which product owns which surface, state root, and TUI); use its terms before
reasoning about anything that touches Hermes Agent.

## What This Repo Is

oh-my-hermes (OMH) is a Hermes-native wrapper orchestration layer: a
deterministic skill catalog, router, and prepared-handoff generator installed
next to Hermes Agent. Core `omh` code makes no LLM, API, or network calls and
never patches Hermes. Pure Python 3.11+, zero runtime dependencies. One scoped
exception: `omh coding fanout dispatch` (explicit opt-in) spawns local agent
CLIs as subprocesses — those CLIs make their own network calls; omh itself
still makes none, and nothing executes without that explicit command.

## Build & Test

```sh
PYTHONPATH=tests uv run python -m unittest discover -s tests -v   # full suite
PYTHONPATH=tests uv run python -m unittest tests/test_cli.py -v   # one file
uv run python -m compileall -q src tests                          # syntax gate
uv run python -m omh.cli docs workflows --check                   # byte gate
uv run python -m omh.cli docs roles --check                       # byte gate
uv run --group lint ruff check src tests                          # static-analysis gate
git diff --check
```

- Always set `PYTHONPATH=tests` for unittest; test helpers live at tests root.
- Run the smallest test that proves your claim, then broaden if the touched
  surface is shared. Full suite before claiming done.
- `uv run --group lint ruff check src tests` installs the pinned Ruff version
  from the `lint` dependency group (declared in `pyproject.toml`) into the
  project's `uv`-managed environment — no globally installed `ruff` needed.
  CI runs the identical command as its own step. The initial rule set is
  Pyflakes (`F`) only, scoped narrow to stay actionable on a ~135k LOC repo;
  see the `[tool.ruff]` block in `pyproject.toml` for the per-file re-export
  exclusions and the deliberately-not-yet-enforced broad-exception
  (`BLE001`) policy, owned by issue #652.
- That broad-exception policy is a gate, not a comment.
  `tests/test_broad_exception_policy.py` re-derives every broad `except` site
  in `src/` from source and fails when one is not classified as either
  intentional (the failure is classified and surfaced) or needing the #637
  treatment (the failure is relabeled as a normal result). Add the verdict in
  that file when you add a broad `except`; do not record hit counts or line
  numbers in prose, they drift.

## Generated Artifacts Map

Source of truth → generated file → regen command → drift gate:

| Source | Generated | Regenerate | Gate |
| --- | --- | --- | --- |
| `src/skills/catalog.py` + `src/skills/render.py` via `builtin_skill_templates()` / `builtin_skill_reference_templates()` | `skills/*/SKILL.md`, `skills/*/references/*.md` | write template `.content` back to `skills/` (short Python loop; no dedicated CLI writer) | tap-skills staleness inside `docs workflows --check` (missing/stale/extra); `tests/test_router_content.py` |
| Same catalog data | `docs/WORKFLOWS.md` | `uv run python -m omh.cli docs workflows --output docs/WORKFLOWS.md` | `uv run python -m omh.cli docs workflows --check` |
| Same catalog data | `docs/ROLES.md` | `uv run python -m omh.cli docs roles --output docs/ROLES.md` | `uv run python -m omh.cli docs roles --check` |
| Demo case engine | `examples/use-cases/g1-g10-demo-cards.json` | `uv run python -m omh.cli cases demo --all --json` output | parse-equality in `tests/test_application_cases.py` |
| `capability_family_projection()` in `src/capabilities/families.py` | `src/plugin_bundle/omh/tools/capability_families.json` | `uv run python -m omh.cli docs capability-families` | `uv run python -m omh.cli docs capability-families --check`; dict-parity in `tests/test_plugin_capabilities.py` |
| `ulw_inventory_payload()` in `src/skills/catalog.py` via `src/catalogs/ulw_surfaces.py` | marked ULW region of `README.md` | `uv run python -m omh.cli docs ulw-inventory` | `uv run python -m omh.cli docs ulw-inventory --check`; `tests/test_ulw_inventory.py` |
| Same producer | marked ULW region of `site/index.html` | `uv run python -m omh.cli docs ulw-site` | `uv run python -m omh.cli docs ulw-site --check`; i18n parity in `tests/test_ulw_inventory.py` |

Rules:

- Never hand-edit `skills/*/SKILL.md`, `docs/WORKFLOWS.md`, `docs/ROLES.md`, or
  the demo-cards JSON. Edit the catalog/render source, regenerate, commit both.
- After any catalog or render change, rerun every `--check` gate before commit.
- The gates are byte-exact comparisons. A one-character drift fails CI.

## Code Conventions

- Small explicit Python functions and data structures. No clever string
  parsing. No new dependencies without explicit user approval.
- Routing lives in `src/routing/` (`chat.py` is the main router). Match on
  normalized phrases or token sets via the existing helpers
  (`normalized_phrase`, `routing_tokens`, `contains_cue_phrase`) — do not add
  raw substring checks. Phrase triggers for multi-word intents; token triggers
  only when a single token is unambiguous.
- Guard patterns: routing and policy changes ship with negative cases
  alongside positive cases. Adding a trigger without a negative case is
  incomplete. Both corpora live in `src/quality/routing_precision.py` and each
  has a name worth searching for: `ROUTING_PRECISION_CASES` is the
  negative-control corpus and its failure metric is `overroute_count`;
  `ROUTING_INTERVENTION_CASES` is the positive-intervention corpus and its
  failure metric is `missed_intervention_count`. Grepping for "underroute"
  finds nothing — the guard exists under the intervention name.
- Tests are contracts. Many fixtures assert exact counts. When you add a
  routing case, skill, or demo card, update the exact-count assertions in the
  same commit — they are the point, not noise. To find them, grep the current
  value read off `tests/test_routing_precision.py` (or the drift registry in
  `src/maintenance/drift.py`), not a number quoted here; per the rule above,
  counts written into prose drift and then send you looking for a string that
  no longer exists.
- English for code, docs, commits, and PR text — and for all user-facing CLI
  output by default. Localized output (ko/ja/zh) is explicit opt-in via
  `--language` or `OMH_LANG` only; never auto-detect the OS locale. Korean-only
  surfaces shrink the audience to Korean users.

## Workflow Rules

- A report that something is broken is not yet repo work. Measure which fault
  domain owns it first — see Fault domains in `CONTEXT.md` for the four domains
  and the command that proves each. Only one of them produces a PR.
- One user goal → one PR. Do not frame partial slices; see Delivery Grain in
  `AGENTS.md` for the only valid split reasons.
- Branch before the first edit: `claude/<topic>` (or `agent/`, `hermes/`).
- Every commit needs DCO `Signed-off-by:` plus the Lore-style trailers listed
  in `AGENTS.md` (Constraint / Rejected / Confidence / Scope-risk / Directive /
  Tested / Not-tested).
- PR bodies follow the repo template: capability, motivation, boundary-level
  implementation, observed verification, risks. Never a one-line changelog.
- Report only observed evidence. `prepared_not_observed` is never execution,
  review, CI, or merge evidence.
- Never revert or clean up unrelated dirty files; report them instead.

## Common Pitfalls

- Adding a new installable skill involves more than `catalog.py` — awareness
  lane + context card, ack/label/card coverage, and the generated
  capability-family sidecar. Follow `docs/ADDING-A-SKILL.md`; the coverage
  gates fail with paste-ready instructions when a surface is missed.
- Hand-editing a generated `skills/*/SKILL.md` — the change is silently lost on
  regeneration and fails the byte gates. Edit `src/skills/catalog.py` /
  `render.py` instead.
- Adding a routing fixture or skill without updating exact-count assertions —
  breaks `tests/test_routing_precision.py`, `tests/test_cli.py`,
  `tests/test_hermes_ux_quality.py`, and `tests/test_release_smoke.py`. Grep
  those four for the old count when totals change.
- Grepping the repo and matching stale strings under `build/lib/` — it is a
  gitignored copy of old sources. Scope searches to `src/`, `tests/`, `docs/`,
  `skills/`.
- Regenerating docs but forgetting the demo cards (or vice versa) when catalog
  data changes — the parse-equality test catches it late; regenerate all four
  artifact families together.
- Dropping `PYTHONPATH=tests` — imports of `_cli_harness` and friends fail with
  confusing errors.
- Making Codex the implicit default owner in wording, schemas, or reports —
  keep Codex, Claude Code, Hermes runtime, and generic executors
  executor-neutral (`AGENTS.md`, Implementation Boundaries).

## Working Style

- State assumptions before editing; if the contract is unclear, ask.
- Minimum code that solves the goal. No speculative options, flags, or hooks.
- Touch only what the goal requires; match surrounding style exactly.
- Define the verifying command before coding; loop until it passes, then run
  the byte gates and full suite as the final proof.
