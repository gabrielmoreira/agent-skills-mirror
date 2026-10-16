<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-TRIG-COMPARE-VERSIONS
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-TRIG-COMPARE-VERSIONS"
name: "REA Guided Workflow: Compare Application Versions"
theme: "Binary & Artifact Version Comparison (Patch Diffing)"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "version diff"
  - "patch diffing"
  - "binary comparison"
  - "artifact diff"
  - "rea differential"
---

# REA Guided Workflow: Compare Application Versions

## 1. Trigger Objective & Operational Mandate
Compare two shipped application artifacts through complete structural inventory and differential static/runtime evidence without equating missing data with unchanged behavior.

## 2. Parameter & Input Specification
- `left_target_path`: Absolute path to the baseline/earlier target artifact (required)
- `right_target_path`: Absolute path to the candidate/later target artifact (required)
- `left_manifest_id`: Retained baseline artifact graph manifest (optional)
- `right_manifest_id`: Retained candidate artifact graph manifest (optional)
- `focus_occurrence_id`: Specific component or function ID to focus comparison on (optional)

## 3. Systematic Execution Workflow
1. Inventory & Structural Diff: Catalog container contents, file hashes, sizes, exported symbols, and dependency graph between versions.
2. Binary & AST Delta Mapping: Compute function-level and basic-block deltas on modified modules using bindiff/diaphora or AST comparison.
3. Identify Added & Removed Behaviors: Isolate added, deleted, or mutated functions, data structures, and constants.
4. Security & Patch Impact Assessment: Inspect changes for vulnerability fixes, API alterations, protocol updates, or logic deprecation.
5. Synthesize Differential Evidence: Compile comprehensive version change matrix with side-by-side evidence citations.

## 4. Reverse Engineering Epistemic Discipline
- Do not assume unreferenced code in candidate version is dead without runtime or static proof.
- Never declare behavior unchanged purely based on name similarity or identical export signatures.
- Explicitly record compiler optimization artifacts vs true source logic changes.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
