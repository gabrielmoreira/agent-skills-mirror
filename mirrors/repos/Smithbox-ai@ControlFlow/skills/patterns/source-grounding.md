# Source Grounding

Use this pattern when a plan or research claim depends on an external framework, API, product, version, or sibling repository.

## Evidence Order

1. Use repository-local evidence for facts about the current repository.
2. Prefer current official primary sources for external contracts and version-sensitive claims.
3. Use secondary sources only to discover leads or when no primary source exists.
4. Record provenance, license, and direct-access status before recommending adoption from a sibling repository.

## Claim States

- `VERIFIED`: current primary evidence directly supports the claim.
- `LOCALLY_OBSERVED`: local files support the claim, but upstream provenance or freshness is unconfirmed.
- `UNVERIFIED`: evidence is inaccessible, stale, contradictory, or indirect.

Material `UNVERIFIED` claims must become an explicit assumption, clarification, or research blocker before implementation. Never present them as settled facts.

## Output Discipline

- Cite the evidence path or URL and summarize it in your own words.
- Do not copy external prompts, code, or hooks without explicit approval and compatible licensing.
- Separate observed facts, inferences, and recommendations.
