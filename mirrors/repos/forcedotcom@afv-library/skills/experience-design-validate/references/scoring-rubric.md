# Scoring Rubric

Use this rubric to judge the visual craft of a rendered design across five dimensions. Scores describe only the evidence observed in the declared evidence mode.

## Scoring rules

Every score must be:

- **Evidence-based:** cite specific, visible or directly observed qualities.
- **Bounded:** do not treat unobserved screens, behavior, states, responsiveness, or performance as good or bad.
- **Repeatable:** another reviewer should land within one point using the same evidence.
- **Actionable:** name what the next supported level requires.
- **Felt:** judge the visible experience, not implementation or intent.

### Anchor selection

Use the anchors at 2, 4, 6, 8, and 10. For each dimension:

1. Determine which criteria are applicable and observable in the declared evidence mode.
2. Evaluate anchors from 10 downward.
3. Assign the **highest anchor whose applicable, observable criteria are all fully supported by evidence**.
4. Assign the odd score above that anchor only when all criteria at the anchor are supported and the evidence clearly exceeds it but does not fully support the next anchor. For example, 7 means all applicable criteria at 6 are supported and some, but not all, applicable criteria at 8 are supported.
5. Assign 1 only when observed evidence falls below the applicable criteria at anchor 2.
6. Use `INSUFFICIENT_EVIDENCE` rather than a number when evidence cannot support the applicable dimension. Use `N/A` only when the dimension genuinely does not apply.

Do not start from an assumed middle score. Do not average unknowns into a score. When evidence supports multiple anchors, choose the highest fully supported anchor, not the lowest level whose criteria happen to be met.

## Scale and visual-craft implication

| Score | Level | Visual-craft implication only |
|---|---|---|
| 10 | Exceptional | Reference-quality visual craft; suitable to showcase for craft |
| 9 | Near-exceptional | Visually excellent with trivial polish opportunities |
| 8 | Strong | Visually ready with minor craft opportunities |
| **7** | **Good** | **Meets the visual-craft threshold with a minor polish plan** |
| 6 | Above adequate | Visually functional but craft is uneven |
| 5 | Adequate | Clear visible friction or roughness remains |
| 4 | Below standard | Significant craft issues diminish the visible experience |
| 3 | Poor | Multiple visible craft failures make the design feel rushed |
| 2 | Very poor | Fundamental visible craft failures require major rework |
| 1 | Critical | The rendered design feels visually broken or abandoned |

These implications do not approve accessibility, functional behavior, security, measured performance, or production release.

## Verdict

- **PASS:** every applicable dimension is scored and all scores are at least 7.
- **WARN:** every applicable dimension is scored; at least one is below 7 and none is below 5.
- **FAIL:** every applicable dimension is scored and at least one is below 5.
- **LIMITED:** at least one applicable dimension is `INSUFFICIENT_EVIDENCE`. Report supported scores as provisional observations, but do not imply complete visual-craft readiness.

`N/A` dimensions do not affect the verdict. If no dimension can be scored, do not issue a Craft Report verdict; follow the `INSUFFICIENT_VISUAL_EVIDENCE` behavior in `SKILL.md` when no rendered pixels exist, or return `LIMITED` with the coverage ledger when pixels exist but support no dimension-level score.

## Dimension anchors

### Useful

Felt question: *Does the visible content earn the space and attention it occupies?*

| Anchor | Observable criteria |
|---|---|
| 10 | Every visible element appears purposeful; priority and restraint anticipate the user's visible needs; no decorative dead weight competes for attention. |
| 8 | Core visible goals are well supported; most elements clearly earn their place; only minor tangents remain. |
| 6 | The visible value is understandable, but some content feels tangential, unfinished, or weakly prioritized. |
| 4 | Multiple visible elements do not earn their space; clutter obscures the apparent purpose. |
| 2 | The surface is dominated by content that does not visibly support the apparent core task. |

Do not infer whether features meet real user needs from pixels alone. Qualify the score as visible usefulness and flag behavioral assumptions for research.

### Usable

Felt question: *Does the visible hierarchy make the intended path feel effortless?*

| Anchor | Observable criteria |
|---|---|
| 10 | The intended path is visually unmistakable; complex structure feels simple; visible affordances prevent likely mistakes. |
| 8 | Primary actions and next steps are clear with minor hierarchy or affordance gaps. |
| 6 | The path is discoverable but invites hesitation; some visible actions compete or lack clarity. |
| 4 | Common visible paths appear confusing, fragmented, or poorly prioritized. |
| 2 | The rendered surface provides little visible guidance toward a core task. |

Static evidence supports visible hierarchy and affordance only, not task completion, recovery behavior, keyboard operation, or observed user success.

### Reliable

Felt question: *Do the observed states and feedback make the experience feel predictable?*

For `DYNAMIC_VISUAL` evidence, use these anchors:

| Anchor | Dynamic observable criteria |
|---|---|
| 10 | Every directly exercised relevant state and transition is clear, calm, and designed; observed feedback and timing remove uncertainty. |
| 8 | Major exercised states and feedback are clear; only minor observed edge gaps remain. |
| 6 | Observed states function but some treatment is generic, ambiguous, or poorly timed. |
| 4 | Directly observed feedback is missing, contradictory, or visibly brittle. |
| 2 | Observed behavior leaves the user unable to tell what happened or whether work persisted. |

For `STATIC_VISUAL` or `MULTI_VIEW_STATIC` evidence, score only the visible communication of depicted states and consequences:

| Anchor | Static observable criteria |
|---|---|
| 10 | Every depicted relevant state or consequence is immediately legible, calm, specifically authored, and unambiguous in context. |
| 8 | Major depicted states and consequences are clear and specifically treated; only minor visual-communication gaps remain. |
| 6 | Depicted states are identifiable, but some treatment is generic, ambiguous, or weakly prioritized. |
| 4 | Important depicted state or consequence cues are contradictory, hard to associate, or visually overwhelmed. |
| 2 | The depicted state leaves the viewer unable to tell what is true, what changed in the captured moment, or which visible action has serious consequences. |

Qualify every static Reliable score as **depicted-state visual communication only**. A static score cannot substantiate state coverage, transition behavior, save behavior, feedback timing, persistence, or performance. Use `INSUFFICIENT_EVIDENCE` when no relevant state or consequence is visibly depicted, or when behavior is necessary to score the dimension responsibly.

### Coherent

Felt question: *Does the visible experience feel like the same hand made it?*

| Anchor | Observable criteria |
|---|---|
| 10 | Every supplied screen shares one disciplined visual language; variants have clear visible purpose; patterns repeat consistently. |
| 8 | Core screens are visibly consistent with minor deviations in secondary areas. |
| 6 | The main visual language is recognizable, but repeated patterns drift. |
| 4 | Major visible inconsistencies make surfaces feel assembled by separate teams. |
| 2 | Supplied screens feel like unrelated products with no discernible shared system. |

One screenshot may support internal composition coherence, but cross-screen coherence requires multiple screens.

### Well-Crafted

Felt question: *Does the rendered design feel precise, considered, and delightful?*

| Anchor | Observable criteria |
|---|---|
| 10 | Every observed detail feels intentional and precise; hierarchy, type, spacing, alignment, color, and any exercised motion work as one quiet whole. |
| 8 | Execution is visibly strong and consistent with only minor polish opportunities. |
| 6 | Execution is generally sound but visible alignment, spacing, hierarchy, or state-treatment gaps remain. |
| 4 | Multiple visible inconsistencies or unfinished treatments make the design feel rough. |
| 2 | Pervasive visual quality failures make the rendered design feel broken or abandoned. |

Do not require motion, responsiveness, dark mode, reduced motion, or unseen states unless they are relevant and directly evidenced.

## Coverage and relevance ledger

The report must include a ledger before scores. Create one row for every dimension and every reference topic considered.

| Field | Allowed content |
|---|---|
| `item` | Dimension or reference topic |
| `relevance` | `APPLICABLE` or `N/A` |
| `coverage` | `SCORED`, `INSUFFICIENT_EVIDENCE`, or `N/A` |
| `evidence_mode` | `STATIC_VISUAL`, `MULTI_VIEW_STATIC`, or `DYNAMIC_VISUAL` |
| `evidence` | Artifact, screen, state, viewport, recording segment, or directly observed action |
| `reason` | Why it is scored, not applicable, or insufficiently evidenced |

`N/A` means the topic is absent or irrelevant. `INSUFFICIENT_EVIDENCE` means it is relevant but not observable. Never collapse these states into `Unknown`, and never invent a score to make the table complete.

## Finding severity

- **critical:** An observed visual-craft failure blocks comprehension of the primary surface or makes a destructive/high-consequence path visibly unsafe. Address before claiming visual-craft readiness.
- **major:** A repeated or prominent issue substantially weakens hierarchy, confidence, or task clarity. It materially lowers one or more dimensions.
- **minor:** A localized issue causes noticeable friction or inconsistency without undermining the primary path.
- **polish:** A small refinement would improve precision or delight but does not create meaningful confusion.

Each finding has one `primary_dimension`, the dimension most directly weakened by the root cause, and zero or more `related_dimensions`. Record the finding once and reference related dimensions rather than duplicating it. If severity could fit multiple levels, use the highest supported severity.

## Output discipline

- Cap findings at five per dimension.
- Consolidate a problem seen in three or more places into one finding with a count and representative location.
- Include zero to five cross-cutting patterns. A pattern must span multiple findings.
- Include zero to five recommendations, ordered by expected effect on observed visual craft.
- Do not add findings, patterns, or recommendations merely to fill the schema.
- Flag recommendations dependent on real-user behavior for usability research.
- Keep accessibility findings out of this report and route compliance to `experience-accessibility-validate`.

## Craft Report schema

```text
scope: visual-craft-only
verdict: PASS | WARN | FAIL | LIMITED
evidence_mode: STATIC_VISUAL | MULTI_VIEW_STATIC | DYNAMIC_VISUAL
evidence_inventory: [artifacts, screens, states, viewports, or recording segments reviewed]
evidence_limitations: [what this evidence cannot substantiate]

first_impressions: [0-3 felt observations recorded before rubric analysis]

coverage_relevance_ledger:
  - item: [dimension or reference topic]
    relevance: APPLICABLE | N/A
    coverage: SCORED | INSUFFICIENT_EVIDENCE | N/A
    evidence_mode: [mode]
    evidence: [specific artifact or observation, or none]
    reason: [concise rationale]

dimensions:
  - name: Useful | Usable | Reliable | Coherent | Well-Crafted
    score: [1-10] | INSUFFICIENT_EVIDENCE | N/A
    evidence: [specific observed evidence]
    gap_to_next_level: [next fully supportable craft improvement] | N/A

findings:
  - severity: critical | major | minor | polish
    primary_dimension: [one dimension]
    related_dimensions: [zero or more other dimensions]
    location: [screen, region, state, viewport, or Figma node; never file:line]
    problem: [visible or directly observed issue]
    why_it_weakens_craft: [design principle and felt effect]
    what_better_looks_like: [improved visible experience]
    fix: [specific design move]

cross_cutting_patterns: [0-5 evidence-backed themes]
recommendations: [0-5 evidence-backed prioritized moves]
fix_prompt: [self-contained design directive] | OMITTED_NO_ACTIONS
```

The report must state that the verdict indicates visual-craft readiness only and is not an accessibility, functionality, performance, security, or production-release approval.

## Comparative schema

Preserve the complete individual audit for each design, then add:

```text
comparison_result: A_HIGHER_CRAFT | B_HIGHER_CRAFT | TIE | MIXED

designs:
  - id: Design A
    first_impressions: [0-3 observations]
    strongest_visible_move: [evidence-backed strength]
    gaps: [0-5 evidence-backed gaps or INSUFFICIENT_EVIDENCE entries]
  - id: Design B
    first_impressions: [0-3 observations]
    strongest_visible_move: [evidence-backed strength]
    gaps: [0-5 evidence-backed gaps or INSUFFICIENT_EVIDENCE entries]

comparison_table:
  - dimension: [dimension]
    design_a: [1-10] | INSUFFICIENT_EVIDENCE | N/A
    design_b: [1-10] | INSUFFICIENT_EVIDENCE | N/A
    outcome: A | B | TIE | NOT_COMPARABLE
    evidence: [why]

differentiating_dimensions: [0-5 dimensions]
craft_moves:
  design_a: [0-5 moves Design A executes better]
  design_b: [0-5 moves Design B executes better]
borrow_without_copying: [0-5 grounded opportunities]
```

Use `TIE` when supported scores and qualitative evidence are materially equivalent. Use `MIXED` when each design leads in different dimensions or unequal evidence prevents a responsible overall ranking.

## Fix prompt

Include a fix prompt only when the report has at least one recommendation. It must:

- Open with a one-sentence felt goal and a short design brief.
- List only the report's evidence-backed recommendations, in priority order.
- Name the affected screen or region and felt outcome for each move.
- End with verification on fresh rendered evidence and identify dimensions expected to improve.
- Preserve parts of the design that already work.

Use design language, not CSS variables, class names, file paths, or implementation diffs. If there are no actionable recommendations, emit `OMITTED_NO_ACTIONS`.
