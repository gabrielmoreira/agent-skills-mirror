<!-- ========================================================================================= -->
<!-- 🏛️ FLOWORK OS SOVEREIGN DIRECTIVE & TRIGGER: REA-WORKFLOW-TOOLCHAIN-RECOVERY
<!-- Co-authored-by: Flowork OS <agent@floworkos.com>                                            -->
<!-- Sourced & Extracted from REA (Reverse Engineering Anything)                                 -->
<!-- ========================================================================================= -->

---
trigger_id: "REA-WORKFLOW-TOOLCHAIN-RECOVERY"
name: "REA Workflow: Toolchain Diagnostics & Fail-Closed Recovery"
theme: "Toolchain Health, MCP Integration & Fail-Closed Diagnostics"
category: "CAT-005"
scopes:
  - "specialist_solo"
  - "specialist_group"
  - "universal_all"
keywords:
  - "toolchain diagnostics"
  - "fail closed"
  - "mcp health"
  - "provider recovery"
  - "environment setup"
---

# REA Workflow: Toolchain Diagnostics & Fail-Closed Recovery

## 1. Trigger Objective & Operational Mandate
Verify analysis provider readiness, handle tool failures gracefully, and maintain fail-closed environment integrity.

## 2. Parameter & Input Specification
- `provider_name`: Target provider: ghidra, ida, jadx, wakaru, unblob, rizin (required)
- `diagnostic_level`: Level of diagnostic check: quick, deep, repair (optional)

## 3. Systematic Execution Workflow
1. Check Tool Presence: Probe PATH, environment variables, and configured server ports for requested engine.
2. Validate Sandbox & Permissions: Ensure scratch workspaces ({effective_ws}/.FL_BIN/scratch/) have write access while source files remain read-only.
3. Execute Health Probe: Run minimal canary analysis (e.g. disassemble 4-byte NOP binary) to confirm exit code 0.
4. Graceful Degradation: If preferred provider is unavailable, automatically fall back to secondary tool (e.g. Ghidra -> Rizin -> objdump).
5. Log Environment Report: Provide clear remediation commands if dependencies are missing, maintaining fail-closed posture.

## 4. Reverse Engineering Epistemic Discipline
- Never proceed with corrupted, partially initialized, or mock analysis engines.
- All temporary databases and lock files must be cleaned up on process exit.
- Report missing dependencies explicitly without stalling the user turn.

## 5. Attestation & Verification (Exit Code 0)
- Execution is ONLY valid when verified with tangible evidence (disassembly output, hash, memory dump, test log).
- All scratch artifacts must reside exclusively in `{effective_ws}/.FL_BIN/scratch/` and be purged upon completion.
- Claiming completion without physical proof is strictly prohibited by Sovereign Law.
