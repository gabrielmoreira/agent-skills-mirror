---
version: "1.0.0"
date: 2026-07-15
---

# Persona Scoring Rubric

Reference for PHASE 3 — SCORE. The 100-point rubric, the brownfield label-mapping table, and
the per-subagent / per-action sub-scoring rules. SKILL.md keeps the SCORE phase procedure
(entry points, extraction walk, recommendations, exit); the detail lives here.

## Brownfield label mappings

When scoring existing agent instructions, map by substance, not label. Mark inferred mappings:
"inferred — [source label]." Absence of a framework concept ≠ zero score; score what's present.

| If you find... | It likely maps to... |
|---|---|
| "Personality," "communication principles," "voice guidelines" | Identity traits |
| "Communication rules," "response guidelines," "style guide" | Dimension selections |
| "Banned phrases," "forbidden phrases," "don't say" | Never-Say List |
| "Vocabulary," "terminology," "glossary" | Lexicon |
| "Tone rules," "emotional guidelines" | Tone Flex / Tone Boundaries |
| "Example responses," "sample language," "approved phrases" | Phrase Book |

## 100-Point Rubric

| Category | Points | Criteria |
|---|---|---|
| **Identity Coherence** | /11 | Traits distinct + behaviorally defined • Personification clear and consistent • Negative Identity (2-4) • Design Inputs coherent (audience → register, channel → chatting style, company → frame of reference) |
| **Dimension Consistency** | /11 | Each of 14 dimensions coherent with Identity, constraints respected • Tone Boundaries consistent with Emotional Coloring/Empathy; Tone Flex within range • Chatting Style adapted for channel |
| **Internal Consistency / Conflict-Pair Check** | /10 | No contradictions between Tone Boundaries and Phrase Book entries • Never-Say doesn't overlap Lexicon • Emotional Coloring + Humor compatible • Identity traits aligned with dimension selections • Immutable content not contradicted by lexicon |
| **Behavioral Specificity** | /9 | Concrete behavioral examples, testable rules • Never-Say ≥5 covering chatbot filler + register violations + cognitive markers + persona-specific • Lexicon populated, immutable distinguished where applicable • Brand input extraction depth |
| **Phrase Book Behavioral Coverage** | /11 | Phrases for the situations the agent will actually encounter (acknowledgement, affirmation, redirect, escalation if external, etc.) • 2-4 per applicable category • Match register and dimensions • For Talking Systems: depersonalized phrasing expected |
| **Tone Flex & Boundaries** | /9 | Triggers + shift directions + magnitudes defined • Content-sensitivity default present (or overridden) • Tone Boundaries testable • Flex range stays within boundaries |
| **Lexicon & Vocabulary** | /7 | Global lexicon populated • Per-subagent lexicon where applicable (brownfield) • Reading Level appropriate for audience • Immutable terms preserved • Lexicon format appropriate |
| **Static Messages** | /7 | Welcome reflects Identity + Register + Voice + Tone + Brevity • Error reflects Formality + Warmth + Coloring + Brevity • All static strings sound like the same agent • Telephony: AI disclosure in welcome, brevity recalibrated • SMS: first-message welcome with system identification |
| **Business Context Alignment** | /7 | Goals and metrics inform design • Persona supports objectives • Audience demographics reflected |
| **Sample Quality / Scenario Coverage** | /9 | Persona recognizable without seeing dimension table • Happy path + uncertainty + boundary + escalation scenarios • Channel-appropriate • Brand vocabulary appears naturally |
| **Completeness** | /9 | All framework sections addressed • Values only if user-provided • No gaps where the framework expects a deliberate decision |

(Total: 100. Conflict-Pair Check is new in this version. Phrase Book and Sample categories tightened to grade behavioral coverage / scenario coverage rather than category counts / aesthetics.)

**Score presentation:** Total presented as percentage — 90-100 production-ready, 75-89 strong
foundation, 50-74 needs revision, <50 significant gaps.

## Per-Subagent and Per-Action Sub-Scoring (brownfield)

For each subagent in the source `.agent` file:
- Persona reminder present in `reasoning.instructions`?
- Tone flex calibrated appropriately for the subagent's purpose (e.g., escalation subagent should drop humor)?
- Lexicon scoped correctly (subagent-specific terms in `reasoning.instructions`, not in global)?

For each action:
- `progress_indicator_message` in voice if channel is voice-bearing?
- Tone-appropriate ("Pulling the numbers..." for casual; "One moment..." for formal)?

Roll up per-layer scores into the overall total with a per-layer breakdown in the output.
