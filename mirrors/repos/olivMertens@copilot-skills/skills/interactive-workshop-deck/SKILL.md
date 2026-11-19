---
name: interactive-workshop-deck
description: >-
  Build a live, facilitated workshop deck as one self-contained HTML file:
  dark "control room" design, fixed 1600x900 stage, agenda bar with timer,
  staged reveals, facilitator notes, audience polls and votes, a co-design
  canvas, a deterministic live simulation (timeline, chart, KPI tiles, event
  feed, rules, alert with a decision), a decision loop, annexes and an exported
  Markdown synthesis. Re-uses the same design and animations for any topic,
  with guided customisation of colours, animation, sound and links.
  Use for "interactive workshop deck", "atelier interactif", "co-design
  session slides", "facilitated workshop with polls and a simulation",
  "reuse this workshop design for another subject", "présentation atelier
  avec démo animée", "change the colours / animations / sounds of the
  workshop deck". Not for video, PowerPoint or static brand decks.
---

# Interactive Workshop Deck

Turn any topic into an interactive, facilitated workshop that runs offline in
a browser. The package ships a tested, brand-neutral starter: you change the
content, not the engine.

Resolve every path from **the directory containing this SKILL.md**.

## Package

- [assets/starter.html](assets/starter.html): engine + 18 slide patterns, all
  content in `CONFIG`, `CONTENT` and `SIM` objects or in `SLOT` comments;
  theme presets, motion levels, synthesized sounds and a links slide.
- [references/slide-patterns.md](references/slide-patterns.md): what each
  pattern is for, its content keys, and the design tokens.
- [references/adaptation-workflow.md](references/adaptation-workflow.md):
  intake, narrative mapping, simulation authoring and validation.
- [references/customization-questionnaire.md](references/customization-questionnaire.md):
  the questions to ask about colours, animation, sound and links, with defaults
  and the `CONFIG` keys each answer sets.

## Procedure

1. **Intake.** Ask one grouped question for anything you cannot infer:
   topic and the one decision the workshop should produce, audience, language,
   duration, number of participants, which interactions matter (poll, canvas,
   simulation, vote), and the identity policy (neutral by default, or an
   approved brand kit). Do not ask about details that have a sensible default.
   Then run the [customisation questionnaire](references/customization-questionnaire.md)
   in one grouped message: **colours** (preset or approved hex values), **animation**
   (level, slide transition, pace, simulation speed), **sound** (on/off, moments,
   volume, synthesized or supplied files) and **links** (which URLs, why each one
   matters, where they appear, who can open them). Defaults are acceptable answers.
2. **Map the story** onto the arc in the adaptation workflow: hook → context →
   definition → co-design → scenario + simulation → intervention threshold →
   decision loop → priority → summary → next step → annexes. Drop or reorder
   patterns freely; propose the slide list and timings before building when the
   brief is large or ambiguous.
3. **Copy** `assets/starter.html` next to the user's other material under a
   topic-specific name. Never edit the packaged starter in place.
4. **Replace all sample content.** Set `CONFIG.storageKey`, `title`, `minutes`,
   `locale` and `segments`; apply the questionnaire answers to `theme`, `motion`,
   `sound`, `links` and `CONTENT.links`; rewrite `CONTENT`, `SIM` and every `SLOT`, kicker,
   title, note and disclaimer. Delete slides you do not need: each module skips
   itself when its `<section>` is missing. Keep `data-seg` aligned with
   `CONFIG.segments`.
5. **Author the simulation** only if a dynamic "watch it happen" moment helps
   the decision. Follow the simulation rules in the workflow reference: a
   deterministic story, a composite detection that precedes the first isolated
   critical threshold, and two to three decisions with different outcomes.
6. **Validate in a real browser** (see the workflow checklist): zero console
   errors, every slide screenshot reviewed at 1600x900, the simulation played
   to the alert and to the end for each decision, the synthesis exported.
7. **Deliver** the single HTML file and state what was validated and what was not.

## Rules

- **Neutral by default.** No logos, product names, vendor fonts, customer names
  or client-specific facts unless the user supplies or approves them. The
  starter's monogram and system font stack are deliberate placeholders.
- **Reuse design, never content.** Do not carry over sample text, metrics or
  scenarios into a new topic; every visible string must belong to the new topic.
- **Fictitious stays fictitious.** Simulations and population maps show
  illustrative data. Keep a visible disclaimer, never present thresholds or
  results as measured, and never imply a real incident.
- **Facilitation first.** Each slide carries `<aside class="notes">` with what
  to say, the question to ask and the expected outcome. Interactions must feed
  the synthesis (`SYNTH.push`) when the answer matters after the session.
- **Self-contained and offline.** One HTML file, no CDN, no network calls, no
  external fonts unless the user approves embedding them. State persists only in
  `localStorage` under `CONFIG.storageKey`.
- **Accessible motion.** Keep `prefers-reduced-motion` handling, real `<button>`
  elements for interactions, readable contrast, and content that still makes
  sense on a static frame.
- **Language.** Write every visible string in the requested language with full
  typography (French accents, « guillemets », non-breaking spaces before
  : ; ? !). Set `<html lang>` and `CONFIG.locale` accordingly.
- **Sound and links are opt-in.** Sound is off by default and toggled with M;
  use only synthesized tones or audio the user supplies. Render only links the
  user supplied or approved, each with a one-line context; never invent URLs.
- Do not publish, upload or send the deck without explicit approval.

## Exit checklist

- [ ] Every sample string, number and scenario replaced; no leftover "unit-07",
      "Team A", "Population Intelligence" unless intentionally kept.
- [ ] No unapproved brand, logo, product or customer name (search the file).
- [ ] Customisation answers applied and restated: theme (contrast checked), motion
      level and transition, sound settings, links with context (reachability checked
      or reported as unverified).
- [ ] `CONFIG.storageKey` is unique; segments, `data-seg` and timer minutes agree.
- [ ] Each remaining slide has notes and an expected outcome.
- [ ] Browser check run: no console errors; all slides screenshotted and reviewed
      for overflow and overlaps at 1600x900.
- [ ] Simulation (if kept): alert fires at the composite day, every decision
      replays to the end with its own outcome and learn message.
- [ ] Synthesis opens, copies and downloads with all expected sections.
- [ ] Reduced-motion mode leaves every slide readable.
- [ ] Validation gaps reported honestly.
