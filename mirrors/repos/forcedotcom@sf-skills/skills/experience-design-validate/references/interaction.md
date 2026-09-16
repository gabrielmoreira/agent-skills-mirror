# Interaction

> **Load this reference only with `DYNAMIC_VISUAL` evidence that directly exercises or records hover, click, focus, drag, touch, keyboard, or motion behavior. Static screenshots cannot substantiate interaction craft; mark interaction coverage `INSUFFICIENT_EVIDENCE` rather than inferring behavior.**

## Why this matters

Interaction is where a static surface becomes a living thing — and where craft is felt before it is seen. When interactions are well-crafted, the interface answers every gesture: a button presses back, a hover hints, a drop animates into place, a focus ring lands instantly and tastefully. The product feels responsive, alive, considerate. When interactions are sloppy, the surface feels dead — clicks land in silence, hovers do nothing, motion is either missing or jangly, and the user starts to doubt whether the interface is even working. Interaction craft is what separates products that feel inert from products that feel inhabited.

---

## Affordance and States

- **The eye sorts interactive from inert without hovering.** Buttons look like buttons. Links carry two visible signals. Static elements never borrow interactive styling. Icon-only buttons say what they are — a tooltip, a label, or both.
- **The primary action is obvious.** One filled button per logical section, sitting where the eye expects it. Secondary actions live one degree quieter.
- **Every interactive element has a full life.** Default, hover, pressed, focus, disabled — each visibly distinct. Hover hints, press confirms — the two are different. Missing states make the interface feel half-built.
- **Focus lands cleanly.** Keyboard focus shows up instantly at a consistent offset, tasteful against light and dark. A disabled element feels disabled and quietly explains why.
- **Selected is heavier than hover.** When both apply at once, they're still distinguishable.

## Motion

- **Every animation earns its place.** If removing the motion doesn't reduce comprehension, the motion shouldn't exist. Decoration without purpose reads as showy.
- **Similar transitions share a tempo.** Micro-feedback is quick. Layout changes are moderate. Cross-view transitions are slightly slower. Drift in tempo costs the product its rhythm. Reduced-motion preferences are honored.
- **Motion never reflows the page.** A "smooth" animation that pushes neighboring content is a layout bug wearing a bowtie.

## Micro-interactions

- **Click feedback lands in a single frame.** The button presses, the toggle commits past its midpoint, the dropdown opens with calm — no waiting to see whether anything took.
- **The wait sets the indicator.** A flash for the very fast, an inline spinner for a brief pause, a skeleton for longer. A spinner that appears for 80ms and vanishes feels worse than silence.

## Drag, Touch, and Keyboard

- **Drag and drop feels confident on any input.** Dragged items lift, neighbors make room, valid drops light up, invalid ones say no, cancel always recovers. Keyboard parity is real, not theoretical.
- **Touch targets feel comfortable to tap, not cramped.** Adjacent controls give fingers breathing room. Destructive actions hold their distance. Primary actions land in the thumb's reach.
- **Keyboard shortcuts shadow visible UI.** They accelerate, never replace. Platform conventions are respected. Single-key shortcuts step aside in text inputs.

## Selection and Latency

- **Selection is unmistakable.** What's chosen, how to change it, and what to do with it — all clear at a glance. A floating action bar handles bulk operations without shifting the layout.
- **Every input is acknowledged within a frame.** Optimistic feedback is reserved for the safe and reversible. Search and filtering feel alive but never anxious — calm refinement, not jittery flicker.

---

## Scoring Guide

**Contributes to dimensions: Usable, Reliable, Well-Crafted**

| Score | Criteria |
|-------|----------|
| 9-10 | The interface feels inhabited. Every gesture is answered. Motion is purposeful and quiet. Touch and keyboard parity is real. Latency is invisible. |
| 7-8 | Strong interaction craft with minor gaps in states or motion consistency. |
| 5-6 | Functional but unpolished. Some interactions land in silence; durations drift; touch targets feel cramped. |
| 3-4 | The surface feels dead. Missing states. Inconsistent motion. Keyboard or touch fails. |
| 1-2 | Clicks vanish into silence. The interface feels uninhabited. |
