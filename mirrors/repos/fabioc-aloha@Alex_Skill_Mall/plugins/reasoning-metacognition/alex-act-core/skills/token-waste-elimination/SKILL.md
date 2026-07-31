---
name: token-waste-elimination
description: "Audit active brain artifacts for context cost, duplicated guidance, oversized routing files, and stale metadata. Use during brain audits, quarterly review, or when instructions feel heavy."
lastReviewed: 2026-07-28
---

# Token Waste Elimination

Reduce active context without weakening behavior. Token cost matters only when
the content is loaded; optimize high-frequency surfaces first and preserve
specialized detail in on-demand skill resources.

## Measure Before Editing

Run your project's brain-QA muscles first (Alex ACT ships two — `scripts/brain-qa.cjs` for structural checks + `scripts/brain-semantic-qa.cjs` for semantic checks):

```pwsh
node scripts/brain-qa.cjs --json
node scripts/brain-semantic-qa.cjs --json
```

If your project doesn't ship equivalents, measure by listing active `applyTo: "**"` and `applyTo: "**/*"` instruction files and their line counts by hand.

Then measure active instructions by scope and line count. Treat `applyTo: "**"`
and `applyTo: "**/*"` as the highest-frequency group. Skill and prompt bodies
are on-demand; their metadata is always discoverable, but their full bodies do
not compete with every turn.

## Prioritize Waste

| Signal | Action |
| --- | --- |
| Two active artifacts give the same rule | Keep one owner; make the other a routing pointer or remove it |
| Instruction carries a long procedure | Move procedure to a skill; retain condition and action only |
| Prompt repeats its skill body | Reduce prompt to invocation, branches, and output contract |
| Hardcoded count or version in living guidance | Derive it or remove it |
| Active artifact references absent paths/tools | Repair or retire; warnings do not make unsafe behavior inert |
| Skill exceeds 500 lines | Move reference material to one-level-deep resources or split responsibility |
| Historical rationale dominates active rule | Move history to ADR/ledger; keep current behavior in the brain |

## Protect Load-Bearing Content

Do not remove content merely because it is long. Keep content that:

- changes decisions under realistic conditions
- establishes a safety or privacy boundary
- supplies examples needed to avoid recurring failures
- records the only current contract for a workflow

Before trimming, name the behavior the text protects and the executable check
that would expose accidental loss. If neither can be named, the text is a
strong removal candidate.

## Workflow

1. Capture the structural and semantic QA baseline.
2. Rank candidates by load frequency, duplication, and stale-contract risk.
3. Change one ownership cluster at a time.
4. Rerun the same focused checks after each cluster.
5. Run the full brain gate before finishing (if your project ships one; Alex ACT uses):

   ```pwsh
   node scripts/brain-qa.cjs
   node scripts/brain-semantic-qa.cjs
   node --test scripts/test-brain-semantic-qa.cjs scripts/test-coherence-check.cjs scripts/test-fleet-inventory.cjs
   ```

6. Report artifact-count and high-frequency-line deltas. Do not claim token
   savings unless measured by the actual loader or a documented approximation.

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Trimming every file to one arbitrary line ceiling | Optimize by load frequency and behavior value |
| Treating skill bodies as always-loaded | Distinguish discovery metadata from on-demand bodies |
| Removing examples without a regression check | Preserve examples that encode known failure prevention |
| Moving prose to a file that the skill always reads | That relocates cost; it does not reduce it |
| Reporting word counts as exact model tokens | Label estimates and name the tokenizer when used |

## Would Revise If

Revisit by **2026-10-28** or sooner if loader semantics change, a trimming pass
removes behavior that later regresses, the semantic muscle misses a stale
contract class it declares, or measured context cost does not improve after a
pass that claimed savings.