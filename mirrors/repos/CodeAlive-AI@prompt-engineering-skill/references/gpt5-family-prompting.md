# GPT-5 Family Prompting Guide

Covers GPT-5, GPT-5.1, and GPT-5.2. Based on official OpenAI Cookbook guides and production patterns.

Sources:
- [GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [GPT-5.1 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5-1_prompting_guide)
- [GPT-5.2 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5-2_prompting_guide)

## Model Comparison

| Aspect | GPT-5 | GPT-5.1 | GPT-5.2 |
|--------|-------|---------|---------|
| Default reasoning_effort | `medium` | `medium` | `none` |
| Reasoning levels | low/medium/high + `minimal` | low/medium/high + `none` | none/minimal/low/medium/high/`xhigh` |
| Key strength | Agentic eagerness control | Calibrated token consumption | Enterprise accuracy & instruction following |
| Verbosity | Steerable | Can be excessively concise | Concise by default, prompt-sensitive |
| Tool calling | Improved vs GPT-4 | Named tools (apply_patch, shell) | Best structured reasoning & grounding |
| API | Responses API + Chat Completions | Responses API (preferred) | Responses API (preferred) |

## Reasoning Effort Parameter

Controls thinking depth before the final answer.

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Your prompt here",
    reasoning={"effort": "medium"}
)
```

| Level | Use Case | Notes |
|-------|----------|-------|
| `none` | Formatting, classification, simple Q&A | No reasoning tokens; similar to GPT-4.1/4o. Supports hosted tools (web search, file search) |
| `minimal` | Latency-sensitive; GPT-4.1 migration | Fastest reasoning mode. Performance varies more with prompt quality |
| `low` | Simple straightforward tasks | Speed-oriented |
| `medium` | General purpose (default for GPT-5) | Balanced |
| `high` | Complex multi-step reasoning | Accuracy over speed |
| `xhigh` | Hardest problems (GPT-5.2 only) | Maximum depth |

### Tips for `minimal` / `none` reasoning

When reasoning is minimal, compensate with explicit prompt structure:
- Add brief explanation summarizing thought process at answer start
- Write thorough, descriptive tool-calling preambles
- Maximize disambiguation of tool instructions
- Add explicit agentic persistence reminders
- Prompt planning at task beginning

```
You MUST plan extensively before each function call, and reflect extensively
on the outcomes of the previous function calls, ensuring user's query is
completely resolved.
```

### Migration Mapping

| Source Model | Target → GPT-5.2 | Notes |
|---|---|---|
| GPT-4o / GPT-4.1 | `none` | Fast/low-deliberation; increase only if evals regress |
| GPT-5 | Same, except `minimal` → `none` | GPT-5 default is `medium` |
| GPT-5.1 / GPT-5.2 | Same value | GPT-5.2 default is `none` |

## Agentic Eagerness Control

GPT-5 is trained to operate along the full control spectrum. Steer via prompts.

### Less Eager (Precise, Fast)

```xml
<context_gathering>
Goal: Get enough context fast. Parallelize discovery and stop as soon as you can act.

Method:
- Start broad, then fan out to focused subqueries.
- In parallel, launch varied queries; read top hits per query.
- Avoid over-searching. If needed, run targeted searches in one parallel batch.

Early stop criteria:
- You can name exact content to change.
- Top hits converge (~70%) on one area/path.

Loop:
- Batch search → minimal plan → complete task.
- Search again only if validation fails or new unknowns appear.
</context_gathering>
```

### More Eager (Autonomous, Thorough)

```xml
<persistence>
- You are an agent — keep going until the user's query is completely resolved.
- Only terminate your turn when the problem is solved.
- Never stop when you encounter uncertainty — research or deduce the most
  reasonable approach and continue.
- Do not ask the human to confirm assumptions — decide what is most reasonable,
  proceed, and document for the user's reference after finishing.
</persistence>
```

### Fixed Tool Call Budget

```xml
<context_gathering>
- Search depth: very low
- Bias strongly towards providing a correct answer as quickly as possible.
- Usually, an absolute maximum of 2 tool calls.
- If you need more time, update the user with findings and open questions.
</context_gathering>
```

## Verbosity Control

### API Parameter

GPT-5+ supports a `verbosity` API parameter controlling final answer length (not thinking length). Supports natural-language overrides in prompts for context-specific deviations.

### Prompt-Level Control

```xml
<output_verbosity_spec>
- Default: 3–6 sentences or ≤5 bullets for typical answers.
- Simple "yes/no + short explanation" questions: ≤2 sentences.
- Complex multi-step or multi-file tasks:
  - 1 short overview paragraph
  - then ≤5 bullets: What changed, Where, Risks, Next steps, Open questions.
- Avoid long narrative paragraphs; prefer compact bullets and short sections.
- Do not rephrase the user's request unless it changes semantics.
</output_verbosity_spec>
```

### Coding Agent Verbosity (GPT-5.1 Pattern)

```xml
<final_answer_formatting>
- Tiny/small change (≤~10 lines): 2–5 sentences or ≤3 bullets. No headings.
- Medium change (single area / few files): ≤6 bullets or 6–10 sentences.
  At most 1–2 short snippets (≤8 lines each).
- Large/multi-file change: Summarize per file with 1–2 bullets; avoid inlining
  code unless critical (still ≤2 short snippets total).
- Never include before/after pairs, full method bodies, or scrolling code blocks.
- No build/lint/test logs unless requested or blocking.
</final_answer_formatting>
```

## Tool Calling Patterns

### Tool Preambles (GPT-5+)

GPT-5 is trained to provide upfront plans and progress updates. Steer their frequency and style:

```xml
<tool_preambles>
- Begin by rephrasing the user's goal clearly before calling any tools.
- Outline a structured plan detailing each logical step.
- As you execute, narrate each step succinctly and sequentially.
- Finish by summarizing completed work distinctly from upfront plan.
</tool_preambles>
```

### Tool Usage Rules

```xml
<tool_usage_rules>
- Prefer tools over internal knowledge for fresh or user-specific data.
- Parallelize independent reads (read_file, fetch_record, search_docs).
- After write/update calls, restate: what changed, where (ID/path), validation performed.
</tool_usage_rules>
```

### Named Tools (GPT-5.1+)

GPT-5.1 introduced named tool types: `apply_patch` and `shell`. Using named tools decreased apply_patch failure rates by 35%.

```python
response = client.responses.create(
    model="gpt-5.1",
    input=RESPONSE_INPUT,
    tools=[{"type": "apply_patch"}]
)
```

### Parallel Tool Calling

Issue multiple tool calls simultaneously for speed. Encourage explicitly:

```
Parallelize tool calls whenever possible. Batch reads (read_file) and
edits (apply_patch) to speed up the process.
```

### Context Preservation (Responses API)

Use `previous_response_id` to pass reasoning between turns. Preserves CoT tokens and eliminates plan reconstruction after tool calls.

Measured improvement: Tau-Bench Retail 73.9% → 78.2%.

## User Updates / Preambles

### GPT-5.2 (Concise)

```xml
<user_updates_spec>
- Send brief updates (1–2 sentences) only when:
  - Starting a new major phase of work, or
  - Discovering something that changes the plan.
- Avoid narrating routine tool calls.
- Each update must include at least one concrete outcome.
- Do not expand scope beyond what was asked.
</user_updates_spec>
```

### GPT-5.1 (Detailed)

```xml
<user_updates_spec>
- Send short updates (1–2 sentences) every few tool calls.
- Post an update at least every 6 execution steps or 8 tool calls.
- If expecting longer heads-down stretch, post a brief note with why and when.
- Before the first tool call, give a quick plan with goal, constraints, next steps.
- Always state at least one concrete outcome since prior update.
- End with a brief recap and follow-up steps.
- Include a brief checklist of planned items with status: Done or Closed (with reason).
</user_updates_spec>
```

## Scope Drift Prevention

```xml
<design_and_scope_constraints>
- Implement EXACTLY and ONLY what the user requests.
- No extra features, no added components, no UX embellishments.
- Style aligned to the design system at hand.
- Do NOT invent colors, shadows, tokens, animations, or new UI elements.
- If any instruction is ambiguous, choose the simplest valid interpretation.
</design_and_scope_constraints>
```

## Ambiguity & Hallucination Mitigation

```xml
<uncertainty_and_ambiguity>
- If the question is ambiguous or underspecified:
  - Ask up to 1–3 precise clarifying questions, OR
  - Present 2–3 plausible interpretations with clearly labeled assumptions.
- When external facts may have changed recently:
  - Answer in general terms and state that details may have changed.
- Never fabricate exact figures, line numbers, or external references.
- Prefer "Based on the provided context…" over absolute claims.
</uncertainty_and_ambiguity>
```

### High-Risk Self-Check

```xml
<high_risk_self_check>
Before finalizing answers in legal, financial, compliance, or safety contexts:
- Re-scan for unstated assumptions.
- Check for specific numbers or claims not grounded in context.
- Soften overly strong language ("always," "guaranteed").
- Explicitly state assumptions.
</high_risk_self_check>
```

## Long-Context Handling

```xml
<long_context_handling>
- For inputs >~10k tokens (multi-chapter docs, long threads, multiple PDFs):
  - First, produce a short internal outline of key sections relevant to the request.
  - Re-state user constraints explicitly.
  - Anchor claims to sections ("In the 'Data Retention' section…").
- Quote or paraphrase fine details (dates, thresholds, clauses).
</long_context_handling>
```

## Structured Extraction

```xml
<extraction_spec>
Extract structured data into this exact schema (no extra fields):
{
  "field_name": "string",
  "optional_field": "string | null"
}
- If a field is not present in source, set to null rather than guessing.
- Before returning, re-scan source for missed fields and correct omissions.
</extraction_spec>
```

For multi-file extractions: serialize per-document results separately, include stable IDs (filename, page range).

## Compaction (GPT-5.2)

Loss-aware compression of prior conversation state for long agentic sessions.

```
POST https://api.openai.com/v1/responses/compact
```

Best practices:
- Compact after major milestones, not every turn
- Keep prompts functionally identical when resuming
- Treat compacted items as opaque
- Monitor context usage and plan ahead

## Personality Shaping (GPT-5.1)

```xml
<final_answer_formatting>
You value clarity, momentum, and respect measured by usefulness.
- Adaptive politeness:
  - Warm user → single succinct acknowledgment, then back to work.
  - High stakes → drop acknowledgment, move straight to solving.
- Core: speak with grounded directness. Efficiency is respect.
- Never repeat acknowledgments. Pivot fully to the task.
- Match user's tempo: fast when they're fast, spacious when verbose.
</final_answer_formatting>
```

## Solution Persistence (GPT-5.1)

```xml
<solution_persistence>
- Treat yourself as autonomous senior pair-programmer: gather context, plan,
  implement, test, and refine without waiting for prompts at each step.
- Persist until task is fully handled end-to-end within current turn.
- Be extremely biased for action. If user asks "should we do x?" and your
  answer is "yes" — go ahead and perform the action.
</solution_persistence>
```

## Metaprompting: Debugging System Prompts

### Step 1: Diagnostic

```
Given the system prompt and failure traces, identify:
1) Distinct failure modes (tool_usage_inconsistency, verbosity_vs_concision, etc.)
2) Specific lines causing or reinforcing each failure
3) How those lines steer toward observed behavior
```

### Step 2: Surgical Revision

```
Propose minimal edits to reduce observed issues while preserving good behaviors.
- Clarify conflicting rules
- Remove redundant/contradictory lines
- Make tradeoffs explicit
- Keep structure and length roughly similar
Output: patch_notes + revised_system_prompt
```

## Migration Checklist

1. **Switch model, keep prompt identical** — isolate the variable
2. **Pin reasoning_effort** — match prior model's latency/depth profile
3. **Run evals** — if results are good, ship
4. **If regressions, tune prompt** — adjust verbosity/format/scope constraints
5. **Re-eval after each small change** — one change at a time

### GPT-4.1 → GPT-5 Adjustments

- Remove explicit encouragement to "gather context thoroughly" — GPT-5 is naturally introspective
- Soften maximization language ("THOROUGH" → "if not confident, gather more information")
- Add agentic persistence explicitly ("keep going until resolved")
- Use `verbosity` API parameter in addition to prompt-level controls
- Leverage Responses API with `previous_response_id`

### GPT-5 → GPT-5.1 Adjustments

- Emphasize persistence and completeness (5.1 can be excessively concise)
- Be explicit about desired output detail (5.1 can occasionally be verbose)
- Migrate apply_patch to named tool implementation (35% fewer failures)
- Check for conflicting instructions — 5.1 is excellent at instruction-following

### GPT-5.1 → GPT-5.2 Adjustments

- Clamp verbosity of user updates (shorter, more focused)
- Make scope discipline explicit
- Adjust for default `none` reasoning — set explicit level if depth needed
- Leverage compaction API for long sessions

## Web Research Agent Pattern

```xml
<web_search_rules>
- Act as expert research assistant; default to comprehensive, well-structured answers.
- Prefer web research over assumptions whenever facts may be uncertain.
- Research all parts of the query, resolve contradictions, follow implications.
- Do not ask clarifying questions; cover all plausible user intents.
- Write clearly using Markdown (headers, bullets, tables).
</web_search_rules>
```

### Research Methodology
- Start with multiple targeted searches; use parallel searches
- Begin broad, add targeted follow-ups to fill gaps
- Stop only when: answered every subpart / found concrete examples / found sufficient sources
- Include citations after paragraphs with web-derived claims

### Ambiguity Handling (Without Questions)
State best-guess interpretation plainly, then comprehensively cover the most likely intent. If multiple intents, cover each one fully.
