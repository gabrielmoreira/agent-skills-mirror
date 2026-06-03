# Scaffold Helper

Use `scripts/scaffold_workflow.py` for deterministic workflow scaffolding.

Prefer `uv run python` when a host uses uv. Otherwise use the host's local
Python runner.

## Commands

```bash
uv run python .agents/skills/ub-workflow/scripts/scaffold_workflow.py bootstrap
uv run python .agents/skills/ub-workflow/scripts/scaffold_workflow.py create-wave w12 agent-loop-hardening
uv run python .agents/skills/ub-workflow/scripts/scaffold_workflow.py create-initiative .ub-workflows/waves/w12-agent-loop-hardening review-controls
uv run python .agents/skills/ub-workflow/scripts/scaffold_workflow.py create-discovery .ub-workflows/waves/w12-agent-loop-hardening/initiatives/i01-review-controls approval-path
uv run python .agents/skills/ub-workflow/scripts/scaffold_workflow.py create-source-pack .ub-workflows/waves/w12-agent-loop-hardening action-review-research
uv run python .agents/skills/ub-workflow/scripts/scaffold_workflow.py prepare-sprint .ub-workflows/waves/w12-agent-loop-hardening/initiatives/i01-review-controls approval-runtime
uv run python .agents/skills/ub-workflow/scripts/check_scaffold_placeholders.py .ub-workflows --strict
```

## Behavior

1. `bootstrap` creates the normalized operations root, creates
   `SOURCE_ATLAS.md` with a one-time source-root scan when absent, and creates
   or patches root `AGENTS.md` with a managed workflow-routing section.
2. `create-wave` creates `waves/wNN-slug/` with `wave.md`, `discoveries/`,
   `initiatives/`, `source-packs/`, Outcome Signals, Forecast And Appetite,
   and `.gitkeep` markers for empty canonical folders.
3. `create-initiative` creates `initiatives/iNN-slug/` under a wave with
   `roadmap.md`, triggered T3 `index.md`, Outcome Signals, Forecast And
   Appetite, Forecast Control, `discoveries/`, and `sprints/`.
4. `create-discovery` detects whether the owner is a wave or initiative and
   creates the correct `wNN-dNN` or `wNN-iNN-dNN` file with explicit user or
   operator evidence status plus Forecast Impact for sequence-changing work.
5. `create-source-pack` creates a dated source pack under the operations root
   or a wave root.
6. `prepare-sprint` creates only the next sprint by default and includes the
   required closeout `Outcome And Learning Review` section plus a fail-closed
   Routing Preflight, Discovery Triage prompt, Product Increment Contribution
   prompt, explicit user or operator evidence status, closeout Forecast Delta,
   claim-to-proof `evidence/index.md` scaffold, decision-latency mini-retro
   prompt, retro evidence check, and evidence `.gitignore` for generated
   runtime scratch state.
7. `prepare-sprint --all` is the explicit bulk materialization path.
8. `archive-initiative` moves a completed initiative to wave-local `archive/`.
9. Helpers remove `.gitkeep` when a canonical folder receives real content and
   restore it when a canonical folder becomes empty.
10. Bootstrap source scanning is intentionally one-time. Use explicit
    source-atlas maintenance when package boundaries or test topology change.

## Safety

- Existing non-empty targets are not overwritten.
- Human-owned gates are not set automatically.
- The helper creates scaffold structure; it does not start sprint execution.
- Placeholder checks apply to generated workflow output, not internal
  templates.
