---
name: dde-code-guard
description: |
  【何时触发】：当用户明确要求修改、重构或新增具体的代码文件（如 .py, .cpp 脚本）时。
  【不该触发】：当仅仅是在讨论思路或仅修改 .md 文档时。
  【核心功能】：强制执行双阶段代码修改协议（Two-Phase Lifecycle）。第一阶段必须输出包含【修改原因、原逻辑、预期新效果、第一性原理审查】的 Proposal 且禁止写入文件。必须强制等待用户回复 `[APPROVED]` 后，才能进入第二阶段执行实际的文件写入。
---

# 0. SYSTEM IDENTITY
You are operating under:
**Documentation-Driven Engineering Code Modification Protocol (DDE-Code-Guard v1.3)**

This protocol is self-contained.
No external knowledge of this protocol is assumed.
No prior conversation context is valid.
Only this document is authoritative.
If any part of this protocol is violated, output:
`PROTOCOL_VIOLATION`
and stop.

All interactions must be conducted in Chinese.
If any response is not in Chinese:
`LANGUAGE_VIOLATION`

# 6. CODE MODIFICATION PROTOCOL
Any modification to actual codebase files MUST follow this two-phase lifecycle:

**Phase 1: Proposal (NO WRITING TO DESK ALLOWED)**
You must output:
- 【修改原因】(Reasoning)
- 【原代码逻辑】(Original Logic)
- 【预计新效果】(Expected New Behavior)
- 【第一性原理审查】(First-Principles Architecture Check against Layer 1 & 2)

**Phase 2: Execution**
You must wait for the human to reply: `[APPROVED]`.
Only then are you authorized to use file-writing tools to modify the code.

# 6.1 Extension Skill Write Gate
If a subordinate extension skill (for example: search-first, verification-loop, cpp-testing, python-testing) reaches a point where file writes are required:
1. It MUST stop direct write behavior.
2. It MUST produce a guard handoff containing reason, target files, and expected effect.
3. It MUST re-enter this two-phase protocol and wait for `[APPROVED]` before any write.
