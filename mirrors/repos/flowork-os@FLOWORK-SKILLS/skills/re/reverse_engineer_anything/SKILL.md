---
name: "Reverse Engineer Anything"
description: "Sovereign runbook for multi-target reverse engineering, decompilation, binary inspection, and clean-room reconstruction across native binaries, Electron/ASAR, APK, and managed code"
keywords: ["reverse engineering","decompilation","binary analysis","disassembly","ghidra","hopper","ida pro","jadx","electron asar","static analysis","dynamic analysis","call graph","clean room design","ast parsing","firmware extraction","evidence graph","pe elf macho","apk analysis","symbol recovery","pseudocode"]
---

# ⚙️ SKILL: Reverse Engineer Anything

## 1. Intent & Trigger Boundaries
Defensive, multi-target reverse engineering SOP for extracting underlying architectures, logic flows, state models, and algorithmic patterns from shipped artifacts (native binaries, Electron/ASAR bundles, Android APKs, managed .NET/Java assemblies, and firmware images).

### Trigger Boundaries:
- User requests extracting or understanding a feature from a binary executable, closed application, or compiled package without available source code.
- Decompiling, disassembling, and inspecting PE (Windows), ELF (Linux), Mach-O (macOS), APK (Android), or ASAR (Electron) files.
- Bridging REA (`morluto/rea`) tools via CLI or integrating native reverse engineering engines (Ghidra, Hopper, IDA Pro, JADX, Binwalk).
- Reconstructing closed-source functionality into clean-room, unencumbered implementation code adhering to sovereign specifications.

## 2. Standard Operating Procedures

### Phase 1: Target Ingestion & Triage
1. **Target Identification & Format Routing:**
   - **Electron / JavaScript / ASAR**: Route directly to static JS analysis without heavy engines:
     ```bash
     npx -y rea-agents@latest analyze-javascript-application /path/to/extracted/app --json
     ```
   - **Native Binary (ELF / PE / Mach-O)**: Inspect file architecture:
     ```bash
     file /path/to/binary
     readelf -h /path/to/binary
     objdump -f /path/to/binary
     ```
   - **Android APK**: Unpack and inspect package manifest and Dalvik bytecode via headless JADX:
     ```bash
     jadx -d output_dir /path/to/app.apk
     ```
   - **Managed Assembly (.NET / Mono / JVM)**: Inspect metadata and IL/bytecode with ILSpy/javap.
   - **Firmware Blob**: Perform entropy calculation and region carving with `binwalk -e` or `unblob`.

### Phase 2: Engine Selection & Headless Decompilation
1. **Engine Selection Protocol:**
   - For native Linux/macOS binaries: Route to headless Ghidra (requires JDK 21+ and `GHIDRA_INSTALL_DIR`) or Hopper (virtual display `Xvfb`).
   - For Windows PE x64 binaries: Route to Windows Ghidra P0 adapter or IDA Pro headless database supervisor.
   - Run readiness check scoped to provider:
     ```bash
     npx -y rea-agents@latest doctor --provider ghidra --json
     ```
2. **Deterministic Binary Decomposition:**
   - Extract symbol tables, exported functions, and imported dynamic link libraries:
     ```bash
     nm -D /path/to/binary
     objdump -T /path/to/binary
     strings -a -n 8 /path/to/binary | grep -E "https?://|API|auth|secret"
     ```
   - Trace control flow graphs (CFG) and identify high-value target routines (entry points, cryptography routines, IPC handlers).

### Phase 3: Evidence Graph Construction & Analysis
1. Extract inline Evidence records:
   - Identify observed facts (addresses, signatures, string literals, call hierarchy).
   - Differentiate strictly between verified facts, decompiler inferences, and unknown boundary conditions.
2. Synthesize API & state transition models:
   - Document payload serialization schemas, request headers, IPC protocol channels, and cryptographic primitives.

### Phase 4: Clean-Room Reconstruction
1. Build an unencumbered sovereign specification document containing:
   - Inputs, outputs, data formats, validation rules, state machine transitions, and error behaviors.
2. Implement native code (Rust, TypeScript, Python) strictly against the specification, ensuring zero proprietary code leakage and full independent implementation.

## 3. Strict Prohibitions & Edge Cases
- **Absolute Portability**: Never hardcode host absolute paths (`/home/...`, `C:\...`). Always use relative or dynamic path resolution.
- **Zero Vibe Reversing**: Never hallucinate API schemas or crypto keys; every claim must be backed by concrete disk strings, disassembler offsets, or decompiler pseudocode.
- **Session Isolation**: Never pollute the workspace root with decompiler database dumps or temporary projects. Isolate all caches, dumps, and extractions to `.FL_BIN/`.

## 4. Verification & Exit Code 0 Proof
1. Verify static parsing output or CLI tool invocation:
   ```bash
   npx -y rea-agents@latest doctor --json
   ```
2. For extracted code or clean-room implementation, execute test suite and confirm Exit Code 0 across all verification steps.
