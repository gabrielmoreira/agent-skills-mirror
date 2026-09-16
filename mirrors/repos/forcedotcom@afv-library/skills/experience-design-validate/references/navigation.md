# Navigation

> **Skip this reference if the input is a single screen with no IA, no nav system, no tabs, no breadcrumbs, no search, and no inter-page linking.**

## Why this matters

Navigation is the structural craft of a product — the bones beneath every surface — and a user feels its quality long before they could articulate it. When navigation is well-crafted, the product feels orienting: you always know where you are, where you can go, and what is one click away; the active state catches the eye, breadcrumbs settle in calmly, and the sidebar collapses with a confidence that suggests someone thought about it. When it is poorly crafted, the product feels like a maze — labels mismatch destinations, the active state drifts, mobile becomes a hamburger graveyard, and every click feels like a guess. Great navigation is invisible discipline; bad navigation is the first thing users complain about.

---

## Information Architecture

- **The map is shallow and task-shaped.** No primary destination feels like an excavation. Labels mirror what the user came to do, not the engineering team's diagram. The top level is small enough to scan in one glance.
- **No junk drawers.** Sections labeled "Other" or "More" without further structure read as places where decisions weren't made.
- **Every label promises what it delivers.** A click that lands somewhere unexpected breaks trust faster than any visual flaw. The same destination never has two labels.

## The Nav Frame

- **The frame holds still.** Primary navigation stays in the same place across every screen. When it drifts, the product feels assembled by different teams.
- **The chrome chooses its style.** Sidebar for many destinations or top bar for a few — never a hamburger on desktop pretending to be a navigation system.
- **Active state announces itself.** The current location reads at a glance — distinct from hover, distinct from default, calm rather than shouty. It lights up the moment the click lands, even if content is still on the way.
- **Collapsed states still navigate.** A collapsed sidebar with unrecognizable icons isn't a feature, it's a riddle.

## Tabs and Breadcrumbs

- **Tabs hold parallel views, not pages.** When the content behind a tab feels like a different topic, that topic deserved a destination. Tabs stay modest in number, never wrap to a second row, and use short uniform labels. The active indicator sits cleanly — a precise underline sized to the label.
- **Breadcrumbs settle into the page; they don't compete with it.** Smaller than the page title, muted, with the current page rendered as plain text. Long trails fold their middle into an ellipsis.

## Search and URLs

- **Search lands where the eye looks and answers calmly.** Top-center or top-right on desktop, persistent on mobile, summoned by shortcut from anywhere. Suggestions arrive without jittery flicker. Exact matches go straight to the destination.
- **The URL is shareable and human-readable.** Every meaningful state has its own address. Back returns to where the user was — filters, scroll, and tab selection preserved.
- **Missing destinations explain themselves.** "Doesn't exist" looks different from "you can't see this." Both offer a way back. Transitions between pages never go blank.

## Responsive

- **Each viewport gets its own nav.** Full sidebar on desktop, icon rail on tablet, bottom tabs or drawer on mobile. A shrunken desktop nav on a phone is the giveaway of unfinished work. Mobile primary actions sit in the thumb zone.

---

## Scoring Guide

**Contributes to dimensions: Useful, Usable**

| Score | Criteria |
|-------|----------|
| 9-10 | The user always knows where they are and where they can go. IA mirrors tasks. Active state is unmistakable. URL and back behave as expected. Each viewport has its own nav voice. |
| 7-8 | Navigation is solid with minor inconsistencies in active state, breadcrumbs, or mobile transformation. |
| 5-6 | Functional but with junk drawers, drifting active state, or mobile that's a reflowed desktop. |
| 3-4 | Confusing IA, broken back behavior, labels that mismatch destinations. |
| 1-2 | Users can't tell where they are or where to go. |
