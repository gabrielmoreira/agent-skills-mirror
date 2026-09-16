# Forms & Flows

> **Skip this reference if the design has no destructive actions, no save model, no multi-step flows, no checkout, no timelines, and no first-run experience — i.e. no journey to craft.**

Forms and flows are where craft compounds. A delete confirmation that names what's about to die, a save indicator that fades at exactly the right moment, an undo toast with a visible countdown — these are the small considered moments that separate a polished product from a functional one. Good craft here feels like the product respects your work; poor craft feels like the product is indifferent to it.

## Why this matters

Flows are where users feel either confident or cornered. A confirmation dialog that uses generic "Are you sure?" copy and a gray "OK" button feels like a form letter; one that names the specific item, explains the consequence, and uses error-styled "Delete project" feels designed by someone who cared. A multi-step flow with a confident step indicator and a graceful "save and exit" feels like a partner; one that resets your inputs on validation feels like an adversary. The craft is in the calibration — friction proportional to consequence, save status unambiguous, every step earning its place. Done well, the product feels trustworthy and humane. Done badly, every save and submit becomes an act of faith.

---

## Destructive Actions

- **Friction is calibrated to consequence.** Archiving gets an undo toast. Deleting gets a simple confirmation. Destroying a project gets specifics and consequences. Wiping an account requires typing the name. Friction matched to stakes reads as respectful.
- **Confirmations name the thing.** "Delete 'Q4 Marketing Plan'?" reads as designed; "Are you sure?" reads as a template. The destructive button names the action — "Delete project," not "OK."
- **Reversible actions earn an undo, not a confirmation.** Destructive actions never sit next to the most-used neighbor. Soft-delete with a recovery window reads as a designed safety net.

## Save

- **The save model is unambiguous.** The user always knows whether their work is saved, saving, or unsaved. A drifting "Saved" indicator that lies during failure is a critical breach of trust.
- **Failure preserves work.** A save that fails never leaves the user thinking it succeeded. Content stays, retry is offered, navigation away from unsaved work prompts a guard.
- **Draft and published states are visually distinct.** "Draft," "Published," "Modified since last publish" each read at a glance.

## Multi-Step Flows

- **Steps feel earned.** Each one addresses a different topic or depends on an earlier choice. Two steps that could've been one read as bloat.
- **The step indicator tells the truth.** Position, progress, and completion visible. Branching paths show the actual route. Hidden steps stay hidden.
- **Back never punishes; the flow can be paused.** Returning to a previous step preserves what was entered. Long flows offer "save and exit" and resume the user where they were.
- **Submission is reviewable and resilient.** Irreversible work gets a summary with edit links. The final button names the action ("Place Order," not "Done"). Submission failure preserves everything — one error to fix, not a full re-entry.

## Checkout

- **The summary stays visible throughout.** Items, pricing, and total in view at every step. Security signals live where the anxiety lives — next to the card input. Confirmation closes the loop with specifics and a copyable reference.

## Timelines

- **Time scale is the user's primary handle.** Day, week, month, quarter, year — toggled cleanly. Today is unmistakable. Detail opens beside the timeline, not away from it. Direct manipulation feels confident — drag to move, drag the endpoint to resize.

## Onboarding

- **Time-to-first-value is the goal.** Every screen between signup and first success has to earn its place. A long onboarding before the user gets to do anything reads as bureaucratic.
- **Empty states do onboarding's job.** The first time the user lands on an empty section, the screen explains what will live here and offers a way to make the first one. Tours don't lock the UI; tooltips arrive one at a time and never block the thing they're describing.

---

## Scoring Guide

**Contributes to dimensions: Useful, Usable, Reliable**

| Score | Criteria |
|-------|----------|
| 9-10 | Friction is calibrated. Save status is unambiguous. Multi-step flows preserve work and recover from failure. Onboarding earns its time. |
| 7-8 | Flows handle destruction, saving, and multi-step competently with minor gaps. |
| 5-6 | Some flows lose data on error. Generic confirmation copy. Onboarding overstays. |
| 3-4 | Flows lose work. Destructive actions sit next to safe ones. No undo. |
| 1-2 | Catastrophic flow failures. Users routinely lose what they typed. |
