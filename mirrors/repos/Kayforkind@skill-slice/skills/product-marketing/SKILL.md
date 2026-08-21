---
name: product-marketing
description: "Creates or updates .agents/product-marketing.md as the positioning source of truth (ICP, personas, differentiation, customer language) for downstream marketing skills. Use when the user mentions product or marketing context, ICP, positioning, or before writing ads and landing copy. Not for writing the ads, competitor battlecards, or a full marketing plan (those sibling skills). Do not invent metrics or testimonials."
version: 2.1.1
---

# Product Marketing Context

This skill creates and maintains a foundational product marketing context document at `.agents/product-marketing.md`. Other marketing skills (competitors, marketing-plan, pricing-strategy) reference this document so the user never repeats positioning, audience, or messaging details.

## When to Use

- Starting any new marketing project or campaign — run this **first** before other marketing skills
- User says "set up context," "product context," "marketing context," "positioning," "who is my target audience," "describe my product," "ICP," "ideal customer profile"
- User wants a single source of truth for product, audience, and competitive positioning
- Before writing ads, emails, landing pages, or sales collateral that need consistent messaging
- Refreshing stale context after product, pricing, or positioning changes

## Prerequisites

- A project repository with at least a README or basic product documentation (for auto-draft mode)
- PowerShell on Windows as the primary host environment
- Write access to the project root (the skill creates `.agents/product-marketing.md`)

## Procedure

### Step 1 — Check for Existing Context

1. Check if `.agents/product-marketing.md` already exists:

   ```powershell
   Test-Path .agents\product-marketing.md
   ```

2. Also check legacy locations that older setups may have used:

   ```powershell
   Test-Path .claude\product-marketing.md
   Test-Path .agents\product-marketing-context.md
   Test-Path .claude\product-marketing-context.md
   ```

3. **If the canonical file exists** at `.agents/product-marketing.md`:
   - Read it and summarize what's captured
   - Ask which sections the user wants to update
   - Only gather info for those affected sections
   - Jump to Step 3 to update

4. **If a legacy file exists** anywhere other than `.agents/product-marketing.md`:
   - Offer to move it to the canonical location:

     ```powershell
     Move-Item .claude\product-marketing.md .agents\product-marketing.md -Force
     ```

   - Confirm the move, then read and summarize

5. **If no file exists anywhere**, offer two options:

   - **Option A — Auto-draft from codebase (recommended):** Study the repo and draft a V1. The user reviews, corrects, and fills gaps. Faster than starting from scratch.
   - **Option B — Start from scratch:** Walk through each section conversationally, one at a time.

   Most users prefer Option A. After presenting the draft, ask: "What needs correcting? What's missing?"

### Step 2 — Gather Information

#### If Auto-Drafting (Option A)

1. Read the codebase for source material:
   - `README.md`, `README.*`, or `readme.*`
   - Landing pages, marketing copy, about pages, pricing pages (HTML, MDX, JSX, etc.)
   - Meta descriptions and `<title>` tags
   - `package.json` (description, keywords, homepage fields)
   - `CHANGELOG.md` or changelog entries
   - Any existing docs (`docs/`, `*.md` files)

2. Draft every section listed in "Sections to Capture" below based on what you find.

3. Present the full draft and ask what needs correcting or is missing.

4. Iterate until the user is satisfied.

**HARD RULE — Never invent facts while auto-drafting.** Metrics, customer names, testimonials, competitor shortcomings, and verbatim quotes must come from the repo or the user. If a section has no source, write `[TBD — needs input]` and ask. A wrong "fact" here propagates into every ad, email, and page the other skills produce.

#### If Starting from Scratch (Option B)

Walk through each section in "Sections to Capture" conversationally, one at a time. Do not dump all questions at once.

For each section:
1. Briefly explain what you're capturing and why
2. Ask relevant, specific questions (see Tips below)
3. Confirm accuracy by summarizing back
4. Move to the next section

Push for **verbatim customer language** — exact phrases are more valuable than polished descriptions because they reflect how customers actually think and speak, which makes downstream copy more resonant.

### Step 3 — Create or Update the Document

After gathering information, create or update `.agents/product-marketing.md` using this exact structure. Keep section names stable — other marketing skills parse the document by section heading.

```markdown
# Product Marketing Context

*Last updated: [date]*

## Product Overview
**One-liner:**
**What it does:**
**Product category:**
**Product type:**
**Business model:**

## Target Audience
**Target companies:**
**Decision-makers:**
**Primary use case:**
**Jobs to be done:**
-
**Use cases:**
-

## Personas
| Persona | Cares about | Challenge | Value we promise |
|---------|-------------|-----------|------------------|
| | | | |

## Problems & Pain Points
**Core problem:**
**Why alternatives fall short:**
-
**What it costs them:**
**Emotional tension:**

## Competitive Landscape
**Direct:** [Competitor] — falls short because...
**Secondary:** [Approach] — falls short because...
**Indirect:** [Alternative] — falls short because...

## Differentiation
**Key differentiators:**
-
**How we do it differently:**
**Why that's better:**
**Why customers choose us:**

## Objections
| Objection | Response |
|-----------|----------|
| | |

**Anti-persona:**

## Switching Dynamics
**Push:**
**Pull:**
**Habit:**
**Anxiety:**

## Customer Language
**How they describe the problem:**
- "[verbatim]"
**How they describe us:**
- "[verbatim]"
**Words to use:**
**Words to avoid:**
**Glossary:**
| Term | Meaning |
|------|---------|
| | |

## Brand Voice
**Tone:**
**Style:**
**Personality:**

## Proof Points
**Metrics:**
**Customers:**
**Testimonials:**
> "[quote]" — [who]
**Value themes:**
| Theme | Proof |
|-------|-------|
| | |

## Goals
**Business goal:**
**Conversion action:**
**Current metrics:**
```

### Step 4 — Confirm and Save

1. Show the completed document to the user.
2. Ask if anything needs adjustment.
3. Save to `.agents/product-marketing.md`:

   ```powershell
   # Ensure .agents directory exists
   if (-not (Test-Path .agents)) { New-Item -ItemType Directory -Path .agents }
   # Document is written by the agent directly to .agents\product-marketing.md
   ```

4. Set the `*Last updated:*` date to today.
5. Tell the user: "Other marketing skills will now use this context automatically. Run `/product-marketing` anytime to update it."

---

## Sections to Capture

### 1. Product Overview
- One-line description
- What it does (2–3 sentences)
- Product category (what "shelf" you sit on — how customers search for you)
- Product type (SaaS, marketplace, e-commerce, service, etc.)
- Business model and pricing

### 2. Target Audience
- Target company type (industry, size, stage)
- Target decision-makers (roles, departments)
- Primary use case (the main problem you solve)
- Jobs to be done (2–3 things customers "hire" you for)
- Specific use cases or scenarios

### 3. Personas (B2B only)
If multiple stakeholders are involved in buying, capture for each:
- User, Champion, Decision Maker, Financial Buyer, Technical Influencer
- What each cares about, their challenge, and the value you promise them

### 4. Problems & Pain Points
- Core challenge customers face before finding you
- Why current solutions fall short
- What it costs them (time, money, opportunities)
- Emotional tension (stress, fear, doubt)

### 5. Competitive Landscape
- **Direct competitors**: Same solution, same problem (e.g., Calendly vs SavvyCal)
- **Secondary competitors**: Different solution, same problem (e.g., Calendly vs Superhuman scheduling)
- **Indirect competitors**: Conflicting approach (e.g., Calendly vs personal assistant)
- How each falls short for customers

### 6. Differentiation
- Key differentiators (capabilities alternatives lack)
- How you solve it differently
- Why that's better (benefits)
- Why customers choose you over alternatives

### 7. Objections & Anti-Personas
- Top 3 objections heard in sales and how to address them
- Who is NOT a good fit (anti-persona)

### 8. Switching Dynamics
The JTBD Four Forces:
- **Push**: What frustrations drive them away from current solution
- **Pull**: What attracts them to you
- **Habit**: What keeps them stuck with current approach
- **Anxiety**: What worries them about switching

### 9. Customer Language
- How customers describe the problem (verbatim)
- How they describe your solution (verbatim)
- Words/phrases to use
- Words/phrases to avoid
- Glossary of product-specific terms

### 10. Brand Voice
- Tone (professional, casual, playful, etc.)
- Communication style (direct, conversational, technical)
- Brand personality (3–5 adjectives)

### 11. Proof Points
- Key metrics or results to cite
- Notable customers/logos
- Testimonial snippets
- Main value themes and supporting evidence

### 12. Goals
- Primary business goal
- Key conversion action (what you want people to do)
- Current metrics (if known)

---

## Keeping It Current

The document decays as the product evolves. Prompt the user to refresh it when any of these happen:

- Pricing or business model changes
- Repositioning, rebrand, or new product category
- A new ICP, segment, or persona becomes the focus
- A major launch adds capabilities that change differentiation
- Sales or support surfaces new objections or customer language

When updating, only re-gather the affected sections, and always bump the `*Last updated*` date. If the date is more than ~6 months old when another task reads it, suggest a review.

## Pitfalls

- **Inventing facts during auto-draft.** This is the #1 risk. A fabricated metric or misattributed quote propagates into every ad, email, and landing page downstream skills produce. Always use `[TBD — needs input]` when no source exists.
- **Renaming section headings.** Other marketing skills parse `.agents/product-marketing.md` by section name. If you rename `## Differentiation` to `## Why We're Better`, downstream skills will fail to find the context they need.
- **Dumping all questions at once.** Overwhelms the user and produces shallow answers. Go one section at a time, confirm, then move on.
- **Polishing customer language.** Verbatim phrases — even grammatically imperfect ones — are more valuable than rewritten descriptions. They reflect how customers actually think and speak.
- **Skipping the `*Last updated*` date.** Other skills check this date to decide whether to suggest a refresh. A missing or stale date breaks that signal.
- **Forgetting legacy file locations.** Older setups used `.claude/product-marketing.md` or `product-marketing-context.md`. Always check all four paths before concluding no context exists.
- **Writing all sections when only some changed.** When updating, only re-gather affected sections. Rewriting the entire document wastes time and risks introducing errors in stable sections.

## Verification

1. Confirm the file exists at the canonical path:

   ```powershell
   Test-Path .agents\product-marketing.md
   ```

   Expected output: `True`

2. Verify all required section headings are present:

   ```powershell
   Select-String -Path .agents\product-marketing.md -Pattern "^## " | ForEach-Object { $_.Line }
   ```

   Expected sections (at minimum):
   - `## Product Overview`
   - `## Target Audience`
   - `## Problems & Pain Points`
   - `## Competitive Landscape`
   - `## Differentiation`
   - `## Objections`
   - `## Switching Dynamics`
   - `## Customer Language`
   - `## Brand Voice`
   - `## Proof Points`
   - `## Goals`

3. Confirm the `*Last updated*` date is set and current:

   ```powershell
   Select-String -Path .agents\product-marketing.md -Pattern "Last updated:"
   ```

4. Check for unfilled placeholders that need user input:

   ```powershell
   Select-String -Path .agents\product-marketing.md -Pattern "\[TBD"
   ```

   If matches are found, remind the user which sections still need input.

5. Confirm no legacy duplicates remain:

   ```powershell
   Test-Path .claude\product-marketing.md
   Test-Path .agents\product-marketing-context.md
   Test-Path .claude\product-marketing-context.md
   ```

   All should return `False` after migration.

## Tips

- **Be specific**: Ask "What's the #1 frustration that brings them to you?" not "What problem do they solve?"
- **Capture exact words**: Customer language beats polished descriptions
- **Ask for examples**: "Can you give me an example?" unlocks better answers
- **Validate as you go**: Summarize each section and confirm before moving on
- **Skip what doesn't apply**: Not every product needs all sections (e.g., Personas for B2C)
- **Mark gaps honestly**: `[TBD — needs input]` beats a plausible guess

## Related Skills

- **competitors** — For competitive deep dives and battlecard creation
- **marketing-plan** — For turning this context into a full marketing strategy
- **pricing-strategy** — For pricing and packaging decisions
