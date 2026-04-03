# Cursor Playbook

Use this file as the fast path for cinematic website prompting. For the full guide, read `../../../shared/cinematic-web-experiences/guide.md`.

## Decide the stack first

- `GSAP only`: reveals, pinning, parallax, hover motion, mouse tracking
- `GSAP + Three.js + GLB`: a real 3D object that rotates or floats with scroll
- `GSAP + Three.js + shaders`: procedural scene, no external model, highest prompt complexity

If Three.js is included, pin:

```text
Install three@0.136.0, @types/three@0.136.0
```

## Build prompts in this order

1. `Visual identity`
   - background, card, primary, accent, foreground, muted, fonts, weights
2. `Tech stack`
   - GSAP, ScrollTrigger, Three.js if needed, Lenis if using 3D
3. `Sections`
   - loading screen, fixed navbar, `100vh` hero, content sections, outro
4. `Animations`
   - exact transforms, trigger points, scrub values, stagger values
5. `Assets`
   - every file path, loader, and procedural fallback
6. `Responsive`
   - `clamp()`, mobile menu, layout collapse, camera distance, `overflow-x: hidden`

## Prompting rules

- Never say "dark blue" or "light gray." Use exact values.
- Never say "animate in nicely." Specify `x`, `y`, `scale`, `rotation`, `opacity`, `start`, `end`, and `scrub`.
- Treat each section as an animation stage with its own `ScrollTrigger`.
- For Three.js pages, prefer a fixed fullscreen canvas with `pointer-events: none` below the HTML layer.
- Use one normalized `scrollProgress` value to drive 3D motion.

## Reusable patterns

- GSAP-heavy 2D scroll storytelling with strong brand tokens
- GLB-based Three.js scene with scroll-reactive product motion
- procedural shader scene with no external 3D assets

## Default answer shape

When the user asks for a cinematic web concept, produce:

1. recommended stack and why
2. exact color and font tokens
3. section architecture
4. animation spec lines
5. asset requirements
6. responsive block
7. a final builder-ready prompt
