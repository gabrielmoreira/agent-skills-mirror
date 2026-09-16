# AI & Agent UX

> **Skip this reference if the design shows no AI, LLM, agent, chat, citation, or model-output surfaces.**

Craft in AI surfaces is the difference between a model that feels considered and one that feels duct-taped. It lives in the visual rhythm of a multi-step progress timeline, the restraint of a "thinking" indicator that respects screen real estate, the elegance of an inline citation marker, and the quiet confidence of reasoning that sits subordinate to the answer. This reference judges the visual and behavioral craft of agent progress, disclosure, reasoning, confidence, citations, and review surfaces.

## Why this matters

AI features are where craft becomes load-bearing — users decide in seconds whether to trust output, and that decision rests almost entirely on visual signals. When craft is high, the interface feels like it understands its own limits: progress is shown with precision, citations sit close to the claim they support, confidence is conveyed without drama, and reasoning collapses politely until invited. When craft is low, AI surfaces feel either showy (every token streaming, walls of "thinking", verbose tool logs) or evasive (no provenance, no progress, no way out). The visual treatment of AI is where the product proves it has thought about how the model fits into a human's workflow.

---

## Agent Progress

- **The work is visible as a timeline.** Each step has a status the user can read at a glance — pending, active, complete. A vague "thinking..." for thirty seconds reads as the product hiding from itself. Tool use is named, not narrated; verbose logs read as developer output left in production.
- **Stop is always available, and the input area stays alive.** The user can interrupt and clarify mid-flight. On completion, progress collapses politely — a summary remains, the scaffolding recedes. Failure preserves what was done.

## Disclosure

- **AI is unmistakable in conversation.** A distinct avatar or label tells the user when they're talking to a model rather than a person. Ambiguity here is a small ethical breach.
- **AI-generated content carries a persistent signal until reviewed.** Handoffs between AI and human agents are clear. An escape to a human is always reachable.

## Reasoning

- **Reasoning is subordinate to the answer.** The result leads; the explanation sits quietly below or behind a click. A wall of reasoning above the answer reads as showing off. Default is short; depth is on demand.
- **Tool invocations are collapsible.** What was called and what came back, summarized; full output one click away. Raw model internals stay out of production.

## Confidence

- **Confidence is communicated without drama.** A simple visual register beats a percentage. Numeric confidence reads as false precision to most users. The source of uncertainty is named when possible. High-stakes outputs prompt review.

## Citations

- **Claims and their sources sit close together.** A citation marker right after the claim, not collected at the bottom. Markers are subtle but reachable. Sources are specific — page, section, timestamp — not just a document name.
- **Quoted text and AI interpretation look different.** Source quality is visible — recency, authority, primary versus user-generated. Conflicts between sources are surfaced rather than hidden. Cited links go directly to the source.

## Human Review

- **High-stakes AI output goes through a human gate.** Irreversible or third-party-affecting actions pause for explicit approval. The review queue presents proposed action, context, confidence, reasoning, and approve/reject/edit in one view.
- **Override is easy and unjudged.** No dark pattern friction punishes the human for disagreeing with the model. Batch approval exists but never defaults to "approve all."

---

## Scoring Guide

**Contributes to dimensions: Useful, Reliable, Coherent**

| Score | Criteria |
|-------|----------|
| 9-10 | The AI surface understands its own limits. Progress reads at a glance, citations sit near their claims, confidence is communicated without drama, and review gates handle the high-stakes work. |
| 7-8 | AI disclosure is present. Confidence and citations are mostly consistent. |
| 5-6 | Vague "thinking" indicators. Citations missing or batched. Confidence over-hedged or unstated. |
| 3-4 | The AI is a black box. No disclosure. Citations absent or misleading. |
| 1-2 | No disclosure. No guardrails. Outputs presented as fact without sources. |
