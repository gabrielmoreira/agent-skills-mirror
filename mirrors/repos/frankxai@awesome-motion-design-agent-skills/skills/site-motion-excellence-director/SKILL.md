---
name: site-motion-excellence-director
description: Use when planning, auditing, specifying, implementing, or improving premium website/app motion across FrankX, Arcanea, Starlight, or Vercel/Next.js sites. Use for motion design systems, site choreography, scroll motion, generated media integration, runtime selection, reduced-motion planning, visual QA, and turning rough motion ideas into implementation-ready specs.
---

# Site Motion Excellence Director

Use this skill before adding substantial motion to a website or app.

## Workflow

1. Identify the brand, route, audience, and first user task.
2. Define the first read before animation.
3. Name the motion job: orient, reveal, explain, confirm, compare, express brand, or convert.
4. Pass the still-frame gate.
5. Write a beat sequence: setup, trigger, primary move, secondary support, hold, final state.
6. Choose the lightest runtime that preserves the intent.
7. Specify reduced motion in the same pass.
8. Implement only after the spec is clear.
9. Verify with browser screenshots, mobile, reduced motion, and video/frame proof.
10. Score with the excellence gate.

## Runtime Rules

- Use CSS for simple state changes, hover/focus, skeletons, and low-risk reveals.
- Use Motion for React for component choreography, layout transitions, presence, and React scroll work.
- Use GSAP ScrollTrigger for pinned, scrubbed, snapped, SVG/canvas, or complex authored timelines.
- Use Rive for interactive vector state machines.
- Use Lottie/dotLottie for portable non-interactive vector loops.
- Use Three.js only when 3D is central and visually verified.
- Use Remotion for rendered video, social variants, product explainers, and exact text/layout in media.
- Discover the session's actual image/video tools before choosing a generator. Check current provider documentation, access, cost, and rights; finish and QA the result in context. A provider name here is not proof of availability or authorization to spend.

## Taste Rules

- Motion is hierarchy over time.
- Do not animate a weak still frame.
- Make one object the hero.
- Use stillness as contrast.
- Keep repeated task motion short and quiet.
- Do not bake exact product text into generated images or videos.
- Treat mobile as separate choreography.
- Never ship meaningful motion without reduced-motion behavior.

## Required Spec

Use the bundled [site motion spec](references/site-motion-spec.md) for substantial site motion.

Use the bundled [site motion excellence gate](references/site-motion-excellence-gate.md) before handoff. Both files are included when this skill is installed alone.

## Interaction and recovery

- Preserve native reading, scrolling, focus, and touch behavior. Required content must remain available when JavaScript or a media request fails.
- Define what happens on repeated clicks, reverse scroll, route changes, resize, hidden tabs, and preference changes. Dispose timelines, observers, and listeners when their owner unmounts.
- Gate hover effects by pointer capability. Provide visible focus and immediate keyboard actions.
- Reduced motion must preserve the full story in reading order. Do not initialize expensive scroll or 3D effects merely to disable them afterward.
- Use current [Motion](https://motion.dev/docs), [GSAP](https://gsap.com/docs/v3/), or [Three.js](https://threejs.org/docs/) documentation for the runtime actually installed. Reuse the site's dependencies and tokens.

## Evidence

Record the exact revision, desktop and phone widths, keyboard/touch observations, reduced-motion result, interrupted-transition result, and inspected video/frame sequence. Distinguish code review, automated checks, emulated input, physical-device checks, and untested behavior. Do not award an excellence score when the visual evidence is missing.

## Output Shape

Return: motion thesis, first-read diagnosis, still-frame verdict, motion map, runtime choice, reduced-motion plan, implementation tasks, QA proof required, and excellence score.
