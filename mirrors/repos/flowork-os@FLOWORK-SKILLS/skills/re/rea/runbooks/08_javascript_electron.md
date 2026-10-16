<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-THEME-JAVASCRIPT-ELECTRON
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-THEME-JAVASCRIPT-ELECTRON"
name: "REA Theme Directive: JavaScript, Web & Electron Reverse Engineering"
theme: "JavaScript, Web & Electron Deobfuscation"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "electron"
  - "asar"
  - "javascript deobfuscation"
  - "source maps"
  - "wakaru"
  - "v8 inspector"
---

# REA Theme Directive: JavaScript, Web & Electron Reverse Engineering

## 1. Trigger Objective & Operational Mandate
Extract, deobfuscate, and reconstruct client JavaScript, Electron ASAR packages, Webpack bundles, and Node.js applications.

## 2. Parameter & Input Specification
- `app_path`: Path to Electron app, ASAR archive, or minified JavaScript bundle (required)
- `source_map_path`: Path or URL to source maps if available (optional)
- `deobfuscator`: Preferred deobfuscation engine: wakaru, webcrack, js-beautify (optional)

## 3. Systematic Execution Workflow
1. Unpack Container: Extract Electron app.asar into isolated workspace using read-only unpacking tools.
2. Map Architecture & IPC: Inspect package.json, main script, preload scripts, and IPC communication channels (ipcRenderer / ipcMain).
3. Recover Source Maps: Locate embedded or external .map files; reconstruct original project file structure via restore tools.
4. AST Deobfuscation: Run automated un-minification and AST pattern simplification (Wakaru/Webcrack) to recover readable variables and syntax.
5. Trace API & Secret Exposure: Audit reconstructed code for hardcoded credentials, backend endpoints, and security bypasses.

## 4. Reverse Engineering Epistemic Discipline
- Always inspect preload scripts for nodeIntegration vulnerabilities and contextIsolation bypasses.
- Do not execute malicious obfuscated JS; perform static AST analysis in isolated environment.
- Verify deobfuscated output against original minified code to prevent hallucinated logic.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
