---
name: "xirang-snack"
description: "Quick code-first artifact reconciliation: from already-written code, conditionally create or update proposal + simplified design + the four-partition Semantic Delta using available code-change evidence. Use after iterative coding to back-fill Xirang artifacts without redoing propose→apply. Does not generate tasks.md."
license: "MIT"
compatibility: "Requires xirang CLI."
metadata:
  author: "xirang"
  version: "1.0"
  generatedBy: "0.0.1"
---

Reconcile Xirang artifacts from already-written code (code-first artifact reconciliation, reverse of propose/apply).

**Xirang Philosophy**

1. Xirang is a structured representation of human intent that an Agent can compile.
2. One Xirang Semantic Model is persisted as a single whole in the four partitions `metamodel/`, `elements/`, `relationships/`, and `views/`; a Semantic Delta uses the same four partitions and adds `operation`.
3. A change reconciles a Semantic Delta toward the target steady state. `proposal.md`, `design.md`, and `tasks.md` are compilation scaffolding, not competing sources of truth.
4. The Xirang Semantic Model is complete only when an Agent need not guess decisions that affect element hierarchy, contracts, or relationships.
5. The Agent acts like a compiler and faithfully translates authorized human intent. Existing code is current implementation evidence and MUST NOT silently override the Xirang Semantic Model.

**Element Contract Semantics**

- Element Contract SHALL 完整表达宿主 Element 在自身抽象层级承担的职责、保证、约束与行为；children 可以进一步精化或共同实现这些承诺，父子 Elements 可以在各自层级表达相互覆盖的完整语义。
- Requirement SHALL 以稳定 identity 表达一项可独立演进的规范承诺。以该承诺能否独立新增、修改或移除判断边界，不得按句子、分句、`SHALL` 数量或目标条数机械拆分。只复述 Declaration summary 或 sibling Requirements 语义并集且不增加规范承诺的内容不形成 Requirement；独立的不变量、顺序、原子性、一致性或完成条件应保留。
- Scenario SHALL 是具有规范约束力的 Requirement 组成，只具体化宿主 Requirement 在特定条件下的行为，不得引入可独立演进的承诺。Scenarios 不默认穷尽 Requirement 的全部适用情况，Scenario 不作为独立 Semantic Delta Entry，其变化由宿主 Requirement 的完整目标内容表达。

Treat `proposal.md`, `design.md`, and the Delta units under `{metamodel,elements,relationships,views}/` as conditional artifacts: create them when missing, update them when stale or inconsistent, and leave them unchanged when current.

## Input

- Optional `<change-name>` (kebab-case).
- If omitted, run `xirang list --json` and reuse the single active change; if multiple or none, ask which change name to target.

## Flow

1. Resolve change name and reconcile mode.
   - If `.xirang/changes/<name>/` does not exist, run `xirang new change "<name>"` and create only artifacts required by evidence.
   - Otherwise read the current proposal, design, and Delta units; classify each as **missing**, **stale**, **inconsistent**, or **current** and preserve unrelated human-authored content.
2. Load the shared Xirang Semantic Model context.
**Xirang Semantic Model Context**
- Resolve the absolute Project Root, then load the Semantic Model from `.xirang/model/{metamodel,elements,relationships,views}/` and locate the unique Project Root Element, whose `parent` is null.
- Use `identity` as the only way to reference a semantic object. FQN, syntax position, and derived local names are generation artifacts and never appear in a persistent source.
- Read relevant parent and children as abstraction/refinement context. Do not assume a fixed element-kind hierarchy or treat nesting as ownership.
- An Element Contract is the body of its Element unit: one Element has at most one Contract, expressed as `## Requirements`, and whether a Contract is required comes from the `contract` field of its Element Kind.
- Use `xirang arch query <identity> --relations --depth <n> --json` for parent, children, and incoming/outgoing semantic relationships; add `--contract` to inline the complete Element Contract.
- Default unit naming is `elements/<identity>.md`, `metamodel/<kind identity>.md`, `views/<view identity>.md`, and `relationships/<relationship kind identity>.yaml` grouped by Relationship Kind; a change reuses these names under `.xirang/changes/<name>/`. Directory and file names carry no model semantics: every entry declares its own `entity` and `identity`, and loading locates entries by those, never by path.
- Treat code paths, symbols, imports, and calls from CodeGraph or ACE/`rg`/`read` as current implementation evidence only; do not promote them to elements or relationships without declared model intent.
- If the model is missing, report `Semantic Model unavailable`. If it is incomplete or unsupported, identify the root, identity, contract, or relationship gap.
- A read-only exploration MAY degrade to available model and code evidence with the limitation disclosed. Workflows that compile or write semantics MUST stop when required model context is missing or incomplete; never treat a missing collection as complete and empty.
3. Collect code-change evidence from conversation context plus `git diff --cached`, `git diff HEAD`, other available working-tree/staged diffs, and user-selected commit/range diffs. `git diff` is one evidence source among several and MUST NOT be treated as the only valid source. Treat natural-language commit/range selectors as agent-parsed evidence selectors, not Xirang CLI flags. Mark conflicts or uncertainty `[REVIEW NEEDED]`.
4. Map changed symbols/files to current Semantic Model context.
   - Use Element `identity` values, refinement, Element Contracts, and relationships.
   - CodeGraph MAY accelerate symbol/call/import discovery; otherwise use ACE, `rg`, and `read`. Never read `.codegraph/codegraph.db`.
   - Treat code locations and call/import edges as implementation evidence, not as proof that the Xirang Semantic Model must change. Do not create elements from uncertain file-name inference.
5. Determine Element Contract impact.
   - Run `xirang arch query <identity> --contract --json` for each candidate Element and keep its current Requirements.
   - Add an identity to **Modified Specs** only when the observable requirements of its Element Contract change. Add it to **New Specs** only for genuinely new observable behavior not governed by an existing Element Contract.
   - An optional-contract Element without a Contract does not by itself require a new one; mark missing coverage `[REVIEW NEEDED]`.
   - Behavior-preserving refactors create no Contract delta; later Checks use `Preserves:` against formal Element Contracts.
6. Determine structural impact.
   - Declare impact only when Element Declarations, refinement, Relationships, Kinds, or Views change.
   - Implementation-only movement, symbol renaming, helper extraction, and mechanical call/import changes do not by themselves change the structure.
   - If no structural fact changes, set the compatible Architecture Source scope to `None`. If impact remains unresolved, stop and ask one focused question; do not write structural Delta units or claim reconciliation complete.
7. Reconcile the Contract and structural scopes as one Semantic Delta; both address the same Element identity space.
8. Reconcile `proposal.md`.
   - Run `xirang instructions proposal --change "<name>" --json`. For each response, follow the authoring order in the returned `instruction`. Keep `definition`, dependencies, `currentState`, `configProjection`, and `template` as separate inputs; do not copy non-artifact inputs into the artifact.
   - Reconcile `## Source Impact` from the Contract and structural scopes of one Semantic Delta. Keep the compatible Behavior Source and Architecture Source headings and reference Elements by `identity`.
   - Reuse the confirmed Contract scope as the Element Contract delta input; preserve `## Why`, `## What Changes`, `## Source Impact`, and `## Impact`.
   - If the proposal already matches evidence and source impact, leave it unchanged.
9. Reconcile Element Contract deltas in `elements/<identity>.md`.
   - Run `xirang instructions specs --change "<name>" --json`. For each response, follow the authoring order in the returned `instruction`. Keep `definition`, dependencies, `currentState`, `configProjection`, and `template` as separate inputs; do not copy non-artifact inputs into the artifact.
   - Create or update only the identities declared by the Contract scope. The default unit name is `<identity>.md`; a file name expresses nothing, so deviating from the default changes no model semantics.
   - Follow returned `## ADDED Requirements`, `## MODIFIED Requirements`, and `## REMOVED Requirements` rules with exact title matching and canonical unlabeled Requirement/Scenario syntax. Express a rename as REMOVED old Requirement plus ADDED new complete Requirement. Preserve unrelated current delta content.
10. Reconcile simplified `design.md`.
   - Run `xirang instructions design --change "<name>" --json`. For each response, follow the authoring order in the returned `instruction`. Keep `definition`, dependencies, `currentState`, `configProjection`, and `template` as separate inputs; do not copy non-artifact inputs into the artifact.
   - Preserve Context, Goals / Non-Goals, Decisions, and Risks / Trade-offs. Mark inferred content `[INFERRED FROM CODE]` and unresolved decisions `[REVIEW NEEDED]`.
11. Reconcile the structural Delta units only after structural impact is resolved. Leave those partitions empty when the structure is confirmed unchanged; author validated Entries otherwise.
   **Write the Semantic Delta**:

Every Markdown unit declares its own `entity` in frontmatter. The partition does not determine the type.

| entity | frontmatter fields |
|---|---|
| `element-declaration` | `identity`, `kind`, `parent`, `title`, `summary` |
| `element-kind` | `identity`, `contract`; optional `root`, `parents`, `children` |
| `relationship-kind` | `identity`; optional `sourceKinds`, `targetKinds` |
| `authored-view` | `identity`, `include`; optional `of`, `title`, `autoLayout` |

- `identity` uses `[A-Za-z0-9._-]+`, contains no path separator, and does not encode parent hierarchy
- Before writing, follow the authoring order in the returned `instruction`; keep `definition`, dependencies, `currentState`, `configProjection`, and `template` as separate inputs
- Read proposal `Source Impact` as compatible scaffolding for one Semantic Delta; use it to locate affected elements, refinement, Element Contracts, and relationships
- Read `design.md` for architecture decisions and the formal Xirang Semantic Model as current semantic state
- Treat proposal entries as scope declarations, not authoritative Semantic Delta records; derive exact target-state Declarations, Requirements, Relationships, Kinds, and Views
- Write Delta units under `.xirang/changes/<name>/{metamodel,elements,relationships,views}/` using the same field structure as the model plus an `operation` of `ADDED`, `MODIFIED`, or `REMOVED`; each Entry carries its complete target state, and `REMOVED` carries identity only
- In an `elements/` unit, the frontmatter is the Element Declaration Entry and the body carries zero or more Requirement Entries under `## ADDED Requirements`, `## MODIFIED Requirements`, or `## REMOVED Requirements`; when only the Contract changes, the frontmatter declares no `operation` and only locates the host Element
- A `relationships/` entry is `{operation, source, kind, target}` and nothing else: it has no `MODIFIED` and no description, because its identity is its whole content
- Reference every semantic object by `identity`; a Delta unit carries no path, position, or derived-name reference
- Leave a partition empty when it does not change; do not invent Declaration, Relationship, Kind, or View changes from Contract changes alone
- Run `xirang arch validate --change "<name>" --json`
- Use current code only as implementation evidence; it MUST NOT override the Xirang Semantic Model
   - Distinguish Requirement Entries in an Element unit body from the Declaration Entry in its frontmatter.
12. Do NOT generate `tasks.md` (code is already implemented).
13. Run `xirang validate --change "<name>" --json`. On ERROR/WARNING, repair once from artifact instructions, validate once more, and report the final result.
14. After validation passes, run `xirang diff --change "<name>" --write`. Treat `.xirang/changes/<name>/effective-change.md` as the only persistent effective-change report and require its status to be Passed before claiming reconciliation complete.
15. Finish with the output hints.

## Output Hints

⚠️ Generated specs are based on code inference. Review items marked [REVIEW NEEDED]

1. **Quick sync**: `xirang sync "<change-name>" --no-verify`
2. **Quick archive**: `xirang archive "<change-name>" --no-verify`
3. **Sync and archive**: `xirang sync "<change-name>" --no-verify && xirang archive "<change-name>" --no-verify`
4. **Continue development**: review change → modify code → run `/skill:xirang-snack` again → continue iterating

## Artifact Contract

**Document Language Contract**:
- Treat `.xirang/config.yaml` as the compact source of truth, but consume its compiled prompt projection rather than reinterpreting raw keys ad hoc
- If the compiled projection includes `proseLanguage`, apply it to natural-language prose you write or revise in the artifact body
- Natural-language prose includes task titles, check names, Requirement titles, Scenario titles, bullet descriptions, Expect/Evidence descriptions, rationale, goals, risks, and summaries
- Follow the existing template structure exactly; do not invent a different layout because the prose language changes
- Keep template headings, normative keywords, BDD keywords, IDs, schema keys, relation types, file paths, commands, and code identifiers in their canonical form
- Preserve exact existing Requirement titles required for MODIFIED matching
- English project terminology may remain embedded in prose, but ordinary English sentences and titles still follow `proseLanguage`
- If no `proseLanguage` projection is present, keep the default writing behavior for prose

Preserve canonical headings, IDs, schema keys, BDD keywords, paths, commands, and code identifiers.
