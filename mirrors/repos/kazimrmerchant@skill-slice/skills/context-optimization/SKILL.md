---
name: context-optimization
version: 1.1.1
description: "Use when improving context efficiency: context budgeting, observation masking, prefix or KV-cache strategy, partitioning, token-cost reduction, retrieval scoping, or extending effective context capacity without lowering answer quality. Load when tool outputs dominate trajectories, cache hit rates are poor, or multi-step sessions approach window limits. Not for diagnosing degradation (context-degradation), designing lossy handoff summaries (context-compression), or explaining attention fundamentals. Action: apply lossless tactics first (KV-cache, masking, scoping), then compaction and partitioning with measured gates. Exception: skip on short low-pressure chats and maximum-fidelity / audit workloads."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Context Optimization

Keep the signal the model needs; shed noise. An optimization that drops a user constraint, error stack, or file path is a **regression**. Measure baseline → one change → measure again.

| Goal | What "good" looks like |
|------|------------------------|
| Capacity | Task finishes without overflow or mid-turn truncation |
| Cost | Lower billed input tokens and cheaper cache hits where supported |
| Latency | Faster TTFT when prefixes stay cacheable |
| Quality | Task success stays within an agreed drop budget (e.g. ≤5%) |

| Path | Role |
|------|------|
| `scripts/compaction.py` | `ObservationStore`, `ContextBudget`, token estimates, `design_stable_prompt`, cache metrics. Run `python scripts/compaction.py` from this skill folder. |
| `references/optimization_techniques.md` | Thresholds, partitioning sketches, monitoring. Load only when the procedure below is not enough. |

## When to Use

- Tool/observation output dominates the trajectory.
- Prefix or KV-cache hit rate is low and a stable prefix exists.
- Retrieval loads many low-relevance documents.
- One window cannot hold the full problem (≥3 independent subtasks).
- Utilization crosses ~70% (plan) or ~80% (act) — see `ContextBudget.should_optimize`.

**Do not use** for:

| Problem | Use instead |
|---------|-------------|
| Why attention/windows behave that way | `context-fundamentals` |
| Lost-in-middle, poisoning, clash | `context-degradation` |
| Structured lossy handoff summaries | `context-compression` |
| Large artifacts that can live on disk | filesystem offload + pointers |

Skip entirely on short low-pressure chats, maximum-fidelity/audit work, and runtimes with no prefix/KV cache (cache ordering buys nothing).

## Prerequisites

- Python 3.10+ to run `scripts/compaction.py`.
- Optional: a runtime with prefix/KV cache (vLLM, TGI, TensorRT-LLM, provider prompt-cache APIs) for Step 2.
- Tokenizer for billing truth (`tiktoken` / vendor tokenizer). The script’s ~4 chars/token heuristic is hot-path only.

## Procedure

Apply in this order so lossy steps see a smaller window:

1. KV-cache / prefix stability (lossless if the runtime supports it)
2. Observation masking (near-lossless if originals stay retrievable)
3. Retrieval scoping
4. Budget policy + triggers
5. Compaction / summarization (lossy; preserve anchors)
6. Partitioning (when one window still cannot hold the problem)

### 1. Baseline

Log per-turn tokens by category (system, tools, history, tool outputs, retrieved docs), task success, latency, and cache hit rate if available. Identify the dominant category before changing anything.

### 2. KV-cache / prefix

A single byte change early in the prompt invalidates every cached block after it.

1. Order **most-stable → most-volatile**: system → tool definitions → reusable templates → history → current user turn.
2. Keep the stable prefix **byte-identical** (whitespace, tool list order, serialization).
3. Move timestamps, request IDs, and counters **out of** the system prefix.
4. Confirm the runtime actually reuses prefixes.

```python
from scripts.compaction import design_stable_prompt, calculate_cache_metrics

stable = design_stable_prompt(raw_prefix)
metrics = calculate_cache_metrics(requests, cache_state)
```

Target: ≥70% cache hit rate on stable workloads.

### 3. Observation masking

1. Store the full observation under a stable reference id.
2. Replace the body with a short placeholder + key point + retrieve instruction.
3. Expose a retrieve path. **Do not mask** active errors / stack traces while debugging.

```python
from scripts.compaction import ObservationStore

store = ObservationStore(max_size=1000)
masked, ref_id = store.mask(long_tool_output, max_length=200)
if ref_id is not None:
    original = store.retrieve(ref_id)
```

```powershell
python scripts/compaction.py
```

### 4. Retrieval scoping

1. Score candidates against the **current** subtask, not the whole session.
2. Cap `top_k` and tokens per doc; drop below a relevance threshold.
3. Prefer just-in-time retrieval over preloading.
4. After use, keep a short extract or mask the full doc.

```python
from scripts.compaction import summarize_content, categorize_messages

brief = summarize_content(doc_text, "retrieved_document", max_length=500)
cats = categorize_messages(messages)
```

Tighten when `irrelevant_hits_ratio > ~0.20` or retrieved-docs exceed their budget.

### 5. Budget + triggers

Default sketch (must sum to 1.0): tool outputs ~0.35, history ~0.30, retrieved docs ~0.20, reserved ~0.15.

```python
from scripts.compaction import ContextBudget

budget = ContextBudget(total_limit=128_000)
budget.allocate("system_prompt", 1_500)
budget.allocate("tool_definitions", 3_000)
budget.allocate("message_history", 40_000)
budget.allocate("tool_outputs", 45_000)
should_act, reasons = budget.should_optimize(current_usage=int(128_000 * 0.85))
```

Fire masking / compact / tighten-scope from those triggers — not guesswork.

### 6. Compaction (lossy)

1. `categorize_messages(messages)`.
2. Preserve system prompt, tool definitions, and latest turn verbatim.
3. Summarize older conversation and resolved tool outputs with `summarize_content`.
4. Keep anchors: decisions, file paths, IDs, open questions.
5. Measure quality; roll back if drop exceeds budget.

**Never:** mask active error stacks; drop file paths/IDs/decisions; compact system/tools/latest turn; silently drop context if the summarizer fails.

### 7. Partitioning

When the full task still exceeds the window and splits into ≥3 independent subtasks: one sub-agent per slice, **structured results only**, parent aggregates. Sub-agents returning raw dumps defeat the point.

```
Context pressure?
├─ Quality collapsed without size pressure? → context-degradation
├─ Durable multi-cycle handoff? → context-compression
├─ Dumps re-fetchable from disk? → filesystem pointers
└─ This skill: stabilize prefix → mask observations → scope retrieval → compact → partition
Always: baseline → one change → gate on tokens AND quality
```

## Pitfalls

- Dynamic data in the system prompt (time, session id) — kills the cache prefix every turn.
- Re-sorting tools some turns and not others.
- Masking active errors or losing the retrieve path.
- LLM-generated mask keys (latency + hallucination) — use deterministic keys in the script.
- Trusting ~4 chars/token for billing.
- Compacting system prompts or the latest user turn.
- Partitioning dependent subtasks.

## Verification

```powershell
python scripts/compaction.py
```

Expected: token estimate, observation mask + retrieve, budget `should_optimize`, stable prompt rewrite. No exceptions.

Then: no-optimization baseline vs one tactic at a time.

| Metric | Default bar |
|--------|-------------|
| Token reduction | ≥30% on the optimized span |
| Quality drop | ≤5 points (0–1 scale) |
| Cache hit rate (stable work) | ≥70% after prefix work |

## Examples

**A — Tool dumps dominate.** Mask oldest resolved observations; if history still ≥75%, compact with system + last turn preserved.

**B — Cache miss ~0.55** because prefix includes `Current time: {iso}`. Move time to a trailing message; freeze tool order; re-measure hit rate.

**C — 7/10 retrievals are distractors.** Tighten `top_k`, raise threshold, summarize kept docs. If research is still huge, partition a research sub-agent that returns notes only.

## Related skills

Point at companions by name if present: `context-degradation`, `context-compression`, filesystem offload, multi-agent isolation. This chair owns **lossless-first token tactics**, not diagnosis or handoff-summary schemas.

## References

- `scripts/compaction.py` — implement or adapt the helpers; run the demo from this folder.
- `references/optimization_techniques.md` — extra thresholds and sketches.
- Provider docs for prompt/prefix caching on your stack (OpenAI, Anthropic, Gemini, vLLM, TGI, TensorRT-LLM).
