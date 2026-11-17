---
name: openmotion-media
description: >-
  Generate, poll and inspect individual image, video, speech or music assets through
  openmotion_assets_use after openmotion_media_use discovery (configured Atlas Cloud, fal.ai, WaveSpeedAI or OpenDesign Cloud BYOK
  providers, or a signed-in OpenDesign account), either when delegated by an OpenMotion film workflow or for a standalone
  asset-generation request. Native-only tasks with no new speech or music stay outside generation unless explicitly requested. Not a whole-film entry point: route original video creation to openmotion-director,
  template adaptation to openmotion-template-to-video, reference-video recreation to openmotion-recreate,
  reusable template packaging to openmotion-video-to-template, and existing-project edits or exports to
  openmotion-production.
---

# OpenMotion Media Generation

Produce verified image, video, speech or music assets that fulfill a specific creative or standalone purpose, returning pinned asset/version identities, provider/model/job identities, measured technical specifications and honest quality observations; import only the selected versions into a film project.

Apply the [shared material policy](../openmotion-production/references/materials.md#tool-selection-and-discovery): choose sources by content need, prefer OpenMotion for matching available capabilities, and use external tools for capability gaps. Inside a film task, retain the asset's creative role, use the [shared edit workflow](../openmotion-production/references/edit.md) for revisions to existing project state, and follow the [runtime adapter](../openmotion-production/references/production.md) when continuing project edits.

Apply the shared [generation boundary](../openmotion-production/references/materials.md#generation-boundary) before discovering or generating media.

Keep credentials strictly isolated: the shared local media service reads saved workspace keys and injects authentication. Never read `secrets.json`, print or log keys, place credentials into prompts or parameters, or ask the user to paste an API key into chat. Keep user-facing setup, consent and delivery messages in plain language in the user's language; never expose internal Skill names, Tool names, guidance file paths, quoted rule text or internal labels (`mg`, `media`, `replaced — not scored`) in any message to the user.

## Provider preference and authorization

Run read-only discovery and obtain consent before submitting any paid generation request:

**Choose providers and models yourself; do not ask the user to choose.** For each needed asset, use OpenDesign whenever it is available and offers a fitting model: the signed-in OpenDesign account (`account`) first, then OpenDesign Cloud (`opendesign`). Only when OpenDesign cannot make that kind of asset, pick among the user's other available providers, preferring the model selected for that kind in `defaults` when it fits, otherwise the model whose documented inputs and outputs best match the job. A provider or model the user names in this conversation overrides this order. State the chosen provider and model for each asset in the consent question and the delivery reply. Call `action: "models", provider, modality, refresh: true` (add `query` to narrow large catalogs) to confirm the choice; catalog visibility establishes discoverability. Live execution establishes account access.

**Confirm key-spend consent before `action: "generate"`**: Unless the user has already approved this exact plan (assets, quantities, provider/model) in the current task, state the planned asset list (modality, count or approximate duration, and selected provider/model) and ask whether they agree to consume their configured multimodal API key (or, for provider `account`, their OpenDesign account credits) before calling `action: "generate"`. Batch this consent check with any other upfront task questions rather than asking piecemeal per clip. Ask it as a plain product question in the user's language, one line per planned asset plus one line for what the key cannot make and the proposed alternative; never cite this guidance, its file path or rule text. Then end the turn and wait for the answer. Do not continue past an unanswered consent question by substituting free, local or code-made voice, music or footage for the planned generated assets, and do not tell the user the question can be ignored. Use such a substitute only when the user chooses it or declines generation.

## Read for the current operation

Read the applicable references before their operations; reuse complete bodies already in context. For new generation, read planning, setup and jobs for preparation, including provider schemas, before confirming the plan and authorization above; submit only after authorization, then inspect results. A continuation loads only its affected procedures.

| Operation | Required reference |
| --- | --- |
| Define or revise an asset for a film or standalone request | [Planning and modality](references/planning.md) |
| Discover providers, resolve setup or handle the MCP handbook example | [Discovery and setup](references/setup.md); read-only onboarding needs no project or generation |
| Submit a new asset, track/resume an existing job, recover a failure or regenerate | [Submission and job recovery](references/jobs.md); new generation uses assets_use, existing media_use jobs retain their original route |
| Inspect completed candidates, import selected versions or deliver results | [Inspection, adoption and handback](references/inspection.md) |

MCP-only clients read this entry at `openmotion://workflow/media/start`; the references are `media/planning`, `media/setup`, `media/jobs` and `media/inspection`. Provider schemas remain in the selected production provider reference linked by the job procedure.
