# Verificar si todas las fases en task_plan.md están completas
# Siempre salir con código 0 — usar stdout para informar el estado
# Llamado por el hook Stop para informar el estado de finalización de la tarea

param(
    [string]$PlanFile = "task_plan.md",
    [switch]$Validate
)

if ($Validate) {
    if (-not (Test-Path -LiteralPath $PlanFile -PathType Leaf)) { Write-Output '[planning-with-files] Plan format invalid: task_plan.md was not found.'; exit 1 }
    $content = Get-Content -LiteralPath $PlanFile -Raw
}

# Explicit creation validation never mutates a plan or changes Stop behavior.
if ($Validate) {
    $phases = 0
    $statuses = 0
    $inPhase = $false
    $invalid = $false
    foreach ($line in ($content -split '\r?\n')) {
        if ($line -cmatch '^### Phase(?:[ \t]|$)') {
            if ($inPhase -and $statuses -ne 1) { $invalid = $true }
            $phases++
            $inPhase = $true
            $statuses = 0
        } elseif ($line -match '^#{1,3}[ \t]') {
            if ($inPhase -and $statuses -ne 1) { $invalid = $true }
            $inPhase = $false
        }
        if ($inPhase) {
            $statuses += ([regex]::Matches($line, '\*\*Estado:\*\*[ \t]+(?:pending|in_progress|complete)(?:[^\p{L}\p{N}_]|$)')).Count
            $statuses += ([regex]::Matches($line, '\[(?:pending|in_progress|complete)\]')).Count
        }
    }
    if ($inPhase -and $statuses -ne 1) { $invalid = $true }
    if ($phases -eq 0 -or $invalid) {
        Write-Output '[planning-with-files] Plan format invalid: use ### Phase headings with exactly one native status per phase.'
        exit 1
    }
    Write-Output ('[planning-with-files] Plan format valid (' + $phases + ' phases).')
    exit 0
}

# issue #195: per-invocation opt-out (PLANNING_DISABLED=1) for one-shot/CI
# sessions that share a cwd with a plan but never opted into it.
if ($env:PLANNING_DISABLED -eq '1') { exit 0 }

if (-not (Test-Path $PlanFile)) {
    # Automatic gate checks have nothing to report without a plan; the explicit report keeps its notice.
    if ($Gate) { exit 0 }
    Write-Host '[planning-with-files-es] No se encontró task_plan.md — no hay sesión de planificación activa.'
    exit 0
}

# Leer contenido del archivo
$content = Get-Content $PlanFile -Raw

# Contar el total de fases
$TOTAL = ([regex]::Matches($content, "### Phase")).Count

# Primero verificar formato **Estado:**
$COMPLETE = ([regex]::Matches($content, "\*\*Estado:\*\* complete")).Count
$IN_PROGRESS = ([regex]::Matches($content, "\*\*Estado:\*\* in_progress")).Count
$PENDING = ([regex]::Matches($content, "\*\*Estado:\*\* pending")).Count

# Alternativa: si no se encontró **Estado:** verificar formato en línea [complete]
if ($COMPLETE -eq 0 -and $IN_PROGRESS -eq 0 -and $PENDING -eq 0) {
    $COMPLETE = ([regex]::Matches($content, "\[complete\]")).Count
    $IN_PROGRESS = ([regex]::Matches($content, "\[in_progress\]")).Count
    $PENDING = ([regex]::Matches($content, "\[pending\]")).Count
}

# Informar estado — siempre salir con código 0, tareas incompletas son estado normal
if ($COMPLETE -eq $TOTAL -and $TOTAL -gt 0) {
    Write-Host ('[planning-with-files-es] Todas las fases completadas (' + $COMPLETE + '/' + $TOTAL + '). Si el usuario tiene trabajo adicional, añadir fases en task_plan.md antes de comenzar.')
} else {
    Write-Host ('[planning-with-files-es] Tarea en progreso (' + $COMPLETE + '/' + $TOTAL + ' fases completadas). Actualizar progress.md antes de detenerse.')
    if ($IN_PROGRESS -gt 0) {
        Write-Host ('[planning-with-files-es] ' + $IN_PROGRESS + ' fases aún en progreso.')
    }
    if ($PENDING -gt 0) {
        Write-Host ('[planning-with-files-es] ' + $PENDING + ' fases pendientes.')
    }
}
exit 0
