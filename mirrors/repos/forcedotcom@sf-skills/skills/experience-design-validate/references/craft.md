# Craft

> **Always load. Craft is the heart of this skill — it applies to every visual design.**

This is the lens. Every finding in a craft audit is, ultimately, an observation about whether the design feels considered or careless. This file holds the felt qualities — what high craft looks like, what low craft looks like, and the decisions that separate them.

## Why this matters

Craft is what users notice without naming. They don't say "the kerning is tight" or "the hierarchy is calibrated" — they say "this feels nice," or, more often, they don't say anything because it just works. Bad craft, by contrast, is felt as friction: a screen that's too busy, an empty state that looks unfinished, three things shouting for attention at once, an animation a beat too long. Craft compounds. Each small decision ladders into the felt quality of the whole.

A design with high craft has visible authorship. Someone made consistent decisions and defended them. A design with low craft has visible compromise — many people contributed under pressure, no one took responsibility for the whole, and the rough edges are where the conversations didn't happen.

The goal of this reference is not to enforce style. It's to teach the reader to see what considered work looks like.

---

## The lens — what high-craft work feels like

When evaluating, hold the design against these felt qualities. Each is a question the audit answers.

### Breathable

The design has room to breathe. White space is a structural element, not waste. The eye can rest. Nothing is shouting; nothing is crammed. There's air around primary actions; there's room between sections; the screen feels like it could be quieter without being emptier.

**What weak craft looks like:** every element fights for space; sections butt up against each other; the screen feels like a checklist of things that had to be included.

### Approachable

A new user can guess what to do without a manual or a tour. The right path is the obvious path. The design isn't trying to teach itself — it's trying to be itself.

**What weak craft looks like:** tooltips and "?"-icons and "click here to learn more" everywhere. Onboarding flows that have to explain what the buttons do. Settings panels that look like a control room.

### Inviting to experiment

The design rewards curiosity. Hovering reveals delight; clicking reveals possibility; empty states feel like an invitation, not a dead end. Users who try things feel encouraged to try more.

**What weak craft looks like:** the design is brittle — exploration feels punishing. Errors are loud. Empty states say "no items" without telling the user how to create the first one. The product feels like it doesn't expect to be tinkered with.

### Considered, not assembled

The design feels like one person made consistent decisions, then defended them. The visual language is unified — type, color, motion, spacing all on the same scales. Drift between screens is rare and feels intentional when it happens.

**What weak craft looks like:** the seams show. Different screens look like different products. Patterns are reinvented; controls behave inconsistently; one section is breathable and the next is dense for no clear reason. The product feels like it was built by a committee.

### Quiet, not shouty

No screen has eight things competing to be primary. The hierarchy is calm — the eye knows where to land first, second, third. Color is used with purpose. Bold weight, large sizes, and accent colors are reserved, not sprinkled.

**What weak craft looks like:** every panel has a border, every label has a background, every button is filled. The visual volume knob is at 9 everywhere. Important things and unimportant things look the same.

### Delightful

There are small moments of considered detail. A transition that lands at the right speed. A micro-interaction that confirms an action without celebrating it. An empty state that has personality. A loading state that's been thought through. None of it is loud — but you notice it isn't there if it isn't.

**What weak craft looks like:** every state is generic. Empty is "no data." Loading is a spinner. Error is a red banner. Nothing feels chosen.

### Confident

The design has a point of view. It doesn't hedge. It picks one way to do things and commits. Settings are sensible defaults, not a quorum of options. The product feels willing to make decisions on the user's behalf — and the decisions feel right.

**What weak craft looks like:** every workflow has three modes. Every screen has a "switch view" toggle. Every preference is a setting. The product is asking the user to design it.

---

## The decisions that separate high craft from low craft

Two designers solving the same brief. What does the higher-craft one do differently?

- **Restraint over inclusion.** They cut features and elements until what remains feels essential. Lower-craft work tends to add — every meeting produces another button, badge, banner, or option.

- **Hierarchy over enumeration.** They design what's important to be loudest, what's secondary to be quieter, and what's tertiary to almost disappear. Lower-craft work treats every element as equally important.

- **One taste over many tastes.** They pick a small visual vocabulary — a few sizes, a few weights, a few tones, a few shapes — and use them consistently everywhere. Lower-craft work accumulates variations.

- **Considered emptiness over filled space.** They use white space as structure, especially around primary actions. Lower-craft work fills available space because it feels productive.

- **Designed states over default states.** They author every state — empty, loading, error, partial, edge — as a deliberate moment. Lower-craft work leaves states to chance: spinners, blank panels, generic messages.

- **Confident defaults over configurable surfaces.** They make decisions for the user. Lower-craft work delegates decisions back to the user via settings, toggles, and modes.

- **Quiet polish over loud features.** They invest in micro-interactions, transitions, hover states, and the felt smoothness of the experience. Lower-craft work invests in the demoable surface and skips the in-between.

These are the moves a comparative audit names.

---

## How to use this reference

When auditing, hold the design against the lens. For each felt quality (breathable, approachable, inviting, considered, quiet, delightful, confident), ask:

- Does the design earn this adjective?
- Where, specifically, does it earn it? (Cite a region or screen.)
- Where, specifically, does it fall short?

Findings flow from the lens, not from the rules. A rule that doesn't translate into something a user could feel doesn't belong in a craft audit.

---

## How findings teach

Every finding must do four things, not one. The skill earns its keep by teaching, not by checklisting.

1. **Problem** — what feels off, in plain language. The kind of thing a designer would say in a critique.

   Example: *"The toolbar feels overworked. There are seven controls in the top row competing for attention; the eye can't tell what's primary."*

2. **Why it weakens craft** — the principle being violated.

   Example: *"Hierarchy is calm when the design tells the eye where to land first. When everything in a row is the same visual weight, the user has to do the work the design should have done. The design feels assembled rather than authored."*

3. **What better looks like** — the improved version.

   Example: *"One primary action visible at full weight. Secondary actions visually quieter — text-only buttons, no fill. Rare actions tucked into an overflow menu. The toolbar reads in three glances: primary, secondary, the rest."*

4. **Fix** — the specific design move.

   Example: *"Promote 'Save' to the only filled button in the toolbar. Demote 'Commit' and the rename action to text buttons. Move 'Builder Settings' and 'Salesforce Org Settings' into the existing overflow menu — they're rarely used in any single session."*

A finding that lists the problem without teaching the principle is rejected. A finding that prescribes the fix without explaining the principle teaches nothing. The point is to leave the reader's eye sharper than you found it.

---

## Anti-patterns in craft audits

The craft audit is **not** a code review. The following kinds of findings do not belong:

- "Three font-family CSS variables for the same intent."
- "Six near-duplicate light grays in `app.css`."
- "`outline: none` without `:focus-visible` replacement on line 137."
- "Two button base classes — `button toolbar-btn` vs `toolbar-icon-button`."
- "Inline `setTimeout(300)` for click-vs-double-click detection."

If the finding is about a token, a class, a selector, a timeout, an ARIA attribute, or anything else inside the implementation — rewrite it as a felt observation or delete it. The user doesn't see CSS. They see a design.

The same observations, at the felt level:

- "Font usage lacks consistency. The product reads in different voices depending on the screen."
- "Surface colors feel scattered. The eye can't tell which grays are intentional and which are accidents."
- "Toolbar buttons feel inconsistent — some are framed, some aren't, the row reads as assembled."
- With `DYNAMIC_VISUAL` evidence only: "The agent name's directly exercised rename gesture has no visible cue before activation, so the interaction feels hidden."

The first list is what a CSS lint would say. The second is what an interior decorator would say.

Do not convert source-code clues into felt claims. Focus visibility, keyboard operation, and hidden gestures require direct evidence; route accessibility compliance to `experience-accessibility-validate`.

---

## Scoring Guide

**Contributes to dimensions: Well-Crafted, Coherent**

| Score | Criteria |
|-------|----------|
| 9–10 | The design feels authored. Restraint is visible — small visual vocabulary, generous space, calm hierarchy. Every state is designed. Motion is purposeful. The eye lands where it should; the user knows what to do without instruction. The product feels confident and quiet. Delight is present in small, considered ways. |
| 7–8 | High-craft work with minor opportunities. The lens mostly holds. A few screens drift; one or two states feel templated; the visual vocabulary is mostly disciplined but shows some accumulation. The design feels considered overall. |
| 5–6 | Functional but uneven. The design earns some craft adjectives — usually breathable or approachable — but not others. Hierarchy works on the main screens; secondary screens feel rushed. Empty states are generic. The seams show on close inspection. |
| 3–4 | Visibly rough. The design feels assembled. Multiple felt qualities fail — the screen is too busy, the hierarchy is flat, the empty states are blank, the visual vocabulary is fragmented. The user can use the product but doesn't enjoy it. |
| 1–2 | No craft. The design feels abandoned. Browser defaults; missing states; visual chaos; no point of view. Using it feels like work. |
