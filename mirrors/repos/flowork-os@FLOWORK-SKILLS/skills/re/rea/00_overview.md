---
name: "Reverse Engineering Assistant (REA)"
category_id: "CAT-005"
category: "technology"
priority: 100
always: true
description: "Systematic reverse engineering methodology for binary triage, feature tracing, decompilation verification, patch diffing, and runtime observation."
---

# 🔬 REA: Reverse Engineering Assistant

## 1. Intent & Capability
The Reverse Engineering Assistant (REA) skill equips Flowork OS agents with structured, reproducible, and verifiable reverse engineering protocols across all target architectures:
- **Native Binaries**: ELF, PE, Mach-O, x86_64, ARM64.
- **Web & Desktop Apps**: JavaScript bundles, Source Maps, Electron ASAR packages.
- **Mobile Applications**: Android APK/AAB, Smali, DEX, JNI native libraries.
- **Runtime Instrumentation**: Dynamic call tracing, memory dump analysis, Frida scripting.

## 2. Core Methodology
1. **Seed Identification -> Routine Tracing -> Call Graph Mapping**: Identify entry strings/symbols, map to candidate functions, decompile, and verify control flow without assumptions.
2. **Structural Diffs -> Binary Patch Analysis -> Behavioral Delta Identification**: Inventory differences between target versions, compute basic-block deltas, and isolate security or logic alterations.
3. **Crash Signal Analysis -> Call Stack Reconstruction -> Root Cause Isolation**: Analyze crash dumps, reconstruct call frames, and locate faulting instructions accurately.
4. **Epistemic Rigor**: Zero speculation, strict provenance, verified terminal proof with Exit Code 0.
