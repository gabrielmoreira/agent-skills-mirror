# CLAIM EXTRACTION

Claim extraction should produce reusable literature notes, not vague summaries.

## Extract at least these fields

For each paper or source note, identify:
- **Claim** — what the paper says it achieves or establishes
- **Evidence** — the concrete support for that claim (dataset, metric, experiment, analysis)
- **Method** — the approach or mechanism behind the claim
- **Limitation** — where the claim may not hold
- **Project relevance** — why this matters for the current project

## Writing rules

- Write claims in plain, reusable language.
- Distinguish the author claim from your project interpretation.
- Do not copy entire abstract sentences when a shorter paraphrase is clearer.
- Pair every durable claim with at least one evidence anchor.

## Minimal output shape

```md
## Key Claims
- Claim: ...
  - Evidence: ...
  - Method: ...
  - Limitation: ...
  - Project relevance: ...
```

## Promotion rule

If a claim is reusable across multiple papers or sources, promote it from a paper note into `Knowledge/` instead of leaving it stranded in `Sources/Papers/`.
