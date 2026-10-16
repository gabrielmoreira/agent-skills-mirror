<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-THEME-ANDROID-APPS
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-THEME-ANDROID-APPS"
name: "REA Theme Directive: Android Application Reverse Engineering"
theme: "Android APK, DEX Bytecode & Native JNI Analysis"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "android reverse"
  - "apk decompilation"
  - "dex bytecode"
  - "jadx"
  - "smali"
  - "native jni"
---

# REA Theme Directive: Android Application Reverse Engineering

## 1. Trigger Objective & Operational Mandate
Decompile, analyze, and inspect Android packages (APK), DEX bytecode, AndroidManifest permissions, and native JNI libraries.

## 2. Parameter & Input Specification
- `apk_path`: Absolute path to APK or AAB package (required)
- `package_name`: Target Android package identifier (optional)
- `decompiler`: Decompiler engine: jadx-headless, apktool, baksmali (optional)

## 3. Systematic Execution Workflow
1. Package Unpacking: Decompress APK; extract classes.dex, resources.arsc, AndroidManifest.xml, and lib/ directory.
2. Manifest & Component Audit: Parse AndroidManifest to map exported activities, services, broadcast receivers, and intent filters.
3. Bytecode Decompilation: Run headless JADX to decompile DEX bytecode into clean Java/Kotlin sources.
4. Native Bridge Inspection: Identify System.loadLibrary calls and cross-reference Java native declarations with JNI exports in .so files.
5. Dynamic ADB Telemetry: Monitor logcat, intent dispatch, and file permissions in connected Android test environment.

## 4. Reverse Engineering Epistemic Discipline
- Always inspect native .so binaries alongside DEX code to detect root checks and obfuscation.
- Respect Android security models and certificate pinning mechanisms.
- Isolate untrusted APKs; do not install on production host machines.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
