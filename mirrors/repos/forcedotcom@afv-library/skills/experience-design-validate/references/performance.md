# Performance

> **Load this reference only with `DYNAMIC_VISUAL` evidence that directly shows timing, latency, loading, scrolling, animation, or layout stability. Static screenshots and source code cannot substantiate felt performance; mark performance coverage `INSUFFICIENT_EVIDENCE` rather than inferring it.**

Craft in performance is the felt quality of an interface that responds the moment you ask it to. It lives in the precision of an instant feedback flash, the calm of a skeleton screen that lands exactly where the content will be, the discipline of motion that doesn't shove the layout around, and the absence of jolts as content settles into place. This reference judges whether the interface feels effortless — load behavior, interaction latency, layout stability, and the formatting craft of numbers, dates, and units that hold the surface together.

## Why this matters

Performance is the most invisible form of craft — users rarely praise a fast app, but they always feel a slow one. When craft is high, the interface feels weightless: pages snap in, content lands without shifting, every press is acknowledged before the user wonders if anything happened, and animations feel quietly confident. When craft is low, the experience feels janky and unsure of itself — buttons that move as you reach for them, skeletons that don't match the content they preview, dropdowns that hang, numbers that change format mid-table. Polish at this layer is what makes the rest of the design feel real instead of staged.

---

## Loading

- **The page never opens to white.** Meaningful structure or a designed loading state arrives quickly. The interface becomes usable before it's complete — primary actions work first, secondary content fills in.
- **Skeletons mirror what's coming.** Same layout, same dimensions, same item count. When the real content lands, nothing shifts. Repeat visits feel instant.

## Interaction

- **Every press is acknowledged immediately.** No silent moments, no wondering if the click registered. Typing feels alive. Dropdowns and route changes open with confidence — no third-of-a-second hang.
- **The wait sets the indicator.** A flash for the very fast, an inline spinner for a brief pause, a skeleton or progress for longer. A spinner that flashes for a fraction of a second is worse than silence. Long work goes background and returns the UI.

## Layout Stability

- **Content lands where it landed.** Buttons don't move as the user reaches. The page doesn't jump as a late image arrives. Layout shift is the visible signature of an unfinished page. Skeletons reserve their final size; toasts overlay rather than push.
- **Lists settle, not lurch.** Append doesn't shift earlier content. Back navigation restores scroll position.

## Scale

- **Large lists feel as smooth as small ones.** Scrolling through thousands of rows doesn't drag or hang. Filtering and sorting respond instantly. Dashboards load independently — one slow widget never holds the rest of the page hostage.
- **Spatial UIs hold their frame rate.** Pan, zoom, and drag feel smooth. Stutter during direct manipulation is the giveaway of a canvas not engineered for the work.

## Perceived Performance

- **The product feels faster than it is.** Optimistic feedback for low-risk actions; content streamed in rather than withheld; the most important elements first. Long operations let the user keep working, with completion finding them wherever they go.
- **Offline is detected immediately.** Cached content stays usable; new work queues for sync. The interface doesn't pretend the network is fine.

## Formatting Craft

- **Recent times read as human time; older times settle into absolute dates.** "Just now," "5 min ago," "Yesterday" feel natural for recent activity. Past a week, real dates arrive. Ambiguous numeric dates ("1/15/24") are avoided. Time zones surface only when they matter.
- **Numbers are formatted for fastest comprehension.** "1.2M" reads faster than "1,247,893" on a dashboard. Full precision belongs in detail views. Number columns right-align so decimals stack. Zero is not null — "—" or "N/A" tells the user nothing was measured. The same metric is formatted the same everywhere.
- **Type, spacing, and stacking follow systems.** When the user enlarges text, the interface scales gracefully. Stacking order is predictable — toasts above modals, tooltips above everything. Adjacent gaps that read as 12, 14, 16, and 18 pixels feel improvised.

---

## Scoring Guide

**Contributes to dimension: Reliable**

| Score | Criteria |
|-------|----------|
| 9-10 | The product feels effortless. Pages snap in. Every interaction is acknowledged. Nothing shifts. Numbers, dates, and units are formatted with discipline. |
| 7-8 | Mostly responsive with minor lulls or layout shifts. Formatting is mostly consistent. |
| 5-6 | Some sluggish moments. Layout shifts as content arrives. Mixed number formats. |
| 3-4 | Slow primary flows. Visible jank. Buttons move as the user reaches. Large lists choke. |
| 1-2 | Long waits with no feedback. Clicks unresponsive. The interface feels janky and unsure of itself. |
