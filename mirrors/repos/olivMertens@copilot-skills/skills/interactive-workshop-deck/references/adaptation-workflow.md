# Adaptation workflow

## 1. Intake (one grouped question, only for what is missing)

- **Decision**: what should the room decide or produce by the end (a priority, a filled canvas,
  a pilot scope)? Every slide must serve that outcome.
- **Audience and size**: role, expertise, number of participants, in person or remote.
- **Language and locale**: visible copy, `<html lang>`, `CONFIG.locale` for numbers and dates.
- **Duration** and fixed constraints (breaks, mandatory sections).
- **Interactions** worth the time: poll, multi-select, stars, canvas, simulation, signals, zones, vote.
- **Identity**: neutral (default) or an approved brand kit (logo file, colours, licensed fonts).
  Never infer a brand from a client name or guess colours from a logo.
- **Source material**: facts, figures and claims the user can stand behind. Without it, write
  generic, clearly illustrative content.

Then ask the [customisation questionnaire](customization-questionnaire.md) (colours, animation,
sound, links) in one grouped message.

## 2. Map the topic onto the arc

| Phase | Pattern(s) | Question the slide answers |
|---|---|---|
| Hook (≈10 %) | P01, P02 | Why should this room care now? |
| Context | P03 | What does the audience already believe or own? |
| Definition | P04, P05, P06, P07 | What exactly are we talking about, and what does it reveal? |
| Co-design (≈25 %) | P08 | What does it look like for *us*? |
| Scenario | P09, P10 | What happens when it goes right or wrong? |
| Threshold | P11 | When do we intervene? |
| Governance | P12 | Who decides, what is automated? |
| Priority | P13 | Where do we start? |
| Close | P14, P15, P18 | What do we take away, what is the next step, where do we read more? |
| Annexes | P16, P17 | Before/after and how it fits the existing landscape. |

Rules of thumb: one idea per slide, one question to the room per interactive slide, at least
one-third of the time spent on audience input, annexes reachable but outside the timed agenda.

Set `CONFIG.segments` to the timed phases (`a`/`b` in minutes) and give every section the matching
`data-seg` index. The timer turns amber when the current segment overruns and red past `minutes`.

## 3. Authoring the content

- Replace each `CONTENT` block entirely; keep array shapes (e.g. pattern cards are
  `[category, colour, title, description]`).
- Kickers state the time slot and the intent ("15–25 min · Co-design").
- Headlines are claims or questions, with one or two words wrapped in `.grad`.
- Notes contain: what to say (one or two sentences), the question to ask, the expected outcome,
  and any caution (what not to promise).
- Population map: adjust group positions (`cx`, `cy`) so circles do not overlap; counts above
  ~50 per group need smaller `rmin`/`rmax`.
- Architecture: nodes are `[x, y, w, h, title, subtitle, colour, flows]` on a 1150×640 canvas;
  edges use ports `t`, `b`, `l`, `r`. Use generic capability names unless the user approves
  specific products.

## 4. Authoring the simulation

1. Write the story first: baseline period, one or two milestones (release, new segment),
   three to five signals that drift, the composite detection, the isolated critical threshold,
   and what each decision changes.
2. Model each metric as `baseline + amplitude * sig((d - day) / width)` plus small noise.
   Stagger the sigmoid centres by one to three days so rules fire one after another.
3. Check the ordering: `compDay` (≥ `composite.min` rules active) must come **before** `isoDay`
   (`critical()` true). The gap is the "days ahead to decide" headline; read it from
   `window.__simInfo` in the browser.
4. Decisions: `target` values pull metrics back exponentially after `compDay`; `'*0.75'` scales
   the base curve; `rollback` changes the version tag; `incident` adds a marker and an event for
   the "do nothing" path. Each decision needs a distinct `learn` sentence.
5. Keep events deterministic (seeded by day and decision), units honest (%, counts), and the
   disclaimer visible. The code panel shows illustrative pseudo-logic unless the user provides
   a real, approved query language.

## 5. Validate in a browser

Use any available headless browser (for example Playwright with a locally installed Chrome).
Install tooling only in a scratch folder and only within the user's policy.

1. Load the file at a 1600×900 viewport; capture `pageerror` and console errors.
2. For each id in `window.__deck.slides`: `window.__deck.go(i)`, wait for animations
   (≈7 s on the hook and race slides), screenshot, and review for overflow, clipped text,
   overlapping labels and empty panels.
3. Simulation: press **P**, raise the speed, wait for the alert, screenshot, click each decision
   (reset between runs) and screenshot the end state.
4. Click through the interactive slides, then check `window.__deck.synth()` contains every section.
5. Emulate `prefers-reduced-motion: reduce` and confirm every slide shows its final state.
   Also load the chosen theme/motion/transition, and with sound enabled confirm tones play
   after the first key press (e.g. count created oscillators) and that **M** toggles them.
   Check every link card points to the approved URL and opens as configured.
6. Search the file for leftover sample strings and unapproved brand or product names.

Report what was checked, any slide not reviewed, and any browser not tested.
