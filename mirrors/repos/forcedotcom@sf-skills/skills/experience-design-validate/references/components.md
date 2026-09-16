# Components

> **Skip this reference if the input contains no buttons, forms, modals, lists/tables, or feedback components. Within the file, sections are independent: skip "Buttons" if no buttons exist, "Forms" if no forms, "Overlays" if no modals/drawers/popovers/tooltips, "Lists & Tables" if no list or table UI, "Feedback" if no toasts/alerts/progress/empty states.**

## Why this matters

Components are where craft compounds — every button, input, and overlay is a small artifact a designer either sweated over or shrugged at, and the difference is felt across an entire product. When components are well-crafted, the interface feels purposeful: a single primary action draws the eye, inputs line up to the pixel, hover and pressed states confirm every touch, and overlays settle into place with calm, considered motion. When they are sloppy, the surface feels noisy and unresolved — competing buttons, mismatched heights, half-built states, modals that pop instead of arrive. A polished component system is one of the clearest signals that designers cared about the small details users feel but never name.

---

## Buttons

- **The eye lands on one action.** Each screen has a single primary button that is unmistakably the thing to do. When two buttons compete for primacy, neither wins and the screen feels indecisive.
- **Hierarchy reads at a glance.** Primary, secondary, and tertiary feel like three distinct registers — not three flavors of the same button.
- **Destructive actions don't masquerade as the answer.** "Delete" is never the bright filled button next to "Cancel." It's quieter, set apart, and only takes on full danger styling inside the dialog that confirms it.
- **Buttons feel resolved, not assembled.** Heights match across a row. Adjacent buttons and inputs align to the pixel. Icons inside feel optically centered. Every press answers back — hover hints, the click depresses, focus lands cleanly.

## Form Controls

- **Inputs line up.** Same heights, same border treatment, same internal padding. Mismatch reads as carelessness even before the user can articulate why.
- **One label position rules the form.** Above, floating, or to the side — pick one and commit. Mixing reads as multiple drafts merged together. Placeholder text never does the label's job.
- **Errors arrive when the user is done, not while they're typing.** Per-keystroke validation feels accusatory. Errors clear the moment correction begins, and never shove the layout around.
- **Selects, toggles, and checkboxes feel like one family.** A dropdown trigger looks like a sibling of the text input next to it. The system feels designed, not collected.

## Overlays

- **The right surface for the moment.** Modals interrupt for genuine blocking decisions; drawers hold detail; popovers handle quick contextual pickers; tooltips stay strictly supplementary. When a modal could've been a page, the screen feels claustrophobic.
- **Modals arrive, they don't pop.** Entry has the calm of a considered transition. Width feels chosen, not arbitrary. The frame holds while the body scrolls — header and footer stay put, the primary action visible without hunting.
- **Drawers don't push the world around.** Opening one shouldn't shift the parent layout.
- **Tooltips whisper.** A short line, two at most. They wait briefly to appear, fade rather than fly, and never restate the visible label.
- **Stacking is rare and shallow.** Modal-on-modal reads as missing IA. Drawers don't pile. Escape always dismisses; backdrop click closes anything not holding unsaved work.

## Lists & Tables

- **One template, repeated cleanly.** Every row shares the same anatomy. Density is chosen and committed — same row heights, padding that doesn't drift between cells. The table reads as a single instrument.
- **Alignment respects the data.** Numbers right, text left, actions last. Mixed alignment within a column makes the eye lose its rail.
- **One separation strategy at a time.** Zebra stripes or borders or whitespace — never a combination. Combining turns a quiet table into a cage. Headers stay subordinate to the data they label.
- **The whole row responds to the cursor.** Hover and click extend across the full width. Cards in a grid are one click target, not a patchwork. Selection looks selected — distinct from hover.
- **Cards in a grid keep their rhythm.** Same width across the row. Truncation rather than reflow.
- **Empty doesn't mean blank.** Empty lists keep their headers, name what would live here, and offer a way to make the first one. Skeletons mirror the shape of what's coming — so the page doesn't lurch when data arrives.

## Feedback

- **Toasts confirm; alerts persist.** Toasts handle "we did the thing." Alerts handle "you need to handle the thing." A critical error delivered as a five-second toast reads as careless. One toast position for the whole product.
- **Severity has a visual register.** Info, success, warning, error each carry their own color and icon — never color alone, never red used twice for unrelated meanings. Severity escalates calmly as stakes rise.
- **Progress feels honest.** A determinate bar moves like it means it. Fake or jumpy progress trains users to distrust every indicator. Skeletons match the final layout — generic gray rectangles read as unfinished.
- **Empty states are designed, not abandoned.** A short headline, a sentence of context, and a way forward. A blank canvas is a defect.

---

## Scoring Guide

**Contributes to dimensions: Usable, Reliable, Well-Crafted**

| Score | Criteria |
|-------|----------|
| 9-10 | The component system feels considered. One primary draws the eye. Inputs and buttons share a single rhythm. Overlays arrive calmly. Lists and cards keep their structure across every state. Feedback is calibrated and complete. |
| 7-8 | Strong component patterns with minor gaps. |
| 5-6 | Competing primaries, mismatched heights, generic empty states. Validation feels accusatory. Feedback is partial. |
| 3-4 | Components feel assembled rather than designed. Destructive actions blend in. Overlays pop. Empty states are blank. |
| 1-2 | No coherent component voice. The interface reads as a collection of defaults. |
