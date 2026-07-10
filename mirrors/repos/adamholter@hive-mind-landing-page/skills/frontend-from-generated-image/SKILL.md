---
name: frontend-from-generated-image
description: "Use for frontend/UI builds, redesigns, polish, or extensions. Before coding, generate a UI reference image, then closely match it instead of inventing a new direction."
---

# Frontend From Generated Image

Use this skill for any task that includes a frontend, screen, page, component set, dashboard, landing page, app shell, modal, chat UI, or other visible interface.

When the task is an iteration on an existing UI rather than a full redesign, treat the current UI as an important constraint.

This skill is intentionally strict: the generated or user-provided image is not a moodboard. It is the target. The implementation should look like a faithful translation of the image into working code.

## Core rule

Before writing frontend code:

1. Use the `imagegen` skill and the built-in OpenAI image generation tool.
2. If iterating on an existing UI, first gather reference screenshots of the current experience unless the user explicitly wants a full redesign.
3. Generate or accept at least one UI design reference image for the requested interface.
4. Treat the reference image as the design source of truth, while preserving existing-product constraints when the task is iterative.
5. Implement the frontend by copying the image's layout, hierarchy, spacing, typography, color relationships, asset placement, and overall composition as closely as practical in real code.
6. Verify with screenshots and refine until the rendered result visibly matches the reference.

Do not skip the image-generation step unless the user explicitly tells you not to.

## Workflow

1. Read the product/task requirements and infer the key UI surfaces that need to exist.
2. If the task is modifying an existing frontend, collect reference screenshots of the current UI first.
3. Unless the user asked for a full redesign, use those screenshots as reference inputs and constraints for the design-generation prompt.
4. Write a design-generation prompt for the interface.
5. Generate the reference image with the built-in OpenAI image tool.
6. Inspect the result and write a concrete visual brief before coding:
   - layout structure
   - alignment and spacing
   - type scale
   - component shapes
   - color palette
   - background treatment
   - visual density
   - major asset locations and dimensions
   - element ordering and z-index/layer relationships
   - motion cues implied by the composition
7. Build the real frontend to match that image closely. Work one section or screen at a time when the reference contains multiple sections.
8. Capture a screenshot of the implementation at the same viewport/aspect ratio as the reference.
9. Compare screenshot to reference and fix mismatches in layout, spacing, scale, color, asset placement, and typography before moving on.
10. If the generated image is weak, generate another one and use the stronger reference.

## Prompting guidance for the image

When prompting the image model:

- Describe the product type and exact screen to render.
- Ask for a polished product UI mockup, not an abstract moodboard.
- Specify the platform when relevant: desktop web app, mobile app, landing page, chat tool, admin panel, etc.
- Include the desired tone and brand feel.
- Ask for clear hierarchy, refined spacing, and realistic interface composition.
- Request a full-screen UI screenshot/mockup perspective.
- If the tool already has an established product direction, preserve it rather than reinventing it.
- If iterating on an existing UI, provide the current UI screenshots as references whenever the image workflow supports that.
- For iterative work, prompt for an improved version of the current design rather than a replacement design, unless the user explicitly asked for a full redesign.

## Image-to-code translation rules

- Do not rebuild illustrated/photo/3D assets with CSS, SVG primitives, gradients, or decorative divs. Use real image assets for those parts.
- If the reference contains embedded product art, character art, photos, renderings, textures, icons, or abstract image panels, create explicit asset slots in the project and tell the user or future agent exactly where those files belong.
- If the user supplied extracted assets, use those assets directly and clone the surrounding layout, components, typography, spacing, and effects.
- If assets need transparent backgrounds, use the local `fal-media-gen` Pixelcut Background Remover workflow; do not send the user to external web tools, fake transparency with white boxes, or rebuild image assets in CSS.
- For multi-section pages, translate one section at a time. Do not rough in all sections and hope the overall impression carries the design.
- Preserve the exact visual hierarchy of the reference: what is biggest, what is quietest, what aligns to what, and where the eye lands first.
- Measure proportions from the reference when possible: viewport coverage, section height, image aspect ratios, column widths, gutters, nav height, button height, and card density.
- Use CSS variables or design tokens for colors, spacing, radii, and shadows that visibly repeat in the reference.
- Avoid adding extra explanatory copy, extra cards, extra badges, or extra decoration that is not present in the reference.
- When text in the generated image is unreadable or nonsensical, replace it with concise realistic copy while preserving the same line lengths, weight, hierarchy, and density.

## Implementation guidance

- Copy the generated image, do not merely "take inspiration from it."
- For iterative work, preserve the recognizable product structure and only change what the task calls for.
- Match the big decisions first: composition, scale, contrast, and layout rhythm.
- Then match the smaller decisions: radii, borders, shadows, gaps, card proportions, and type treatment.
- Preserve usability and accessibility while translating the image into production code.
- If the generated image includes impossible or unclear details, infer the closest practical implementation without changing the visual direction more than necessary.

## Fidelity checklist

Before calling the implementation done, check these against the reference image:

- Same viewport framing: hero/section height, first-fold composition, and visible next-section hint when applicable.
- Same macro layout: column count, alignment, negative space, overlap, asymmetry, and section rhythm.
- Same visual weight: heading scale, supporting text scale, button prominence, image size, and card density.
- Same color relationships: background, text contrast, accent amount, borders, shadows, and gradients.
- Same component geometry: radii, stroke weights, padding, gaps, and icon/button sizes.
- Same asset behavior: images use correct aspect ratio, cropping, object position, transparency, and layering.
- Same responsive intent: mobile should feel like a faithful adaptation, not a different design.
- No accidental additions: remove default nav text, generic feature cards, filler badges, random icons, and decorative effects that were not in the reference.

If the screenshot does not match, keep iterating. Name the top mismatches, patch them, and screenshot again.

## Priority over default design behavior

If another frontend skill suggests inventing a fresh visual direction, this skill takes priority for UI direction. The generated image should anchor the design.

## Deliverable behavior

For frontend tasks covered by this skill, the expected flow is:

1. Generate the reference image.
2. Extract or prepare any needed assets and define their project paths.
3. Build the UI to match the reference section-by-section or screen-by-screen.
4. Verify the implementation visually with screenshots.
5. Refine toward the reference until the main mismatches are resolved.
