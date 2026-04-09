# Paper Triage Playbook

Use this reference during `scout` when you need a more explicit process for building the paper and repo neighborhood.

## 1. Search objective

The goal is not to collect many papers.
The goal is to map the smallest neighborhood that can justify:

- the task frame
- the evaluation contract
- the baseline shortlist

## 2. Search buckets

Try queries from these buckets:

- task + dataset + metric
- task + benchmark
- baseline method name + dataset
- task + failure mode
- task + official repo
- benchmark name + official evaluation
- strongest recent paper title or method name

## 2.1 Search order and reuse discipline

Before broad web search:

1. read recent quest `papers`, `knowledge`, and `decisions`
2. read relevant global `papers`, `knowledge`, and `templates`
3. run `memory.search(...)` on task, benchmark, dataset, metric, split, and likely baseline names

Then search externally for the missing pieces:

1. arXiv for paper discovery
2. benchmark docs and official repos for contract truth
3. broader web search for provenance checks or follow-up references

The goal is to avoid repeating the same scouting pass when the quest already has durable notes.

## 3. Retain only useful references

For each retained item, record:

- identifier
- title
- why it matters
- whether it informs:
  - task framing
  - eval contract
  - baseline route
  - future ideation

Reject references that do not materially change the next stage.

## 4. Repo triage

When a paper has code, inspect:

- whether the repo is official or clearly linked
- whether the evaluation path is obvious
- whether dependencies are realistic
- whether the repo appears maintained enough to be usable

Do not assume "has GitHub repo" means "good baseline candidate".

## 5. Stop condition

Stop when:

- strongest obvious references are mapped
- baseline candidates can be ranked credibly
- metric and split ambiguity are no longer the main blocker

If external search materially informed the answer, leave behind a literature scouting report.
Prefer `literature-scout-template.md`.
