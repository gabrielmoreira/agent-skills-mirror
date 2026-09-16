# Responsive Design

> **Skip this reference if the input targets a single fixed viewport with no media queries, no mobile/tablet/desktop variants, and no embedded use case.**

## Why this matters

Responsive craft is the discipline of composing the same product gracefully across every viewport, and it is one of the surest signs that a designer thought past the artboard. When it is well-crafted, mobile feels designed for the thumb, tablet earns its width with side-by-side layouts, desktop uses space for density rather than empty margins, and the spaces between breakpoints never feel cramped or abandoned. When it is poorly crafted, the product feels like one screen warped to fit others — buttons drift off the edge, text walls appear at wide widths, mobile becomes a sad shrunken desktop. Considered responsiveness is what makes a product feel native everywhere it lives.

---

## Across Breakpoints

- **Each viewport feels intentional.** Not a single layout warped to fit, but distinct compositions that look designed for the size they live at. The dead zones between common breakpoints are tended — content doesn't crowd, clip, or strand itself in awkward gutters.
- **Content priority leads the layout.** Most important elements stay visible; decoration drops away first; secondary content collapses or moves before primary content does. Multi-column layouts collapse with grace — never an orphan trailing item that exposes the grid's seams.
- **Spacing scales with the viewport.** Generous on desktop, moderate on tablet, modest but never zero on mobile. Hierarchy holds at every width.

## Mobile

- **Mobile is its own design, not a shrunken desktop.** Designed for the thumb, the glance, and the interruption. Targets feel comfortable to tap, not cramped. Primary actions live in thumb territory; rare or dangerous ones sit out of reach.
- **Single-column layouts feel calm, not stretched.** Buttons, inputs, and cards span the width with intent. Body text never shrinks below comfort. Safe areas — notches, home indicators, rounded corners — are accommodated rather than fought.

## Tablet

- **Tablet earns its width.** Side-by-side list/detail layouts, persistent navigation, two-pane workflows — not a stretched phone screen. Both orientations feel designed. Touch parity holds at the larger size; every action remains reachable by tap alone.

## Desktop

- **Space serves density, not emptiness.** A narrow centered column with massive margins on a wide screen reads as wasted real estate. Multi-column architecture is composed with deliberate widths and breathable gaps.
- **The layout works from a small laptop to a wide monitor.** Ultrawide doesn't yield endless empty gutters; small desktop doesn't crowd. Max-width keeps reading lines from sprawling.
- **Mouse and keyboard precision are leveraged.** Hover layers, right-click menus, drag-and-drop, shortcuts, command palette — the input device's strengths are used rather than ignored. Density modes give intensive users a calmer view.

## Embedded

- **An embedded surface behaves like a guest.** Minimal chrome, compact controls, denser spacing. Visual integration respects the host's palette and typography. Overflow stays inside — the embed never pushes the host's layout around. A path to the full experience exists when space gets tight.

---

## Scoring Guide

**Contributes to dimensions: Well-Crafted, Usable**

| Score | Criteria |
|-------|----------|
| 9-10 | Every viewport feels intentionally composed. Mobile is designed for the thumb. Desktop uses space for density. The spaces between breakpoints are tended. |
| 7-8 | Strong responsive craft with minor gaps at edge widths. |
| 5-6 | Mobile reads as a reflowed desktop. Some breakpoints feel cramped or empty. |
| 3-4 | Touch targets are too small. The layout fights the viewport. |
| 1-2 | Layout breaks at common viewports. The product wasn't designed for the screens it lives on. |
