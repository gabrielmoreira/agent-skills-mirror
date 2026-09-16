# Visual System

> **Always load for any visual design. Skip only if the input is purely textual or pre-visual (a wireframe with no visual decisions yet made).**

What does the design look like? This reference judges the felt qualities of the visual system — layout, typography, color, surfaces, and visual assets — at the level a designer would discuss them in a critique. Not at the level of CSS variables.

## Why this matters

The visual system is the voice of the product. It's what users see before they read a word. A coherent visual system feels like one person made it; a fragmented one feels like a committee shipped it. Two designers can have the same layout brief and end up in completely different places — one with a system that feels intentional and quiet, one with a system that feels accumulated and loud.

Visual system findings are about *taste applied consistently*. The eye notices when the type sizes don't relate to each other, when the grays are slightly off from each other, when borders happen sometimes and not other times, when icons are different weights, when avatars are different sizes. None of these failures is catastrophic alone. Together, they're what separates "looks pro" from "looks built."

---

## Layout

### What good layout feels like

- **One focal point per screen.** The eye knows where to land first. Everything else is calmer.
- **Generous whitespace around what matters.** Primary actions and headlines have air around them. Density is reserved for content where users need to compare or scan many items at once.
- **A consistent rhythm.** The vertical beat of the page is predictable — sections are spaced consistently, and the spacing between a heading and its content is tighter than the spacing between sections.
- **Aligned, not approximate.** Elements share precise edges, not "near enough" edges. The eye can detect 2-pixel misalignment even when it can't name it.
- **Density matched to context.** A dev tool earns dense, utilitarian layout. A consumer onboarding screen earns generous breathability. The layout reflects what the product is trying to be.

### Felt observations to make

- The eye knows where to land within the first second.
- Primary content is clearly heavier than chrome (toolbars, headers, sidebars).
- Headings are closer to their content than to the section above.
- Page margins are equal and don't change between similar pages.
- Whitespace around primary actions feels deliberate, not accidental.
- The grid feels consistent — columns don't shift between similar pages.
- Toolbar heights, sidebar widths, and content margins feel consistent across screens.
- Sticky headers stay put; scroll position is preserved when navigating away and back.

### What weak layout looks like

- The eye doesn't know where to start. Multiple things tied for primary.
- Sections butt up against each other; nothing breathes.
- Spacing varies subtly between similar screens — same component, different padding.
- Elements are *almost* aligned (a few pixels off) — looks like a mistake, not a choice.
- Page margins are uneven; one page has a wide gutter, another has none.
- Density mismatches the context — a marketing page is dense, a dashboard is sparse.

---

## Typography

### What good typography feels like

- **A small set of sizes, used consistently.** The product has 4–6 distinct text sizes that map to clear roles: page heading, section heading, body, label, metadata. Each role has one size. The reader knows what kind of text is what at a glance.
- **A tight set of weights.** Two or three weights. Bold for headlines, regular for body, perhaps medium for emphasis. Weight isn't sprinkled across the design.
- **Headlines have presence.** They feel like something to land on, not something to scroll past. The line break is intentional.
- **Body text is readable.** Lines are at a comfortable length (not edge-to-edge across a wide screen). Line-height is generous enough that reading feels relaxed.
- **One voice across the product.** The product speaks in one type voice, not three.

### Felt observations to make

- Type sizes feel like steps in a scale, not arbitrary choices.
- Headings stand out clearly. The hierarchy is unmistakable.
- Body text feels comfortable to read at a glance.
- The number of weights in active use feels small.
- Numbers in tables align (don't twitch as values change).
- Truncated text is signaled cleanly with an ellipsis, with full content available on hover or expand.
- Text doesn't run edge-to-edge across the entire viewport on wide screens.

### What weak typography looks like

- The product has many sizes that don't relate to each other — 13px, 14px, 15px, 16px all visible.
- Three or four weights mixed without clear logic.
- Headings and body text feel similar in weight or size — flat hierarchy.
- Body text runs the entire width of a wide screen, exhausting to read.
- Numbers in tables shift position as values change — feels unfinished.
- Capitalization is inconsistent: "Save Changes" here, "save changes" there, "SAVE" elsewhere.

---

## Color

### What good color feels like

- **A small, intentional palette.** The product uses few colors and uses them consistently. Each color earns its place — brand, action, error, success, neutral. Nothing decorative.
- **Surfaces feel intentional.** Three or four surface tones — page background, card, hover, selected — each visibly distinct. The eye doesn't have to ask "is this a different gray?"
- **Color signals meaning.** Green is positive, red is negative, the brand color is reserved for primary moments. The mapping is consistent everywhere.
- **Restraint with accent color.** The brand color appears where it matters — primary actions, key indicators — not as decoration.
- **Considered dark mode (if present).** Dark mode is its own design, not a color-inverted afterthought.

### Felt observations to make

- The palette feels tight and disciplined.
- Surface tones feel distinct from each other — no near-duplicates.
- The brand or accent color is used sparingly and purposefully.
- Status colors (positive, negative, warning) are consistent across the product.
- Dark mode (if present) feels like its own designed surface.
- Information isn't carried by color alone — pair with icon, label, or position.

### What weak color looks like

- Many near-identical grays accumulating across surfaces — the eye registers wear.
- The accent color is everywhere, including decorative uses, so primary actions don't stand out.
- Status colors flip meaning between views (green meant "complete" here, "ready to start" there).
- Dark mode looks like a contrast inversion of light mode, not a designed surface.
- The palette feels accumulated — colors added by different contributors over time.

---

## Surfaces

### What good surfaces feel like

- **Cards, panels, modals all feel like one family.** Same border treatment, same radii, same elevation language. A card on one screen is recognizable as a card on another.
- **Elevation has intent.** When something is lifted (modal, popover, sticky element), the elevation is clear and consistent. Shadows are tasteful, not heavy.
- **Borders are restrained.** Not every container has a border. When a border appears, it earns its place — separating things that need separating.
- **Radii are limited.** The product picks one or two corner radii and sticks to them. Cards aren't 4px-rounded in one place and 12px-rounded in another.

### Felt observations to make

- Cards across the product feel like the same family.
- Modals and popovers feel like the same family.
- Borders appear where separation is needed, not as decoration.
- Shadows are subtle and consistent — same elevation gets the same shadow.
- Corner radii are consistent within a context.

### What weak surfaces look like

- Cards on different screens have different radii, different shadows, different border treatments — the family is fragmented.
- Borders everywhere — every container framed for no reason.
- Shadows are too heavy or inconsistent — some elements feel like they're floating in front of glass, others feel painted on.
- A modal looks like a card looks like a popover looks like a panel — no elevation hierarchy.

---

## Visual Assets

### What good visual assets feel like

- **Icons are one family.** Same stroke weight, same style (outlined vs filled), same proportions. They look like a set, not a collection.
- **Icons are sized consistently in the same context.** A toolbar icon is the same size as another toolbar icon.
- **Imagery has intent.** Photos and illustrations feel chosen, not searched-and-pasted. They support the content, not decorate it.
- **Avatars are consistent.** Same size, same shape, same fallback treatment.
- **Empty states have personality.** When the product needs to fill space because there's nothing to show, the design uses the moment — a small illustration, a clear invitation, a personality.

### Felt observations to make

- Icons feel like a set — consistent stroke weight and style.
- Icons in similar contexts are similar sizes.
- Avatars are the same shape (round vs square) across the product.
- Imagery feels chosen, not generic.
- Empty states are designed moments, not blank screens with "No items."

### What weak visual assets look like

- Icons mix outlined and filled styles randomly. Stroke weights vary.
- Toolbar icons are different sizes from each other.
- Stock photography that doesn't match the brand voice.
- Avatars are round in one place, square in another.
- Empty states are blank, with a generic "No data" string.

---

## Cross-cutting felt qualities

When evaluating the visual system as a whole, ask:

- **Does the system feel like it has a point of view?** Or does it feel like an accumulation of contributions?
- **Could a new contributor extend this system without guessing?** The patterns should be self-documenting.
- **Does the visual vocabulary feel small?** Disciplined products use few sizes, weights, colors, and shapes — and use them everywhere.
- **Is anything shouting that doesn't need to?** Bold weights, accent colors, large sizes, and heavy borders should be reserved.
- **Where does the eye land first? Second? Third?** If you can't answer, hierarchy is broken.

---

## Scoring Guide

**Contributes to dimensions: Well-Crafted, Coherent**

| Score | Criteria |
|-------|----------|
| 9–10 | The visual system feels disciplined and intentional. Small vocabulary used consistently. Hierarchy is calm; restraint is visible. Surfaces, type, color, and assets all read as one family. The eye lands where it should. |
| 7–8 | Strong visual system with minor inconsistencies. The discipline is mostly visible; small drift in secondary screens. |
| 5–6 | Functional but uneven. Some inconsistencies are felt — type sizes drift, surface colors don't quite match, icons are mixed weights. The system reads as accumulated. |
| 3–4 | Visibly fragmented. Multiple type sizes without logic, color used decoratively, surfaces don't relate, icons from different families. The product feels assembled by different hands. |
| 1–2 | No visual system. Browser defaults visible; nothing relates to anything else; chaos. |
