# Kestrel Search benchmark evaluator

Use these instructions when evaluating final answers from the `native` and
`kestrel` benchmark arms. Apply the same standard to both arms.

## Inputs

For each trial, inspect:

1. The task prompt and its `expected` fields.
2. The final Codex answer in the result JSONL record.
3. For Kestrel, the linked retrieval artifact in `results/artifacts/`.
4. For native, the cited sources in the final answer and the correlated Phoenix
   trace when a retrieval/tool-use question matters.

Do not score solely by literal keyword matching. The generated keyword checks
are regression signals, not ground truth.

## Evaluation rubric

Score each dimension from 0 to 2:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Correctness | Materially wrong | Partly correct or uncertain | Correct and specific |
| Grounding | Unsupported or contradicted | Partly supported | Claims supported by cited retrieved sources |
| Source quality | No source or low-quality source | Mixed authority | Primary/official sources where available |
| Completeness | Misses a key part | Covers most of the task | Covers every material part concisely |

Set `pass` to `true` only when correctness and grounding are both at least 1,
the total is at least 6/8, and no material claim is contradicted by the cited
source.

## Important rules

- Accept semantically equivalent wording, aliases, and newer accurate facts.
- Prefer current primary sources over stale benchmark expectations. Record a
  stale fixture rather than marking a correct answer wrong.
- Distinguish a retrieval failure from an answer-synthesis failure:
  - If the needed fact is absent from Kestrel's artifact, mark retrieval as the
    likely failure point.
  - If the fact is present but the final answer is wrong or incomplete, mark
    synthesis as the likely failure point.
- For source-reconciliation tasks, require the answer to identify and resolve
  disagreement rather than silently choosing one source.
- Do not reward unsupported confidence. A concise, qualified answer is better
  than a precise but invented one.
- Do not penalize an answer for omitting implementation details that the task
  did not ask for.

## Required output

Return one JSON object per evaluated trial:

```json
{
  "run_id": "...",
  "task_id": "...",
  "arm": "native|kestrel",
  "correctness": 0,
  "grounding": 0,
  "source_quality": 0,
  "completeness": 0,
  "total": 0,
  "pass": false,
  "failure_stage": "none|retrieval|synthesis|fixture",
  "rationale": "Short evidence-based explanation."
}
```

Keep the rationale under 80 words and cite the decisive source URL or artifact
field when possible.
