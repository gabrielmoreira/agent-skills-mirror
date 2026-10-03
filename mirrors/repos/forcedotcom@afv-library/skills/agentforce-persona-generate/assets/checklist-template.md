---
version: "1.0.0"
date: 2026-05-15
---

# Persona Completeness Checklist — {{AGENT_NAME}}

> Date: {{DATE}}
> Generated from: `{{agent-name}}-persona.md`
> Mode: {{greenfield | brownfield}}

**Legend:** `[+]` present · `[-]` missing or required-but-empty · `—` not applicable / optional and not provided

One-line definitions are pulled from `references/persona-framework.md`. The checklist is the framework's coverage map applied to this persona — not opinions about quality. (For quality, run SCORE.)

---

## Identity (anchor)

- {{[+] | [-]}} **Identity Traits** — 3-5 adjectives that anchor every other decision.
- {{[+] | [-]}} **Negative Identity** — Character-level anti-patterns ("not a salesperson"). Auto-generates from Identity Traits — re-run DRAFT step 3 if missing.
- {{— | [+]}} **Values** — *(optional, explicit-input only)* What the agent believes; worldview and motivational core.

## Context

- {{[+] | [-]}} **Channel** — Single channel choice (web chat, SMS, telephony, etc.). Constrains Brevity defaults and rich-text features.
- {{[+] | [-]}} **Company / Brand** — Who the organization is.
- {{[+] | [-]}} **Audience** — employees / customers / partners / mixed.
- {{[+] | [-]}} **Use case(s)** — at least one. Drives REFINE's sample dialog scenarios; the dialog will be weak without this.
- {{— | [+]}} **Business goals + success metrics** — *(optional)* What the agent achieves and how success is measured.
- {{— | [+]}} **Regulated industry flag** — *(optional)* Triggers stricter handling of immutable content.

## Personification + Naming

- {{[+] | [-]}} **Personification** — Talking System / Familiar Thing / Personal Assistant. The first dimension on the Identity-anchored chain.
- {{[+] | [-]}} **Name decision** — named / unnamed / brand-as-name. ENCODE blocks if this is `pending`.
- {{[+] | — | [-]}} **Display name** — Required if `name_decision = named`.

## Dimensions (13)

- {{[+] | [-]}} **Register** — Subordinate / Peer / Advisor / Coach.
- {{[+] | [-]}} **Formality** — Casual / Informal / Professional / Formal.
- {{[+] | [-]}} **Warmth** — Cool / Neutral / Warm / Bright / Radiant.
- {{[+] | [-]}} **Personality Intensity** — Reserved / Moderate / Bold.
- {{[+] | [-]}} **Reading Level** — Plain / Conversational / Mid / Advanced (or Match).
- {{[+] | [-]}} **Emotional Coloring** — Blunt / Neutral / Encouraging / Clinical / etc.
- {{[+] | [-]}} **Empathy Level** — Minimal / Moderate / Attuned.
- {{[+] | [-]}} **Brevity** — Terse / Concise / Moderate / Expansive. *(Default bound to channel.)*
- {{[+] | [-]}} **Humor** — None / Dry / Light / Playful.
- {{[+] | [-]}} **Emoji** — None / Functional / Expressive.
- {{[+] | [-]}} **Formatting** — Plain / Selective / Heavy.
- {{[+] | [-]}} **Punctuation** — Conservative / Standard / Expressive.
- {{[+] | [-]}} **Capitalization** — Standard / Casual.

## Verbal fingerprint

- {{[+] | [-]}} **Phrase Book** — Situation-keyed sample phrases (acknowledgements, redirects, etc.). 2-4 per applicable category. *Categories filled: {{N}} of {{Total applicable}}.*
- {{[+] | [-]}} **Never-Say List** — Phrase-level prohibitions (≥5 entries). *Entries: {{N}}.*
- {{[+] | [-]}} **Discourse Markers** — Conversational connectors ("So," "Right," "Here's the thing").
- {{[+] | [-]}} **Lexicon (global)** — Brand and domain vocabulary used everywhere.
- {{— | [+]}} **Lexicon (per-subagent)** — *(brownfield or when subagents declared)* Subagent-specific vocabulary.
- {{— | [+]}} **Immutable content** — *(when domain warrants)* Legal/brand-defined content preserved verbatim.

## Boundaries

- {{[+] | [-]}} **Tone Boundaries** — Anti-sounds ("never sound apologetic"). Auto-generated from Identity.
- {{[+] | [-]}} **Tone Flex** — Triggers + shift directions + magnitudes (system state, content sensitivity, etc.).
- {{— | [+]}} **Guardrails** — *(optional)* Content-level boundaries ("Don't offer medical advice"). Distinct from Never-Say. Only relevant when domain is regulated or brand-bounded.

## Subagent / action calibrations *(only if applicable)*

- {{— | [+]}} **Per-subagent persona adjustments** — *(only when subagents exist)* e.g., "drop humor to zero in escalation."
- {{— | [+]}} **Per-action loading text** — *(only when actions exist + voice channel)* `progress_indicator_message` strings.

## Channel-specific

- {{— | [+]}} **Voice selection** — *(telephony or multimodal-with-audio)* Voice from catalog with fine-tuning starting points.
- {{— | [+]}} **AI disclosure in welcome** — *(telephony)* Required for trust and compliance.
- {{— | [+]}} **Pronunciation dictionary** — *(voice channels, when brand terms have non-obvious pronunciation)*.

---

## Summary

- **{{N}} of {{Total}}** required elements present.
- **{{Optional applicable}} of {{Optional total}}** optional-but-applicable elements present.

### Suggested next steps

(Each is **quotable** — paste any of these back to the skill to take the action.)

1. **"go to NAME"** — *(if name_decision pending)*
2. **"go to FILL OUT, add Lexicon"** — *(if Lexicon empty)*
3. **"go to FILL OUT, expand Phrase Book"** — *(if Phrase Book has fewer than 2 phrases per applicable category)*
4. **"go back to DRAFT, capture use case"** — *(if no use case captured)*
5. **"go to ADJUST"** — *(if subagents declared but not calibrated)*
6. **"run SCORE"** — *(if all required elements [+] and you want a quality assessment)*
7. **"run ENCODE"** — *(if all required elements [+] and SCORE is passing)*

Pick what's most leveraged for your next move. The hub will route you.
