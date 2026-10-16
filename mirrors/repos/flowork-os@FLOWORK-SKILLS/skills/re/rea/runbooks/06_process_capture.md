<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-TRIG-BOUNDED-CAPTURE
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-TRIG-BOUNDED-CAPTURE"
name: "REA Guided Workflow: Prepare Bounded Process Capture"
theme: "Bounded Dynamic Process Capture & Telemetry"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "process capture"
  - "bounded execution"
  - "runtime trace"
  - "telemetry sandbox"
  - "rea capture"
---

# REA Guided Workflow: Prepare Bounded Process Capture

## 1. Trigger Objective & Operational Mandate
Design and execute a bounded, controlled runtime capture experiment that answers specific behavioral questions with zero collateral damage.

## 2. Parameter & Input Specification
- `behavior_question`: Behavioral question the capture must answer and explicit stopping condition (required)
- `executable`: Command name or executable path requested for scenario (required)
- `working_directory`: Working directory requested for the scenario (required)
- `prior_capture_evidence_id`: Retained process capture evidence to compare or extend (optional)

## 3. Systematic Execution Workflow
1. Define Bounded Scope: Formulate precise question, timeout limit, max memory/disk threshold, and non-destructive boundaries.
2. Instrument Observation Points: Select minimal telemetry hooks (system calls via strace/dtruss, network pcap, or Frida API hook).
3. Execute Under Quarantine: Run the target in an isolated, unprivileged sandbox with bounded CPU and network constraints.
4. Capture & Filter Telemetry: Collect traces matching the targeted behavior while discarding irrelevant background noise.
5. Correlate with Static Evidence: Align observed runtime calls/packets with static disassembly offsets and emit Evidence report.

## 4. Reverse Engineering Epistemic Discipline
- Never execute untrusted binaries outside strict sandbox boundaries.
- Always enforce hard timeouts and max-output buffer limits to prevent process lockup.
- Ensure capture tools do not alter target execution timing in ways that mask race conditions.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
