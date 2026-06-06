# Model Dispatch — Plugin Instructions

**Scope**: `.hi/plugins/model-dispatch/`
**Last Updated**: 2026-06-04

> Depth-priority leaf. Authoritative for work performed inside this plugin
> directory only. Outside this directory the framework's normal rules apply.

---

## Contents

| Section | What's here |
|---------|-------------|
| [Purpose](#purpose) | Why this plugin exists |
| [Authority](#authority) | What this file governs and what it does not |
| [Tier Naming](#tier-naming) | How tier names are formed |
| [The `model:` Frontmatter Field](#the-model-frontmatter-field) | Contract for agents and prompts |
| [Privacy Pinning](#privacy-pinning) | When a task MUST stay local |
| [Capability Gate](#capability-gate) | Is the model appropriate for *this* question? |
| [Loaded-Model Preference](#loaded-model-preference) | Use the model the user actually loaded |
| [Self-Awareness & Healing](#self-awareness--healing) | Detect local AI, propose/self-implement tiers, heal+notify |
| [Adding a New Tier](#adding-a-new-tier) | Step-by-step |
| [Adding a New Adapter](#adding-a-new-adapter) | Step-by-step |
| [Discovery Scripts](#discovery-scripts) | Conventions for `scripts/detect-*.ps1` |

---

## Purpose

Express **policy** for which class of model handles which class of task, without baking provider choices into the core framework. Concrete dispatch is left to the runtime that reads the policy.

## Authority

This file is authoritative for:

- The schema of `tiers.yaml`.
- The meaning of `model:` frontmatter values.
- Naming and shape of files inside this plugin directory.

This file is **not** authoritative for:

- Whether any specific agent uses a model — that lives in the agent's own frontmatter.
- How the runtime actually dispatches a call — that is the runtime's concern.
- Provider-specific behaviour — that lives in `adapters/*.md`.

## Tier Naming

- Use kebab-case.
- Encode the **constraint** the tier guarantees, not a vendor name. Good: `local-fast`, `local-strong`, `cloud-frontier`, `local-vision`, `local-embed`. Bad: `gpt-5`, `qwen-27b`.
- Names are stable identifiers — renaming a tier requires updating every `model:` frontmatter reference. Consult the naming agent before renaming.

## The `model:` Frontmatter Field

When this plugin is `experimental` or `stable`, an agent or prompt MAY add:

```yaml
---
description: ...
tools: [...]
model: local-strong       # MUST exist as a key under `tiers:` in tiers.yaml
---
```

Rules:

- `model:` is **optional**. Absent = "no preference; runtime decides."
- The value MUST resolve to a tier in the active `tiers.yaml`.
- The validator check `model-tier-resolves` enforces this when the plugin is active.

## Privacy Pinning

If `tiers.yaml` marks a tier with `privacy: local-only: true`, the runtime MUST NOT fall back to a cloud tier when the local tier is unavailable. It must surface an error and wait. This protects:

- Tasks touching credentials, customer data, or proprietary source.
- Adopters operating in regulated environments.

The `hia-environment` agent should refuse to silently downgrade.

> **Enforced, not just documented.** The routing decision is the pure function `select_dispatch_tier()` in [`dispatcher.py`](dispatcher.py): for a privacy-pinned request it restricts fallback candidates to other `local_only` tiers and refuses (returns no tier) rather than crossing the cloud boundary. This invariant is regression-tested in [`.hi/engine/tests/test_dispatch_privacy.py`](../../engine/tests/test_dispatch_privacy.py) — stdlib-only, so it runs in CI without LM Studio, `requests`, or PyYAML.

## Capability Gate

The dispatcher's **first-class, first question** is: *"is the model I would run actually appropriate for this question?"* Routing locally is pointless if the loaded model is too small for the task.

1. The classifier scores each turn's **difficulty** on a four-rung ladder: `trivial < simple < moderate < hard`.
2. Each tier has a **capability ceiling** on the same scale. By default it is inferred from the parameter count parsed from `model_id` (`<4B` → simple, `4–13B` → moderate, `≥14B` → hard). A tier MAY state it explicitly with `max_complexity:` (the hint wins over the size guess). Unknown size with no hint is assumed capable, so the gate never over-escalates.
3. When a turn is **harder than the ceiling** (`under_capacity`), the decision honours the privacy boundary:
   - **Not privacy-pinned** + cloud allowed → `escalate: "frontier"`: hand off to the user's selected chat model automatically.
   - **Privacy-pinned** → stay local and **warn**, offering an explicit `/frontier` hand-off. The pin always wins over auto-escalation.

This lives in `model_capability_rank()` and `build_resolution()` in [`dispatcher.py`](dispatcher.py) (pure, no I/O) and is regression-tested in [`test_dispatch_privacy.py`](../../engine/tests/test_dispatch_privacy.py).

## Loaded-Model Preference

A `model_id` in `tiers.yaml` is a **preference, not a hard requirement**. If the user has LM Studio (or Ollama) running with a *different* model loaded — they loaded it for a reason — the dispatcher uses **what is actually loaded** by default. `pick_model_id()` in [`dispatcher.py`](dispatcher.py) resolves the configured id against the live endpoint inventory (`get_loaded_models()`): an `auto`/`*`/empty id, or a configured id that isn't loaded while something else is, resolves to the loaded model and the resolution reports `model_source: "loaded"`. Only when the configured id *is* loaded (or nothing is) does it stay `"configured"`.

## Self-Awareness & Healing

The [Router](../../agents/tier-1/hia-router.agent.md#local-ai-self-awareness) is *aware of the compute it runs on* and drives three actions through this plugin (entry point: `/hip-route --models`):

1. **Detect** — `scripts/detect-local-llms.ps1` and `suggest_tiers.py` probe local runtimes + hardware (read-only, fail-soft).
2. **Propose → self-implement** — if local AI is present but `tiers.yaml` is missing/stale, the advisor proposes a tier list from the loaded models. On the user's approval, `suggest_tiers.py --apply` writes a complete `tiers.yaml` (every local tier stamped `privacy.local_only: true`, `policy.allow_cloud` preserved) and backs up any existing file. The pure renderer `render_tiers_yaml()` is unit-tested in [`test_suggest_tiers.py`](../../engine/tests/test_suggest_tiers.py).
3. **Heal + notify** — `plan_healing(tiers, previously_available, currently_available, allow_cloud)` in [`dispatcher.py`](dispatcher.py) compares the last probe to the current one; for each tier that dropped it computes a safe reroute (via `select_dispatch_tier`, so privacy-pinning and the kill-switch still hold) **and** a user-facing notification. Healing is never silent. Tested in [`test_dispatch_privacy.py`](../../engine/tests/test_dispatch_privacy.py).

Consent and boundaries are non-negotiable: the Router proposes and heals, but never auto-adopts local AI and never crosses a privacy/cloud boundary on its own.

### Execution surfaces

The routing *decision* is the single authority `build_resolution()` in [`dispatcher.py`](dispatcher.py), exposed as `python dispatcher.py resolve <tier>` (one JSON line). Two surfaces consume it (Option A — decide in Python, call the model in the caller):

- **Standalone Python** — [`phase2_executor.py`](../../engine/phase2_executor.py) dispatches to LM Studio/Ollama directly. Headless/CI-capable.
- **VS Code extension** — [`.hi/extensions/hia-dispatch/`](../../extensions/hia-dispatch/README.md) registers an `@hia` chat participant: simple prompts run on a local tier; everything else runs on the model the user selected in Copilot Chat (`request.model`) via the official `vscode.lm` API. The capability gate runs first (it can escalate an under-powered local turn to the selected model), the loaded model is preferred over the configured id, and privacy-pinning and the kill-switch still hold on both surfaces.

## Adding a New Tier

1. Open `tiers.yaml` (or `tiers.example.yaml` if still in template form).
2. Add the tier under `tiers:`. Include `description:`, `provider:`, `endpoint:`, `model_id:`, and `privacy:` keys per the example.
3. Update [README.md](README.md) if the new tier introduces a new privacy class or constraint.
4. Run the validator.

## Adding a New Adapter

1. Create `adapters/<provider>.md`.
2. Document: endpoint URL pattern, authentication mechanism, request/response shape, known limitations, how to detect availability.
3. Reference the adapter from any tier that uses it (`provider: <provider>` in `tiers.yaml`).
4. Do NOT add adapter code here — adapter files are contracts, not implementations.

## Discovery Scripts

Scripts under `scripts/` MUST:

- Be **read-only**. No installs, no config writes, no API calls that mutate state.
- Print human-readable output (not JSON) — they target adopters running them interactively.
- Fail soft. If a probe target is offline, report "not detected" and continue.
- Honour [.hi/environment.md](../../environment.md) — never mutate the host.
