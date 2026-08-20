# planning-with-files: Pre-tool-use hook for Cursor (PowerShell)
# Reads the first 30 lines of task_plan.md to keep goals in context.
# Returns {"decision": "allow"} — this hook never blocks tools.

# Issue #195 opt-out. The disabled branch reproduces this hook's own
# no-plan-file behaviour, so the Cursor protocol shape never changes.
if ($env:PLANNING_DISABLED -eq '1') {
    Write-Output '{"decision": "allow"}'
    exit 0
}

$PlanFile = "task_plan.md"

if (Test-Path $PlanFile) {
    Get-Content $PlanFile -TotalCount 30 | Write-Host
}

Write-Output '{"decision": "allow"}'
exit 0
