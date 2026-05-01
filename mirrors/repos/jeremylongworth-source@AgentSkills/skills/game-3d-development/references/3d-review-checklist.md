# 3D Review Checklist

Use this checklist before finishing a 3D game feature.

## Playability

- Controls respond consistently across frame rates.
- Camera keeps the primary action visible and avoids unnecessary clipping, jitter, or nausea-inducing motion.
- Collision, triggers, and interactables behave predictably at normal and edge-case speeds.
- Failure, reset, pause, and focus-loss states are handled.
- Debug or tuning affordances exist for values likely to need iteration.

## Technical Fit

- Code follows the project's scene, component, ECS, or object ownership patterns.
- Gameplay entities use composition where capabilities need to be reused, swapped, tested, or shared across players, enemies, props, items, and interactables.
- Components have one clear responsibility and communicate through signals, events, interfaces, or narrow typed references.
- Orchestrator scripts coordinate state without absorbing component internals.
- Hot paths avoid avoidable allocation and expensive per-frame searches.
- Asset loading, pooling, and disposal are explicit.
- Physics layers, tags, masks, and units are documented in code or data where ambiguity would hurt maintenance.
- Network, save/load, replay, or determinism requirements are considered if the project has those systems.

## Presentation

- Animation and gameplay state cannot silently disagree.
- VFX, SFX, haptics, and UI feedback align with the gameplay event timing.
- Placeholder assets are named clearly and isolated for replacement.
- Lighting, scale, and readability work at expected camera distances.

## Verification

- Run available tests, editor checks, or builds.
- For browser/WebGL, capture desktop and mobile screenshots and confirm the canvas is nonblank and framed correctly.
- Test at least one low-end or constrained quality profile when performance is relevant.
