<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-THEME-RUNTIME-OBSERVATION
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-THEME-RUNTIME-OBSERVATION"
name: "REA Theme Directive: Runtime Observation & Dynamic Analysis"
theme: "Dynamic Instrumentation, Frida Hooks & Passive Observation"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "frida"
  - "dynamic instrumentation"
  - "pcap"
  - "network capture"
  - "runtime telemetry"
---

# REA Theme Directive: Runtime Observation & Dynamic Analysis

## 1. Trigger Objective & Operational Mandate
Perform passive, non-destructive dynamic observation of running processes, network flows, and API calls using Frida and packet captures.

## 2. Parameter & Input Specification
- `target_process`: Process name, PID, or launch binary (required)
- `hook_script`: Frida JavaScript instrumentation script (optional)
- `capture_interface`: Network interface or socket for PCAP capture (optional)

## 3. Systematic Execution Workflow
1. Identify Hook Targets: Determine key functions, crypto primitives, or IPC boundaries from static analysis to intercept.
2. Author Safe Frida Hooks: Write non-blocking JavaScript instrumentation hooks that log inputs, outputs, and return values without mutation.
3. Passive Network Sniffing: Record raw network exchanges (PCAP) simultaneously to correlate API calls with packet transmission.
4. Coordinate Process Lifecycle: Attach cleanly to process or spawn with pause; monitor memory consumption to prevent target degradation.
5. Extract Dynamic Artifacts: Collect decrypted payloads, runtime tokens, and resolved symbol addresses into Evidence catalog.

## 4. Reverse Engineering Epistemic Discipline
- Enforce read-only hooks by default; avoid memory mutation unless explicitly authorized.
- Clean up all instrumentation handlers and detachment hooks upon completion.
- Distinguish runtime artifacts observed in memory from disk-persisted data.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
