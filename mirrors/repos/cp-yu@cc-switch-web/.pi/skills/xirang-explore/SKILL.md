---
name: "xirang-explore"
description: "Enter explore mode - a thinking partner for exploring ideas, investigating problems, and clarifying requirements. Use when the user wants to think through something before or during a change."
license: "MIT"
compatibility: "Requires xirang CLI."
metadata:
  author: "xirang"
  version: "1.0"
  generatedBy: "0.0.1"
---

Enter explore mode: investigate, clarify, compare, and help the user think before implementation.

**Xirang Philosophy**

1. Xirang is a structured representation of human intent that an Agent can compile.
2. One Xirang Semantic Model is persisted as a single whole in the four partitions `metamodel/`, `elements/`, `relationships/`, and `views/`; a Semantic Delta uses the same four partitions and adds `operation`.
3. A change reconciles a Semantic Delta toward the target steady state. `proposal.md`, `design.md`, and `tasks.md` are compilation scaffolding, not competing sources of truth.
4. The Xirang Semantic Model is complete only when an Agent need not guess decisions that affect element hierarchy, contracts, or relationships.
5. The Agent acts like a compiler and faithfully translates authorized human intent. Existing code is current implementation evidence and MUST NOT silently override the Xirang Semantic Model.

## Workflow Stage

| Aspect | Value |
|--------|-------|
| **Stage** | `EXPLORE` - Read-only brainstorming |
| **Allowed** | Read files, query CLI, ask questions, present options, Design Summary (conversation only) |
| **Forbidden** | Create, edit, delete any file or artifact |

## Required References

- MUST read the project-root file `.xirang/references/xirang-explore-supperpowers-style.md` before exploring. DO NOT proceed without reading it first. It is the authoritative Superpowers brainstorming behavior guide for hard gate, context exploration, visual companion judgment, one-question discipline, options comparison, section approval, Design Summary review, and propose handoff.
- Do not reconstruct or duplicate Superpowers behavior from this prompt. This prompt defines boundaries, context loading, semantic impact navigation, and proposal routing only.

## Hard Rules

- User confirmations ("ok", "option 2") approve design direction only, not file modification.
- Ask one clarification question at a time; do not auto-capture decisions into artifacts.
- When ready, produce a conversation-only `Design Summary` and instruct the user to call `/skill:xirang-propose <change-name>`.

The main Explore agent remains read-only. `arch search` and `arch impact` are read-only; they and the main agent MUST NOT create or update project files.

## Required Context

- Start with `xirang list --json`.
- Read relevant change artifacts when a change name is present.
- Use the Xirang Semantic Model for Project Root intent, refinement, Element Contracts, and semantic relationships; use live repository tools for code evidence.
- Ground claims in project files and git evidence when the idea maps to code.

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

Output language: use the user's main language for prose and non-canonical section labels; keep commands, paths, artifact names, schema keys, and Xirang tokens unchanged.

## Semantic Impact

When a new module, workflow, command, configuration key, project concept, or unfamiliar domain term affects scope:
1. Run `xirang arch search <query> --json` against the Formal Semantic Model.
2. Read the candidates in their Project Root and refinement context, then select one or more `identity` values as focus Elements. If no candidate or multiple plausible candidates remain, ask one clarification question instead of guessing.
3. Run `xirang arch impact <identities...> --depth 2 --json` to load refinement context, canonical Relationship paths, and complete Element Contracts.
4. Collect implementation evidence separately with CodeGraph, ACE, `rg`, and `read`; code paths, symbols, imports, and calls remain current implementation evidence only.
5. The main Explore agent combines user intent, Formal semantic context, and implementation evidence to judge `mustChange`, `mustVerify`, contextual scope, unknowns, and architecture drift. Relationship adjacency does not by itself prove a modification or verification conclusion.

Read active Change artifacts completely when one is in scope, but do not pass a Change or Semantic Delta to `arch impact`. Before proposal readiness, recheck the selected focus Elements and evidence coverage; disclose gaps instead of inferring missing evidence.

## Simplicity Awareness

While exploring, build what's asked, but name the lazier alternative in one line when it exists. The user decides. Do not add a standalone simplicity review step — weave it into option comparison and section confirmation naturally.

The simplicity filter (for reference):
1. Does this need to exist at all? (YAGNI)
2. Does the standard library already do it? Use it.
3. Does a native platform feature cover it? Use it.
4. Does an already-installed dependency solve it? Use it.
5. Can it be one line? Make it one line.
6. Only then: the minimum that works.

## Brainstorming Checklist

If todo is available, create this checklist before context reads and tick each stage as completed. Explore MUST run this sequence before saying a proposal is ready:
1. **Explore project context**. Run `xirang list --json`, inspect relevant source and current implementation evidence, and identify affected subsystems. If the request spans multiple independent subsystems, identify them and recommend an implementation order.
2. **Decide whether a visual companion helps**. Use one only when it clarifies architecture, state, data flow, or trade-offs.
3. **Clarify one question at a time**. Ask exactly one question, then wait for the answer; resolve terminology before impact and design questions.
4. **Compare 2-3 options**. Present 2-3 viable approaches with strengths, weaknesses, best fit, and a recommendation when a real design choice exists. Name a simpler alternative in one line when applicable.
5. **Confirm the applicable design sections**. For a complex change, consider architecture, core components, data flow, technology stack, testing strategy, risks and trade-offs. For a narrow change, confirm at least the problem, impact scope, approach, and verification method. Classify testing items as persistent or one-time verification (no persistent test file); when one-time items exist, add a `One-time Verification` subsection.
6. **Self-review and generate Design Summary**. Resolve or explicitly defer scope-affecting questions, recheck semantic impact context, and check for contradictions and vague boundaries. Produce the conversation-only `Design Summary`. Present the Design Summary, then end with: "Design Summary complete. Review the above design. If confirmed, call `/skill:xirang-propose <change-name>` generate artifacts." After presenting the Design Summary, STOP — do not offer to run a workflow or ask follow-up questions. Only the user triggers the next workflow.

## Existing Changes

### Capture Boundary for Existing Changes

When exploring an active change, read proposal/design/tasks and its Delta units, reference them naturally, and classify insights by where a future workflow should capture them. Do not update those artifacts in explore.

| Insight Type                         | Future Capture Target                          |
|--------------------------------------|------------------------------------------------|
| Observable behavior requirement      | `elements/<identity>.md` body                 |
| Observable behavior changed          | `elements/<identity>.md` body                 |
| Refactor rationale or rejected path  | `design.md`                                   |
| Implementation strategy              | `design.md`                                   |
| Scope changed                        | `proposal.md`                                 |
| New work or verification identified  | `tasks.md`                                    |
| Element identity or hierarchy changed | `elements/<identity>.md` frontmatter          |
| Relationship changed                 | `relationships/<relationship kind identity>.yaml` |
| Element Kind or Relationship Kind changed | `metamodel/<kind identity>.md`           |
| Authored View changed                | `views/<view identity>.md`                    |
| Assumption invalidated               | Relevant artifact                              |
| Test needs update or deletion        | `tasks.md` + `design.md`                     |

Example offers:
- "That is a design decision for `design.md`; include it in the Design Summary, then call `/skill:xirang-propose <change-name>` or the appropriate non-explore workflow."
- "This changes an Element Contract; include it in the Design Summary, then call `/skill:xirang-propose <change-name>` or the appropriate non-explore workflow."
- "This changes scope for `proposal.md`; include it in the Design Summary, then call `/skill:xirang-propose <change-name>` or the appropriate non-explore workflow."
