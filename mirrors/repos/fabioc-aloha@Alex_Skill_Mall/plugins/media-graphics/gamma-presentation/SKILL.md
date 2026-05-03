---
type: skill
lifecycle: stable
inheritance: inheritable
name: gamma-presentation
description: Author markdown files optimized for Gamma import — card structure, layout hints, image directives, speaker notes, and chat-agent refinement workflow
tier: extended
applyTo: '**/*gamma*,**/*presentation*'
currency: 2026-04-23
lastReviewed: 2026-04-30
---

# Gamma Presentation Authoring


> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

This skill teaches you to **write markdown that imports cleanly into Gamma**, then refine the result using **Gamma's in-app AI chat agent**. Two workflows are supported:

1. **API workflow** — `.github/muscles/gamma-generator.cjs` posts directly to the Gamma API (one-shot)
2. **Manual workflow** — author the file in VS Code → paste/upload into Gamma UI → refine with the agent (recommended for high-stakes decks)

Choose manual when the user wants creative control over layout, image style, and theme. Choose API when speed matters more than polish.

---

## Authoring Rules

### Card Breaks Are `---`

Each `---` (markdown horizontal rule on its own line, blank line above and below) becomes a new card. Cards are Gamma's slide unit. Without explicit `---`, Gamma's importer auto-splits unpredictably.

```markdown
# Quarterly Review

Opening card content.

---

## Revenue

Second card.

---

## Next Steps

Third card.
```

**Rule of thumb**: One core idea per card. If a card needs scrolling at 16:9, split it.

### Heading Hierarchy

| Markdown | Gamma role |
|---|---|
| `# H1` | Title card — use exactly **once** at the top |
| `## H2` | New card title |
| `### H3` | Section header within a card |
| `#### H4` | Sub-section / column header |

Do not skip levels. `# Title` → `## Card` → `### Section` keeps the importer's outline correct.

### Card Length Budget

| Card type | Body words | Bullet count |
|---|---|---|
| Title / section divider | 0–10 | 0 |
| Content card (16:9) | 40–80 | 3–5 |
| Detail / data card | 80–140 | 5–8 |
| Appendix card | up to 200 | 8–12 |

Long-form documents (mode `document`) tolerate more; presentations should breathe.

### Speaker Notes

Gamma reads HTML comments as speaker notes:

```markdown
## Pricing Strategy

We're moving to tiered pricing in Q3.

<!-- Speaker note: Emphasize the migration window. Reference the Q2 churn data
when asked. Do not commit to a launch date — legal review pending. -->
```

Notes are hidden in published view, exported in PPTX speaker-notes panel.

### Image Directives

Three patterns, in order of fidelity:

| Pattern | When to use |
|---|---|
| `![](https://example.com/file.png)` | Exact image you control |
| `![A photorealistic close-up of a chess piece on a marble board, dramatic side lighting]()` (empty src) | Let Gamma's AI generate from your alt text |
| `<!-- gamma-image: cinematic shot, low-angle, golden hour, no text -->` (HTML comment marker) | Hint for the chat agent to swap later — placeholder card uses theme default |

Write **alt-text prompts as if briefing a photographer**: subject, framing, lighting, mood, what to exclude (`no text`, `no people`, `no logos`).

### Tables

Standard pipe tables import as Gamma tables:

```markdown
| Tier | Price | Seats |
|---|---|---|
| Starter | $29/mo | 5 |
| Pro | $99/mo | 25 |
| Enterprise | Custom | Unlimited |
```

Keep ≤ 5 columns, ≤ 8 rows per card. Wider tables → split or move to appendix.

### Charts

Gamma renders simple data via its chart card. To hint the importer, use a fenced block labelled `chart` with TSV/CSV:

````markdown
```chart
type: bar
title: Revenue by Quarter
Q1 120
Q2 145
Q3 180
Q4 210
```
````

For complex visualizations, generate the chart externally (`data-visualization` skill) and embed as an image.

### Columns / Multi-Column Layouts

Gamma's importer recognizes a 2- or 3-column layout from `###` siblings within a card:

```markdown
## Comparison

### Old Approach
- Manual ticketing
- Email follow-up
- 5-day SLA

### New Approach
- Auto-routed
- Slack threads
- 4-hour SLA
```

The card renders as side-by-side columns. Keep parallel structure (same bullet count).

### Callouts

Use blockquote with a leading emoji to trigger Gamma's callout card style:

```markdown
> 💡 **Insight**: 73% of churned customers never opened the onboarding email.

> ⚠️ **Risk**: API rate limits cap us at 12K syncs/hour during the launch window.
```

### Toggles / Collapsibles

For appendix detail that shouldn't crowd the main flow, use HTML `<details>`:

```markdown
<details>
<summary>Methodology</summary>

We surveyed 1,240 users across 3 cohorts between Jan and Mar 2026...

</details>
```

Gamma renders these as expandable toggles.

---

## Document Skeleton

Every well-formed Gamma source follows this shape:

```markdown
# {Deck Title}

{One-sentence promise of what the audience will learn.}

<!-- Speaker note: Audience = {who}. Goal = {what they should do next}.
Tone = {confident / exploratory / instructive}. -->

---

## Agenda

1. The problem
2. What we did
3. What changed
4. What's next

---

## {Section 1 Title}

{Body — 40-80 words or 3-5 bullets.}

![Illustrative image alt text — describe scene, lighting, mood]()

---

{... more cards ...}

---

## Recommendation

> 💡 **Bottom line**: {one sentence}

---

## Appendix

<details>
<summary>Methodology</summary>
...
</details>

<details>
<summary>Data sources</summary>
...
</details>
```

Always end with an **Appendix** section using `<details>` toggles for backup data, methodology, glossary, and FAQs. The audience sees a clean main flow; the presenter has depth on demand.

---

## Workflow A: Manual (Recommended for High-Stakes Decks)

1. **Draft** the markdown file using the skeleton above. Keep it under 75 cards (Gamma's import limit).
2. **Pre-process** with the preprocessor muscle to auto-insert card breaks, demote stray H1s, and flag dense cards / weak alt-text:

   ```bash
   node .github/muscles/md-to-gamma.cjs ./deck.md
   # writes ./deck-gamma.md with inline <!-- Gamma: ... --> recommendations
   ```

   Or right-click any `.md` in VS Code Explorer → **Convert Markdown → Gamma (preprocess)**.
3. **Validate locally**: render to HTML (`md-to-html` skill) or PPTX (`md-to-word` → PowerPoint) to sanity-check structure before paying for credits.
4. **Import to Gamma**:
   - Open <https://gamma.app> → **Create new** → **Import** → paste markdown or upload `<name>-gamma.md`
   - Choose theme + page format (16:9 fixed for presentations, fluid for docs)
   - Click **Generate**
5. **Refine via chat agent** (see next section)
6. **Export** as PPTX or PDF

This workflow gives the user control over theme, brand, and per-card image direction.

---

## Workflow B: API One-Shot

Use `.github/muscles/gamma-generator.cjs` when speed matters and the user is okay with the default theme:

```bash
node .github/muscles/gamma-generator.cjs --file ./deck.md --slides 12 --dimensions 16x9 --export pptx --open
```

Always pass `--slides N` and `--dimensions 16x9` for presentations. Without them, Gamma auto-splits and may default to fluid layout.

For draft-then-edit workflow:

```bash
# 1. Generate draft markdown
node .github/muscles/gamma-generator.cjs --topic "Q2 review" --draft --draft-output ./q2.md

# 2. User edits q2.md in VS Code

# 3. Generate final
node .github/muscles/gamma-generator.cjs --file ./q2.md --slides 14 --dimensions 16x9 --export pptx --open
```

Full parameter reference: see `instructions/gamma-presentation.instructions.md`.

---

## Refining with Gamma's Chat Agent

Once the deck is open in Gamma's editor, the **sparkle icon** ✨ opens the AI chat agent. It can edit any card, regenerate images, restyle the whole deck, translate, and add new cards.

### Effective Agent Prompts

| Goal | Prompt template |
|---|---|
| Tighten a wordy card | *"Condense this card to 3 bullets, keep the data point"* |
| Regenerate one image | *"Replace this image with a wide cinematic shot, low-angle, no people"* |
| Restyle whole deck | *"Apply a more conservative tone — dark navy theme, serif headings, minimal images"* |
| Add a missing card | *"Insert a 'Next Steps' card after Pricing with 4 owner/date bullets"* |
| Fix imbalance | *"Card 6 is much denser than the others — split it into two"* |
| Translate | *"Translate the deck to Brazilian Portuguese, keep the data labels in English"* |
| Generate speaker notes | *"Add 2-sentence speaker notes to every card that has data"* |
| Add data viz | *"Convert this table into a horizontal bar chart, sorted descending"* |

### Agent Strengths vs Limits

**Agent does well:**

- Per-card edits (text, images, layout)
- Theme application across deck
- Adding individual cards from a topic
- Translation and tone shifts
- Restyling images consistently

**Agent struggles with:**

- Multi-card structural rewrites (do those in markdown, re-import)
- Embedded chart data corrections (edit source data, regenerate)
- Brand asset injection (upload assets to workspace first)
- Cross-card narrative consistency (you stay the editor here)

**Rule**: Use markdown for structure, agent for polish. If you find yourself re-prompting the agent 4+ times for the same card, the source markdown is wrong — fix it there and re-import.

---

## Recommendations to Surface to the User

When generating or reviewing a Gamma source file, proactively call out these issues:

| Issue detected | Recommendation to user |
|---|---|
| First card has more than a title | "Add a one-sentence promise under the H1 — Gamma's title card looks empty otherwise" |
| Any card body > 140 words | "Card N is too dense for a 16:9 slide — split or move detail to an appendix toggle" |
| No `![]()` image directives | "No image prompts found — Gamma will use stock images. Add 2-3 alt-text prompts for hero cards" |
| No speaker notes | "Add `<!-- Speaker note: ... -->` blocks for talking points — they export to PPTX" |
| No appendix | "Add `## Appendix` with `<details>` toggles for methodology and data sources" |
| Heading levels skip (H1 → H3) | "Heading hierarchy skips a level — Gamma's outline will look broken" |
| Identical bullet counts across all cards | "Vary card density — uniform cards feel monotonous; mix bullets, tables, callouts, images" |
| All-text deck with `--image-model` set | "No `![]()` directives but image-model is set — generation will be expensive without alt-text guidance" |

---

## Cost Awareness

Default 10-card deck with standard images: **80–150 credits** (~$1.50–3 on Pro plans).

Tier the image model to deck importance:

- **Throwaway / iteration**: `flux-quick` (2 credits)
- **Standard work**: `flux-pro` (10 credits) — recommended default
- **Client-facing**: `imagen4` or `recraft` (25 credits)
- **Hero deck**: `flux-ultra` or `gpt-image-hd` (75–125 credits)

Full model table in `instructions/gamma-presentation.instructions.md`.

---

## Related

- `instructions/gamma-presentation.instructions.md` — auto-loaded routing + muscle parameters
- `prompts/gamma.prompt.md` — `/gamma` command reference
- `muscles/md-to-gamma.cjs` — markdown preprocessor (`name.md` → `name-gamma.md`); also surfaced as **Convert Markdown → Gamma (preprocess)** in the VS Code right-click menu
- `muscles/gamma-generator.cjs` — API runner (one-shot generation)
- `skills/presentation-tool-selection` — Marp vs Gamma vs manual decision matrix
- `skills/data-visualization` — produce chart images for embed
- `skills/markdown-mermaid` — diagrams that survive Gamma import
- `skills/brand-asset-management` — upload brand assets to Gamma workspace before generation
