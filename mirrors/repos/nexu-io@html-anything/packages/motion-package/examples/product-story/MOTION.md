# Product Story — MOTION.md

Package: product-story, version 0.1.0. Motion Package contract: 0.2.
Status: original recipe with a deterministic shot-plan helper; no animated project, video export or human visual acceptance is included.

## Purpose and provenance

Make a short story where a promise is followed by evidence and one clear action. Use it for a product introduction or an educational explanation with supplied material. The documents, element and sample text are original examples maintained by OpenMotion contributors under the bundled license. There is no reference film to reconstruct.

## Design

Design source: [DESIGN.md](DESIGN.md).

Use its normative visual tokens and prose. Map `{colors.primary}` to text, `{colors.neutral}` to the canvas and `{colors.tertiary}` to the emphasis element. The opening uses `{typography.h1}`; evidence and the closing use `{typography.body}`. Do not copy a replacement token table into this document.

Video adaptation: the recipe targets a 1920 by 1080 landscape canvas. The design's sizes are authored for that canvas; a different frame size requires deliberate layout/type review. Generic font appearance is not portable pixel fidelity. No Studio interface theme is changed.

## Brand and materials

Use approved facts and supplied evidence. The fictional presets demonstrate input substitution only. Read [material requirements](materials/requirements.md) before production. The optional [emphasis element](elements/emphasis.svg) is supplied; bind its currentColor to the tertiary design role. Real logos, footage, screenshots, fonts and audio are user inputs, not bundled licensed media.

## Story and timing

The maintained timing source is [sequence.json](materials/sequence.json), expressed in output seconds. Read it rather than inventing a second timing table. The scene order is promise → evidence → action. `scripts/plan.mjs` combines that sequence with an input preset; its JSON output is a plan, not a rendering format.

## Motion and sound

Reveal the opening phrase with a short upward movement and opacity change, then hold. Bring the evidence panel into the same focal area; settle before the viewer needs to read it. Use a single continuous transition into the closing action, with no last-frame exit. Proposed entrance duration is 0.4 seconds with a cubic ease-out; preserve a minimum 1.5-second readable hold per scene. These are authored decisions awaiting implementation and playback review.

The sample is silent. Narration, music or effects require approved assets and a new timing decision. Retiming for speech must update dependent transitions and holds together. Do not silently add music to the user's request.

## Invariants and replaceable inputs

Keep the three scene purposes, one visual focal point per hold and a settled ending. Replace the subject, headline, evidence caption and action through [inputs.schema.json](inputs.schema.json). Limits count Unicode code points. For overflow, shorten approved copy or redesign/retime the affected scene; do not shrink it until unreadable.

The [product preset](presets/product.json) introduces a fictional planning tool; the [lesson preset](presets/lesson.json) introduces a fictional geometry lesson. Changing the text does not supply proof imagery or create a complete video. A full education fork should change name/version, industry metadata, material requirements and any story overrides while preserving attribution.

## Review

Check the actual material against the approved text, the whole headline at its hold, evidence legibility, the transition and final action. Play the completed work at full speed with the intended audio policy. Record the project/runtime version, inputs, exported file identity, checks performed and remaining differences. The helper's successful output proves only that valid inputs were mapped into the declared sequence.
