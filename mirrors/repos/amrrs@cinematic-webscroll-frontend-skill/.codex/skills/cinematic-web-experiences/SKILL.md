---
name: cinematic-web-experiences
description: Build prompts and implementation plans for cinematic websites that use GSAP ScrollTrigger, scroll storytelling, pinned heroes, parallax, Three.js scenes, GLB assets, custom shaders, and premium loading screens. Use when Codex needs to design or prompt a landing page, multi-section microsite, or interactive brand experience with exact motion specs, responsive behavior, fixed-canvas 3D effects, or a repeatable framework for prompt-based site builders.
---

# Cinematic Web Experiences

Use this skill when the user wants a site that feels editorial, premium, or cinematic rather than generic.

## Quick workflow

1. Define exact visual tokens first.
2. Pick the animation stack before writing the prompt.
3. Design sections from top to bottom.
4. Specify each animation with exact values.
5. Declare asset paths and loaders.
6. Finish with responsive rules.

## Required defaults

- Use exact hex or `hsl(...)` tokens.
- Pin `three@0.136.0` and `@types/three@0.136.0` for any Three.js build.
- Prefer one accent color on a near-black base unless the user asks otherwise.
- Add `overflow-x: hidden` on `html`, `body`, and `#root`.

## Optional companion dependency

If the user needs fresh media assets such as concept images, textures, or background video loops, use the `fal-ai-community/skills` repo as a companion workflow to generate them first, then feed the resulting files back into this website workflow.

If the design depends on exact multiline text wrapping, balanced editorial headings, or dynamic text measurement, optionally use `pretext` alongside this workflow.

## Read next

- Read `references/guide.md` for the Codex-ready condensed reference.
- Read `../../../shared/cinematic-web-experiences/guide.md` for the full canonical guide and prompt template.
