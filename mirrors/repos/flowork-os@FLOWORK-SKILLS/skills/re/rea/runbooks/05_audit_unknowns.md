<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-TRIG-AUDIT-UNKNOWNS
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-TRIG-AUDIT-UNKNOWNS"
name: "REA Guided Workflow: Audit Residual Unknowns"
theme: "Residual Unknowns & Hypothesis Auditing"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "residual unknowns"
  - "hypothesis audit"
  - "epistemic tracking"
  - "unresolved questions"
  - "rea unknown"
---

# REA Guided Workflow: Audit Residual Unknowns

## 1. Trigger Objective & Operational Mandate
Audit current unresolved hypotheses, missing symbols, and residual questions against qualified evidence to eliminate reversing blindspots.

## 2. Parameter & Input Specification
- `scope`: Target investigation scope or subsystem name (required)
- `target_artifact`: Artifact path being audited (optional)
- `unknown_id`: Specific tracked unknown identifier to re-evaluate (optional)

## 3. Systematic Execution Workflow
1. Catalog Active Unknowns: Query and list all tracked unknowns, hypotheses, and unverified assumptions from previous turns.
2. Evaluate Against Fresh Evidence: Cross-check each unknown against newly discovered strings, decompilations, or runtime captures.
3. Falsify or Promote: If evidence disproves hypothesis, mark rejected with counter-evidence; if proven, promote to Observation/Derivation.
4. Prioritize Remaining Unknowns: Rank remaining unknowns by architectural impact and risk to target objectives.
5. Generate Targeted Resolution Plan: Specify exact tools and experiments required to resolve highest-priority unknowns.

## 4. Reverse Engineering Epistemic Discipline
- Never silently drop an unknown because it is difficult to answer.
- Every promoted claim must link directly to immutable artifact evidence.
- Maintain revision tracking on unknowns to prevent concurrent overwrites.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
