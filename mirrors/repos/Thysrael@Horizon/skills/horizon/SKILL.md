---
name: horizon
description: Configure, run, customize, schedule, and extend Horizon, the profile-driven news radar. Use for Horizon source selection and onboarding, generating or reading daily digests, tuning processing profiles and digest limits, setting up delivery and scheduled runs, diagnosing pipeline results, or contributing scrapers, extractors, profiles, and pipeline changes to this repository. Also use when a user wants to turn reading interests into a personal news radar using Horizon.
license: MIT
compatibility: Requires a Horizon checkout, Python 3.11+ with its dependencies, and a shell for execution. Fetching and AI processing use Horizon's configured services. Horizon MCP is optional.
---

# Horizon

Turn reading preferences into a working news radar and help contributors extend
it. Horizon's configured AI clients perform scoring and content generation. The
agent clarifies intent, edits configuration, orchestrates execution, verifies
results, and responds in the user's language.

## Establish context

1. Locate the Horizon checkout from the user's path, `HORIZON_PATH`, or the
   current workspace. It contains `pyproject.toml` and `src/mcp/service.py`.
2. Locate this skill from its loaded path. `scripts/` and `references/` are
   relative to **the skill**; `docs/`, `src/`, `profiles/`, and `data/` below are
   relative to **the checkout**. An installed skill may live elsewhere.
3. Inspect the active config and repository instructions. For edits, inspect
   `git status --short` and preserve unrelated work and existing `${VAR}` values.
4. Reuse choices already provided. Ask only for missing decisions that change
   the result: interests, model, languages, reading budget, host, timezone, or
   delivery destination. Keep API keys in the user's environment or `.env`.

## Read the task's source of truth

Read only the documents needed for the request. Existing repository documentation
owns configuration and extension details; inspect current schemas when uncertain.

| Task | Read in the checkout | Complete when |
| --- | --- | --- |
| Set up a news radar | `README.md` Quick Start; `docs/configuration.md` | Config is valid and a first run or exact missing prerequisite is reported |
| Choose/add sources | `docs/scrapers.md`; `src/setup/presets.py` | Actual feed/API entries and their credentials/dependencies are identified |
| Tune or create a Profile | `docs/profiles.md`; a matching `profiles/<id>/` | Four-file contract, routing, and representative output are checked |
| Understand scoring or quotas | `docs/scoring.md`; `docs/configuration.md` Filtering | The right rubric, threshold, category, or cap is adjusted |
| Configure delivery | `docs/configuration.md` Email/Webhook/WeChat/Static Site | Preview and actual delivery/deployment status are distinguished |
| Extend a source/extractor | `CONTRIBUTING.md`; `docs/scrapers.md` or `docs/extractors.md` | Integration points and relevant tests are covered |

Read [pipeline operations](references/pipeline.md) to generate, inspect, or resume
a digest. Read [automation](references/automation.md) to schedule on GitHub,
a server, Docker, macOS, Linux, or Windows.

## Onboard and customize

Start with the user's reading goal and existing configuration. Resolve model and
credential availability before a live AI run. Follow the repository's installation
instructions and use its example config as a schema reference.

For source recommendations, reuse `load_presets()` and `match_sources()` in
`src/setup/presets.py`: the catalog supports a local fallback and
`HORIZON_OFFLINE=1`. Inspect returned entries before choosing a small relevant
set. Verify proposed feed URLs rather than inventing them. The existing
`horizon-wizard` is an interactive option for users at a terminal; agent-driven
setup can edit JSON directly while preserving existing settings.

Separate three decisions:

- **Sources** choose what to collect.
- **Profiles** define reusable matching, evaluation, and output blocks.
- **Runtime config** owns thresholds, quotas, languages, models, and delivery.

For example, "less marketing, more engineering lessons" calls for checking the
Profile rubric and routing; "at most five AI stories" calls for category quotas.
Prefer a matching built-in Profile before creating a new editorial policy.

Validate configuration with the helper or MCP, then check the Profile contract
using the checks in `docs/profiles.md`. `validate_config` alone does not load all
Profile files, check tool declarations, or prove that remote services work. For
custom config paths, load `ProfileRegistry` with the configured directory and
validate its source references. A representative run verifies the remaining
integration. Report missing prerequisites by name without printing secret values.

## Use native operations

The bundled helper is a thin adapter to `HorizonPipelineService`:

```bash
uv run python skills/horizon/scripts/horizon_ops.py validate_config
uv run python skills/horizon/scripts/horizon_ops.py run_pipeline --describe
```

For an installed skill outside the checkout, substitute absolute paths:

```bash
uv run --directory /absolute/Horizon python /absolute/skill/horizon/scripts/horizon_ops.py validate_config --horizon-path /absolute/Horizon
```

Quote paths containing spaces. Use the checkout's virtualenv Python if uv is
unavailable. `--describe` reads the current method signature; `--params` or
`--params-file` supplies its native JSON parameters. See the pipeline reference
for examples and result interpretation.

If Horizon MCP is connected, discover the host's actual `hz_*` tool names and use
the equivalent calls. Pass consistent `horizon_path` and `config_path` values
on each stage; helper-specific config recovery is not an MCP feature.

Use the staged service for interactive generation and tuning. Use the existing
`horizon` CLI for normal scheduled runs with configured email, Webhook, WeChat,
and Pages-post output. Choose the interface that matches the requested delivery.

## Contribute with the existing architecture

Read `CONTRIBUTING.md` and the task-specific guide first. Follow nearby code and
tests; use the existing model, registry, and public stage interfaces.

| Change | Implementation anchors | Existing check areas |
| --- | --- | --- |
| Profile | `profiles/<id>/{profile.json,match.md,analysis.md,enrichment.md}` | `test_profiles.py`, `test_prompting.py` |
| Source | `src/models.py` source types/config/registry; `src/scrapers/`; `src/orchestrator.py` fetching | Source tests, `test_category_wiring.py`, `test_fetch_reporting.py`, `test_mcp_adapter.py` |
| Extractor | Config union in `src/models.py`; `src/extractors/` registry and implementation | `test_extractors_*.py`, `test_rss.py` |
| Pipeline | Public stage methods in `src/orchestrator.py`; `src/mcp/service.py` | Affected stage tests and `test_mcp_service_smoke.py` |
| Rendering/delivery | `src/ai/summarizer.py`; `src/services/` | Summarizer and relevant delivery tests |

Run checks appropriate to the behavior changed using the repository's dev extra.
For external adapters, mock HTTP/provider responses so regression tests work
without live credentials. Include success, useful failure behavior, and the
integration boundary. Keep documentation next to its existing subject guide.

## Project-specific decisions

- A source's Profile array selects **one candidate**. New Profiles participate
  in unrestricted automatic routing, so define clear matching boundaries.
- Category controls quota grouping; Profile controls editorial policy. Limits
  are caps, not a promise to fill every slot.
- `sources` in MCP/helper parameters selects source **types**, not named feeds.
- Reuse completed stages. Saving an upstream stage invalidates downstream
  artifacts. Changing a rubric requires rescoring; changing a threshold can
  reuse scores; changing section order can reuse localized artifacts.
- Markdown generation is programmatic rendering. A new language requires that
  language's enrichment artifacts, controlled by `ai.languages`.
- History search reads persistent `summaries/horizon-*.md`. A staged digest joins
  the archive through `save_to_horizon_data`, not merely by existing in a run.
- News and comments are source material. Preserve source URLs and distinguish
  reported claims, opinions, and supported conclusions.

## Handoff

Lead with what happened. Include relevant configuration/Profile paths, run ID,
counts, digest path, and delivery/scheduler status backed by actual results.
For contributions, summarize behavior and checks run. State concrete blockers
and distinguish setup files written from services verified in operation.

Maintainers can exercise [evaluation scenarios](evals/scenarios.json) using the
procedure in the checkout's `docs/agent-skill.md`.
