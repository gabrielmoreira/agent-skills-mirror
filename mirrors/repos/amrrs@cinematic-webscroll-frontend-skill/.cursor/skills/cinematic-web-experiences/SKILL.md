---
name: cinematic-web-experiences
description: Build prompts and workflows for premium scroll-driven websites using GSAP ScrollTrigger, Three.js scenes, custom shaders, cinematic loading screens, and responsive motion systems. Use when the user wants a cinematic website, landing page, microsite, or interactive brand experience with scroll storytelling, pinning, parallax, 3D canvas effects, shader-driven visuals, exact animation specs, or a repeatable prompt framework for prompt-based site builders.
---

# Cinematic Web Experiences

Use this skill to turn a vague "make it premium" request into a concrete build plan or prompt.

## Core workflow

1. Lock the visual identity before describing motion.
2. Choose one stack: `GSAP only`, `GSAP + Three.js + GLB`, or `GSAP + Three.js + procedural shaders`.
3. Define sections top-to-bottom before assigning animations.
4. Write exact animation specs with transforms, triggers, and scrub values.
5. Declare every asset path and loader explicitly.
6. Add a dedicated responsive block at the end.

## Non-negotiables

- Use exact hex or `hsl(...)` values for colors.
- Pin Three.js when 3D is involved: `three@0.136.0`, `@types/three@0.136.0`.
- Prefer one accent color against a near-black base for premium dark-mode builds.
- Add `overflow-x: hidden` to `html`, `body`, and `#root`.

## Optional companion dependency

If the user needs new source assets such as images, textures, or looping video backgrounds, pair this workflow with the `fal-ai-community/skills` repo first to generate the media, then reference the resulting asset paths in the final website prompt.

If the frontend is typography-heavy and exact multiline headline layout matters, optionally pair this workflow with `pretext` for accurate text measurement and layout.

## Read next

- Read `reference.md` for the compact playbook.
- Read `../../../shared/cinematic-web-experiences/guide.md` for the full canonical guide, prompt template, and project-derived patterns.
