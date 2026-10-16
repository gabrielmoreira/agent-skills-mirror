---
priority: 90
keywords: ["reverse_engineering", "binary_analysis", "decompilation", "disassembly", "patch_diffing"]
---

# 📊 PERFORMANCE & FIDELITY RUBRIC: REA

## Evaluation Metrics
1. **Decompilation Fidelity**: Semantic equivalence between decompiled AST and machine bytecode.
2. **False Positive Rate**: Zero speculation on unobserved routines or speculative control flows.
3. **Trace Completeness**: Unbroken provenance from user-facing feature seed to verified binary offset.
4. **Portability**: Toolchain scripts must execute cross-platform (Linux/macOS/Windows).
