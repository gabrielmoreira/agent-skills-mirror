<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-TRIG-TRACE-CRASH
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-TRIG-TRACE-CRASH"
name: "REA Guided Workflow: Trace Crash"
theme: "Crash, Segfault & Fault Symptom Analysis"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "crash trace"
  - "segfault"
  - "core dump"
  - "panic analysis"
  - "fault triage"
---

# REA Guided Workflow: Trace Crash

## 1. Trigger Objective & Operational Mandate
Correlate a crash symptom, panic message, or segfault with static disassembled paths and runtime memory state to determine exact root cause.

## 2. Parameter & Input Specification
- `executable_path`: Path to binary executable under analysis (required)
- `crash_symptom`: Crash description, error code, signal (e.g. SIGSEGV, EXCEPTION_ACCESS_VIOLATION) (required)
- `fault_address`: Instruction pointer (RIP/EIP/PC) or memory address where fault occurred (optional)
- `core_dump_path`: Path to core dump or minidump file (optional)
- `stack_trace`: Raw stack trace or register dump string (optional)

## 3. Systematic Execution Workflow
1. Triage Crash Artifact: Parse crash log, core dump, or register state (registers, flags, signal).
2. Map Faulting Instruction: Locate fault address in disassembler; identify the exact machine instruction causing memory/CPU fault.
3. Reconstruct Stack Frame: Unwind call stack to discover upstream callers, parameter values, and return addresses.
4. Dataflow & Taint Backtracking: Trace register/variable values backward to identify the unvalidated input, NULL pointer, or buffer overflow point.
5. Formulate & Verify Hypothesis: Determine whether root cause is memory corruption, race condition, type confusion, or unhandled exception.

## 4. Reverse Engineering Epistemic Discipline
- Do not accept the immediate crashing instruction as the root defect; always trace back to original corrupted state.
- Distinguish deterministic reproducibility from transient timing/concurrency bugs.
- Verify all memory offsets against relocations, ASLR slide, and base addresses.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
