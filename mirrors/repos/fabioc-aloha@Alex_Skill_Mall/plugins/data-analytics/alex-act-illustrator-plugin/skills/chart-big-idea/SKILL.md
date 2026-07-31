---
name: chart-big-idea
description: "Distill the one-sentence Big Idea, story arc, audience, and style stance for a chart BEFORE picking a chart type. Starts by questioning intent — whether the artifact should exist at all, and whether the stated purpose is the real one. Reads the surrounding docs / prose / ticket for an existing Big Idea first, then helps the user articulate one via a 3-question elicitation ladder if none is found. Asks whether the user wants a TRADITIONAL (safe) or INNOVATIVE (higher-impact, higher-risk) treatment. Use before invoking the flint-chart skill or the /render-chart prompt whenever the user's ask is 'chart this', 'visualize', 'make a chart', 'show the data', or when framing is unclear."
lastReviewed: 2026-07-25
---

# Chart Big Idea

Frame the chart before you pick it. A chart is a rhetorical act — it makes an argument about the data. If you can't state the argument in one sentence, the chart type will be wrong no matter how it's rendered.

This skill produces a **Chart Brief** — a short structured record of Big Idea + story arc + audience + style stance — which then feeds the `flint-chart` skill's §0.2 selection table.

**Scope.** Steps 0, 1, and 3 — read the context, state the claim in one sentence, read the audience — apply to **any** communication artifact: a slide, a memo, a diagram, a report section. Steps 2, 4, and 5 are chart machinery, which is why this skill is chart-named. If you are framing something that is not a chart, run Steps 0–1 and 3 and stop there.

## When to invoke

Invoke this skill BEFORE `flint-chart` selection when any of these fire:

- User says "chart this", "visualize this", "make a chart", "show me the data"
- User attaches a dataset without a stated question
- User says "which chart should I use for..." and gives a data description
- The `/render-chart` prompt fires — this skill is its Step 0
- Existing chart is being redesigned ("this doesn't land — can we improve it?")

Do NOT invoke when:

- User provides a fully-formed spec asking to render it verbatim
- User is iterating on style/color/spacing of an already-chosen chart type
- The chart is diagnostic-only (e.g. exploratory data profiling); framing overhead isn't earned

## Step 0: Read the surrounding context first (before asking anything)

Before you ask the user for the Big Idea, look for it in the material they've already produced. Often the Big Idea is written in prose next to where the chart will live — you just have to find it and lift it. Interrogating the user for a claim they already wrote is wasteful and slightly insulting.

**Where to look, in order:**

| Source                                                                                | What to grep for                                                                                                                             | Example                                                                           |
| ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| The paragraph immediately before/after the chart's insertion point                    | Claim-shaped sentences ("...shows that...", "...demonstrates...", "...surprisingly...", "...contrary to...", "...three of the last five...") | Paper section says "Skeptics span the full Likert range" — that's a Big Idea seed |
| The doc / report / notebook section heading the chart sits under                      | The heading often IS the topic; the sentence beneath is often the Big Idea                                                                   | Section titled "Clusters differ in shape, not just center"                        |
| The PR description, ticket, issue, or commit message that spawned the chart request   | The "why" that justified opening the ticket                                                                                                  | "Need to show finance the West is pulling away"                                   |
| Any existing chart caption, figure title, `alt=` text, or prior version of this chart | Prior authors' framing you can inherit or sharpen                                                                                            | Old caption: "BI by cluster with SD bars" (topic — needs upgrade)                 |
| The user's own recent messages in this conversation                                   | Adjectives, verbs, and framings they used to describe the finding                                                                            | User said "the Skeptics story is vivid" — "vivid" is the tell                     |
| README / abstract / one-pager / project overview                                      | Confirms the audience the whole document is targeting                                                                                        | Fixes Step 3 audience-read without a separate question                            |
| Adjacent charts in the same doc                                                       | Their captions establish the narrative rhythm this chart plugs into                                                                          | Fig06 caption sets up the comparison; fig07 caption should extend it              |

**What to do with what you find:**

- **Found a claim-shaped sentence**: draft the Big Idea from it, show it to the user in Step 1 as _"Here's what I think you're arguing — confirm or correct?"_, let them fix in one hop. Do not silently rewrite the user's own words — if their prose already states the Big Idea, quote it verbatim in the Brief and cite the source.
- **Found only a topic**: skip to Step 1 elicitation with the topic as your anchor.
- **Found nothing** (cold ask, no doc, no ticket): go directly to Step 1 elicitation with no anchor.
- **Found conflicting framings** (e.g. ticket says one thing, prose says another): surface the conflict to the user before drafting — "the ticket asks for X but the section prose argues Y — which is the chart supposed to land?"

**Skip Step 0 when**: the user pasted a Big Idea directly ("Chart this: X grew 3× faster than Y"). Context-gathering isn't needed when the framing arrived on the request.

**Time budget**: Step 0 should take under a minute. If you're spelunking through 20 files trying to reconstruct intent, stop and ask the user — the doc genuinely doesn't have it.

## Step 0.5: What earns a figure — the 5-criteria gate

Before drafting the Big Idea, verify the figure earns its place. A figure earns its place when it does one (or more) of:

1. **Compresses a decision rule** — matrix, decision tree, or before/after that turns branching prose into a single scan
2. **Shows a temporal or procedural sequence** — a loop, flow, or timeline the prose can only enumerate
3. **Makes an abstraction concrete** — labeled anatomy, storyboard, worked example that anchors an otherwise floating concept
4. **Surfaces a hidden failure mode** — a side-by-side that reveals a defect the reader would miss in prose
5. **Anchors a recurring visual concept** — a figure the reader will need to reference repeatedly across sections

If none apply, the figure does not earn its place. Restate the claim as a sentence or a table instead. An unearned figure adds visual weight without adding argument, which weakens the surrounding argument.

**Deletion test**: if the surrounding prose reads fine when the figure is removed, the figure is decorative. If the prose has to be substantially rewritten to compensate, the figure was doing real work.

Adapted from _The Defensible Decision_ (Fabio Correa, Ch 5) via the `dd-book-illustrator` skill in Alex_DDA.

## Step 1: The Big Idea (one sentence)

### First, check the intent — not just the finding

The Big Idea asks _what the data shows_. Before that, ask **what this artifact is actually for**. Answer both from Step 0 context where you can; escalate to the user only when the answer is unclear or uncomfortable.

1. **Should this exist at all?** A chart with no claim is decoration. If Step 0 surfaced no argument and the data holds no surprise, say so and offer the cheaper alternative — a sentence, a table, or nothing. A competent chart nobody needed is a failure that looks like success.
2. **Is the stated purpose the real one?** Sometimes the request is "show that X worked" rather than "show what X did" — a decision already made, looking for a picture to ratify it. That is a legitimate thing to build, but name it: it belongs in the Brief as **Persuasive**, and the honest version makes its case without suppressing the counter-evidence.

**If the intended message and the data disagree, surface it before drafting the Big Idea.** Do not quietly pick the chart that makes the requested point. Say what the data supports, name the gap, and let the user decide. This is the one moment in the workflow where the right answer may be _"not this chart"_ — every later step assumes the chart should exist.

Adapted from Cole Nussbaumer Knaflic's _Storytelling with Data_ framing. Write ONE sentence that:

1. **States a unique point of view** — not a topic. "Adoption is up" beats "Q3 adoption metrics".
2. **Conveys what's at stake** — why the reader should care. "…so we need to reallocate the training budget" beats "…which is notable".
3. **Is a complete sentence** — subject + verb + object. If it reads like a chart title, tighten it into a claim.

**Template**: _"[Subject] [did/is/shows] [specific finding], [therefore/so-what implication]."_

**Examples:**

| Weak (topic)               | Strong (Big Idea)                                                                                                                                        |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Sales by region"          | "The West region grew 3× faster than the rest of the company last quarter, so the FY26 hiring plan should shift 15 headcount west."                      |
| "AI readiness scores"      | "One-third of respondents are Skeptics with BI below the Likert midpoint — training programs that treat them the same as Enthusiasts will underperform." |
| "Portfolio risk over time" | "Portfolio VaR crossed the policy ceiling in three of the last five quarters — the risk-appetite statement needs a formal review."                       |

### If the Big Idea is still not clear after Step 0 — help the user find it

Run this 3-question elicitation ladder. Ask **one question at a time**; stop as soon as a Big Idea sentence writes itself. Do not batch the questions — batching is an interrogation, not a conversation.

1. **"What surprised you in this data?"** — the surprise is almost always the Big Idea. If nothing surprised, the chart may not have a claim to make (in which case, ask whether it's decorative / reference-only).
2. **"What decision should change if this chart lands?"** — gets the "so-what" clause. If no decision changes, the chart is informational; that's fine, but the Big Idea shape shifts from persuasive to descriptive.
3. **"If a colleague read only the chart title and moved on, what one sentence do you want stuck in their head?"** — the Big Idea reframed as a headline the user can imagine writing. This one usually unlocks users who couldn't answer #1 or #2 abstractly.

**If all three come back vague** ("just show the data", "I don't know, you pick"): propose a Big Idea _yourself_ from Step 0 context + what the data actually shows, mark it clearly as `**Proposal**:`, and let the user confirm or edit. Do not stall waiting for a perfect answer. A specific proposal the user can react to is faster than an open-ended prompt.

**Anti-pattern**: running the whole ladder in one message ("What surprised you? What decision changes? What headline?"). One question, wait, listen, next.

## Step 2: Story arc

Once the Big Idea is written, classify the story arc. This narrows chart families before `flint-chart` §0.2 fires:

| Story arc                | What it argues                                 | Chart-family shortlist                                  |
| ------------------------ | ---------------------------------------------- | ------------------------------------------------------- |
| **Comparison**           | A > B, A ≠ B, ranking                          | Bar, dot plot, lollipop, bullet                         |
| **Change over time**     | X trended up/down/inflected                    | Line, area, slope, small-multiple line                  |
| **Composition**          | X is made up of parts                          | Stacked bar, treemap, waffle, donut (rarely pie)        |
| **Distribution**         | X is spread this way                           | Histogram, box, violin, strip, jittered dot, density    |
| **Relationship**         | X co-varies with Y                             | Scatter, bubble, connected scatter, hexbin              |
| **Deviation**            | X differs from a benchmark / expectation       | Diverging bar, dumbbell, bullet, error-bar              |
| **Flow**                 | X moves from A to B                            | Sankey, chord, alluvial                                 |
| **Anomaly**              | X is unusual                                   | Annotated line/scatter with the anomaly highlighted     |
| **Ranking-with-context** | X's position vs peers _and_ distribution shape | Lollipop on distribution, dot plot with reference bands |

A single chart usually leans on ONE arc. If the Big Idea needs two arcs (e.g. "compare + show distribution"), that's the hybrid signal — flag it for Step 4.

## Step 3: Audience + stakes

Three quick reads. Do not turn this into an interview:

| Read                    | Options                                        | Impact on chart choice                                                                  |
| ----------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Reading time**        | Glance (5s) / Read (30s) / Study (2min+)       | Glance → traditional + one message. Study → can afford complexity.                      |
| **Statistical fluency** | General / Domain-fluent / Technical            | Fluent audiences can read box/violin/parallel coords; general audiences cannot.         |
| **Stakes**              | Informational / Persuasive / Decision-critical | Decision-critical earns a title-sentence overlay and annotation; informational may not. |

If the user hasn't told you, infer defaults: **Glance / General / Persuasive** for external audiences, **Read / Domain-fluent / Decision-critical** for internal analytics work.

## Step 4: Style stance — TRADITIONAL vs INNOVATIVE

**Ask the user explicitly** (unless they already stated a preference):

> _"Do you want the traditional treatment — a familiar chart everyone will read at a glance — or an innovative treatment that shows more of the story but costs the reader a few seconds of study?"_

Both are valid design choices. The tradeoff:

| Dimension                     | TRADITIONAL (safe)                                          | INNOVATIVE (higher-impact, higher-risk)                         |
| ----------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| **Legibility**                | Universal — no explanation needed                           | Needs a caption, sometimes a legend walkthrough                 |
| **Information density**       | One dimension per chart                                     | Multiple dimensions layered                                     |
| **Risk of misreading**        | Low                                                         | Moderate — some readers will bounce off                         |
| **Best for**                  | Executive dashboards, first exposure, glance-time audiences | Analytical narratives, technical reports, curated presentations |
| **Comparison example**        | Bar chart of cluster means                                  | Lollipop on strip-jitter distribution                           |
| **Change-over-time example**  | Line chart                                                  | Slope chart (first + last only) or connected scatter            |
| **Distribution example**      | Histogram                                                   | Ridgeline plot or beeswarm                                      |
| **Composition example**       | Stacked bar                                                 | Waffle grid or treemap                                          |
| **Deviation example**         | Bar with target line                                        | Bullet chart or dumbbell                                        |
| **Ranking + context example** | Ranked bar                                                  | Dot plot with reference band, or lollipop on distribution       |

**Style-stance × Story-arc → concrete chartType hints for flint-chart §0.2**:

| Story arc            | Traditional pick                    | Innovative pick                                                                                  |
| -------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| Comparison           | `bar_chart` (grouped or single)     | `lollipop_chart`                                                                                 |
| Change over time     | `line_chart`                        | `slope_chart` or annotated `line_chart` with markers                                             |
| Composition          | `stacked_bar_chart`                 | `treemap` or faceted `bar_chart` (small multiples)                                               |
| Distribution         | `histogram` or `bar_chart` of bins  | `strip_plot` + jitter, `boxplot`, or `violin` where Flint supports it                            |
| Relationship         | `scatter_plot`                      | `scatter_plot` with color/size encoding + trendline layer                                        |
| Deviation            | `bar_chart` with reference `rule`   | `bullet_chart` or dumbbell (two-point layered)                                                   |
| Flow                 | `bar_chart` of source→target counts | `sankey` (if backend supports it — see `flint-chart` §0.4)                                       |
| Anomaly              | `line_chart` with annotated point   | `line_chart` with shaded band + annotation callout                                               |
| Ranking-with-context | Ranked `bar_chart`                  | Layered `lollipop_chart` overlaid on `strip_plot` (see AIRS fig07 ultimate for a worked example) |

**Rule of thumb**: default to TRADITIONAL when the audience is glance-time or general-fluency. Default to INNOVATIVE when the audience is domain-fluent AND has 30+ seconds of study time AND the extra dimensions materially strengthen the Big Idea. When in doubt, ask.

## Step 4.5: Focus discipline (executing the chosen stance)

Style stance decides scope. Focus discipline decides execution. Three rules govern the mark-level choices once Step 4 has picked TRADITIONAL or INNOVATIVE.

### One pre-attentive attribute per emphasis

Color, size, position, and typeface are pre-attentive attributes — the eye finds them without scanning. Use exactly one to mark the point of the Big Idea. Two adds no signal (the reader already found it). Three degrades the signal (the emphasis reads as random rather than intentional).

Example: in a bar chart where the story is one region's shortfall, most bars in slate-300 and the story-carrying bar in blue-800 is enough. Adding stroke-width AND size on top is over-encoding.

### Redundant encoding for accessibility

When color carries meaning (categorical distinction, severity, target vs actual), pair it with a second cue — shape, label, position, or texture. Roughly 8% of male readers cannot reliably distinguish red from green; a color-only encoding fails them silently. Color + shape and color + label both survive deuteranopia.

Deuteranopia-simulate any red/green pairing (browser DevTools, macOS Accessibility Inspector, or a color-blindness plug-in) before shipping.

### BEFORE-only anti-pattern figures: neutral title

When a figure teaches by showing failure (a flawed chart the reader is asked to diagnose), keep the title and subtitle neutral. "As generated" / "First draft" / "Cold Copilot output" describe the artifact state without previewing what's wrong. Editorializing in the title spoils the diagnostic task the figure exists to teach.

Paired BEFORE/AFTER figures are the exception: the AFTER panel already reveals the argument, so the title can name it directly.

Adapted from _The Defensible Decision_ (Fabio Correa, Ch 5-6) via the `dd-book-illustrator` skill in Alex_DDA.

## Step 5: Write the Chart Brief and hand off

Output a compact brief (fits in one message, ~10 lines) that the `flint-chart` skill or `/render-chart` prompt consumes directly:

```markdown
### Chart Brief

- **Big Idea**: <one sentence, from Step 1>
- **Story arc**: <one label from Step 2 taxonomy>
- **Audience**: <reading-time> / <fluency> / <stakes>
- **Style stance**: TRADITIONAL | INNOVATIVE (with one-sentence rationale)
- **Suggested chartType(s)**: <1-2 from the Step 4 crosstab>
- **Alternates considered**: <1-2 the crosstab surfaced but you didn't pick, with why>
- **Anti-patterns to avoid**: <call out any per flint-chart §0.3 that this brief risks>
```

Then invoke `flint-chart` §0.2 with the brief as context. The brief locks the framing; §0.2 handles the mechanical chartType lookup + Flint coverage check.

## Anti-patterns

| Anti-pattern                                                           | Correction                                                                                                                                                                                                 |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Asking the user for the Big Idea without doing Step 0 first**        | Read the surrounding prose / ticket / section heading first. If the user already wrote the claim, lift it — don't make them re-articulate it.                                                              |
| Accepting the stated purpose without testing it                        | Ask what the artifact is really for before writing the claim. A chart built to ratify a decision already made is legitimate, but it belongs in the Brief as Persuasive — not dressed as neutral reporting. |
| Framing a chart that should not exist                                  | If the data holds no claim, the honest output is a sentence or a table, not a well-framed chart. Say so before Step 2.                                                                                     |
| Silently rewriting the user's own claim into your preferred phrasing   | If Step 0 surfaces their sentence, quote it verbatim in the Brief and cite the source. Sharpen only with permission.                                                                                       |
| Writing a topic ("Q3 metrics") and calling it a Big Idea               | Topics don't argue anything. Force the subject-verb-implication shape.                                                                                                                                     |
| Running the Step 1 elicitation ladder as a batch of 3 questions        | Interrogation, not conversation. One question at a time; stop as soon as the sentence writes itself.                                                                                                       |
| Stalling forever when the user can't articulate the Big Idea           | Propose one yourself from Step 0 + the data, mark it `**Proposal**:`, let them react. Specific proposals unlock faster than open prompts.                                                                  |
| Skipping Step 4 because "the chart is obvious"                         | If the chart is obvious, the style stance is a 10-second confirmation, not skipped work. Ask.                                                                                                              |
| Defaulting to INNOVATIVE because it's more visually interesting to you | Traditional charts win most decisions. Innovation is earned by audience + stakes, not by aesthetics.                                                                                                       |
| Picking INNOVATIVE when the reader has 5 seconds                       | Innovative charts need study time. If the audience is glance-time, an innovative chart fails the Big Idea, no matter how elegant.                                                                          |
| Writing the Brief AFTER rendering                                      | The Brief is the constraint on the render, not a post-hoc justification.                                                                                                                                   |

## Worked example (AIRS fig07 ultimate)

- **Step 0 sources** (context found before asking the user anything):
  - `AIRS/paper/manuscript.html` § Results — paragraph before the figure reads _"cluster centroids on BI diverge sharply, but the within-cluster spread tells the more actionable story"_ → near-verbatim Big Idea seed
  - Existing R plot caption: "BI by cluster with SD bars" → topic-shaped, needed upgrading to a claim
  - `AIRS/SUMMARY.md` audience note: technical readers, decision-critical for training program design → fixed Audience read without a separate question
- **Big Idea**: _"The three AI-readiness clusters differ not just in average Behavioral Intention but in how tightly their members cluster around the mean — Enthusiasts are uniformly high, Skeptics span the full Likert range."_ (drafted from Step 0 seed, confirmed by user in one hop — no elicitation ladder needed)
- **Story arc**: Ranking-with-context (comparison + distribution)
- **Audience**: Study (2min+) / Domain-fluent / Decision-critical
- **Style stance**: INNOVATIVE — the Big Idea has two arcs, so a traditional single-arc chart (bar of means) loses half the argument. Study-time + domain-fluent audience can afford the extra read cost.
- **Suggested chartType**: layered `lollipop_chart` (centroid + stem) overlaid on `strip_plot` (respondent-level jitter)
- **Alternates considered**: (a) traditional bar with error bars — chosen against because it hides the floor/ceiling clamping that makes the Skeptics story vivid; (b) boxplot + strip — chosen against because box quartile lines are redundant with the strip density and add visual noise.
- **Anti-patterns to avoid**: over-layering (kept to strip + lollipop + centroid, no boxplot); starting y at 0 on a Likert scale (started at 1); putting metadata inside the plot area (n= labels moved to the axis).

## Related skills

- [`big-idea`](../big-idea/SKILL.md) — the generalized Big Idea distillation for any summary-shaped output. `chart-big-idea` is the chart-specific specialization.
- [`chart-vocabulary`](../chart-vocabulary/SKILL.md) — 7-goal catalog + CSAR override table. Consumed by Step 5 (Chart Brief) to pick a chart type once the Big Idea is locked; also consumed by the selection tree in `chart-vocabulary` Module 5 which delegates back here for Step 1.
- [`flint-chart`](../flint-chart/SKILL.md) — §0.2 chart-family-before-type + `ChartAssemblyInput` authoring. Consumes the Chart Brief.
- [`render-verify`](../render-verify/SKILL.md) — post-render check + Prose-coupling check for the shipped figure.
- [`print-svg-style-guide`](../print-svg-style-guide/SKILL.md) — how figures LOOK once framing (this skill) is locked. Canvas + typography + palette + composition idioms.
- [`figure-generator`](../figure-generator/SKILL.md) — deterministic engineering discipline for shipping figures backed by real datasets.

## Would Revise If

Revise this skill by 2026-10-22 (90 days) or sooner if any of the following fires:

- The Brief format is skipped in ≥3 consecutive `/render-chart` invocations because it's too heavy for the common case → tighten to 3 fields.
- The TRADITIONAL/INNOVATIVE binary produces user confusion in ≥2 sessions (users say "I don't know, you pick") → replace the ask with an inferred default per audience, keep the binary as an override.
- The Step 4 crosstab produces a chartType that `flint-chart` §0.4 can't render more than once per quarter → the crosstab is out of sync with Flint coverage and needs a refresh pass.
- Cole Nussbaumer Knaflic publishes a materially revised Big Idea framing that supersedes the three-part rule used here.
- The Step 1 intent check never changes an outcome across ~10 invocations → it is ceremony; fold it back into the elicitation ladder's first question.
- Users invoke this skill to frame **non-chart** artifacts often enough that Steps 2/4/5 are routinely skipped → the general half (Steps 0/1/3) has outgrown the chart-specific half, and it should be split into its own skill rather than scope-noted.
