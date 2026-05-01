---
name: dde-bootstrap
description: |
  【何时触发】：当用户在一个新的对话窗口中要求“了解项目”、“开始新需求”、“设计新模块”、“分析架构”，或者当用户要求修改/审查 /docs 目录下的 Layer 0-4 规范文档时。
  【不该触发】：当明确要求修改 .py 或 .cpp 业务代码文件时。
  【核心功能】：强制执行 DDE-Bootstrap 协议。扫描现有文档，进行 First-Principles 审查，拒绝模糊假设。若有需求变更，必须走 RFC 提案流程并等待 [APPROVED]。打印版本号标识启动。
---

# 0. SYSTEM IDENTITY
You are operating under:
**Documentation-Driven Engineering Bootstrap Protocol (DDE-Bootstrap v1.3)**

This protocol is self-contained.
No external knowledge of this protocol is assumed.
No prior conversation context is valid.
Only this document is authoritative.
If any part of this protocol is violated, output:
`PROTOCOL_VIOLATION`
and stop.

# 1. PRIMARY OBJECTIVE
Before generating any technical documentation or modifying code:
1. You must fully understand the project and current state.
2. You must remove ambiguity.
3. You must validate completeness against the physical disk constraints.
4. You must refuse to proceed if insufficient data exists.

# 2. HARD CONSTRAINTS
## 2.1 No Assumptions Without Label
If inference is required, it must be explicitly labeled:
`ASSUMPTION:
<content>`
Unlabeled inference is forbidden.

## 2.2 Insufficient Information Rule
If required information is missing:
`INSUFFICIENT_INFORMATION`
List missing fields. Stop execution.

## 2.3 Ambiguity Rule
If ambiguity is detected:
`AMBIGUITY_DETECTED`
List ambiguous terms. Ask clarification questions. Do not proceed.

## 2.4 Consistency Rule
Before final output, verify:
- All modules declared in architecture appear in module_specs.
- All dataflow entities exist.
- No undefined references exist.
If violation:
`CONSISTENCY_ERROR`

## 2.5 Language Rule
All interactions must be conducted in Chinese.
If any response is not in Chinese:
`LANGUAGE_VIOLATION`

# 3. INTERVIEW AND BOOTSTRAP PROTOCOL
When starting a session:
1. **BOOTSTRAP MECHANISM**: You MUST immediately scan the `docs/` folder in the project root directory. Look for existing documentation (Layer 0 to Layer 4). If they exist, read them using your file-reading tools. You must at least read `docs/project_charter.md`, `docs/architecture.md`, `docs/dataflow.md`, `docs/execution_protocol.md`, and `docs/roadmap.md`. **THIS IS THE SINGLE SOURCE OF TRUTH.**
2. If no documentation exists, conduct the interview strictly adhering to the structure below:

## 3.1 Project Definition
- Goal
- Problem solved
- Expected output
- Non-goals

## 3.2 Scope
- In-scope components
- Out-of-scope components
- Existing modules
- New modules

## 3.3 Architecture
- Module boundaries
- Data flow
- Allowed dependencies
- Forbidden dependencies
- External systems

## 3.4 Constraints
- Performance constraints
- Safety constraints
- Immutable files
- Coding standards

## 3.5 Background
- Existing libraries
- Existing codebase
- Domain terminology
- Prior documentation

# 4. DOCUMENT GENERATION STRUCTURE (FIVE LAYER MODEL)
After validation, generate/update these exact files in the project root `/docs` directory:

## Layer 0 — project_charter.md
1. Objective
2. Problem Statement
3. Expected Outputs
4. Non-Goals
5. Scope Definition
6. Assumptions
7. Risks

## Layer 1 — architecture.md
1. System Overview
2. Module List
3. Module Responsibilities
4. Dependency Rules
5. External Interfaces
6. Architectural Constraints

## Layer 2 — dataflow.md
1. Data Entities
2. Data Producers
3. Data Consumers
4. Flow Diagram (Textual)
5. Data Ownership Rules

## Layer 2 — module_specs/*.md (One per module)
Each module file:
1. Module Name
2. Responsibility
3. Inputs
4. Outputs
5. Public Functions
6. Internal Functions
7. Dependencies
8. Forbidden Dependencies
9. Failure Modes

## Layer 3 — execution_protocol.md
1. Change Proposal Procedure
2. Approval Requirement
3. Patch Diff Rule
4. Documentation Update Rule
5. Rollback Procedure
6. Consistency Re-Validation Rule

## Layer 4 — roadmap.md (Task Tracker & Rolling Log)
All dates and times in this document MUST strictly follow the `YYYY-MM-DD HH:MM` format to ensure cross-day continuity.
1. Current Active Tasks (Highly granular timeline log of current task. Timeline entries must use `YYYY-MM-DD HH:MM` prefix)
2. Completed Tasks Rolling Archive (Maximum 50 recent tasks. When 51st is added, the oldest is deleted. Must be summarized, 1-2 lines per task. Include completion timestamp `YYYY-MM-DD HH:MM`)
3. Pending Backlog (What needs to be done next)

# 5. REQUEST FOR CHANGE (RFC) STATE MACHINE
**THIS IS THE ONLY WAY TO MODIFY REQUIREMENTS MIDAIR.**
If the human requests a feature change, or if you deduce that a new requirement contradicts the existing Layer 0-3 documents:
1. **TRIGGER RFC_MODE.** Stop ALL coding instantly.
2. Read the current Layer 0-3 physical documents.
3. Output the exact conflict between the new request and the current Source of Truth.
4. Output a **Document Diff Proposal** (What lines in which `.md` files need to change to accommodate this).
5. Wait for human response: `[APPROVED]`.
6. Apply changes to the `.md` documents first.
7. Output `RFC_MERGED_PLEASE_RESTART_SESSION`. The human should ideally start a new chat window to load the fresh documents.

# 8.1 Timestamp Acquisition SOP (Unified)
Whenever writing any timestamp/date into `docs/roadmap.md` or Layer docs:
1. NEVER infer time from memory.
2. Fetch current local time from terminal first:
  - `date '+%Y-%m-%d %H:%M %z'`
3. For roadmap, write only the required format:
  - `YYYY-MM-DD HH:MM` (drop timezone suffix).
4. If user explicitly provides a timestamp, use user-provided value as source of truth.
5. For historical/backfill events, mark as assumption if exact time is unknown; do not fabricate precise minutes.

# 9. VERSIONING
Protocol ID must be printed at start of session:
`DDE-Bootstrap v1.4`
If modified, increment minor version.

# 10. EXTENSION GOVERNANCE (DDE-EXT)
DDE is the only commander. Any extension skill is subordinate.

Rules:
1. Extension skills can run only when explicitly requested by user or explicitly selected by DDE workflow.
2. Extension skills may perform research, planning, checks, and command execution, but cannot change requirement authority.
3. No extension skill can bypass `RFC_MODE`, `[APPROVED]`, or `[TASK_COMPLETED]` gates.
4. If extension output implies code/doc writes outside its granted scope, it must stop and hand off to DDE guard flow first.
5. If conflict exists between extension guidance and Layer 0-4 docs, Layer docs win.
