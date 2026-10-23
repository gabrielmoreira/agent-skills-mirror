---
name: "omh-show-reel"
description: "[omh] Motion showcase to make: produce a source-grounded product film with audience-specific concepts, segment direction, authored motion, measured locale/export QA and reproducible source delivery. Use when the user says: show-reel, show reel, showreel, product showcase video, animated product film, motion showcase, animated portfolio, launch film."
license: MIT
author: "oh-my-hermes maintainers"
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, design]
    category: design
    phase: motion-production
    role: operator
    quality_tier: evidence-gated
    related_skills: [omh-image-cards, omh-frontend, omh-materials-package, omh-design-quality-gate, omh-visual-qa]
---

# Show Reel

## Why This Exists

`show-reel` owns the complete motion-production method so factual claims, visual decisions, locale timing, revision budget, measured exports, and delivery receipts cannot drift apart. It does not render inside OMH core.

## First Steps

- Read `references/brief-and-locales.md` and `references/storyboard-and-evidence.md` before proposing visuals. Recover objective, audience, channel, duration, aspect ratio, fps, size cap, source/brand permissions, and tool availability from supplied context; honor explicit format and duration, ask only for irretrievable hard facts, and label reversible creative assumptions.
- Resolve content language from current explicit user/audience/channel instructions, then applicable stable preferences, then user language. Keep reply_language under host persona and separate content_locale, onscreen_text, subtitle_text, pronunciation_text, voice_policy, font_policy, and direction_policy; never replace literal IDs, commands, URLs, or trademarks.
- Compare at least 3 genuinely distinct concept candidates before selection; record the rubric, winner, rejected alternatives, and per-segment art direction. Read `references/craft-workflow.md` (the full upstream production method), `toolkit/README.md` under the loaded skill directory with a file reader, then `references/renderer-adapter.md` before choosing tools; a missing renderer means HOLD on a requested video, not a completed delivery.

## Production Method

Read `references/procedure.md` for the ordered brief → source verification → concept selection → segment direction → measured timing → authored motion → critique/revision → export → QA → delivery method. `references/full-contract.md` owns boundaries, quality and completion criteria; read it before production, not after export.

Require actual style frames and moving draft playback, keep/fix/rebuild critique and a weakest-scene revision budget. Inspect the final encoded artifact at delivery-size; no tiny crowded labels or PASS from full-resolution stills alone. Requested video, codec/color/filesize, cut/motion, localization and source-package checks need observed receipts or remain HOLD.

Required: objective/audience/channel, explicit duration/format/budget, source/brand rights and available tools. Outputs: brief, source register, concept selection, storyboard, timing map, renderer handoff, preview review, export, QA and delivery manifests. These are authored contracts, not new executable schemas or core runtime operations. Missing renderer permits useful preparation, never a completed video claim.

## When to Use

Use when a user needs an authored time-based product or work showcase, from evidence and audience framing to rendered motion, localized variants, export inspection, and source delivery.

## Catalog Metadata

Category: `design`. Phase: `motion-production`. Hermes role: `operator`. Quality tier: `evidence-gated`. Detailed quality and authority checks: `references/full-contract.md`.

## Completion Checklist

- Load the full-contract checklist and `references/render-qa-delivery.md` before claiming completion; separate generated, attached, received and published.
- Preserve the user's stop conditions, language choices and literal tokens. Keep the host's reply language and persona independent of content language.
- Report actual files, source package, observed checks and every missing required check; publication and spending need separate exact-target approval.

## Recovery Notes

- If source rights, audience facts or explicit requirements conflict, HOLD and ask only the decision-changing question. Label reversible creative assumptions instead of blocking on them.
- Missing renderer/font/voice or failed/partial exports remain visible; do not install tools, call APIs or fabricate receipts.

## Workflow Lane

- Current lane: **Materials and visual summaries** (`show-reel`, `design-orchestration`, `apple-design`, `design-quality-gate`, `award-bar-score`, `frontend`, `accessibility-audit`, `visual-qa`, `+7 more`) - web, accessibility, visual QA, files, and packages.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `skill_view(name='omh-routing', file_path='references/skill-common-rail.md')`.

## Runtime Evidence

Preferred harness for this skill: `show-reel`.

```sh
omh runtime record --skill show-reel --harness show-reel --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.
Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a real unresolved user decision or a useful briefing discussion remains, offer one specific, content-linked question. Completed work needs no question; omit unrelated non-action footers and generic offers to continue.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `skill_view(name='omh-routing', file_path='references/skill-common-rail.md')`. Load it when applicable; otherwise name an unavailable capability.
