#!/bin/bash
# planning-with-files: Post-tool-use hook for Cursor
# Injects a reminder after file modifications using postToolUse's context field.

# Issue #195 opt-out. The disabled branch reproduces this hook's own
# no-plan-file behaviour, so the Cursor protocol shape never changes.
[ "${PLANNING_DISABLED:-}" = "1" ] && { echo '{}'; exit 0; }

HOOK_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)" || { echo '{}'; exit 0; }
[ -f "${HOOK_DIR}/resolve-plan-context.sh" ] || { echo '{}'; exit 0; }
. "${HOOK_DIR}/resolve-plan-context.sh"
cursor_resolve_plan_context "${HOOK_DIR}"
[ -n "${CURSOR_PLAN_DIR}" ] || { echo '{}'; exit 0; }
PLAN_FILE="${CURSOR_PLAN_DIR}/task_plan.md"

if [ -f "$PLAN_FILE" ]; then
    echo '{"additional_context":"[planning-with-files] Update progress.md with what you just did. If a phase is now complete, update task_plan.md status."}'
else
    echo '{}'
fi
exit 0
