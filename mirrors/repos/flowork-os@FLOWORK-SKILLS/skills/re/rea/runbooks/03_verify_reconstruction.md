<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-TRIG-VERIFY-RECONSTRUCTION
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-TRIG-VERIFY-RECONSTRUCTION"
name: "REA Guided Workflow: Verify Reconstruction"
theme: "Clean-Room Reconstruction & Parity Verification"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "reconstruction"
  - "clean room"
  - "reimplementation"
  - "parity verification"
  - "rea verify"
---

# REA Guided Workflow: Verify Reconstruction

## 1. Trigger Objective & Operational Mandate
Evaluate a finite reimplementation or clean-room reconstruction against retained ground-truth evidence to guarantee complete semantic fidelity.

## 2. Parameter & Input Specification
- `target_path`: Absolute path to the original binary or target artifact (required)
- `reconstruction_path`: Path to clean-room reconstructed code or specification (required)
- `evidence_id`: Retained baseline evidence snapshot ID (required)
- `verification_scope`: Specific subsystem, algorithm, or protocol to verify (optional)

## 3. Systematic Execution Workflow
1. Boundary & Interface Conformance: Verify reconstructed public interfaces, data layouts, structs, and calling conventions match original binary.
2. Semantic Equivalence Check: Step through critical algorithmic branches and verify state mutations match original decompilation step-by-step.
3. Edge-Case & Error Path Parity: Validate behavior under invalid inputs, boundary values, and simulated error conditions.
4. Dynamic Behavioral Test: Run differential fuzzing or automated test suites against both original target (in bounded sandbox) and reconstructed code.
5. Attestation & Gap Analysis: Produce formal parity matrix certifying verified components and listing remaining discrepancies as Unknowns.

## 4. Reverse Engineering Epistemic Discipline
- Reconstruction verification must reject 'looks similar' assertions—only mathematical or behavioral equivalence is accepted.
- Test vectors must be derived strictly from original binary observations.
- All assumed external side-effects must be isolated and explicitly mocked.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
