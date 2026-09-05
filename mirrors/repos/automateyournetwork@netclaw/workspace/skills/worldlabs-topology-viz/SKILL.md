---
name: worldlabs-topology-viz
description: "Turn a real network topology into a free, no-cost themed prompt preview, and optionally (after explicit confirmation) generate an explorable, AI-generated 3D 'world' via World Labs Marble — a decorative companion visualization, never a substitute for the accurate topology diagram it is derived from. Use when the operator asks for a fantastical, explorable, or AI-generated 3D world/scene of a network topology."
license: Apache-2.0
user-invocable: true
metadata:
  openclaw:
    requires:
      env: ["WLT_API_KEY"]
---

# World Labs Fantastical Topology Visualization Skill

**Version**: 1.0.0
**Feature**: 122-worldlabs-topology-viz
**Status**: Active

## Overview

Produces an AI-augmented, explorable 3D "world" visualization of a real network topology, built on
top of the existing spec 121 `topology-diagram-mcp` pipeline. World Labs' Marble API is a generative
world model — it does not accept structured/graph input and has no mechanism for precise node
placement, so this is explicitly a **decorative, companion visualization**, never a replacement for
the accurate topology diagram. The real, structurally-correct diagram (produced by the existing,
unmodified `topology-diagram-mcp/render_structural` tool) remains the authoritative artifact and is
always referenced alongside any result this skill produces.

Two distinct modes:

1. **Preview** — free, instant, no World Labs call, repeatable with a different theme.
2. **Generate** — spends real World Labs credits (~5 minutes per world), and only runs after an
   explicit, separate user confirmation, enforced both conversationally and by the
   `worldlabs-marble-mcp` tool itself (it will not proceed without `user_confirmed=true`).

## Prerequisites

- **`WLT_API_KEY`** in `.env` — your World Labs API key (`platform.worldlabs.ai/api-keys`), with a
  funded account (`platform.worldlabs.ai/billing`). Required only for the generate mode — preview
  needs no credential at all.
- The `worldlabs-marble-mcp` server (`mcp-servers/worldlabs-marble-mcp/`), registered in
  `config/openclaw.json`.
- The existing `topology-diagram-mcp` server (spec 121), already registered — reused unmodified.

### Topology sources

Any topology snapshot already normalized into the devices/links shape `topology-diagram-mcp`
accepts (CML, pyATS, or any of NetClaw's other topology-of-record integrations, or a freeform
description).

## Workflow: Free Preview (User Story 1)

Zero cost, instant, repeatable with a different theme. **No call to `worldlabs-marble-mcp` is ever
made in this workflow.**

1. Obtain the topology snapshot (devices/links) from whatever source the operator named (or a
   freeform description), normalized into the shape `topology-diagram-mcp/render_structural`
   already accepts: `devices: [{"hostname","role","state"}]`, `links: [{"a","b","label"}]`.
2. Call `topology-diagram-mcp/render_structural(snapshot_id, devices, links)` — reused unmodified.
   This tool has two existing failure modes that MUST both be surfaced clearly, distinctly, and
   *before* anything else in this workflow runs (FR-012 and its Edge Cases correction):
   - **Empty topology** (`devices` is empty): the tool raises `"devices list is empty — nothing to
     render"`. Report exactly that — this topology has nothing to preview. Do not attempt to
     fabricate a prompt or a result.
   - **Too many devices** (over the working-resolution density ceiling, 60 devices): the tool
     raises a message naming the ceiling. Report that specific reason (e.g. "this topology has N
     devices, exceeding the 60-device legibility ceiling — narrow the scope and try again"), not a
     generic failure.
   - A **single device with zero links** is NOT a failure — `render_structural` already supports
     it (a one-node layout), and this workflow proceeds normally.
3. On success, build a `topology_model.TopologySnapshot` from the same `devices`/`links` data (via
   `topology_model.Device`/`Link`), and call
   `fantastical_prompt_builder.build_prompt(snapshot, theme=<operator-specified theme, or None for
   the default>)`.
4. Present the result to the operator:
   - The reference diagram (`render_structural`'s `image_base64`, or a note of where it's shown).
   - The composed text prompt from step 3.
   - `topology_model.DECORATIVE_LABEL`, verbatim, every single time (FR-009) — this is a preview
     of what *could* be generated, not a claim about what a generated world will precisely look
     like (Marble is non-deterministic).
   - An explicit statement that no credits were spent and no call was made to World Labs.

## Workflow: Confirm and Generate (User Story 2)

**This is the one part of this skill that spends real money.** Only run this after Workflow: Free
Preview has already produced a reference diagram and prompt for the same topology snapshot.

1. State plainly, as its own message, separate from anything else: *"Generating this world will
   spend World Labs credits and typically takes about 5 minutes. Proceed?"* Do not combine this
   with the preview step's output, and do not proceed without an explicit affirmative reply
   (FR-004). This conversational check is the first of two independent layers — see step 2.
2. Only once the operator has explicitly confirmed, call
   `worldlabs-marble-mcp/generate_world(text_prompt=<from the preview's composed prompt>,
   display_name=<derived from the snapshot's identity, max 64 chars>, user_confirmed=true)`.
   **Do NOT pass `image_base64`** (research.md R9/R10, corrected 2026-09-03 after live evidence
   from six real production generations): attaching the reference diagram as an image gets pasted
   flat and unchanged into the generated scene instead of being used as structural guidance, and
   is also measurably less reliable (3 of 4 image-bearing attempts failed; 4 of 4 text-only
   attempts succeeded on the first try). `fantastical_prompt_builder.build_prompt` already
   describes every real device and every real link individually in the text — that is the thing
   that actually carries real data into the result, not the image. The `user_confirmed=true`
   argument is the second, code-level layer (FR-016) — `generate_world` itself refuses to make any
   outbound call without it, so this is not optional plumbing to skip.
3. Immediately after that call returns (success, failure, or a `confirmation_required` rejection —
   which should never happen if step 1 was actually followed, but is handled the same way if it
   does), record a GAIT entry via `gait_record_turn` (Constitution Principle IV, FR-015): `user_text`
   names the topology snapshot's identity/theme and that the operator confirmed; `assistant_text`
   names the `operation_id` and, once known, the `world_id`/`world_marble_url`/`cost.total_credits`
   or the failure category; `artifacts` is empty or references the reference diagram's identity
   only — never the API key, never raw device data beyond hostname/role identity. This step is
   required for every confirmed attempt, not optional, and is distinct from any end-of-session GAIT
   summary.
4. Report the result:
   - **Success**: the `operation_id` (tell the operator to note it — nothing server-side tracks
     it, Clarifications Q1), and that status can be checked later.
   - **`confirmation_required`**: this means step 1/2 were skipped — report it and restart from
     step 1, do not retry the call with the flag silently added.
   - **`authentication_failure`**: tell the operator to check `WLT_API_KEY` — never repeat the key
     value itself.
   - **`insufficient_credits`**: pass through World Labs' own message (it already names the fix —
     add credits or enable auto-refill).
   - **`rate_limited`**: tell the operator to wait and retry later — do not resubmit automatically.
   - **`generic_failure`**: pass through the provider's message.
5. To check status later, call `worldlabs-marble-mcp/check_generation_status(operation_id)`.
   - `done: false` — still in progress; report that plainly.
   - `done: true` with a `response` — completed. Report `world_marble_url` (the viewer link),
     `assets`, and `cost.total_credits`, **plus `topology_model.DECORATIVE_LABEL` verbatim, every
     time** (FR-009) — a completed generation is exactly the case someone could mistake for an
     accurate diagram, so this label matters most here.
   - `done: true` with an `error` — the generation itself failed after starting; report the error
     plainly, and do not retry automatically.
   - `not_found_or_expired` — the operation record itself expired (they carry a roughly one-hour
     `expires_at`). If an earlier poll's `metadata` included a `world_id`, fall back to
     `worldlabs-marble-mcp/get_world(world_id)` instead of reporting a hard failure — the world
     itself is not necessarily gone just because the operation record is. Include
     `DECORATIVE_LABEL` here too if `get_world` succeeds.

## Workflow: Direct Prompt Generation (bring your own prompt)

For when the operator has already written a complete, ready-to-use prompt themselves (e.g.
iterating creatively on wording) and wants it sent straight to Marble — **no topology fetch, no
`render_structural` call, no `fantastical_prompt_builder`, no other skill or data source
involved at all.** The operator's own words are the entire `text_prompt`, verbatim.

1. Confirm credits/time exactly as in step 1 of Confirm and Generate above — this requirement
   does not change just because the prompt is hand-written.
2. Call `worldlabs-marble-mcp/generate_world(text_prompt=<the operator's prompt, verbatim>,
   display_name=<a short label the operator gives, or a reasonable default>, user_confirmed=true)`
   — no `image_base64`, same reasoning as above.
3. Record the GAIT entry and report the result exactly as steps 3-5 of Confirm and Generate above
   — those steps do not depend on where the prompt came from. `DECORATIVE_LABEL` still applies:
   a hand-written prompt with no topology data behind it at all is not a diagram substitute either.

## Natural Language Commands

### Free preview (no cost)

```
"Give me a fantastical world preview of the CML lab topology, floating-islands theme"
"Preview what this topology would look like as an underwater city, using the current pyATS testbed"
"Show me a fantastical preview of this topology: a router r1 connected to a switch sw1"
```

### Generate (spends credits — requires confirmation)

```
"Yes, generate it"
"Go ahead and generate that world"
```

### Direct prompt (bring your own prompt, spends credits — requires confirmation)

```
"<a full hand-written scene description>" send this straight to Marble and send me the link
"<a full hand-written scene description>" generate that, no need to pull any topology for this one
```

### Check status

```
"Is the world done yet?"
"Check the status of that generation"
```

## How this differs from every other topology visualization

Unlike `threejs-network-viz`, `blender-3d-viz`, `ue5-network-viz` (precise, data-driven 3D scenes)
and `comfyui-topology-viz` (a stylized flat still image), this skill's output is a generative,
non-deterministic 3D *world* whose geometry is not driven by the topology's actual structure — only
its *theme* is. It is closer in spirit to concept art than to a diagram. Every result this skill
produces says so explicitly and points back to the accurate diagram it was generated from (FR-009).
