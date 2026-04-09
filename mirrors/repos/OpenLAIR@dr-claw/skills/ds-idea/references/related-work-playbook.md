# Related-Work Playbook

Use this reference during the `idea` stage when you need a deeper and more explicit process for literature scouting, novelty checking, and value judgment.

## 1. Search objective

The goal is not to collect random citations.
The goal is to answer:

- what has already been tried?
- what is the strongest nearby prior work?
- what remains unresolved or weakly defended?
- does the candidate still have novelty or at least research value?

## 2. Query families

Do not rely on one query.
Use several query families and refine them iteratively:

- task + dataset + metric
- task + failure mode or bottleneck
- baseline method name + limitation keyword
- proposed mechanism + task
- proposed mechanism + dataset
- adjacent-domain principle + task
- strongest recent paper title or method name + "extension", "robustness", "ablation", or "failure"

## 2.1 Source order and de-dup protocol

Before opening a fresh broad search, check durable memory first:

1. recent quest `papers`, `ideas`, and `knowledge`
2. recent global `papers`, `knowledge`, and `templates`
3. `memory.search(...)` with the baseline name, task, dataset, mechanism, and current idea labels

Then search externally for the missing neighborhood:

1. arXiv for direct paper discovery
2. citation trails for nearest-neighbor expansion
3. broader web or repo search for implementation overlap and follow-up work

The goal is not to search the same cluster from zero every time.
The goal is to reuse what the quest already knows and only spend new search budget on gaps, recency, or unresolved overlap.

## 3. Coverage targets

Try to cover these buckets before final selection:

- seminal papers that define the line
- strongest recent direct competitors
- nearest mechanism-level neighbors
- papers focused on the same failure mode
- papers with the same task but different mechanism families

For a normal selected-idea decision, the survey should durably cover at least `5` and usually `5-10` related and usable papers.
Prefer direct task-modeling papers first; if that pool is truly small, fill the rest with the closest adjacent and translatable work instead of pretending the literature is empty.

If the area is active, recent work matters a lot.
If the area is stable, seminal work may matter more than recency.

## 4. Reading order

For each promising paper, use a layered read:

1. abstract, introduction, conclusion
2. figures, tables, and headline claims
3. method overview
4. experiment section for dataset / metric overlap
5. ablations, limitations, or failure cases

Deep-read only the papers that materially affect the novelty or selection verdict.

## 5. Comparison table

Build a closest-prior-work table.
Recommended columns:

- identifier
- year
- task overlap
- dataset overlap
- metric overlap
- mechanism overlap
- main claim
- evidence strength
- weakness or unresolved edge
- implication for our candidate

Before stopping, also leave behind a literature survey report.
Prefer the structure in `literature-survey-template.md`.

## 6. Novelty triage logic

Ask these questions in order:

1. Did prior work already use essentially the same mechanism for the same task?
2. If yes, is our claim still different because of boundary condition, evidence package, or failure-mode resolution?
3. If not, is our direction still only an obvious combination of known ingredients?
4. If the idea is incremental, is the increment still important enough to justify experiments?

Possible verdicts:

- `novel`
- `incremental but valuable`
- `not sufficiently differentiated`

## 7. Research-value checks

Even if novelty is limited, a direction may still be worth doing when it offers:

- stronger evidence on a disputed claim
- a valuable transfer to a new but important setting
- resolution of a known failure mode
- a negative result that closes off a tempting but weak path
- reusable infrastructure or methodology

If none of these apply, the candidate is usually not worth promoting.

## 8. Common failure patterns

Watch for these traps:

- only reading one or two papers
- repeating the same broad search without checking memory first
- comparing to weak baselines instead of the strongest nearby work
- declaring novelty from implementation detail rather than research claim
- mistaking recency for relevance
- importing a concept from another domain without proving the translation makes sense here
- treating a paper title match as evidence without checking dataset and metric overlap

## 9. Exit condition

The related-work search is good enough to stop when:

- the strongest obvious nearby papers are mapped
- the closest-prior-work table is complete enough to compare seriously
- each top candidate has an explicit novelty or value verdict
- the usable-paper floor for the selected idea has been satisfied or the shortage is explicitly documented
- the remaining uncertainty is recorded rather than hidden
