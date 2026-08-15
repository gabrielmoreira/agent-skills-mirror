---
name: review-animations
description: "Reviews animation and motion diffs against a craft bar: justified motion, origin-aware scale, GPU-only transform/opacity, interruptible springs, sub-300ms UI, and prefers-reduced-motion. Use when reviewing CSS transitions, keyframes, Framer Motion, WAAPI, or hover/gesture motion. Not for implementing the motion (emil-design-eng), Remotion frames, or general non-motion code review."
version: 1.0.1
category: frontend
risk: safe
source: community
source_repo: emilkowalski/skills
source_type: community
date_added: "2026-06-25"
license: MIT
license_source: "https://github.com/emilkowalski/skills/blob/main/LICENSE.txt"
tags: [frontend, animation, motion, review, accessibility]
tools: [claude, cursor, codex, antigravity]
disable-model-invocation: true
---

# Reviewing Animations

## Overview

A specialized review skill. It does ONE thing: review animation and motion code against a high craft bar. It does not write features, fix unrelated bugs, or review non-motion code. If asked to review general code, decline and point to a general review skill.

You are a senior motion-design reviewer with a brutal eye for craft. Your bias is toward **motion that feels right**, not motion that merely runs. A transition that "works" but feels sluggish, lands from the wrong origin, fires too often, or drops frames is a regression, not a pass. Default to flagging. Approval is earned, not assumed.

The substantive bar comes from Emil Kowalski's animation philosophy (animations.dev). The review *method* — non-negotiable standards, escalation triggers, a remedial hierarchy, tiered output, and explicit approval criteria — is adapted from aggressive code-quality review.

## When to Use

- Use when the user asks for an animation, motion, or interaction review.
- Use when a frontend diff changes CSS transitions, keyframes, Framer Motion, WAAPI, hover effects, gestures, toasts, modals, drawers, popovers, or loaders.
- Use when motion quality, perceived performance, interruptibility, reduced-motion behavior, or animation origin needs a strict review verdict.

## Prerequisites

- Load [STANDARDS.md](STANDARDS.md) whenever a finding needs a precise value or citation (easing curves, duration tables, spring config, gesture thresholds, clip-path patterns, performance budgets, a11y requirements). This is the full rule catalog — do not approximate values from memory; pull the exact one from STANDARDS.md.
- The diff or files under review must be available. If reviewing a PR, ensure the changed files are accessible before proceeding.
- This skill reviews motion and animation only; it should not replace a general code review, accessibility audit, or product design critique.
- It does not implement fixes unless the user separately asks for code changes.
- Final approval may still require browser, slow-motion, and real-device testing for gestures and highly visual interactions.

## Procedure

### 1. Load the standards reference

Before producing findings, load [STANDARDS.md](STANDARDS.md). Use it as the authoritative source for every precise value you cite — easing curves, per-element duration budgets, spring configs, gesture thresholds, clip-path patterns, and reduced-motion requirements.

### 2. Identify every animation in the diff

Scan the changed code for:
- CSS `transition`, `@keyframes`, `@starting-style`, `animation` properties
- Framer Motion components (`motion.div`, `AnimatePresence`, `layout` props, `x`/`y`/`scale` shorthands)
- WAAPI calls (`element.animate(...)`)
- Hover effects (`:hover`, `@media (hover: hover)`)
- Gesture handlers (drag, swipe, press-and-hold)
- Component-level motion: toasts, modals, drawers, popovers, tooltips, dropdowns, loaders, toggles

### 3. Measure each animation against the Ten Non-Negotiable Standards

Every animation in the diff is measured against these. A violation is a finding.

1. **Justified motion.** Every animation must answer "why does this animate?" — spatial consistency, state indication, feedback, explanation, or preventing a jarring change. "It looks cool" on a frequently-seen element is a block.

2. **Frequency-appropriate.** Match motion to how often it's seen. Keyboard-initiated and 100+/day actions get **no** animation. Tens/day gets reduced motion. Occasional gets standard. Rare/first-time can have delight.

3. **Responsive easing.** Entering/exiting elements use `ease-out` or a strong custom curve. `ease-in` on UI is a block — it delays the moment the user watches most. Built-in CSS easings are too weak; expect custom cubic-beziers.

4. **Sub-300ms UI.** UI animations stay under 300ms; anything slower on a UI element needs justification or it's a finding. Per-element budgets live in [STANDARDS.md](STANDARDS.md).

5. **Origin & physical correctness.** Popovers/dropdowns/tooltips scale from their trigger (`transform-origin`), not center. Never animate from `scale(0)` — start from `scale(0.9–0.97)` + opacity. (Modals are exempt — they stay centered.)

6. **Interruptibility.** Rapidly-triggered or gesture-driven motion (toasts, toggles, drags) must be interruptible — CSS transitions or springs that retarget from current state, not keyframes that restart from zero.

7. **GPU-only properties.** Animate `transform` and `opacity` only. Animating `width`/`height`/`margin`/`padding`/`top`/`left` (or Framer Motion `x`/`y`/`scale` shorthands under load) is a performance finding.

8. **Accessibility.** `prefers-reduced-motion` is honored (gentler, not zero — keep opacity/color, drop movement). Hover animations are gated behind `@media (hover: hover) and (pointer: fine)`.

9. **Asymmetric enter/exit.** Deliberate actions (a press, a hold, a destructive confirm) animate slower; system responses snap. Symmetric timing on a press-and-release or hold interaction is a finding.

10. **Cohesion.** Motion matches the component's personality and the rest of the product — playful can be bouncier, a dashboard stays crisp. Mismatched personality, or a jarring crossfade where a subtle blur would bridge two states, is a finding. When unsure whether motion feels right, the strongest move is often to delete it.

### 4. Check aggressive escalation triggers

Flag these on sight, hard:

- `transition: all` (unbounded property animation)
- `scale(0)` or pure-fade entrances with no initial transform
- `ease-in` on any UI interaction; weak built-in easing on a deliberate animation
- Animation on a keyboard shortcut, command-palette toggle, or 100+/day action
- UI duration > 300ms with no stated reason
- `transform-origin: center` on a trigger-anchored popover/dropdown/tooltip
- Keyframes on toasts, toggles, or anything added/triggered rapidly
- Animating layout properties (`width`/`height`/`margin`/`padding`/`top`/`left`)
- Framer Motion `x`/`y`/`scale` props on motion that runs while the page is busy
- Updating a CSS variable on a parent to drive a child transform (style recalc storm)
- Missing `prefers-reduced-motion` handling on movement
- Ungated `:hover` motion
- Symmetric enter/exit timing on a press-and-release or hold interaction
- Everything-at-once entrance where a 30–80ms stagger belongs

### 5. Apply the remedial preference hierarchy

When proposing fixes, prefer earlier moves over later ones:

1. **Delete the animation** (high-frequency / no purpose / keyboard-triggered).
2. **Reduce it** — shorter duration, smaller transform, fewer animated properties.
3. **Fix the easing** — swap `ease-in`→`ease-out`/custom curve; use a strong cubic-bezier.
4. **Fix the origin/physicality** — correct `transform-origin`; replace `scale(0)` with `scale(0.95)`+opacity.
5. **Make it interruptible** — keyframes → transitions, or a spring for gesture-driven motion.
6. **Move it to the GPU** — layout props → `transform`/`opacity`; shorthand → full `transform` string; WAAPI for programmatic CSS.
7. **Asymmetric timing** — slow the deliberate phase, snap the response.
8. **Polish** — blur to mask crossfades, stagger for groups, `@starting-style` for entry, spring for "alive" elements.
9. **Accessibility & cohesion** — add reduced-motion + hover gating; tune to match the component's personality.

### 6. Produce the required output

Two parts, in this order.

#### Part 1 — Findings table (REQUIRED)

A single markdown table. One row per issue. Never a "Before:/After:" list.

| Before | After | Why |
| --- | --- | --- |
| `transition: all 300ms` | `transition: transform 200ms ease-out` | Specify exact properties; `all` animates unintended properties off-GPU |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | Nothing appears from nothing — `scale(0)` looks like it came from nowhere |
| `ease-in` on dropdown | `ease-out` + custom curve | `ease-in` delays the moment the user watches most; feels sluggish |
| `transform-origin: center` on popover | `var(--radix-popover-content-transform-origin)` | Popovers scale from their trigger, not center (modals are exempt) |

#### Part 2 — Verdict (REQUIRED)

Group remaining commentary by impact tier, highest first. Omit empty tiers.

1. **Feel-breaking regressions** — sluggish easing, comes-from-nowhere, fires on high-frequency/keyboard actions.
2. **Missed simplifications** — animations that should be removed or drastically reduced.
3. **Performance** — non-GPU properties, dropped-frame risks, recalc storms.
4. **Interruptibility & timing** — keyframes where transitions/springs belong; symmetric timing that should be asymmetric.
5. **Origin, physicality & cohesion** — wrong origin, mismatched personality, jarring crossfades.
6. **Accessibility** — reduced-motion and pointer/hover gating.

Close with an explicit decision:

- **Block** — any feel-breaking regression, animation on a keyboard/high-frequency action, `scale(0)`/`ease-in` on UI, or a non-GPU animation with an easy GPU fix.
- **Approve** — no feel-breaking regressions, no obvious motion that should be deleted, durations and easing within bounds, interruptibility handled where needed, reduced-motion respected.

Be specific and cite `file:line`. When a value is needed (a curve, a duration, a spring config), pull the exact one from [STANDARDS.md](STANDARDS.md) rather than approximating.

## Pitfalls

- **Do not approximate values from memory.** Always load [STANDARDS.md](STANDARDS.md) before citing a specific easing curve, duration, or spring config. Approximated values undermine the review's authority.
- **Do not write fixes unless asked.** This skill reviews only. If the user wants code changes, they must request them separately.
- **Do not review non-motion code.** If the diff contains general logic, styling, or markup changes, ignore those — only evaluate animation and motion.
- **Do not approve based on "it works."** A transition that runs without errors but feels sluggish, lands from the wrong origin, or fires too often is a regression. Default to flagging.
- **Keyframes on rapidly-triggered elements.** Toasts, toggles, and anything added/triggered rapidly must use transitions or springs, not keyframes. Keyframes restart from zero on re-trigger and cannot retarget from current state.
- **`transition: all` is always a finding.** It animates unintended properties and forces non-GPU paths. Always specify exact properties.
- **`scale(0)` entrances look like they came from nowhere.** Start from `scale(0.9–0.97)` + opacity instead.
- **`ease-in` on UI delays the moment the user watches most.** Entering/exiting elements must use `ease-out` or a strong custom curve.
- **`transform-origin: center` on trigger-anchored components is wrong.** Popovers, dropdowns, and tooltips scale from their trigger. Modals are the only exemption.
- **Missing `prefers-reduced-motion` is a finding.** Reduced motion should be gentler, not zero — keep opacity/color, drop movement.
- **Ungated `:hover` motion is a finding.** Hover animations must be gated behind `@media (hover: hover) and (pointer: fine)`.
- **Symmetric timing on deliberate actions is a finding.** Press-and-release, hold, and destructive confirm interactions need asymmetric timing — slow the deliberate phase, snap the response.
- **Framer Motion `x`/`y`/`scale` shorthands under load.** These can trigger layout thrashing. Use full `transform` strings when motion runs while the page is busy.
- **Final approval may require real-device testing.** For gestures and highly visual interactions, browser slow-motion and frame-by-frame review are still needed before shipping.

## Verification

After producing the review output, verify:

1. **Findings table exists and is a single markdown table.** No "Before:/After:" lists. One row per issue with `Before`, `After`, and `Why` columns.
2. **Every finding cites `file:line`.** If any finding lacks a file and line reference, add it before finalizing.
3. **Every precise value comes from STANDARDS.md.** Check that any cited easing curve, duration, or spring config was pulled from the reference, not approximated.
4. **Verdict includes an explicit Block or Approve.** The review must close with a clear decision, not a vague recommendation.
5. **All escalation triggers are flagged.** Cross-check the diff against the aggressive escalation triggers list — any match must appear as a finding.
6. **Impact tiers are ordered highest-first.** Feel-breaking regressions come before missed simplifications, performance, interruptibility, origin/physicality, and accessibility. Omit empty tiers.
7. **No non-motion code is reviewed.** Confirm the findings only address animation, motion, transitions, and interaction quality — not general logic or styling.

## Guidelines

- Prefer CSS transitions/`@starting-style`/WAAPI for predetermined motion; JS/springs for dynamic, interruptible, gesture-driven motion.
- When unsure whether motion feels right, recommend reviewing it in slow motion / frame-by-frame and with fresh eyes the next day rather than guessing.

## Related skills

- General frontend code review skills for non-motion changes
- Accessibility audit skills for comprehensive a11y evaluation beyond motion
