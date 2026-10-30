# Guided diagram walkthrough: step-by-step facilitation

Explain an architecture or flow diagram one step at a time, the way a facilitator walks a room through it.
The pattern is tested with reveal.js 6.0.2 and Mermaid 12.2 (Chromium): normal and reduced motion,
`?print-pdf`, speaker view and deep links.

Files in `assets/`:

| File | Role |
|------|------|
| `diagram-walkthrough.js` | Drives the diagram from reveal.js fragment events. No dependency. |
| `diagram-walkthrough.css` | States, moving flow, step line, evidence card, PDF layout. Themed with CSS variables. |
| `diagram-walkthrough-example.html` | Working deck: a 7-step walkthrough with a failure step, a recap and per-step facilitator notes. |

## What the audience sees

1. **The whole picture first.** The full diagram and one hint line: "press → or Space to follow the flow".
2. **One step per press.** A numbered sentence appears under the diagram. The view zooms smoothly on the
   components that sentence talks about. Everything else dims, but the containers that hold the focused
   components stay visible as context. Dashes move along the active connectors.
3. **Failure states.** A failed component turns red with a label ("unavailable", localisable). Connectors into it
   turn red and stop moving.
4. **Evidence, optional.** A screenshot from a real run appears beside the diagram for the steps that have one;
   selecting it enlarges it.
5. **Recap.** The last step zooms back out to the whole diagram and stays on screen.

In speaker view (S), the presenter sees the facilitator notes of the **current step**, not one block for the slide.

## When to use it

- An architecture, request, data or process flow that you explain in 3 to 9 steps.
- Resilience and security stories: what happens when a component fails or is revoked.
- Workshops, RFI or design reviews, customer briefings and self-guided decks (the viewer presses → themself).

Avoid it when:

- the diagram has fewer than 3 meaningful steps: a static diagram with one highlight fragment is enough;
- the diagram is so dense that zooming loses the reader: split it into two diagrams;
- the "diagram" is only a screenshot or a bitmap: redraw it as SVG, or use `r-stack` with highlight boxes.

## Intake: ask before building

Ask these once, together with the Phase 1 questions, and only what you cannot infer:

1. **Diagram source**: a drawio or SVG with stable ids, a Mermaid flowchart, or an image only (needs a redraw)?
2. **The thread**: which single request, order, claim or user do we follow from start to finish?
3. **Steps**: for each step, what happens (one sentence) and which components are involved?
4. **Failure or alternative path** to show? **Evidence images** from a real run, per step?
5. **Facilitation**:
   - live presenter or self-guided?
   - facilitator notes for each step? In which language?
   - how much time for the slide?
   - questions to ask the room?
6. **Language** of the on-screen text, the hint line and the failure label.

## Slide markup

```html
<section class="dw-slide" id="request-flow" aria-label="Request flow, step by step"
         data-keep="c-platform" data-fail-label="unavailable" data-timing="240">
  <span class="eyebrow">Architecture · step by step</span>
  <h2>Follow one request through the governed path</h2>

  <div class="dw-stage">
    <svg class="dw-svg" data-diagram="demo" viewBox="0 0 1200 660" role="img" aria-labelledby="demo-title">
      <title id="demo-title">Request flow: customer, web app, API gateway, agent…</title>
      <!-- direct children: demo-c-* containers, demo-e-* connectors, demo-* components, demo-legend -->
    </svg>
  </div>

  <div class="dw-steps r-stack" aria-live="polite">
    <p class="dw-intro">The whole picture first · press <kbd>→</kbd> or <kbd>Space</kbd> to follow the flow, one step at a time</p>

    <div class="fragment fade-in-then-out dw-step" data-focus="user app">
      <span class="n">1</span>A customer asks about an order in the web app.
      <aside class="notes">…facilitator notes for step 1…</aside>
    </div>
    <div class="fragment fade-in-then-out dw-step" data-focus="gateway agent" data-fail="model">
      <span class="n">2</span>If the model is unavailable, the gateway switches to a degraded answer.
      <aside class="notes">…</aside>
    </div>
    <div class="fragment fade-in dw-step" data-focus="">
      <span class="n">3</span>One governed path: one door, one identity, one trace.
    </div>
  </div>

  <aside class="notes">Before step 1: orient the room on the whole picture.</aside>
</section>
```

Load `diagram-walkthrough.css` after the reveal.js theme, and `diagram-walkthrough.js` after `Reveal.initialize(...)`.
Keep `hash: true` (and the default `fragmentInURL: true`), so `#/request-flow/3` opens step 4 directly.

Rules that are easy to get wrong:

- **The SVG must be inline** in the slide. An `<img src="diagram.svg">` or `<object>` cannot be driven.
- **Steps are `<div>`, not `<p>`**, when they contain `<aside class="notes">`: HTML closes a `<p>` before an
  `<aside>`, which would detach the notes from their step.
- Every step except the last uses `fade-in-then-out`; the last uses `fade-in` so the recap stays on screen.
- Put the hint line (`.dw-intro`) first inside `.dw-steps`; it fades out at step 1 and is hidden in PDF.

## Step attributes

| Attribute | On | Effect |
|-----------|----|--------|
| `data-focus` | step | Ids to highlight and zoom on. A connector lights up when it is named, or when both of its ends are named. |
| `data-fail` | step | Ids shown as failed, with a label. Connectors into them turn red, without a moving flow. |
| `data-alert` | step | Ids outlined as at risk, without a label. |
| `data-edges="named"` | step | Only connectors listed in `data-focus` light up (use when two focused nodes have several links). |
| `data-zoom="full"` | step | Highlight without zooming in. |
| `data-evidence` / `data-evidence-caption` | step | Image beside the diagram for this step, with a caption. |
| `data-fail-label` | step or slide | Failure label text (localise it, for example "indisponible"). |
| `data-keep` | slide | Ids always kept as context, for example the main platform boundary. |
| `data-evidence-tag` | slide | Tag above evidence images (default "From a real run"). |
| `data-notes` | step | Short plain-text notes, if you don't use `<aside class="notes">`. |
| `data-autoslide` | step | Milliseconds before the next step in a self-guided deck with `autoSlide` enabled. |

A step whose `data-focus`, `data-fail` and `data-alert` are all empty shows the whole diagram: use it for the recap.

## Diagram sources

### A. SVG with the id contract (architecture diagrams)

`<svg class="dw-svg" data-diagram="KEY">`, with these ids on its **direct children**:

| Id | Element | Meaning |
|----|---------|---------|
| `KEY-<node>` | `<g>` with the shape first, then labels and icon | A component. |
| `KEY-c-<name>` | `<g>` with the boundary shape first | A container, zone or subscription. It stays as context when it holds a focused component. |
| `KEY-e-<name>` | `<path>`, with `data-from="<node>" data-to="<node>"` | A connector. Without `data-from`/`data-to`, light it by naming it in `data-focus`. |
| `KEY-legend…` | `<g>` or `<path>` | Legend items, always kept as context. |

`KEY` keeps ids unique when a deck holds several diagrams. Draw connectors before components, so the moving
flow passes under the boxes. If the diagram is authored in drawio (for example with the
`architecture-diagram-author` skill), keep the drawio file as the source of truth. Have its build step emit or
post-process the SVG into this contract, then rerun the audit below.

### B. Mermaid flowchart (process and integration flows)

Pre-render at build time, so the deck stays offline and the PDF stays sharp:

```bash
mmdc -i flow.mmd -o flow.svg -I flow-a -c mermaid.json   # mermaid.json: {"flowchart": {"htmlLabels": false}}
```

- Use a distinct svgId per diagram (`-I`): Mermaid scopes its embedded styles to that id.
- Paste the SVG inline in `.dw-stage`. Add `class="dw-svg"`, remove the inline `style="max-width:…"`, and set
  `width="100%" height="100%"`. Do **not** add `data-diagram`.
- In `data-focus`, use the Mermaid node ids and subgraph ids: focusing a subgraph zooms on the whole group.
  Connectors light up when both ends are focused; their labels follow.
- Ids may contain `_` or `-`. The script resolves edge ends against the known nodes.

## Facilitation script, step by step

reveal.js shows the notes of the **current fragment** in speaker view (checked in reveal.js 6.0.2's notes plugin).
So each step carries its own script, and the slide-level notes cover the moment before step 1.

Template for each step's `<aside class="notes">`:

```html
<aside class="notes">
  <p><b>~40 s · Point at:</b> the gateway, between the app and the agent.</p>
  <p><b>Say:</b> One door in. Authentication, quotas and logs are enforced here, not in each service.</p>
  <p><b>Ask the room:</b> "Where are these controls applied today?"</p>
  <p><b>Next:</b> the agent needs to prove who it is.</p>
</aside>
```

- **Before step 1** (slide notes): name the zones from left to right and the thread you will follow.
- **Timing:** split the slide's time across the steps; about 30 to 45 s per step in a workshop. Set `data-timing`
  (seconds) on the section, so the speaker-view pacing timer knows the slide's budget.
- **Point at** names what is lit, so the presenter's words match the screen.
- **Say** has 1 to 3 speakable sentences that add to the on-screen sentence instead of repeating it.
- **Ask the room** is optional: one open question, used in workshops and discovery sessions.
- **Next** is the bridge sentence that motivates the next press.
- If the user has their own speaker-notes conventions (language, a summary line in a second language, a
  sign-off), apply them to every step.
- Self-guided decks: make each on-screen sentence self-sufficient. For autoplay, set `autoSlide` in the config and
  `data-autoslide` per step.

## Writing the steps

- **Follow one thread**: one request, order or claim from start to finish. The audience should be able to retell it.
- **One idea per step**, one sentence of at most about 20 words, in plain language and the present tense.
- **Focus 1 to 5 components per step.** Consecutive steps should share at least one component, so the zoom glides
  instead of jumping.
- **3 to 9 steps.** Above that, split the diagram or the story.
- **Name the failure.** A resilience step says what fails, what the user sees and what keeps working.
- **End on the recap**: an empty focus brings back the whole picture, with one sentence that sums up the path.

## Accessibility

- The SVG has `role="img"` and a `<title>` that describes the whole diagram.
- The step sentences are real text in an `aria-live="polite"` container, so screen readers read each step.
- With `prefers-reduced-motion: reduce`, the zoom jumps instead of animating, the dashes stop and the fades are
  removed. The highlight still changes.
- Colour is never the only signal: a failure carries a text label, and focus also thickens the outline.
- Everything the step needs is in its sentence. Dimmed parts are context only.

## PDF and no JavaScript

With `?print-pdf`, the slide shows the whole diagram and lists every step in two columns; the hint line is hidden.
Without JavaScript, the whole diagram shows. Evidence images only appear during stepping. If they must survive
in the PDF, add a slide after the walkthrough with an evidence grid.

## QA checklist

- [ ] `DiagramWalkthrough.audit()` in the browser console returns `[]` (no unknown ids), and stepping logs no
      `[diagram-walkthrough]` warnings.
- [ ] Every step frames the components it names. Nothing important is cropped, and text stays readable when zoomed.
- [ ] Stepping back to the start restores the whole diagram with nothing dimmed.
- [ ] Deep link `#/<slide-id>/<step-index>` opens that step.
- [ ] Reduced-motion emulation: instant zoom, no moving dashes.
- [ ] `?print-pdf`: whole diagram plus the numbered step list, on one page.
- [ ] Speaker view (S) shows each step's own notes, and the slide notes before step 1.
- [ ] Projector check: the dimmed context is still faintly legible, and the focused labels are at least about
      14 px on screen.
