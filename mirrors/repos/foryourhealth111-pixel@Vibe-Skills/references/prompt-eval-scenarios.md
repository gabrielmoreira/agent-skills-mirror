# Prompt Evaluation Scenarios

Each scenario validates a prompt card as an advisory asset rather than a hidden router.

| Scenario | What is checked | Healthy signal |
|---|---|---|
| `pattern_card_provenance` | source citation and extraction trace | card references the canonical prompt pattern source |
| `advisory_only_route_hint` | route hint safety | card cannot override routing and is labeled as advisory |
| `risk_label_presence` | safety metadata | card includes explicit risk note and operator owner |
| `duplication_overlap_check` | card redundancy | duplicate cards are flagged before bundling |
| `operator_readability_check` | clarity for human reviewers | instructions remain concise and non-authoritative |

The QA corpus should remain small, auditable, and explicitly non-authoritative.
