# planning-with-files: Post-tool-use hook for Cursor (PowerShell)
# Reminds the agent to update task_plan.md after file modifications.

# Issue #195 opt-out. The disabled branch reproduces this hook's own
# no-plan-file behaviour, so the Cursor protocol shape never changes.
if ($env:PLANNING_DISABLED -eq '1') { exit 0 }

if (Test-Path "task_plan.md") {
    Write-Output "[planning-with-files] Update progress.md with what you just did. If a phase is now complete, update task_plan.md status."
}
exit 0
