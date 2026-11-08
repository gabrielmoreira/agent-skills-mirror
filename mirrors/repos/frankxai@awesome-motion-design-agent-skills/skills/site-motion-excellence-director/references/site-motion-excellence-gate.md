# Site Motion Excellence Gate

Use this to decide whether website/app motion is ready to ship.

Score each category 1-5. Target 45+ for premium launch work.

## Scorecard

| Category | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Intent | Decorative or unclear | Some purpose | Motion clarifies hierarchy, state, or story |
| Still Frame | Weak without motion | Acceptable | Strong enough to ship static |
| Product Specificity | Generic atmosphere | Some relevant signals | Real product/workflow/world is visible |
| Hierarchy | Eye wanders | Mostly clear | Eye lands exactly where intended |
| Choreography | Many unrelated moves | Basic sequence | Setup, reveal, support, hold, resolve |
| Timing | Slow/noisy/default | Usable | Deliberate rhythm, pause, and settle |
| Restraint | Everything moves | Some contrast | Stillness makes signature motion stronger |
| Brand Fit | Template-like | On-brand surface | Behavior expresses the brand without a logo |
| Usability | Blocks reading/tasks | Minor friction | Fast, readable, interruptible |
| Accessibility | No reduced-motion | Partial fallback | Complete reduced-motion experience |
| Runtime Fit | Overbuilt or fragile | Reasonable | Lightest tool that preserves intent |
| Evidence | No proof | Screens only | Browser/mobile/reduced-motion/video proof |

## Automatic Fails

- No reduced-motion route for non-trivial motion.
- Generated text is garbled or baked into important UI.
- Motion hides controls or causes layout shift.
- Scroll pinning traps reading.
- The page is weaker when motion is disabled.
- No visual proof was inspected.

## Upgrade Prompts

When score is below 38:

- What should remain still?
- What one motion deserves to be remembered?
- Can the product be shown more concretely?
- Can this be explained with a static diagram instead?
- Is the runtime too heavy for the job?
- What is the first frame and final hold?

When score is 38-44:

- Shorten repeated interactions.
- Reduce stagger distance.
- Improve easing and settle.
- Add a clearer hold.
- Remove one secondary movement.
- Capture mobile and reduced-motion proof.

When score is 45+:

- Package the pattern into tokens/specs.
- Add a poster/static fallback.
- Save proof artifacts.
- Add the pattern to the brand motion library.
