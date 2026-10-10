---
name: precost
description: |
  Runs a fast, visual "cost & value" pre-check on a Copilot Cowork task BEFORE
  the work starts. Estimates credits from five cost signals (model, context size,
  runtime, tools / skills / plugins, attachment weight), classifies the task as
  Light / Medium / Heavy, estimates Copilot Credits, dollar cost, time saved and
  value returned, shows it as an inline Adaptive Card with a disclaimer and
  sustainability tips, then asks whether to proceed, proceed more sustainably, or
  use a lighter tool (Copilot Chat / M365 Copilot).
  Invoke when the user types "/precost", "precost", "pre-check first", "cost check",
  "estimate this task", "what will this cost", "is this worth running in Cowork",
  or "should I run this here".
  Do NOT use for follow-ups or refinements WITHIN a task already in progress, or to
  report the real metered cost of a finished task (that is the built-in /cost
  command and the Cost Management dashboard).
metadata:
  category: analysis
  icon: Calculator
---

<!---
Precost is not an official Microsoft skill or a productized Microsoft feature. All outputs are estimates only. The real cost will always depend on the prompt, context, documents, tools used, model behavior, runtime and final execution. Pre-cost is advisory — it does not enforce or cap spend. Only the admin spending limits and alerts in the Microsoft 365 admin center do that. This repository is for learning, experimentation and demonstration only.

This skill was downloaded from https://github.com/pvernocchi/precost-cowork-skill where an updated version might be available
-->

# precost — Cowork Task Cost & ROI Pre-check

A lightweight gate that runs **once at the start of a new task** (or whenever the
user types **`/precost`**). It tells the user, before any credits are spent,
roughly what the task will **cost** and what it will **return**, shows it
visually inline, points out how to run it more **sustainably**, and lets them
decide whether to proceed, proceed leaner, or switch to a cheaper tool.

Keep it **fast**. This is a quick estimate, not research. The only lookups
allowed are the cheap, local ones: read the active model from the session, list
attachments with `Glob`, and **Read the companion reference files in the
`references/` subfolder**. Do **not** call search, email, calendar, web, or
file-content tools to produce the estimate.

## Reference files (load on demand — cheap local Reads)

All the pricing/value detail lives in three files in the `references/` subfolder
so this workflow stays short. **Read the relevant file when the step says to** —
a local `Read` is cheap and fast, unlike web/search.

- **`references/pricing-reference.md`** — official Cowork/Copilot pricing, the
  credit model, model cost multipliers (§4), attachment weights (§5), base credit
  bands (§6), and the adjustment formula (§7). Use it in Steps 1–3.
- **`references/value-and-routing.md`** — time-saved/value bands & formula (§1),
  verdict logic (§2), which-Copilot-to-use routing (§3), and the
  **step-by-step instructions** for doing the task in M365 Copilot / Copilot Chat
  (§4). Use it in Steps 4, 6, and 8.
- **`references/card-template.md`** — the ready-to-fill Adaptive Card JSON
  skeleton. Use it in Step 7.

These files are the **single source of truth** for every number this skill
quotes. Do not invent figures that aren't in them.

## When to run

- The user types **`/precost`** (or "precost", "pre-check first", "cost check").
- The user has just delegated a **new task** to Cowork (the first substantive
  request of a task), e.g. "prep me for my customer meeting and build a deck",
  "analyze this data and produce a report", "draft and send the team update".

## When NOT to Use (when NOT to run)

- **Follow-ups within the same task** — "make the title bigger", "add a slide",
  "change the tone", "now email it too". The pre-check already ran for this task;
  do not run it again.
- Pure questions / chit-chat that aren't a delegated task ("what's on my
  calendar?", "who is the PM for X?").
- A request for the **actual** cost of a completed task — point the user to the
  built-in `/cost` command and the Cost Management dashboard instead.

## Step 1 — Gather the five cost signals (cheap, local only)

Read these five signals to build the most approximate estimate, from the prompt +
session + a quick attachment listing only — no expensive lookups.

1. **Model in use.** Detect the active model from the session/environment, then
   apply its credit multiplier. **The multiplier table is
   `references/pricing-reference.md` §4** (anchored to the Cowork default,
   **Opus 4.8 = 1.0×**; 1 credit ≈ $0.01).
   If the model can't be determined, assume the Cowork default (Opus 4.8, 1.0×)
   and say so on the card.
2. **Context size.** Roughly how much material the model must read/hold — sources,
   timeframe, attachment size, prior conversation. More context = more input
   tokens = more credits. Judge it **small / moderate / large**.
3. **Runtime.** Roughly how long it runs (more turns + tool calls = more credits).
   Light ≈ under a minute; Medium ≈ 1–3 min; Heavy ≈ 3 min+.
4. **Tools / skills / plugins.** Which capabilities the task invokes:
   - **Cheap:** a single read (one calendar/email/file), one render card.
   - **Moderate:** multi-source M365 search, a doc skill (`docx`/`xlsx`/`pptx`),
     a few tool calls.
   - **Expensive:** `ImageGenerate`, `deep-research`, browser automation,
     multi-step workflows, or anything that spawns subagents.
5. **Attachments.** List them (`Glob input/**/*`) and note type + size. **Format
   drives credit weight far more than file size — the weight table is
   `references/pricing-reference.md` §5.** (`.md` cheapest; PDFs/slides/images
   cost multiples more.)

> Read `references/pricing-reference.md` now to pull the model-multiplier and
> attachment-weight tables for Steps 1–3.

## Step 2 — Classify the base task (Light / Medium / Heavy)

Judge the task on sources, reasoning depth, and deliverables to set the **base**
credit band. **The band table (credits + USD per class) is
`references/pricing-reference.md` §6.** Pick the class by the **heaviest signal
present** (one short email summary = Light; multi-source briefing + Excel + deck
= Medium; 6-month data analysis + leadership report vs. prior period = Heavy).

## Step 3 — Adjust the estimate (model + one class bump)

Turn the base band into the final band with the formula in
**`references/pricing-reference.md` §7** — deliberately just **two** levers, so
the estimate is reproducible and the badge always matches the number:

```
adjusted_credits ≈ base_band(effective_class) × model_multiplier
```

- **effective_class:** start from the Step 2 class, then **bump up one level** if a
  **heavy input** (`.pptx`, scanned PDF, or several images) **or** an **expensive
  tool** (`ImageGenerate`, `deep-research`, browser automation, subagents) is present;
  **bump down** for a single trivial read on a light (`.md`/`.txt`/`.csv`) input;
  otherwise keep it. Move by the heaviest driver only — don't stack bumps.
- **model_multiplier:** apply §4 (Opus 4.8 = 1.0× baseline; Sonnet 4.6 ≈ 0.6×; etc.).
- Do **not** also multiply by attachment weight or a context/tool factor — the class
  already prices context, runtime and tools, and the §5 weights only decide the bump.
- Keep the result a **band**, never false-precise. Round to clean ranges, e.g.
  **"≈ 200–450 credits · ≈ $2–4.50 (Sonnet 4.6)."**

## Step 4 — Estimate the return (time saved + value)

Map the task to the Cowork ROI categories and **sum the Typical minutes saved**
for the categories it touches (a multi-part task touches several). **The category
table, the value formula, and the default `HOURLY_RATE` (€75/hr) are in
`references/value-and-routing.md` §1.** Cost is USD; value is the user's
currency; do **not** invent an FX rate — present them side by side.

## Step 5 — Sustainability check (recommendations + a leaner prompt)

Decide whether the **same outcome** could be reached for fewer credits. Only raise
levers that genuinely apply — never pad. Common, concrete levers:

- **Model right-sizing.** Routine task (summary, extraction, simple draft) on a
  heavy model (Opus 4.8 / a premium model)? Recommend Sonnet 4.6 / an efficiency
  model. Genuinely hard reasoning? Keep the heavy model.
- **Lighter attachments.** No-image PDF / scanned doc attached? Recommend
  converting to `.md` first (multiples cheaper). Flag image-heavy or `.pptx`
  inputs as the cost driver.
- **Tighter scope.** Broad prompt ("analyze everything")? Suggest narrowing the
  timeframe, source set, or number of deliverables.
- **Cheaper route.** Single artifact or quick Q&A? Point to Copilot Chat / M365
  Copilot (no metered credits — see Step 6).

If at least one lever applies, prepare a **sustainable rewrite** of the user's
prompt (same goal, leaner execution) to offer in Step 8. If nothing meaningful
applies, say the task is already running efficiently and skip the recommendations.

## Step 6 — Verdict & whether to suggest an alternative

Apply the **verdict logic and the which-Copilot-to-use routing table in
`references/value-and-routing.md` §2–§3**:

- **Strongly positive** — time-value clearly dwarfs credit cost (typical for
  Medium/Heavy multi-deliverable tasks). Recommend **proceed**.
- **Marginal** — a Light task a per-seat tool does at **no metered credit cost**.
  Suggest the alternative (Copilot Chat / M365 Copilot) but let the user choose.

## Step 7 — Render the visual card (inline, not a file)

Render the estimate as an **Adaptive Card in the conversation** via the
`render-ui` skill (invoke `render-ui`, then `render_ui`). Never write it to a
file. Keep it compact and professional. Include, in this order:

1. **Title** — "Cowork task pre-check"
2. A **Badge** for the class: `Light` / `Medium` / `Heavy`.
3. A **FactSet**: `Model`, `Estimated cost` (adjusted band), `Attachments`,
   `Estimated time saved`, `Estimated value` (state the hourly rate), `Verdict`.
4. **Recommendations** (only if Step 5 found levers) — a short `TextBlock` list,
   e.g. "Switch to Sonnet 4.6 · Convert the PDF to .md · Narrow to last 30 days".
5. A short **disclaimer** TextBlock (small, `isSubtle: true`, `wrap: true`) — use
   this exact concise wording:

   > *Estimate only — not the metered bill. It factors the model, context,
   > runtime, tools and attachments, but the real cost depends on what actually
   > runs and is shown by `/cost` and the Cost Management dashboard after the
   > task. This pre-check is advisory, not a spending limit, and uses
   > research-based pricing and time-savings bands (directional, not a
   > guarantee). Running this check itself uses a small amount of credits.*

A **ready-to-fill JSON skeleton** lives in **`references/card-template.md`** —
Read it at this step, fill in the values, keep colours subtle and on-brand, and
drop the "Run it leaner" block when Step 5 found no levers.

## Step 8 — Ask how to proceed

Immediately after the card, use **AskUserQuestion** (one question) so the user
decides after reading the numbers. Tailor the options to what applies:

- **Question:** "How would you like to proceed?"
- **Options:**
  - **"Proceed in Cowork"** — run the task as written (recommend for Medium/Heavy).
  - **"Use Cowork — sustainably"** — *offer this whenever Step 5 found at least one
    lever.* On selection: apply the **sustainable rewrite** from Step 5 (switch the
    model where supported, convert heavy attachments to `.md`, tighten scope),
    briefly list the adjustments made, then run the task with the leaner setup.
  - **"Use Copilot Chat / M365 Copilot instead"** — *offer for marginal/Light
    tasks.* On selection: **Read `references/value-and-routing.md` §4, pick the
    recipe that matches the task, and walk the user through the concrete
    step-by-step** for that tool (which app, which button, what to type). Then
    stop — don't run it in Cowork.

**Conditional follow-up:** If the user picks plain **"Proceed in Cowork"** *and* a
sustainable rewrite is available, ask one more short question before starting:
"Want me to convert your prompt into a more sustainable one to save resources?"
— Yes → apply the rewrite and proceed; No → proceed exactly as written.

If they cancel (empty answer) → acknowledge and wait. Never block the task behind
more than these questions.

## Guardrails

- **Run once per task, at the start.** Never re-run on follow-ups or refinements
  within the same task.
- **Only cheap, local lookups for the estimate** — detect the active model, list
  attachments (`Glob`), and Read the companion files in `references/`. Do
  **not** call search, email, calendar, web, or file-content tools. Stay fast.
- **Never present the estimate as the real bill.** Always show the disclaimer. The
  authoritative figures are `/cost` and the Cost Management dashboard, which the
  user runs **after** the task completes.
- **Quote ranges, not false precision.** Cost is a band read from the effective
  class and scaled only by the model multiplier (heavy inputs / expensive tools move
  the class up one level — they are not extra multipliers); value uses a stated,
  user-editable hourly rate.
- **Recommend sustainability only when it genuinely helps.** Don't invent levers;
  if the task already runs efficiently, say so and skip the recommendations.
- **Advisory, not enforcement.** This does not block spend — only admin spending
  limits/alerts do that.
- **Card is inline only** — render via the `render-ui` skill; never write it to
  `output/`.
- **No fabrication.** Use only the credit bands, model multipliers, attachment
  weights, time-savings bands, and routing in `references/pricing-reference.md`
  and `references/value-and-routing.md`, plus the signals you can actually
  observe (model, attachments, prompt). Do not invent credit figures, dollar amounts, savings
  numbers, an FX rate, or a model that isn't in use. If the task doesn't map
  cleanly to a class or category, say it's a rough estimate rather than guessing.
