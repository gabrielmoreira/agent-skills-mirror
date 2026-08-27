# Design System Contract (DESIGN.md)

**The gate: no component code before `DESIGN.md` exists.** Design decisions
that live only in chat evaporate between screens; a contract file makes every
later component answer to the same tokens. When a project already has one,
read it and follow it — and when the work introduces a token, primitive,
interaction state, motion rule, or piece of accepted debt the contract
lacks, amend the contract before touching the code.

## Structure

`DESIGN.md` carries these sections, in order. An empty section is written as
an explicit decision ("no elevation system; flat surfaces only") — silence is
not a decision.

0. **Research Log** (greenfield builds) — an entry for every research lane
   that ran: the source consulted, what was taken from it (layout rhythm,
   color logic, type pairing choices), and any skipped lane with its
   reason. No log entry means the lane did not run.
1. **Atmosphere & Identity** — three adjectives the surface must read as,
   the chosen taste direction (primary, plus any deliberately borrowed
   elements with their reasons), the one signature element a template would
   not have, and the audience.
2. **Color** — the full palette as tokens: background layers, text
   hierarchy, accent budget, semantic states, borders. Name the proportion
   discipline (for example 60/30/10) and the contrast floor (WCAG AA at
   minimum).
3. **Typography** — the pairing (at most two families), a modular scale with
   named steps, weights in use, and line-height rules for body versus
   display. When the audience reads CJK: the fallback stacks, CJK
   line-height and letter-spacing rules, and `word-break`/truncation
   behavior for the heavy script.
4. **Spacing & Layout** — the base unit, the spacing scale, container
   widths, the grid, and which element owns scroll on every screen shape.
5. **Components** — the reusable primitives (button, input, card, nav,
   table, ...) with their variants and every interaction state: default,
   hover, focus-visible, active, disabled, loading, error, empty.
6. **Motion & Interaction** — duration and easing tokens, what animates and
   what never does, and the `prefers-reduced-motion` behavior. Motion is
   punctuation, not decoration.
7. **Depth & Surface** — the elevation system (shadows, borders, blur) or
   the explicit decision not to have one.
8. **Accessibility Constraints & Accepted Debt** — the constraints honored
   (keyboard paths, focus order, contrast) and the debt knowingly accepted,
   each with its reason.

## Workflow

- Greenfield: design research is a build step, not optional exploration —
  consult references and real product surfaces, record each lane in section
  0, and write the contract BEFORE the first component.
- Existing UI without a contract: stop and ask the user which path they
  want — either match the existing visual language and keep new styling
  local to the code it touches, or pause to extract the contract and shared
  primitives before continuing. Never decide silently.
- Every implementation cites the token it uses. A value that appears in
  code but not in `DESIGN.md` is drift: either the contract or the code is
  wrong, and one of them gets fixed.

## Boundary

`DESIGN.md` is a prepared contract, not rendered evidence: implementation,
screenshots, accessibility checks, and visual verdicts stay observed-only
through the visual-QA and web-QA owners.

## Attribution

The idea of pairing a design-system contract file with taste-direction
material and an evidence-bound critique lane adapts concepts from the
`frontend` skill of `code-yeongyu/oh-my-openagent@9c62b62` (Sustainable Use
License 1.0) and its permissively licensed design upstreams:
`Leonxlnx/taste-skill` (MIT), `nextlevelbuilder/ui-ux-pro-max-skill` (MIT),
`Owl-Listener/designpowers` (MIT), and `nexu-io/open-design` (Apache-2.0).
No upstream text is reproduced; the wording here is OMH's own, and OMH keeps
its deterministic no-render boundary. Product names appear as quality
analogies only; OMH is not affiliated with, endorsed by, or sponsored by any
named company.
