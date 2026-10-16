---
priority: 99
always: true
---

# 🛡️ SOVEREIGN SKILL RULES: REA

## 1. Reason Dispatch Matrix
| Trigger / Signal | Target Operation | Required Verification |
| :--- | :--- | :--- |
| `investigate`, `trace_feature` | Trace user-visible feature to binary routine | Verified offset & decompiled AST |
| `compare`, `diff_patch` | Compare versions or patch deltas | Basic-block delta & symbol diff |
| `verify_decompilation` | Audit decompilation fidelity against assembly | Disassembly vs AST congruence |
| `trace_crash`, `fault` | Call stack reconstruction & root cause | Register state & crash offset |
| `dynamic_capture`, `frida` | Bounded process capture & instrumentation | Memory/trace dump in `{effective_ws}/.FL_BIN/scratch/` |

## 2. Epistemic Invariants
1. Distinguish physical observation from analyst inference at all times.
2. Every claim must cite concrete evidence: offsets, file hashes, or register values.
3. Cleanliness: Raw decompilation artifacts must remain in `{effective_ws}/.FL_BIN/scratch/`.
4. Verification: Terminal confirmation with Exit Code 0 proof before closing analysis.
