---
name: recommend-strategies
description: Maps deterministic v2 dimension priorities, or archived v1 capability gaps, to strategies S1-S7 by invoking scripts/assessment_engine.py. Use for "recommend strategies", "recomendar estrategias", "which initiatives should we prioritize", "qué iniciativas priorizar".
---

# Skill: Recommend strategies

Do not map strategies by hand. Run the official engine.

## Command

```bash
python3 scripts/assessment_engine.py all
```

## v2 strategy rules

- Strategies are `S1` to `S7`.
- The engine sums priority for mapped dimensions.
- A strategy is recommended when the summed priority is at least `0.9`.
- Preserve links to contributing dimensions and questions from `output/recommendations.json`.

## Implementation guide phases

The implementation guide uses the same priority and horizon rules:

- P0: first 30 days.
- P1: next quarter.
- P2: semester.
- P3: backlog.

## v2 context

Report groups for PDFs are:

- G1: D1, D2, D9.
- G2: D3, D4, D5.
- G3: D6, D7, D8.

## Chat response

List recommended strategies in priority order with contributing dimensions or capabilities, priority total, first actions, and horizon. State that the values came from `output/recommendations.json`.
