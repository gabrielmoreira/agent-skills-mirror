---
name: cowork-vs-copilot-advisor
description: |
  Evaluates a prompt or use case and recommends whether it is a better fit for
  Microsoft 365 Copilot (included in the license — no marginal cost) or Copilot
  Cowork (pay-as-you-go / consumption-based), weighing five factors: input,
  output, time saved, prompt complexity, and — above all — cost. Because M365
  Copilot has no per-task cost, the default is to prefer it and escalate to
  Cowork only when complexity or output genuinely require it and the value
  clearly justifies the spend.
  Use when the user asks "Cowork or M365 Copilot?", "which tool should I use for
  this?", "is this worth running in Cowork?",
  "should I do this in M365 Copilot instead?", "is Cowork overkill for this?", or
  pastes a prompt/use case and asks which surface fits best.
  Do NOT use to produce a single quantified credit/dollar estimate before running
  one Cowork task — use the precost skill instead. Do NOT use to report the real
  metered cost of a finished task — that is the built-in /cost command and the
  Cost Management dashboard.
cowork:
  category: analysis
  icon: Lightbulb
---

<!---
cowork-vs-copilot-advisor is not an official Microsoft skill or a productized Microsoft feature. All outputs are estimates only. cowork-vs-copilot-advisor is advisory only.
This skill was downloaded from https://github.com/pvernocchi/precost-cowork-skill where an updated version might be available.
-->


# cowork-vs-copilot-advisor — Right-tool routing: Cowork vs M365 Copilot

A decision-support skill that takes a **prompt or a described use case** and
recommends the surface that delivers the outcome at the **lowest justified cost**:
**Microsoft 365 Copilot** (flat, included in the license — every extra task is
free) or **Copilot Cowork** (pay-as-you-go — every task consumes credits/dollars).

## Overview

The two surfaces have very different cost models, and that asymmetry drives the
recommendation:

- **M365 Copilot** is bundled in the user's license. Marginal cost of one more
  prompt is effectively **zero**. Best at fast, in-app, single-step work grounded
  in the user's own M365 data (Outlook, Teams, Word, Excel, PowerPoint, SharePoint).
- **Cowork** is **consumption-priced (PAYG)** — each run spends credits that map to
  real dollars. It earns its cost on **complex, multi-step, agentic** work:
  orchestrating many tools, producing rich or multiple deliverables, long-running
  autonomous tasks, and anything M365 Copilot simply cannot do.

**Guiding principle:** default to M365 Copilot because it is free at the margin.
Recommend Cowork only when the task's **complexity or output** cannot be met in
M365 Copilot **and** the **time saved / value returned** clearly outweighs the
PAYG spend.

## When to Use

- The user is deciding where to run a specific prompt or workflow.
- A task feels like it *might* be overkill (or underpowered) for one surface.
- The user wants a quick, reasoned "which tool, and why" before starting work.

## When NOT to Use

- The user wants a **quantified per-task credit/dollar estimate** before running a
  single Cowork task — use the **precost** skill instead.
- The user wants the **actual metered cost** of a task already finished — that is
  the built-in **/cost** command and the Cost Management dashboard.
- The user has already decided the surface and just wants the work done — proceed
  with the work; don't gate it behind a routing analysis.

## Quick Start

```
User: "Summarize this 3-page Word doc and pull out the action items."
1. Read the prompt; score the five factors (input, output, time saved,
   complexity, cost).
2. Single-step, single-file, no orchestration → M365 Copilot can do it at zero
   marginal cost.
3. Recommend M365 Copilot; note Cowork adds cost without added value here.

User: "Take these 6 transcripts, build a findings deck, a summary doc, and
       email each owner their action items."
1. Score the five factors: multi-file input, multiple deliverables, high time
   saved, multi-tool agentic workflow.
2. Beyond a single M365 Copilot turn → Cowork's orchestration justifies the PAYG
   spend.
3. Recommend Cowork; suggest running `precost` for the dollar estimate.
```

## Core Instructions

### Phase 1: Gather the facts

Read the prompt or use-case description. If a load-bearing factor is missing (e.g.
number of deliverables, or whether it must run unattended), ask **one** focused
question with `core-AskUserQuestion` — otherwise assume a reasonable default and
proceed. Do not interrogate the user.

### Phase 2: Score the five factors

Rate each factor and note which surface it favors:

| Factor | Favors **M365 Copilot** | Favors **Cowork** |
|--------|-------------------------|-------------------|
| **Input** | One file/thread; data already in an M365 app | Many sources, mixed formats, uploads, cross-app data to be gathered |
| **Output** | One short/medium artifact in-app (reply, summary, a few slides) | Multiple or rich deliverables (deck + doc + email), generated files, images |
| **Time saved** | Minutes; a person could do it quickly | Hours of manual effort collapsed into one run |
| **Complexity** | Single step, one turn, no tool chaining | Multi-step, agentic, many tools, branching, iteration |
| **Cost (decisive)** | Included license → **$0 marginal** for this task | PAYG credits/$ — only worth it if value clears the spend |

**Cost is the tie-breaker.** When both surfaces could do the job, prefer M365
Copilot because the task is already paid for. Cowork wins only when it unlocks an
outcome M365 Copilot can't reach, or saves enough time/value to more than repay
its consumption cost.

### Phase 3: Recommend (with rationale)

Give a clear verdict in one of three tiers:

- **Use M365 Copilot** — fits the license, no extra cost; Cowork would add spend
  without added value. **When the verdict is M365 Copilot, ALWAYS also offer 3
  "Cowork upgrade" example prompts** (see Phase 3b) — concrete ways to expand the
  user's base prompt into work that would genuinely justify running it in Cowork.
- **Use Cowork** — complexity/output exceeds a single M365 Copilot turn and the
  value justifies the PAYG cost. Point the user to the **precost** skill for the
  dollar figure.
- **Either works** — both are viable; recommend M365 Copilot on cost unless the
  user values Cowork's richer output. State the trade-off plainly.

### Phase 3b: Cowork upgrade prompts (only when the verdict is M365 Copilot)

When you recommend M365 Copilot, help the user see where Cowork *would* pay off.
Take their **base prompt** and write **3 escalated variations** of it — same core
task, expanded so the complexity/output crosses the line into Cowork territory.
Each should push a different lever so they aren't three of the same idea:

1. **Scale the input** — many more sources / files / threads to gather and reconcile
   (e.g. "…across all 12 project channels" instead of one document).
2. **Enrich the output** — multiple or richer deliverables in one run (e.g. add a
   deck + a summary doc + per-owner emails instead of a single reply).
3. **Chain the workflow** — make it multi-step / agentic / unattended (e.g. gather,
   analyze, draft, and route follow-ups in one autonomous pass).

Keep each example a single realistic sentence, recognizably built on the user's
original wording. Add a one-line note that these would warrant a `precost` check
before running. If the verdict is **Use Cowork** or **Either works**, skip this —
the examples are only for steering an M365-Copilot task toward Cowork value.

### Phase 4: Show the reasoning

Present the recommendation, the factor scorecard, and a one-line cost note. For a
side-by-side comparison of 3+ factors, render it with `render_ui` (a small table
or two-column card); otherwise a short markdown table is enough.

## Output

- **Verdict** (1 line): the recommended surface + the single biggest reason.
- **Scorecard**: the five factors, each marked M365 Copilot / Cowork / neutral.
- **Cost note** (1-2 lines): why this is or isn't worth PAYG spend; if Cowork,
  suggest running `precost` for the exact estimate.
- **Cowork upgrade prompts** (M365 Copilot verdict only): 3 escalated variations of
  the user's base prompt that would justify Cowork, one per lever (scale input /
  enrich output / chain the workflow), plus a note to `precost` before running.
- Keep it under ~200 words unless the user asks for depth. Neutral, advisory tone.

## Guardrails

- **Default to the cheaper surface.** When in doubt, recommend M365 Copilot —
  it is already paid for. Only push Cowork when the value clearly justifies it.
- **Never invent prices or credit amounts.** This skill gives a *reasoned fit*
  recommendation, not a dollar figure. For quantified costs, delegate to
  `precost` (estimate) or `/cost` (actuals).
- **Don't block work.** If the user has already chosen a surface, respect it; this
  skill advises, it doesn't gate.
- **State assumptions.** If you assumed a default (e.g. "one deliverable"), say so,
  so the user can correct the routing.
- **No fabricated capabilities.** If unsure whether a surface can do something,
  say so rather than guessing.
