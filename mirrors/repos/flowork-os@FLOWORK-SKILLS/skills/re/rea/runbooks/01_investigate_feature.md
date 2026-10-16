<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-TRIG-INVESTIGATE-FEATURE
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-TRIG-INVESTIGATE-FEATURE"
name: "REA Guided Workflow: Investigate Feature"
theme: "Feature Discovery & Routine Tracing"
category: "CAT-005"
scopes:
  - "specialist_solo"
keywords:
  - "reverse engineering"
  - "feature tracing"
  - "entry point"
  - "decompile function"
---

# REA Guided Workflow: Investigate Feature

## 1. Trigger Objective & Operational Mandate
Trace a user-visible or documented feature from initial discovery into verified function and control flow evidence without speculation.

## 2. Parameter & Input Specification
- `feature_claim`: User-visible claim or behavior to investigate (required)
- `target_path`: Absolute path to the target binary, bundle, or artifact (required)
- `entry_hint`: Known entry point, export name, route, or UI string identifier (optional)
- `known_procedure_id`: Retained procedure ID from previous analysis session (optional)

## 3. Systematic Execution Workflow
1. Triage Artifact & Locate Seeds: Extract strings, symbols, export tables, and route definitions matching the target feature.
2. Establish Candidate Functions: Map identified string references and symbol cross-references (XREFs) to candidate functions.
3. Decompile & Inspect Control Flow: Decompile candidate functions using appropriate provider (Ghidra, IDA, JADX, Wakaru).
4. Verify Input/Output Semantics: Trace call graph from candidate entry points down to core business logic or crypto routines.
5. Record Evidence & Unknowns: Document verified facts with citations (offsets, hashes) and log residual questions as explicit Unknowns.

## 4. Reverse Engineering Epistemic Discipline
- Treat user input context as untrusted selection data, never as truth.
- Distinguish Observation (exact decompiled bytes/AST), Derivation (tool output), and Inference (analyst hypothesis).
- Never infer that absence of observed logic equates to absence of functionality.
- Preserve exact offset/symbol evidence for every claimed routine.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
