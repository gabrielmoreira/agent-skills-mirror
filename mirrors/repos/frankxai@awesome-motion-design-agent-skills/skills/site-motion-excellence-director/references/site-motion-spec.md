# Site Motion Spec

Use this before implementing meaningful website or app motion.

## Context

Brand:
Site/repo:
Page/route:
Audience:
Primary user task:
Surface:

## First Read

In two seconds, the visitor should understand:

- What this is:
- Who it is for:
- Main product/object/state:
- Primary action:
- Trust/proof signal:

## Motion Thesis

Motion job:
Behavior keywords:
What should feel more understandable because this moves:
What should feel more memorable because this moves:

## Still Frame Gate

Static first frame or screenshot:
Hero object:
Supporting elements:
What stays still:
What is removed:

Pass/fail:
Notes:

## Motion Map

Motion name:
Trigger:
Affected elements:
Initial state:
Animated state:
Final resting state:

Beat sequence:

1. Setup:
2. Trigger:
3. Primary motion:
4. Secondary motion:
5. Hold:
6. Exit or loop return:

## Timing

Duration:
Delay:
Stagger:
Easing/spring:
Interruption behavior:
Loop behavior:

## Runtime

Chosen runtime:
Why this runtime:
Fallback runtime:
Files/components likely touched:
Asset needs:

## Reduced Motion

Reduced-motion behavior:
What information remains visible:
What motion is removed:
Static replacement:

## Performance And Accessibility

Layout shift risk:
Paint/composite risk:
Autoplay/sound policy:
Keyboard/focus impact:
Pause/stop controls needed:

## QA Proof

Required proof:

- desktop screenshot
- mobile screenshot
- reduced-motion screenshot
- short video or frame sequence
- build/type/lint result
- Vercel preview URL when connected

Acceptance checks:

- Motion has a clear job.
- The most important object is easiest to see.
- Text remains readable.
- Controls do not move away from the user.
- Mobile is intentionally composed.
- Reduced motion preserves meaning.
- Final asset/page feels brand-specific, not template-like.
