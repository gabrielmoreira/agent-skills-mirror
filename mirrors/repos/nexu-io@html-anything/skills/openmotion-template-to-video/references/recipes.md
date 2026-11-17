# Template adaptation recipes

Optional story guidance for a template adaptation that needs an editorial outline; do not load for unchanged template opening/export or a scoped text edit. These examples do not replace reference reconstruction or dictate a template's accepted motion.

For a requested starter draft, selected template defaults and graphics are usable without optional media. For an actual product film, adapt copy, sample brands and data to verified facts; apply the [shared material policy](../../openmotion-production/references/materials.md) when selecting, obtaining or replacing assets.

The three recipes below help adapt the story. They do not identify installed presets or impose a fixed scene count. Implement the chosen outline as native compositions with source files or Studio, following the pinned authoring guide.

## `product-proof` — show one useful transformation

Best for a product feature with real before/action/result material. Illustrative 15-second sequence, not a default requirement:

| Time | Purpose | Visual/material | Layout |
| --- | --- | --- | --- |
| 0–2s | Recognizable problem | Real before state, tightly framed | Short caption away from the important detail |
| 2–5s | Introduce the action | Actual interface/action recording | `contain` for UI whose edges matter |
| 5–9s | Demonstrate the change | Real interaction/result footage | One explanatory caption, stable placement |
| 9–12s | Let the viewer verify the result | Legible result screenshot or held video section | Hold without competing copy |
| 12–15s | Next action | Supplied branded end card/product image | Clear CTA and one accent |

Character: direct, evidence-led, with deliberate reading holds. Requires real UI or result assets; do not invent a dashboard, cursor interaction or numerical proof. If only stills exist, describe the result as a still-image edit, not an animated UI reconstruction.

## `detail-led` — a product through tangible details

Best for physical products, spaces or a small photo/video set. Illustrative 12-second sequence, not a default requirement:

| Time | Purpose | Visual/material | Layout |
| --- | --- | --- | --- |
| 0–3s | Establish the object | Strong hero image or close footage | `cover` only if the subject survives the crop |
| 3–6s | Show a meaningful detail | Material/process/detail image | Minimal caption, consistent accent |
| 6–9s | Show use or context | Real usage footage or a second useful view | Alternate scale through source selection |
| 9–12s | Leave a memorable ending | Product/brand image | Readable name and CTA |

Character: fewer words, longer holds, variety through the supplied views. Requires genuinely different useful shots; repeating one image with different adjectives does not establish value. No synthetic camera motion is implied by this recipe.

## `reference-rhythm` — follow an inspected reference's pacing

Best when the user supplies a reference clip and replacement material. Duration and scene count come from inspected cut points and the agreed delivery specification.

1. Inspect the reference and state what will be reused: timing, order of reveals, crop relationships or caption placement.
2. Inspect candidate cuts with available reference-analysis tools or player/frame review; record evidence. The removed legacy cut detector is not an available MCP tool.
3. Write a reference-time → new-shot → new-asset mapping. A detected cut is not semantic scene understanding.
4. Build native compositions and clips with approved final material, then adapt copy, audio and `data-media-start` source ranges.
5. Inspect each cut and the overall pacing again after replacements; different assets may need longer holds.

Character: resembles the reference's rhythm while expressing this project's content. Validate each effect against the pinned native guide and rendered evidence; do not promise baked-in text removal or pixel-perfect reconstruction without suitable tools and comparison. Reference clips can remain in a delivered film only if the user explicitly wants that material and its use is authorized.

## Custom direction

Use a user-supplied template, a combination of recipes, or a new shot outline when it better serves the brief. Keep the same storyboard fields and capability checks. Do not force an educational film or an existing brand format into a product-ad structure.

## Selection card and lock-in

Example card structure, filled with this project's facts:

```text
Native template ID / name / recommended if applicable (or custom/reference direction)
Editorial recipe, if used: product-proof, detail-led or reference-rhythm
Opening: exact proposed visual and line
Story: shot-by-shot outline and durations
Material: existing assets and any essential gaps
Look: composition, caption placement, accent, reading rhythm
Preview: actual image path or “text storyboard; not yet rendered”
Tradeoff: what this direction emphasizes or requires
```

Allow a choice by ID/name, a requested adjustment, or “you decide.” Record the native template ID separately from any editorial recipe and note earlier authorization in `STATE.md`; refine the selected outline into `STORYBOARD.md`. Do not apply competing templates to the live project just to show samples; use the gallery preview or separate artifacts. Keep sample labels and template IDs out of final footage.
