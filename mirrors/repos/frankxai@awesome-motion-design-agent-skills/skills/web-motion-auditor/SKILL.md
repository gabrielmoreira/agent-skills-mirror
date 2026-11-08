---
name: web-motion-auditor
description: Use when reviewing web animations, UI transitions, scroll effects, hover states, loading states, GIF/video captures, reduced-motion support, animation performance, or motion polish in HTML, React, Next.js, or Vercel apps.
---

# Web Motion Auditor

## Workflow

1. Identify the exact revision and target URL. Reuse a qualified preview; run a local app only within the environment's resource and ownership rules.
2. Inspect the animated states: load, hover, focus, click, route transition, scroll, empty/loading/success/error.
3. Check accessibility:
   - `prefers-reduced-motion`
   - focus visibility
   - no motion that blocks reading or interaction
4. Check performance on desktop and mobile widths.
5. Capture screenshots/video when possible.
6. Use the bundled [motion quality rubric](references/motion-quality-rubric.md), citing evidence per scored category. Leave unobserved categories unscored.
7. Return concrete fixes with file references.

## Common Fixes

- Shorten transitions.
- Use transforms/opacity instead of layout-heavy properties.
- Reduce stagger count.
- Add reduced-motion branch.
- Replace decorative motion with state-explaining motion.
- Move complex narrative motion to Remotion or a controlled hero scene.

## Required probes

| Probe | Observe |
| --- | --- |
| Keyboard | Visible focus, logical order, Escape/close behavior, no delayed command response |
| Touch | Every action available without hover; scrolling and taps remain usable |
| Reduced motion | Content, hierarchy, and state remain clear; large movement has a designed alternative |
| Interruption | Open then close mid-transition; repeat rapidly; verify the latest state, focus, and cleanup |
| Navigation and resize | No orphan overlays, pinned scroll, duplicate listeners, or stale transforms |
| Failure | Failed media or unavailable JavaScript preserves required content and controls |
| Performance | Measure on the target environment; separate traces, frame captures, and subjective observations |

## Report

Return severity, reproduction steps, file/line, fix, and verification evidence for each finding. Compare before and after in a table when reviewing a patch. Include revision, URL, viewport, input mode, and motion preference. Label missing checks explicitly; a still screenshot cannot prove frame rate or interruption behavior.

This is a review workflow, not a scanner or browser installation. If browser access is unavailable, complete the source review and report runtime checks as pending. Do not invent observations or start other agents or services without authorization.

