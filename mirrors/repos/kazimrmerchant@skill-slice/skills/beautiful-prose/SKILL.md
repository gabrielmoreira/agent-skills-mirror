---
name: beautiful-prose
description: "Applies a hard English prose contract: concrete nouns, varied sentence length, banned em dashes, reversal pivots, filler transitions, and therapeutic cadence. Use when the user wants essays, literary rewrites, punchy long-form, or text free of AI tells. Not for UI microcopy, YAML skill descriptions, marketing slogans, or code comments."
version: 1.0.1
risk: unknown
source: community
---

# Beautiful Prose

A hard-edged writing skill for producing timeless, forceful English prose without modern AI tics.

This is a style contract, not a vibe. Treat violations as failures.

## When to Use

- The user requests prose or rewrites with strong style discipline and no generic AI cadence.
- The task involves essays, literary-style writing, sharp rewrites, or exacting English prose.
- The user wants a forceful, concrete voice instead of friendly assistant-style copy.
- Trigger keywords: "beautiful prose," "rewrite this," "make it punchy," "clean up my writing," "essay," "literary style," "no AI tone," "forceful prose."

## Prerequisites

- None. This is a pure style contract with no external dependencies, scripts, or API calls.
- Optional: review the Examples section (banned vs allowed) before finalizing any long-form output (over 300 words).

## Procedure

### 1. Activate the skill

When the user invokes this skill (or when the task clearly matches the trigger keywords above), apply the full style contract below. Do not announce that the skill is active. Produce prose only.

### 2. Parse optional control tags

If the user provides control tags before their request, honor them. If absent, use defaults.

| Tag | Values | Default |
|-----|--------|---------|
| `REGISTER` | `founding_fathers` \| `literary_modern` \| `cold_steel` \| `journalistic` | `literary_modern` |
| `DENSITY` | `lean` \| `standard` \| `dense` | `standard` |
| `HEAT` | `cool` \| `warm` \| `hot` | `warm` |
| `LENGTH` | `micro` \| `short` \| `medium` \| `long` | (from request) |

Example invocation:

```
Apply the Beautiful Prose skill.
REGISTER: literary_modern
DENSITY: dense
HEAT: cool
Write a 700 word essay on why discipline beats motivation.
```

### 3. Apply absolute prohibitions

Every one of the following is a hard failure. If any appear in output, rewrite before delivering.

**Em dashes.** Ban `--` used as em dashes. Use periods, commas, colons, semicolons, or line breaks instead.

**"It's not X, it's Y" constructions.** Ban the pattern and all masked variants:
- "This isn't about X. It's about Y."
- "Not X but Y."
- "X is a symptom. Y is the cause." (when used as a cheap reversal)
- "The real story is Y." (when it is only a pivot)

**Filler transitions and scene-setting.** Ban these phrases and their close cousins:
- "At its core"
- "In today's world"
- "In a world where"
- "That said"
- "Let's explore"
- "Ultimately"
- "What this means is"
- "It's important to note"
- "On the one hand"

**Therapeutic or validating language.** Ban:
- "I hear you"
- "That sounds hard"
- "You're valid"
- "Give yourself grace"
- "Be kind to yourself"

**AI tells and meta commentary.** Ban:
- "In this essay"
- "This piece explores"
- "As a writer"
- "We will discuss"
- "Here are the key takeaways"
- Any apology for style or capability

**Symmetry padding.** Ban:
- Balancing sentences for the sake of balance.
- Three-part lists unless earned.
- "X, Y, and Z" as decoration.

### 4. Apply positive constraints

**Sentence craft.**
- Prefer declarative sentences.
- Vary length aggressively.
- Use short sentences as impact.
- Questions are allowed only when they cut.

**Word choice.**
- Prefer concrete nouns to abstractions.
- Prefer strong verbs to adverbs.
- Prefer Anglo-Saxon weight when possible.
- Use Latinate precision only when it buys accuracy.

**Rhythm and structure.**
- Paragraphs should breathe.
- White space is intentional.
- Open with substance, not a hook.
- Close cleanly without summary.
- Do not restate the thesis.

**Authority.**
- Write as if truth does not need permission.
- Avoid hedging unless uncertainty is essential and explicit.
- Do not posture. Do not moralize.

### 5. Apply the selected register

**`founding_fathers`** — formal, spare, civic gravity. Balanced syntax, but not decorative. Moral clarity without sermon.

**`literary_modern`** (default) — vivid, lean imagery. Controlled heat, sharp observation. Minimal ornament.

**`cold_steel`** — severe compression. Punchy, unsentimental. High signal, low warmth.

**`journalistic`** — crisp, factual, narrative clarity. Clean momentum. No clickbait cadence.

### 6. Run the internal quality check

Before finalizing, check internally:
- Remove any line that sounds like it was assembled from templates.
- Remove any sentence that merely repeats the previous one.
- Remove any sentence that exists to guide the reader's emotions.
- Ensure every paragraph advances meaning.

If quality is uncertain, write less. Silence beats slop.

### 7. Format output

- Plain text prose by default.
- No headings unless requested.
- No bullet points unless requested.
- If the user requests bullets, keep them taut and non-corporate.

## Examples

### Banned vs. allowed

**Bad (banned reversal):** "This isn't about money. It's about power."

**Good:** "Money is the instrument. Power is the habit."

**Bad (filler):** "At its core, this is a complex issue. That said, in today's world..."

**Good:** "It is complex. Complexity is not an excuse for fog."

## Pitfalls

- **Em dashes slip in during long sentences.** The longer the sentence, the more likely an em dash appears as a shortcut. Break the sentence instead.
- **Reversal pivots feel clever but are cheap.** "Not X but Y" is the most common violation. Rewrite as two independent declarations.
- **Filler transitions survive editing because they sound natural.** They are natural to AI output, which is exactly why they are banned. Cut them without replacement.
- **Therapeutic tone leaks into conclusions.** Endings are the most common place for "give yourself grace" or "be kind to yourself" to appear. Close cleanly without summary or comfort.
- **Symmetry padding masquerades as structure.** A three-part list feels organized but is often decoration. Cut unless every item earns its place.
- **Five consecutive sentences of similar length.** This is a cadence tell. Vary aggressively. Short sentences as impact.
- **Meta commentary in openings.** "In this essay, I will..." is the most common opening violation. Open with substance, not a roadmap.

## Verification

Before delivering output, run this manual lint checklist. Fail the output if any condition is true:

1. Contains `--` used as an em dash.
2. Contains a reversal pivot pattern ("not X, Y" or any masked variant).
3. Contains any filler transition from the banned list.
4. Contains therapy language or validation phrases.
5. Contains meta writing talk ("this essay," "we will," "this piece explores").
6. Contains five consecutive sentences of similar length.
7. Contains symmetry padding (decorative three-part lists, balancing sentences with no new meaning).
8. Restates the thesis in the closing paragraph.
9. Opens with a hook rather than substance.

For long-form output (over 300 words), cross-check against the Examples section in this skill for known pass/fail patterns before delivering.

## Related skills

- None currently. This skill is self-contained and does not depend on other agent-skills library entries.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
