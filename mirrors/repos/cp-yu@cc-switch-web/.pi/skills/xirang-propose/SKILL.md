---
name: "xirang-propose"
description: "Propose a new change with all artifacts generated in one step. Use when the user wants to quickly describe what they want to build and get a complete proposal with design, specs, and tasks ready for implementation."
license: "MIT"
compatibility: "Requires xirang CLI."
metadata:
  author: "xirang"
  version: "1.0"
  generatedBy: "0.0.1"
---

Propose a new change or update an existing change, generating all artifacts needed for implementation.

**Xirang Philosophy**

1. Xirang is a structured representation of human intent that an Agent can compile.
2. One Xirang Semantic Model is persisted as a single whole in the four partitions `metamodel/`, `elements/`, `relationships/`, and `views/`; a Semantic Delta uses the same four partitions and adds `operation`.
3. A change reconciles a Semantic Delta toward the target steady state. `proposal.md`, `design.md`, and `tasks.md` are compilation scaffolding, not competing sources of truth.
4. The Xirang Semantic Model is complete only when an Agent need not guess decisions that affect element hierarchy, contracts, or relationships.
5. The Agent acts like a compiler and faithfully translates authorized human intent. Existing code is current implementation evidence and MUST NOT silently override the Xirang Semantic Model.

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

**Element Contract Semantics**

- Element Contract SHALL 完整表达宿主 Element 在自身抽象层级承担的职责、保证、约束与行为；children 可以进一步精化或共同实现这些承诺，父子 Elements 可以在各自层级表达相互覆盖的完整语义。
- Requirement SHALL 以稳定 identity 表达一项可独立演进的规范承诺。以该承诺能否独立新增、修改或移除判断边界，不得按句子、分句、`SHALL` 数量或目标条数机械拆分。只复述 Declaration summary 或 sibling Requirements 语义并集且不增加规范承诺的内容不形成 Requirement；独立的不变量、顺序、原子性、一致性或完成条件应保留。
- Scenario SHALL 是具有规范约束力的 Requirement 组成，只具体化宿主 Requirement 在特定条件下的行为，不得引入可独立演进的承诺。Scenarios 不默认穷尽 Requirement 的全部适用情况，Scenario 不作为独立 Semantic Delta Entry，其变化由宿主 Requirement 的完整目标内容表达。

## Workflow Stage

| Aspect | Value |
|--------|-------|
| **Stage** | `PROPOSE` - Artifact generation (no implementation) |
| **Allowed** | Generate proposal, design, tasks, and the four-partition Semantic Delta units in .xirang/changes/<name>/ |
| **Forbidden** | Implement code, modify project files outside the selected change directory |

## Flow

1. Resolve a provisional kebab-case change ID. Ask one focused question when the requested change itself is unclear. Report status only at readiness, blocker, and final-summary points; do not emit per-artifact progress updates.
2. Gather read-only evidence before any write.
   - Run `xirang list --json` and inspect relevant existing change artifacts when present.
   - Load the formal Xirang Semantic Model through the shared context above.
   - Run `xirang arch search <query> --json` to locate the Elements a request touches.
   - For known or affected Elements, run `xirang arch query <identity> --relations --depth 2 --json`, adding `--contract` when the current Element Contract matters.
   - Use implementation evidence only where needed to resolve current behavior or lowering constraints.
3. Assess semantic readiness.
   - Reuse a confirmed `Design Summary` when the conversation contains one, and state that it is being reused. Route architecture decisions to proposal Architecture Source, `design.md`, and the Declaration, Relationship, Metamodel, and View Delta units; route testing strategy to `design.md` and concrete test work to `tasks.md`; route risk and trade-off decisions to `design.md`.
   - Otherwise require a clear problem, impact scope, approach, verification method, and no unresolved Semantic Delta decisions across Contract or structural scope. Multi-subsystem scope is evidence, not an automatic Explore requirement; report a gap only when it cannot form one coherent change scope.
   - If readiness is incomplete, list the concrete missing items, recommend `/skill:xirang-explore`, and stop: do not create a change directory or modify project files.
   - If the user explicitly overrides the readiness recommendation, continue, but the override does not authorize guessing source decisions. Ask one focused question at a time for every unresolved behavior or architecture decision.
   - For an existing change, assess readiness from existing artifacts, current input, the confirmed Design Summary, formal source, and implementation evidence together.
   - Keep readiness, missing-item, and override state in the conversation only; do not copy it into change artifacts.
4. Resolve change identity after readiness passes or is explicitly overridden.
   - If the user explicitly requests a new change and the ID is unused, run `xirang new change "<name>"`.
   - If the user explicitly requests a new change and the ID already exists, stop and ask for a different ID. Do not overwrite, continue, or synthesize an alternative ID.
   - If the user explicitly requests an existing change, update that change in place without asking for another ID.
   - If intent is ambiguous and the ID exists, ask whether to update the existing change or create an independent new change; in non-interactive mode, fail and request an explicit choice.
   - Run `xirang status --change "<name>" --json` for `applyRequires`, artifact order, dependencies, and schema.
5. Determine source impact before writing `proposal.md`.
   - Compare requested observable behavior with formal Element Contracts. Reuse the Element whose Contract already governs the behavior; add a Contract to another Element only for genuinely new observable behavior. An optional-contract Element without a Contract does not by itself require a new one.
   - Compare structural impact with the formal Xirang Semantic Model. Identify affected Element Declarations, refinement, Relationships, Element Kinds, Relationship Kinds, and Authored Views. Implementation movement or call/import evidence alone is not a structural change.
   - Determine the Contract and structural scopes of one Semantic Delta. Keep the compatible `Behavior Source` and `Architecture Source` proposal headings: `Behavior Source` lists `New Specs` or `Modified Specs` as the Element identities whose Element Contract is added or modified, and `Architecture Source` lists the identities whose Declaration, Relationship, Metamodel, or View semantics change. Both sections address the same identity space; they separate Contract impact from structural impact, not two kinds of identifier. Use `None` only when that scope truly does not change.
6. Generate ready artifacts in dependency order. For each artifact, run `xirang instructions <artifact-id> --change "<name>" --json`.
   - For each response, follow the authoring order in the returned `instruction`. Keep `definition`, dependencies, `currentState`, `configProjection`, and `template` as separate inputs; do not copy non-artifact inputs into artifacts.
   - For `proposal.md`, write `## Source Impact` with the compatible Behavior Source and Architecture Source sections, referencing Elements by `identity`.
   - When creating `specs`, write the Element Contract delta into `.xirang/changes/<name>/elements/<identity>.md` for exactly the identities declared under proposal `Behavior Source`; the frontmatter locates the host Element and the body carries the Requirement Entries. Read the exact Requirement titles from the formal Element Contract before authoring ADDED, MODIFIED, or REMOVED deltas. Express a rename as REMOVED old Requirement plus ADDED new complete Requirement. Author only canonical unlabeled `#### Scenario: <title>` headings. Rely on combined change validation for deterministic header compatibility. Follow the returned Specs authoring contract.
   - Route obsolete-test rationale from **Test Maintenance** to `design.md` and concrete test updates/removals to `tasks.md`. Route **One-time Verification** items to evidence-only `tasks.md` Checks with no persistent test file; absence assertions use `Verifies: <path> REMOVED Requirement`.
7. Continue until all `applyRequires` artifacts are done. Ask one focused question when an artifact decision remains unresolved.
8. After Specs and Design are complete, reconcile structural scope before writing the remaining Delta units.
   - Re-read proposal Architecture Source, `design.md`, the formal Xirang Semantic Model, and current implementation evidence.
   - If Design confirms a different structural impact across Declarations, refinement, Relationships, Kinds, or Views, update only proposal `Architecture Source` to declare final scope.
   - Write each affected Entry into its partition under `.xirang/changes/<name>/`: `elements/<identity>.md` frontmatter for a Declaration Entry, `relationships/<relationship kind identity>.yaml` for `{operation, source, kind, target}` entries, `metamodel/<kind identity>.md` for Kind Entries, and `views/<view identity>.md` for Authored View Entries. Every Entry carries `operation` and its complete target state; `REMOVED` carries identity only; `relationships/` has no `MODIFIED`.
   - If Architecture Source is `None`, leave those partitions empty; do not invent structural changes from Contract changes alone.
   - Validate the Expected Semantic Model with `xirang arch validate --change "<name>" --json` and fix all errors before continuing.
9. Check compilation scaffolding before semantic-source validation.
   - Run `xirang instructions proposal --change "<name>" --json` and `xirang instructions design --change "<name>" --json`; compare each file with its current resolved definition and template.
   - Run `xirang instructions tasks --change "<name>" --json` and use deterministic `validateTaskStructure`. Support Actions and coarse `### Task N:`, Goal, Files, Requirements, Checks, Covers:, Verifies:, change-local `Verifies:` Element unit paths, Requirement/Scenario references, Command:, Evidence:, and Expect:. Do NOT invent semantic lint rules beyond the current templates. Do NOT judge whether a check is semantically sufficient.
10. Run combined change validation exactly once with `xirang validate --change "<name>" --json`. Do NOT run `xirang sync`.
    - ERROR from either scaffolding checks or combined change validation blocks ready-for-apply. Perform at most one repair pass, re-check once, and stop with the remaining blockers if any ERROR remains.
    - WARNING does not block ready-for-apply; retain it for the final summary.
11. After validation passes, run `xirang diff --change "<name>" --write`.
    - Treat `.xirang/changes/<name>/effective-change.md` as the only persistent effective-change report.
    - Verify its recorded status is Passed and its source and target fingerprints match the validated compilation.
    - If report generation fails, keep the failed report as evidence and stop; do not claim ready-for-apply.
12. Finish with `xirang status --change "<name>"`. Summarize artifacts created or updated, validation errors and warnings, effective-change report status, and readiness for `/skill:xirang-apply-change`.

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

Keep tasks coarse: `### Task N:`, `Goal`, `Files`, `Requirements`, and nested Checks; at most 5 Requirements per task. Preserve canonical headings, IDs, schema keys, paths, commands, BDD keywords, and code identifiers.
