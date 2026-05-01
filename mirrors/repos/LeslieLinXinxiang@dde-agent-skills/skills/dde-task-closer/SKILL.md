---
name: dde-task-closer
description: |
  【何时触发】：当用户明确表示“这个任务做完了”、“测试通过了”、“可以收尾了”，或者主动输入 `[TASK_COMPLETED]` 时。
  【核心功能】：强制执行任务收尾生命周期。在收到 [TASK_COMPLETED] 前禁止更新 Roadmap。收到指令后，将 roadmap.md 中的 Active Task 移入 Archive 并记录精确时间戳，扫描并同步 Layer 1&2 架构文档以保证与最新代码的一致性，最后提醒用户 Commit 提交并关闭当前窗口。
---

# 0. SYSTEM IDENTITY
You are operating under:
**Documentation-Driven Engineering Task Completion Protocol (DDE-Task-Closer v1.3)**
**Documentation-Driven Engineering Task Completion Protocol (DDE-Task-Closer v1.6)**

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

# 7. TASK COMPLETION PROTOCOL
When you believe the current active task (from `roadmap.md`) is fully implemented and tested, you MUST enter a formalized completion lifecycle:

**Phase 1: Completion Request**
You must output a summary of the changes made and explicitly ask the human: "Is this task considered complete? If so, please reply with `[TASK_COMPLETED]`."
**NO ROADMAP OR SPEC UPDATES ALLOWED YET.**

**Phase 2: Finalization**
You must wait for the human to reply: `[TASK_COMPLETED]`.
Only upon receiving this exact string, you are authorized to execute the completion sequence:
1. **Update Tracker**: Move the task from "Current Active Tasks" to "Completed Tasks Rolling Archive" in `roadmap.md`. Append the `YYYY-MM-DD HH:MM` completion timestamp.
2. **Update Specs**: Scan Layer 1 (Architecture) and Layer 2 (Dataflow/Module Specs) documents. If the completed task altered the system's design or module behavior, update these `.md` files to reflect the new reality.
3. **Git & Close**: Prompt the human to commit the changes and explicitly advise them to **CLOSE the current conversation window** to start a fresh bootstrap for the next task.

# 7.1 Timestamp Acquisition SOP (Unified)
For any completion timestamp written to `roadmap.md`:
1. Always fetch local current time first via terminal:
  - `date '+%Y-%m-%d %H:%M %z'`
2. Write timestamp in roadmap format only:
  - `YYYY-MM-DD HH:MM`
3. If user gives explicit completion time, use user-provided value.
4. Do not fabricate minute-level precision.

# 7.2 Roadmap Status Migration Semantics (Mandatory)
When user uses natural-language status instructions for roadmap (e.g., "拉到已完成", "拉到 in progress"), you MUST perform structural migration, not text-label-only edits.

Mapping rules:
1. "已完成 / done / completed"
  - Move task entry into `## 2. Completed Tasks Rolling Archive`.
  - Add completion timestamp in `YYYY-MM-DD HH:MM` (use Timestamp SOP).
  - Remove the task from `Current Active Tasks` and `Pending Backlog` if present.
2. "进行中 / in progress"
  - Move task entry into `## 1. Current Active Tasks (Timeline Log)` as an active task block.
  - Include fields: `Status=[In Progress]`, `Created`, `Completed=N/A`, and at least one timeline line.
  - Remove the task from `Pending Backlog` if present.
3. Do NOT keep pseudo-status tags like `[DONE]`/`[IN PROGRESS]` in backlog as a substitute for migration.
4. If user requests both moves in one turn, execute both migrations in one patch and keep numbering/order consistent.

# 7.3 In-Progress <-> Pending Log Preservation Rule (Mandatory)
When tasks are moved between `## 1. Current Active Tasks` and `## 3. Pending Backlog`, timeline history must be preserved.

Required behavior:
1. Never discard existing `Timeline` lines during migration.
2. On every move, append one new migration line with timestamp (`YYYY-MM-DD HH:MM`) describing source and destination.
3. If a task moved to pending previously had an active-task block, pending representation must keep structured metadata (`Status`, `Created`, `Completed`, `Timeline`) instead of collapsing into a single bullet summary.
4. If task is later moved back to active, carry the same timeline forward and continue appending; do not reset or rewrite old lines.
5. If a pending task exists only as a simple bullet and has no prior timeline on disk, mark missing history as assumption instead of fabricating details.

# 9. VERSIONING
Protocol ID:
`DDE-Task-Closer v1.6`

# 8. MULTI-PROJECT ISOLATION RULE
Each project must begin in a new conversation window.
If project identifier changes inside conversation:
`PROJECT_CONTEXT_VIOLATION`
Stop.
