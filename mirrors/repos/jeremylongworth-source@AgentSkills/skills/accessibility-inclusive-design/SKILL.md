---
name: accessibility-inclusive-design
description: Design, audit, and improve accessibility and inclusive user experiences. Use when Codex is asked about WCAG, keyboard navigation, focus states, screen readers, ARIA, contrast, captions, reduced motion, forms, semantic HTML, accessible UI, game accessibility, inclusive design, accessibility QA, or compliance-sensitive accessibility work.
license: MIT
---

# Accessibility Inclusive Design

## Core Workflow

1. Identify the product surface, audience, platform, assistive technologies, input methods, legal/compliance context, and risk level.
2. Use semantic structure first. Add ARIA only when native semantics cannot express the interaction correctly.
3. Check the experience across keyboard, pointer/touch, screen reader, zoom/reflow, color/contrast, motion, captions/audio alternatives, and error recovery.
4. Separate automated checks from human judgment. Automated tools catch some issues; they do not prove accessibility.
5. Prioritize blockers that prevent task completion, then issues that create confusion, fatigue, or exclusion.
6. Verify fixes in the actual interface and target states.

## Freshness Rule

Verify current W3C/WAI WCAG guidance and platform accessibility documentation before giving compliance-sensitive advice. WCAG 2.2 is the current W3C recommendation for maximizing future applicability, but legal requirements vary by jurisdiction and this skill is not legal advice.

## Accessibility Priorities

- Keyboard: every interactive control is reachable, operable, visible on focus, and ordered logically.
- Semantics: landmarks, headings, labels, buttons, links, forms, tables, lists, and status messages expose correct meaning.
- Screen readers: dynamic updates, dialogs, menus, comboboxes, errors, and live regions are announced appropriately.
- Visual access: color contrast, text size, spacing, reflow, zoom, and non-color signals are handled.
- Motion: animation, parallax, camera shake, flashing, and transitions respect reduced-motion needs.
- Media: captions, transcripts, audio description, and visual alternatives are considered.
- Games: provide remapping, subtitles, visual audio cues, difficulty assists, readable UI, pause options, and avoid audio-only critical signals unless intentional.

## Deliverable Shape

For accessibility work, provide:

- Surface and user task
- Applicable standard or target quality bar
- Findings by severity
- Evidence and affected users
- Recommended fixes
- Verification steps
- Remaining compliance or legal uncertainty

## References

- Read `references/accessibility-checklist.md` when auditing or designing accessible experiences.
