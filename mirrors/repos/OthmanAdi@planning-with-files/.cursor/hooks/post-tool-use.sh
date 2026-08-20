#!/bin/bash
# planning-with-files: Post-tool-use hook for Cursor
# Reminds the agent to update task_plan.md after file modifications.

# Issue #195 opt-out. The disabled branch reproduces this hook's own
# no-plan-file behaviour, so the Cursor protocol shape never changes.
[ "${PLANNING_DISABLED:-}" = "1" ] && exit 0

if [ -f task_plan.md ]; then
    echo "[planning-with-files] Update progress.md with what you just did. If a phase is now complete, update task_plan.md status."
fi
exit 0
