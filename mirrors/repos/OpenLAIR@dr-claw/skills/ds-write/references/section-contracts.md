# Section Contracts

Use this reference when outline design or drafting needs sharper section-level contracts.

## Title

The title should:

- name the task or mechanism clearly
- preserve search-relevant keywords
- state the work in one memorable line
- avoid empty slogans

## Abstract

Default four-slot contract:

1. problem
2. what we do
3. how at a high level
4. main result or strongest evidence

Keep it readable for a broad technical audience.
Avoid formula-heavy or jargon-heavy abstracts.

## Introduction

Prefer:

- problem
- why it matters
- strongest current bottleneck
- our remedy
- evidence preview

Do not use the introduction as a loose literature dump.

## Related work

The section should:

- cover the important papers
- group them into meaningful lines
- compare assumptions and mechanisms
- show lineage and distinction without attacking prior work

## Method

Default order:

1. baseline or background setup
2. running example
3. intuition
4. formalism
5. implementation-critical details

Every equation should have a clear role and clear symbol definitions.

## Experiments

Prefer:

1. setup and evaluation contract
2. main comparison
3. ablations
4. supporting analyses
5. limitations exposed by the evidence

## Conclusion

Summarize what was actually shown.
Do not silently upgrade the claim in the conclusion.

## Appendix

Move high-formality or lower-priority material here:

- proofs
- extended derivations
- extra ablations
- extra implementation detail
- additional tables that would overload the main text
