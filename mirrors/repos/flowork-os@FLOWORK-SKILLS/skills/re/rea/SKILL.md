---
name: "Reverse Engineering Assistant (REA)"
category_id: "CAT-005"
category: "technology"
description: "Systematic reverse engineering methodology for binary triage, feature tracing, decompilation verification, patch diffing, and runtime observation."
keywords: ["reverse_engineering","binary_analysis","decompilation","disassembly","patch_diffing","control_flow","symbol_extraction","fault_localization","crash_analysis","dynamic_instrumentation","ghidra","jadx","electron_deobfuscation","android_reversing","call_stack_trace","epistemic_discipline","runtime_observation","static_analysis","exit_code_0","quality_control"]
provenance: "Engineered from Reverse Engineering Anything (REA) framework under Flowork OS Sovereign Architecture."
---

# 🔬 SKILL: Reverse Engineering Assistant (REA)

## 1. Intent & Trigger Boundaries
Comprehensive operational runbook and systematic standard operating procedure for reverse engineering across native binaries (ELF/PE/Mach-O), managed runtimes (Android/DEX/Smali), and web/desktop apps (JavaScript/Electron). Activate this skill whenever tasked with binary analysis, vulnerability triage, feature extraction, patch diffing, or crash fault localization.

## 2. Standard Operating Procedures (SOP)
Follow the 6-Stage REA Analysis Protocol:
1. **Triage & Artifact Fingerprinting**:
   - Extract metadata, hashes (SHA-256), entropy, compiler flags, and imported/exported symbols.
   - Run string isolation and symbol cross-referencing to find candidate routines without speculative jumps.
2. **Feature Tracing & Decompilation**:
   - Decompile target routines using appropriate toolchains (Ghidra, IDA, JADX, Wakaru).
   - Trace control flow from known entry points or API routes down to core algorithmic/cryptographic logic.
3. **Patch Diffing & Version Comparison**:
   - Perform structural inventory diffs, AST delta mapping, and basic-block delta comparison.
   - Isolate mutated functions, modified constant tables, and ABI alterations.
4. **Fault Localization & Crash Tracing**:
   - Reconstruct crash call stacks, unwind stack frames, and map register state to decompiled source lines.
5. **Dynamic Process Observation & Telemetry**:
   - Deploy non-coercive runtime hooks (Frida, eBPF, strace) in bounded environments.
   - Capture I/O boundaries, IPC payloads, and decrypted in-memory buffers.
6. **Detailed Sub-Runbooks**:
   - Inspect specific domain procedures in `{engine_root}/skills/rea/runbooks/`:
     - `runbooks/01_investigate_feature.md` (Feature Investigation)
     - `runbooks/02_compare_versions.md` (Version Diffing)
     - `runbooks/03_verify_reconstruction.md` (Reconstruction Fidelity)
     - `runbooks/04_trace_crash.md` (Crash Tracing)
     - `runbooks/05_audit_unknowns.md` (Unknowns Audit)
     - `runbooks/06_process_capture.md` (Bounded Capture)
     - `runbooks/07_native_binaries.md` (Native Binaries)
     - `runbooks/08_javascript_electron.md` (JS/Electron Apps)
     - `runbooks/09_android_apps.md` (Android Applications)
     - `runbooks/10_runtime_observation.md` (Runtime Observation)
     - `runbooks/11_epistemic_discipline.md` (Epistemic Discipline)
     - `runbooks/12_toolchain_recovery.md` (Toolchain Diagnostics)

## 3. Strict Prohibitions & Epistemic Discipline
- **Observation vs Inference**: Never state analyst hypothesis as fact. Label decompiled bytes as *Observation*, tool output as *Derivation*, and hypotheses as *Inference*.
- **No False Equivalences**: Never infer that the absence of observed logic equates to absence of functionality.
- **Portability Invariant**: No hardcoded host absolute paths. Use relative offsets and portable identifiers.
- **Artifact Isolation**: All raw disassembly outputs, Ghidra projects, or unpack dumps must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be cleaned up post-analysis.

## 4. Verification & Exit Code 0 Proof
- Every reverse engineering conclusion must be attested with tangible physical proof: exact offsets, byte sequences, cryptographic hashes, or verified terminal execution with Exit Code 0.
