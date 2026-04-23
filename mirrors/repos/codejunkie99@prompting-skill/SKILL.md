---
name: prompting
version: 2026-04-22
triggers: ["write a prompt", "prompt engineering", "improve this prompt", "system prompt", "few-shot", "prompt template"]
tools: [bash, memory_reflect]
preconditions: []
constraints: ["do not invent capabilities the model lacks", "do not promise deterministic output from a stochastic model", "every claim in output must trace to source data in the prompt"]
---

# Prompting — building reliable LLM prompts

Use when drafting or refining a prompt for Claude (or any LLM) and reliability
matters more than cleverness. Distilled from production patterns for
document/form analysis and agent workflows.

## The five load-bearing rules

1. **State task, role, goal upfront.** One paragraph. No warm-up.
2. **Separate dynamic content from instructions.** Inject user data between
   XML-style delimiters (`<form>`, `<sketch>`, `<data_to_analyze>`).
3. **Give step-by-step instructions.** Ordered list. One action per step.
4. **Few-shot the tricky cases, not the easy ones.** Bake in human-labeled
   reasoning traces for edge cases the model otherwise fumbles.
5. **Repeat critical constraints at the end.** Recency wins when the model
   chooses what to obey.

## Structure a production prompt in this order

1. **System prompt (stable, cacheable):** role, goal, static domain knowledge
   (form schema, row meanings, how the data is produced), output format spec.
   This content does not change per request — mark it for prompt caching.
2. **Few-shot examples:** 2–4 cases. Prefer edge cases with the ideal reasoning
   steps written out, not just input→output pairs.
3. **User turn (dynamic):** the data to analyze, wrapped in named XML tags.
4. **Final reminder:** 3–5 bullets re-asserting the non-negotiables
   (no fabrication, cite source data, handle uncertainty).
5. **Pre-filled assistant turn:** start the response with the opening token of
   the required format (`{`, `<final_verdict>`, etc.) to lock structure.

## Anti-hallucination checklist

- [ ] Prompt tells the model to only state what it can confidently assess.
- [ ] Prompt specifies what to do when not confident (abstain, return `null`,
      emit `"uncertain"` — pick one and name it).
- [ ] Prompt orders the reasoning: factual/structured data *before* ambiguous
      data. Use the form to interpret the sketch, never the reverse.
- [ ] Every factual claim in the output must cite a span from the source.
- [ ] Final reminder re-states "do not invent details."

## Output format

- For programmatic downstream use: request JSON with a named schema.
- For human-extractable answers: wrap the key field in a unique tag
  (`<final_verdict>...</final_verdict>`).
- Pre-fill the assistant turn with the opening delimiter — this is the single
  highest-leverage trick for format compliance.

## Worked examples

**Bad — leaks instructions and data together:**
```
Look at this form and tell me if the signature matches: [image bytes]
Also be careful about fake ones.
```

**Good — structured, cacheable, bounded:**
```
System: You verify signatures on tax form TF-104. The form has 12 rows;
row 11 is the declarant signature. Humans fill this by hand — expect
smudges, off-center marks, and partial overlaps with row 12. Output
JSON: {"match": bool, "confidence": 0-1, "evidence": string}.
If confidence < 0.7, return "match": null.

<examples>...</examples>

User: <form_image>...</form_image> <reference_signature>...</reference_signature>

Reminder: cite the row and pixel region for every claim. Do not invent
details not visible in the image. If row 11 is illegible, return null.

Assistant (pre-filled): {"match":
```

## Failure mode logged

One ambiguous-sketch prompt interpreted the sketch *before* the form,
propagating a wrong label into downstream fields. Fix: hardcode the
reading order in step instructions — factual/structured data first,
ambiguous data second, always.

## Self-rewrite hook

After every 5 prompts authored with this skill, or on any reported
hallucination / format miss:
1. Read the last 5 prompting entries from episodic memory.
2. If a new failure class appears (e.g., tool-use prompts need different
   structure than extraction prompts), add a section; do not rewrite
   existing sections unless two independent failures agree.
3. Commit: `skill-update: prompting, <one-line reason>`.