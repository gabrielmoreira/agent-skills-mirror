---
name: output-voice-friendly-short
description: "Flattens copy for TTS and screen readers: sentences of at most 15 words, no nested clauses, spoken sources at the end, and no tables or Markdown markers. Trigger on voice assistant, spoken briefing, or read-aloud delivery. Do not use for printed memos, IRAC opinions, or inline pinpoint citations."
version: 1.0.1
---

# Voice-Friendly Short Output

## Overview

Voice output has strict constraints that written output does not: the listener cannot re-read a sentence, cannot scan a table, and loses the thread if a clause nests more than two levels deep. This skill adapts output for text-to-speech systems, screen readers, and voice assistants without sacrificing accuracy.

**Sources verified (2026-05-31):**
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html

## When to Use

Activate when **any** of the following are true:
- The output will be read aloud by a text-to-speech system
- A screen reader is the primary access mode
- The user requests a "spoken" or "voice" format answer
- The interface signals a voice or accessibility context
- A quick verbal briefing is requested ("give me a 30-second summary")

Do **not** activate for:
- Formal written deliverables (memos, opinions, contracts)
- Outputs that will be printed or reviewed on screen
- Complex multi-issue analysis requiring parallel structure

## Prerequisites

- Confirm the target delivery channel (TTS engine, screen reader, voice assistant) if unclear
- Confirm the target language and register (e.g., MSA for Arabic)
- If a design-system or UI implementation task is also in scope, load the UI/UX workflow in the second half of this skill

## Procedure

### Step 1 — Apply the four core rules

#### Rule 1: Short sentences (max 15 words)

If a legal or technical rule requires a longer sentence, break it at the conjunction.

**Before:** "Under UAE Federal Decree-Law 33/2021, a non-compete clause must be proportionate in scope, limited in geography, limited in duration, and necessary to protect a legitimate employer interest."

**After:** "A non-compete in the UAE must meet four tests. It must be proportionate in scope. It must be limited to a specific geography. It must not exceed two years. And it must protect a real business interest. That's UAE law, Decree-Law 33 of 2021."

#### Rule 2: No nested clauses

Flatten any clause that qualifies a qualification.

**Before:** "The obligation, which arises unless the employee (who was not a signatory to the original NDA, having joined after its execution) can demonstrate..."

**After:** "The obligation arises by default. One exception: if the employee joined the company after the NDA was signed, they may argue they were never bound by it."

#### Rule 3: No footnotes, tables, or inline citations

Citations are spoken as plain text at the end in a short "sources" statement.

**Inline written format:** " (UAE FDL 33/2021 art 10) "

**Voice format:** " under Article 10 of the UAE employment law " — then deliver citations at the end: "Source: UAE Federal Decree-Law 33 of 2021, Article 10."

Tables become a brief comparative statement: "In the UAE, notice is 30 days. In KSA, it is also 30 days. In Lebanon, it depends on the contract."

#### Rule 4: Confidence signal by phrase, not icon

Written/mobile output may use emoji confidence signals. Voice output uses spoken equivalents:

- **High confidence:** "This is well-established law."
- **Moderate confidence:** "This is generally the rule, but it depends on the specific facts."
- **Low confidence:** "This area is uncertain—you should check with a lawyer before acting."

### Step 2 — Follow the voice delivery structure

Use this template for every voice output:

```
[One-sentence answer]
[Brief explanation: 2–4 sentences maximum]
[One key caveat if needed]
[Source reference in plain language]
[Offer to expand]
```

**Example:**

> "Under UAE law, a maximum notice period of 30 days applies for employees with under five years of service. The rule is in the 2021 employment law. If the contract says more, the contract governs. Source: UAE Federal Decree-Law 33 of 2021, Article 43. Want the full breakdown?"

### Step 3 — Respect length limits

| Content type | Voice limit |
|---|---|
| Direct answer to a legal question | 60–90 seconds of speech (~150–225 words) |
| Summary of a document | 90–120 seconds (~225–300 words) |
| Full advice (voice briefing) | 3 minutes maximum (~450 words); offer a written follow-up |

Beyond these limits, pause and ask: "Want me to continue, or would a written version be more useful?"

### Step 4 — Handle Arabic / multilingual voice output

For Arabic-language voice delivery:
- Use formal Modern Standard Arabic (MSA), not colloquial
- Avoid transliterated legal terms where Arabic equivalents exist
- Number articles in spoken form: "Article Ten" not "Art. 10"
- Read dates in Gregorian format unless the audience specifically expects Hijri

### Step 5 — UI/UX and frontend implementation (when design work is in scope)

When this skill is invoked for interface design, UX review, accessibility, responsive layouts, design systems, or frontend implementation:

1. **Collect inputs:** target users, primary task, platform, viewport range, existing design system, accessibility requirements, brand constraints, data density, interaction states, success metric. Ask for screenshots or reference URLs when visual fidelity matters.
2. **Start from the user task and information architecture**, not decoration.
3. **Map key states:** empty, loading, success, error, disabled, permission-limited, offline, and responsive variants.
4. **Apply accessibility requirements early:** keyboard flow, focus visibility, labels, contrast, reduced motion, touch targets, text resizing, and semantic structure.
5. **Use design-system primitives** where available; otherwise define tokens for spacing, color, type, elevation, radius, and motion.
6. **Design responsive layouts** with stable dimensions and no text overlap across desktop and mobile.
7. **Validate with realistic content:** long labels, error text, touch/keyboard interaction.
8. **Deliver concrete implementation guidance**, not vague aesthetic notes.

**Output format for UI/UX tasks:** Return a design or implementation plan with user goal, layout structure, component list, states, accessibility checks, responsive behavior, copy notes, and verification steps. For code tasks, include exact files/components and testing guidance.

## Pitfalls

- **Reading out Markdown formatting.** Never speak "double asterisk bold double asterisk." Strip all formatting markers before TTS delivery.
- **Listing multiple citations inline.** Consolidate all citations into a single "Source:" statement at the end.
- **Using acronyms without spelling them out.** First mention must expand: "the DIFC—that's the Dubai International Financial Centre."
- **Delivering tables as tables.** Convert every table to a spoken comparison before output.
- **Exceeding length limits without offering an exit.** Always pause and offer a written version when approaching the 3-minute ceiling.
- **Nested clauses surviving into voice output.** Any clause that qualifies a qualification must be flattened into a separate sentence.
- **Conflicting UI/UX requirements.** Prioritize usability, accessibility, and product fit over novelty. If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant.
- **Ornamental drift in styling.** Styling must follow the app's existing design system and avoid decorative additions that serve no functional purpose.

## Verification

### Voice output checklist

1. **Sentence length:** No sentence exceeds 15 words. Count any sentence that feels long.
2. **No nested clauses:** Read aloud—if you lose the thread, rewrite.
3. **No inline citations:** All references appear only in the final "Source:" statement.
4. **No tables:** Any tabular data has been converted to spoken comparisons.
5. **No Markdown artifacts:** No asterisks, pipes, brackets, or formatting syntax would be read aloud.
6. **Acronyms expanded:** Every acronym is spelled out on first use.
7. **Confidence signal present:** A spoken confidence phrase appears where appropriate.
8. **Length within limits:** Word count is within the applicable limit (150–225 for direct answers, 225–300 for summaries, max 450 for full briefings).
9. **Offer to expand:** The output ends with an offer to continue or provide a written version.

### UI/UX checklist (when design work is in scope)

1. User can complete the core task quickly and repeatedly.
2. UI supports keyboard, screen readers, visible focus, and sufficient contrast.
3. Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
4. Controls use familiar affordances and expose state clearly.
5. Motion is purposeful and respects `prefers-reduced-motion`.
6. Visual direction is intentional and consistent with the product domain.
7. All states are implemented: empty, loading, success, error, disabled, validation, permission, offline, long-content.
8. Verification steps are specific enough for an engineer to run.

## Examples

### Legal question (direct answer, voice format)

> "Yes, a non-compete can be enforced in the UAE. But it must meet four tests. It must be limited in scope. It must cover a specific area. It must not exceed two years. And it must protect a real business interest. Source: UAE Federal Decree-Law 33 of 2021, Article 10. Want the details?"

### Document summary (voice format)

> "This contract has three key risks. First, the liability cap is very low. Second, the termination notice is only seven days. Third, there's no cap on indirect damages. Source: Sections 8, 12, and 15 of the agreement. Want me to draft suggested edits?"

## Related skills

- [[output-mobile-friendly-short]]
- [[output-partner-memo-style]]
- [[output-irac-structure]]
- [[output-inline-citations-with-pinpoints]]
