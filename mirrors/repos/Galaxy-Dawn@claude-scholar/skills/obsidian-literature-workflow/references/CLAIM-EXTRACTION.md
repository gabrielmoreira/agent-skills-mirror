# CLAIM EXTRACTION

Claim extraction should produce reusable literature notes, not vague summaries.

## Extract at least these fields

For each paper or source note, identify:
- **Claim** — what the paper says it achieves or establishes
- **Claim type** — author claim, community consensus, or project interpretation
- **Claim strength** — speculative, observed, supported, or strong
- **Evidence** — the concrete support for that claim (dataset, metric, experiment, analysis)
- **Method** — the approach or mechanism behind the claim
- **Limitation** — where the claim may not hold
- **Contradicts / weakens** — evidence or conditions that reduce confidence in the claim
- **Project relevance** — why this matters for the current project

## Writing rules

- Write claims in plain, reusable language.
- Distinguish the author claim from your project interpretation.
- Do not copy entire abstract sentences when a shorter paraphrase is clearer.
- Pair every durable claim with at least one evidence anchor.
- Do not promote a claim strength without naming the evidence that justifies the stronger level.

## Minimal output shape

This `Key Claims` block is a paper-note projection of the shared Evidence Record contract. Preserve the same evidence anchor, limitation, contradiction, project relevance, and claim strength so downstream synthesis can map it back to the canonical evidence record.

```md
## Key Claims
- Claim: ...
  - Claim type: author claim | community consensus | project interpretation
  - Claim strength: speculative | observed | supported | strong
  - Evidence: ...
  - Method: ...
  - Limitation: ...
  - Contradicts / weakens: ...
  - Project relevance: ...
```

## Promotion rule

If a claim is reusable across multiple papers or sources, promote it from a paper note into `Knowledge/` instead of leaving it stranded in `Sources/Papers/`.

Only promote claims that include both an evidence anchor and a claim strength. If the evidence is weak or indirect, keep the claim as `speculative` or `observed` and preserve the uncertainty.
