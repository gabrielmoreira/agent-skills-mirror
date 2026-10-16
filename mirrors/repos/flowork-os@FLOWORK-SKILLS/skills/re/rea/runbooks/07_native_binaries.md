<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-THEME-NATIVE-BINARIES
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-THEME-NATIVE-BINARIES"
name: "REA Theme Directive: Native Binaries & Artifacts Analysis"
theme: "Native Executable & Assembly Analysis (ELF, PE, Mach-O, NativeAOT)"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "ghidra"
  - "ida pro"
  - "disassembly"
  - "decompilation"
  - "elf pe macho"
  - "nativeaot"
---

# REA Theme Directive: Native Binaries & Artifacts Analysis

## 1. Trigger Objective & Operational Mandate
Disassemble, decompile, and analyze compiled machine code across x86_64, ARM64, and managed NativeAOT binaries using industry-grade disassemblers.

## 2. Parameter & Input Specification
- `binary_path`: Absolute path to native binary executable or shared library (.so, .dll, .dylib) (required)
- `architecture`: Target architecture hint (e.g. x86_64, aarch64, armv7, riscv) (optional)
- `tool_preference`: Preferred analysis tool: ghidra, ida, hopper, rizin, gdb (optional)

## 3. Systematic Execution Workflow
1. Binary Header Triage: Inspect file headers (magic bytes, architecture, endianness, sections, imports/exports, security flags ASLR/DEP/NX).
2. Symbol & String Extraction: Extract ASCII/Unicode strings, demangle C++/Rust symbols, locate import address tables (IAT/GOT).
3. Headless Decompilation: Invoke headless decompiler (Ghidra/IDA) in isolated workspace without altering source binary.
4. Calling Convention & Struct Recovery: Recover function signatures, calling conventions (cdecl, fastcall, sysv), and complex struct layouts.
5. Cryptographic & Protocol Analysis: Identify cryptographic constants, S-boxes, hash algorithms, and proprietary packet encodings.

## 4. Reverse Engineering Epistemic Discipline
- Analysis engines must run read-only on ephemeral databases without writing back to original binaries.
- Account for compiler optimizations (inlining, loop unrolling, register reuse).
- Handle NativeAOT structures (.NET Native) by decoding runtime type metadata tables.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
