---
name: "xirang-apply-change"
description: "Implement tasks from an Xirang change. Use when the user wants to start implementing, continue implementation, or work through tasks."
license: "MIT"
compatibility: "Requires xirang CLI."
metadata:
  author: "xirang"
  version: "1.0"
  generatedBy: "0.0.1"
---

Implement tasks from an Xirang change.

**Xirang Philosophy**

1. Xirang is a structured representation of human intent that an Agent can compile.
2. One Xirang Semantic Model is persisted as a single whole in the four partitions `metamodel/`, `elements/`, `relationships/`, and `views/`; a Semantic Delta uses the same four partitions and adds `operation`.
3. A change reconciles a Semantic Delta toward the target steady state. `proposal.md`, `design.md`, and `tasks.md` are compilation scaffolding, not competing sources of truth.
4. The Xirang Semantic Model is complete only when an Agent need not guess decisions that affect element hierarchy, contracts, or relationships.
5. The Agent acts like a compiler and faithfully translates authorized human intent. Existing code is current implementation evidence and MUST NOT silently override the Xirang Semantic Model.

For workflow-managed writes, read the resolved file definition before its instruction and template, and MUST NOT copy definitions, config projections, or reasoning into artifacts.

## Flow Outline

1. Step 1: Preparation — read `.xirang/references/xirang-apply-step-1-preparation.md`.
2. Step 2: Pre-flight scan — read `.xirang/references/xirang-apply-step-2-preflight-scan.md`.
3. Step 3: Isolation router — read the one method reference selected by Step 1; do not load mutually exclusive methods.
4. Phase 0 implementation — Master executes pending tasks serially with the implementation discipline below.
5. Step 4: Phase 1 verification — read `.xirang/references/xirang-apply-step-4-phase1-verification.md` and delegate to the clean-context `xirang-reviewer` agent.
6. Step 5: Phase 2 optimization — read `.xirang/references/xirang-apply-step-5-phase2-optimization.md` and delegate to the clean-context `xirang-optimizer` agent when eligible.
7. Step 6: Phase 3 seal — read `.xirang/references/xirang-apply-step-6-phase3-seal.md`.
8. Step 7: Output — read `.xirang/references/xirang-apply-step-7-output.md`.

## Implementation Discipline

- Before implementation, run `xirang arch query <identity> --relations --depth 2 --contract --json`, then read the returned Element Contract and current code.
- Process unfinished `## Remediation` `[code_fix]` and `[artifact_fix]` items before pending tasks. Finish every Check in the current task before starting the next; never execute tasks in parallel.
- Assess interface testability before writing tests for each behavior/code Check: inject external dependencies, prefer returned results over hidden side effects, and keep the public interface minimal.
- Write or update a targeted test first. Exercise public behavior; mock only injected system boundaries, never internal collaborators.
- Run the declared or equivalent targeted command and confirm the expected RED before implementation; make the minimal fix, then rerun the same check for GREEN.
- Non-runtime text/artifact Checks do not require an artificial RED; run their declared command or inspect `Evidence:` and `Expect:` for final proof.
- Prefer deletion, standard library, native platform support, installed dependencies, direct expressions, then minimal new code. Add no abstraction, dependency, or file unless required.
- Update Check and remediation checkboxes only after their evidence passes. Preserve canonical headings, schema keys, IDs, commands, template tokens, and document-language projection.
- For unexpected failures, read the full error, classify the layer, compare a working pattern, state one hypothesis, change one variable, and rerun the same check. Pause after two consecutive identical normalized errors or three failed fixes in one task.

When Phase 3 seal passes, end with an explicit call-to-action: `Archive ready. Run /skill:xirang-archive-change <change-name> to complete the workflow.`
