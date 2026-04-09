# Literature Scouting Report Template

Use this template when `scout` needed external search to clarify the task frame, evaluation contract, or baseline shortlist.

The goal is to keep the discovery work reusable so later `baseline` and `idea` passes do not restart from zero.

## 1. Survey header

- quest id
- date
- task under investigation
- why scouting was needed now
  - unclear task framing
  - unclear dataset / split
  - unclear metric contract
  - missing baseline candidate
  - resumed quest refresh

## 2. Memory consulted before external search

List:

- quest cards read
- global cards read
- what they already answered
- what remained missing or stale

## 3. Search ledger

For each meaningful search pass, record:

| query | source | reason | new references | known references reconfirmed | unresolved ambiguity |
| --- | --- | --- | --- | --- | --- |
| benchmark + metric | arXiv | find direct benchmark papers | 2 | 1 | split naming still unclear |

Recommended source labels:

- `memory`
- `arXiv`
- `benchmark-doc`
- `official-repo`
- `open-web`
- `repo-search`

## 4. Reference buckets

Split retained references into:

- task-defining papers
- benchmark / evaluation docs
- candidate baseline papers
- candidate baseline repos
- watchlist / uncertain provenance

For each retained item include:

- title
- identifier or arXiv id
- URL
- year
- why it matters
- which question it informs:
  - task framing
  - evaluation contract
  - baseline route
  - future ideation
- provenance label:
  - `official`
  - `community`
  - `uncertain`

## 5. Evaluation-contract implications

State:

- task
- dataset / benchmark
- split
- primary metric
- fairness constraints
- still-open ambiguity, if any

## 6. Baseline-shortlist implications

For each serious candidate:

- method or baseline name
- paper evidence
- repo evidence
- provenance confidence
- route recommendation:
  - attach
  - import
  - reproduce
  - reject

## 7. Durable follow-up writes

List:

- quest `papers` cards to create or refresh
- quest `knowledge` cards to create or refresh
- any global lesson that may later be promotable

At least one survey-derived memory card should be written if external search materially changed the frame.

## 8. Next anchor recommendation

Choose one:

- `baseline`
- `idea`
- remain in `scout`

State why that anchor is now justified.
