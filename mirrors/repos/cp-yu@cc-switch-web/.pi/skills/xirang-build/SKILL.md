---
name: "xirang-build"
description: "Build or rebuild the project Xirang Semantic Model as one reviewed Candidate."
license: "MIT"
compatibility: "Requires xirang CLI with candidate commands."
metadata:
  author: "xirang"
  version: "1.0"
  generatedBy: "0.0.1"
---

Build the project Xirang Semantic Model from user-authorized intent and evidence.

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

**Semantic Model Unit Notation**

Every Markdown unit declares its own `entity` in frontmatter. The partition does not determine the type.

| entity | frontmatter fields |
|---|---|
| `element-declaration` | `identity`, `kind`, `parent`, `title`, `summary` |
| `element-kind` | `identity`, `contract`; optional `root`, `parents`, `children` |
| `relationship-kind` | `identity`; optional `sourceKinds`, `targetKinds` |
| `authored-view` | `identity`, `include`; optional `of`, `title`, `autoLayout` |

- `parent: null` marks the single Project Root. `include` is `'*'` or a list of element identities; `of` is one element identity.
- A `relationships/` file is a container of `{source, kind, target}` entries. A Relationship's identity is its entire content and it carries no other field.
- An `elements/` unit body is exactly the `## Requirements` section: `### Requirement: <name>` with `#### Scenario: <name>` beneath it. Descriptive prose belongs to the Declaration's `summary` and MUST NOT be repeated in the Contract. Any other body content is a validation error.
- A `views/` unit has no body.
- `identity` uses `[A-Za-z0-9._-]+` and contains no path separator. Element Kind and Relationship Kind identities are globally unique within the Metamodel. Do not encode a parent path or hierarchy position into an identity: position changes over time while identity does not.
- Default file naming, non-normative: `elements/<identity>.md`, `metamodel/<kind identity>.md`, `views/<view identity>.md`, `relationships/<relationship kind identity>.yaml` grouped by Relationship Kind.

## Workflow

1. Confirm that the project has been prepared with `xirang setup`, then run `xirang candidate status --json`.
2. If a Candidate is active, present its baseline, inventory, and status. Ask the user to choose either to continue the active Candidate or explicitly authorize discarding it and initialize a replacement. Build MUST NOT silently continue, discard, or replace an active Candidate.
3. Ask the user to choose the exploration scope: whole project, code and tests, documentation and current Xirang, or custom paths and rules.
4. Resolve the Candidate baseline before authoring any Build file. Summarize the Formal Model when it exists, ask the user to choose the starting point, then run exactly one applicable command:
   - `xirang candidate init --from current`
   - `xirang candidate init --from clean`
   - `xirang candidate init --from-path <path>`
5. After initialization succeeds, write `.xirang/candidate/build.md` with the authorized scope, authority order, current requirements, and explicit exclusions. Current user requirements have highest priority.
6. Explore the authorized scope in any useful order. Code, tests, documents, configuration, Git history, and current Xirang are evidence only unless the user explicitly designates them as source of truth. Subagents MAY accelerate read-only exploration.
7. Run the conditional Modeling Decision Gate after exploration and before the first Candidate model write.
   - Ask only when multiple reasonable choices would change identity, hierarchy, Contract, Kind, Relationship, or Authored View semantics. Do not block on implementation details or wording preferences that cannot change the target Semantic Model.
   - Resolve decisions in dependency order: authority conflicts → Element identity and boundaries → hierarchy → Metamodel → Contracts → Relationships → Authored Views.
   - Present bounded options with trade-offs and ask one decision at a time. If no semantic choice remains, continue without asking.
   - Append only exception provenance to `build.md`: user rulings, authority-conflict resolutions, non-obvious evidence choices, and explicit exclusions. Record each decision, evidence, and affected scope; do not create a Requirement provenance matrix.
8. Author the Candidate breadth-first across the whole model: Metamodel → Element Declarations and hierarchy → Element Contracts → Relationships → Authored Views.
   - Write `.xirang/candidate/{metamodel,elements,relationships,views}/` in the unit notation above. An Element Contract is the body of its Element unit, so one Element has at most one Contract; whether a Contract is required comes from the `contract` field of its Element Kind.
   - Check each completed layer with focused Agent inspection. Do not require full `candidate validate` for an intentionally incomplete intermediate layer.
   - If a later layer exposes an earlier defect, correct the affected layer and recheck every dependent later layer without rewriting unrelated layers.
9. Run `xirang candidate validate --json` after all five layers exist. Fix every ERROR in Candidate source and repeat deterministic validation until it succeeds. The CLI is read-only and must not author or normalize semantics.
10. After deterministic validation succeeds, delegate one complete semantic review to a generic read-only subagent with a clean context.
    - Provide the absolute project root, Candidate root, `build.md`, current `reviewDigest`, authorized scope, authority order, recorded user rulings, validation result, review checklist, and output contract.
    - Require the subagent to independently read build.md, all four Candidate partitions, authority sources, and necessary project evidence. Main-Agent completion claims are not evidence.
    - Review authorization coverage, unauthorized durable semantics, hierarchy, Kinds, Contracts, Requirement boundaries, Scenario confinement, Relationships, Authored Views, cross-level overlap, and exception provenance.
    - Only `BLOCKER` and `HIGH` findings fail the gate. Correct a finding or return to the Modeling Decision Gate as appropriate.
    - Any Candidate modification invalidates the review. Rerun `xirang candidate validate --json` and delegate another new clean-context subagent; never resume or reuse the previous review context.
    - If a clean-context subagent is unavailable, fail closed. Do not substitute author self-review or use `xirang-reviewer`.
11. Present the Project Root, Metamodel, hierarchy, Element Contracts, Relationships, Authored Views, important confirmed decisions, Formal comparison, semantic-review result, and returned `reviewDigest` directly to the user.
12. Only after the user confirms that exact version, run `xirang candidate promote --digest <reviewDigest>`. Promotion replaces `.xirang/model/` with the Candidate as a whole; a unit absent from the Candidate is not retained.
13. After promotion succeeds, verify these postconditions in order:
    - Run `xirang candidate status --json` and require `active === false`.
    - Verify `.xirang/model/metamodel`, `.xirang/model/elements`, `.xirang/model/relationships`, and `.xirang/model/views` are real directories, even when a partition is empty.
    - Run `xirang arch validate --json` and require success. Report warnings without failing the postcondition.
    - Report Build complete only after all checks pass. On failure, report whether promotion succeeded, the failed condition, and current Formal/Candidate state; MUST NOT retry promotion automatically.

## Guardrails

- The Candidate is one complete Semantic Model, authored and reviewed as a whole.
- `build.md` is temporary compilation scaffolding, not durable semantic source.
- The breadth-first authoring order does not impose a fixed evidence scan order.
- Do not infer hierarchy, behavior, or relationships from paths, imports, calls, passing tests, or implementation existence alone.
- Do not modify formal `.xirang/model/` before digest-confirmed promotion.
- Build and promotion provide no guarantee that Git status or index remain unchanged.
- Preserve canonical identities, paths, commands, and schema keys.
