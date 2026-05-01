<#
.SYNOPSIS
    Interactive diagnostic checklist for Fabric User Data Functions performance issues.

.DESCRIPTION
    Walks through a structured remediate flow to identify the root cause of
    UDF performance problems. Generates a diagnostic summary with recommended actions.

.PARAMETER FunctionName
    Name of the User Data Function experiencing issues. Optional.

.PARAMETER Symptom
    Primary symptom category: SlowFirstCall, ConsistentlySlow, IntermittentTimeout,
    ResponseTooLarge, HighCuUsage, ImportErrors. Optional - prompts interactively if omitted.

.EXAMPLE
    .\diagnostic-checklist.ps1

.EXAMPLE
    .\diagnostic-checklist.ps1 -FunctionName "get_sales_data" -Symptom ConsistentlySlow

.NOTES
    Requires: PowerShell 7+
    No Azure authentication required - this is a guided checklist tool.
#>

[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Name of the function experiencing issues")]
    [string]$FunctionName = '',

    [Parameter(HelpMessage = "Primary symptom category")]
    [ValidateSet('SlowFirstCall', 'ConsistentlySlow', 'IntermittentTimeout',
                 'ResponseTooLarge', 'HighCuUsage', 'ImportErrors', '')]
    [string]$Symptom = ''
)

Set-StrictMode -Version Latest

#region Display Helpers

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host " $Text" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([int]$Number, [string]$Text)
    Write-Host "  [$Number] " -ForegroundColor Yellow -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Write-Check {
    param([string]$Text, [bool]$Passed)
    $icon = if ($Passed) { '[PASS]' } else { '[FAIL]' }
    $color = if ($Passed) { 'Green' } else { 'Red' }
    Write-Host "    $icon " -ForegroundColor $color -NoNewline
    Write-Host $Text
}

function Write-Action {
    param([string]$Text)
    Write-Host "    -> " -ForegroundColor Magenta -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Read-YesNo {
    param([string]$Prompt)
    $response = Read-Host "    $Prompt (y/n)"
    return $response -match '^[Yy]'
}

function Read-Selection {
    param([string]$Prompt, [string[]]$Options)
    Write-Host ""
    Write-Host "  $Prompt" -ForegroundColor Yellow
    for ($i = 0; $i -lt $Options.Count; $i++) {
        Write-Host "    $($i + 1). $($Options[$i])" -ForegroundColor Gray
    }
    $selection = Read-Host "    Enter number (1-$($Options.Count))"
    $index = [int]$selection - 1
    if ($index -ge 0 -and $index -lt $Options.Count) {
        return $Options[$index]
    }
    return $Options[0]
}

#endregion

#region Diagnostic Flows

function Invoke-ColdStartDiagnostic {
    Write-Header "Cold Start Diagnostic"

    Write-Step 1 "Check historical logs for duration pattern"
    Write-Host "    In the Fabric portal: Run only mode > function > View historical log" -ForegroundColor Gray
    $hasPattern = Read-YesNo "Is the first invocation 3-10x slower than subsequent calls?"

    if ($hasPattern) {
        Write-Check "Cold start pattern confirmed" $true

        Write-Step 2 "Check library footprint"
        $heavyLibs = Read-YesNo "Does definition.json include heavy libraries (pandas, numpy, scipy, etc.)?"

        if ($heavyLibs) {
            Write-Action "Move heavy imports inside function body (lazy imports)"
            Write-Action "Remove unused libraries from definition.json"
            $script:recommendations += "Implement lazy imports for heavy libraries"
            $script:recommendations += "Audit definition.json for unused dependencies"
        }

        Write-Step 3 "Check warm-up strategy"
        $hasWarmUp = Read-YesNo "Do you have a scheduled health-check invocation?"

        if (-not $hasWarmUp) {
            Write-Action "Create a lightweight health_check() function"
            Write-Action "Schedule it via Pipeline every 10-15 min during business hours"
            $script:recommendations += "Implement scheduled warm-up via Pipeline"
        }

        Write-Step 4 "Check private libraries"
        $hasPrivateLibs = Read-YesNo "Are you using private .whl libraries?"

        if ($hasPrivateLibs) {
            Write-Action "Reduce private library count and size"
            Write-Action "Each .whl adds to initialization time (max 28.6 MB each)"
            $script:recommendations += "Minimize private library count and size"
        }
    }
    else {
        Write-Check "Not a cold start issue - investigate other causes" $false
        $script:recommendations += "Symptom does not match cold start - re-evaluate"
    }
}

function Invoke-SlowCodeDiagnostic {
    Write-Header "Slow Function Code Diagnostic"

    Write-Step 1 "Identify the slow phase"
    $slowPhase = Read-Selection "Which phase is slowest?" @(
        'Data retrieval (queries/file reads)',
        'Data processing (computation/transformation)',
        'Response serialization',
        'Not sure - need to instrument'
    )

    switch -Wildcard ($slowPhase) {
        '*retrieval*' {
            Write-Step 2 "Check query patterns"
            $selectStar = Read-YesNo "Are any queries using SELECT * ?"
            if ($selectStar) {
                Write-Action "Replace SELECT * with explicit column lists"
                $script:recommendations += "Eliminate SELECT * queries"
            }

            $noFilter = Read-YesNo "Are any queries missing WHERE clauses?"
            if ($noFilter) {
                Write-Action "Add WHERE clauses to filter data at the source"
                Write-Action "Add TOP/LIMIT clauses to cap result sets"
                $script:recommendations += "Add WHERE and LIMIT clauses to queries"
            }

            $noParams = Read-YesNo "Are queries using string formatting instead of parameters?"
            if ($noParams) {
                Write-Action "Use parameterized queries for plan caching and safety"
                $script:recommendations += "Convert to parameterized queries"
            }
        }
        '*processing*' {
            Write-Step 2 "Check processing patterns"
            $usesIterrows = Read-YesNo "Is the code using df.iterrows() or row-by-row loops?"
            if ($usesIterrows) {
                Write-Action "Replace iterrows() with vectorized pandas operations"
                Write-Action "Use .apply() or built-in pandas methods"
                $script:recommendations += "Replace iterrows() with vectorized operations"
            }

            $stringConcat = Read-YesNo "Is the code building strings with += in a loop?"
            if ($stringConcat) {
                Write-Action "Use ''.join() or list comprehension instead"
                $script:recommendations += "Replace string concatenation with join()"
            }
        }
        '*serialization*' {
            Write-Action "Use df.to_json(orient='records') instead of manual serialization"
            Write-Action "Return only required fields"
            $script:recommendations += "Optimize response serialization"
        }
        '*instrument*' {
            Write-Action "Add timing instrumentation to function code"
            Write-Action "Use the perf_logging.py template from this skill"
            Write-Action "Review Invocation details in historical logs"
            $script:recommendations += "Instrument function with timing (see perf_logging.py template)"
        }
    }
}

function Invoke-TimeoutDiagnostic {
    Write-Header "Intermittent Timeout Diagnostic"

    Write-Step 1 "Check capacity utilization"
    $highCu = Read-YesNo "Does the Capacity Metrics app show CU% > 100% during failure windows?"

    if ($highCu) {
        Write-Action "Capacity is throttled - functions are competing for resources"
        Write-Action "Options: scale up SKU, reduce concurrent workloads, stagger schedules"
        $script:recommendations += "Address capacity throttling (scale SKU or reduce concurrency)"
    }

    Write-Step 2 "Check connection stability"
    $connErrors = Read-YesNo "Do logs show connection timeout or connection refused errors?"

    if ($connErrors) {
        Write-Action "Verify data source is accessible independently"
        Write-Action "Check credential expiration"
        Write-Action "Add retry logic with exponential backoff"
        $script:recommendations += "Implement connection retry with exponential backoff"
    }

    Write-Step 3 "Check execution duration trend"
    $gettingSlower = Read-YesNo "Are function durations trending upward over time?"

    if ($gettingSlower) {
        Write-Action "Data volume may be growing - add explicit limits"
        Write-Action "Implement pagination to cap per-invocation work"
        $script:recommendations += "Implement pagination to handle growing data volumes"
    }
}

function Invoke-ResponseSizeDiagnostic {
    Write-Header "Response Size Diagnostic"

    Write-Step 1 "Identify return data volume"
    Write-Action "Add response size logging: sys.getsizeof(json.dumps(result))"

    Write-Step 2 "Mitigation options"
    Write-Action "Add TOP/LIMIT clauses to queries"
    Write-Action "Implement pagination with page/pageSize parameters"
    Write-Action "Return aggregated/summary data instead of raw rows"
    Write-Action "Filter to only required columns"

    $script:recommendations += "Add response size monitoring"
    $script:recommendations += "Implement pagination or aggregation"
}

function Invoke-HighCuDiagnostic {
    Write-Header "High Capacity Consumption Diagnostic"

    Write-Step 1 "Identify top CU consumers in Capacity Metrics app"
    Write-Host "    Filter: Compute page > Item kind = User Data Functions" -ForegroundColor Gray

    Write-Step 2 "Check Portal Test sessions"
    $testSessions = Read-YesNo "Are developers frequently using Test mode in the portal?"
    if ($testSessions) {
        Write-Action "Portal Test sessions have a 15-min minimum charge"
        Write-Action "Consider using VS Code extension for local testing"
        $script:recommendations += "Reduce Portal Test sessions - use VS Code extension"
    }

    Write-Step 3 "Check invocation frequency"
    $highFrequency = Read-YesNo "Are functions being called more often than necessary?"
    if ($highFrequency) {
        Write-Action "Add caching in the calling item (Pipeline, Notebook)"
        Write-Action "Reduce polling frequency"
        Write-Action "Consolidate multiple calls into batch operations"
        $script:recommendations += "Reduce invocation frequency with caching"
    }

    Write-Step 4 "Check publish frequency"
    $frequentPublish = Read-YesNo "Are functions published frequently during development?"
    if ($frequentPublish) {
        Write-Action "Each publish triggers OneLake storage write operations"
        Write-Action "Batch changes and publish less frequently"
        Write-Action "Use Test mode to validate before publishing"
        $script:recommendations += "Reduce publish frequency during development"
    }
}

function Invoke-ImportErrorDiagnostic {
    Write-Header "Library / Import Error Diagnostic"

    Write-Step 1 "Verify library installation"
    Write-Action "Check definition.json libraries section for correct names and versions"
    Write-Action "Ensure library installation completed before testing"

    Write-Step 2 "Check service limits"
    Write-Action "Private .whl files must be under 28.6 MB each"
    Write-Action "Verify library compatibility with Python 3.11 (Run) or 3.12 (Test)"

    $script:recommendations += "Audit library versions and compatibility"
    $script:recommendations += "Verify .whl file sizes are under 28.6 MB"
}

#endregion

#region Main

$script:recommendations = @()

Write-Header "Fabric User Data Functions - Performance Diagnostic"

if ([string]::IsNullOrEmpty($FunctionName)) {
    $FunctionName = Read-Host "  Function name (or press Enter to skip)"
}
if ($FunctionName) {
    Write-Host "  Diagnosing: $FunctionName" -ForegroundColor Gray
}

if ([string]::IsNullOrEmpty($Symptom)) {
    $Symptom = Read-Selection "What is the primary symptom?" @(
        'SlowFirstCall',
        'ConsistentlySlow',
        'IntermittentTimeout',
        'ResponseTooLarge',
        'HighCuUsage',
        'ImportErrors'
    )
}

Write-Host "  Symptom: $Symptom" -ForegroundColor Gray

switch ($Symptom) {
    'SlowFirstCall'       { Invoke-ColdStartDiagnostic }
    'ConsistentlySlow'    { Invoke-SlowCodeDiagnostic }
    'IntermittentTimeout'  { Invoke-TimeoutDiagnostic }
    'ResponseTooLarge'    { Invoke-ResponseSizeDiagnostic }
    'HighCuUsage'         { Invoke-HighCuDiagnostic }
    'ImportErrors'        { Invoke-ImportErrorDiagnostic }
}

# Summary
Write-Header "Diagnostic Summary"

if ($FunctionName) {
    Write-Host "  Function: $FunctionName" -ForegroundColor White
}
Write-Host "  Symptom:  $Symptom" -ForegroundColor White
Write-Host ""
Write-Host "  Recommendations:" -ForegroundColor Yellow

for ($i = 0; $i -lt $script:recommendations.Count; $i++) {
    Write-Host "    $($i + 1). $($script:recommendations[$i])" -ForegroundColor White
}

Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    - Review SKILL.md for detailed guidance on each recommendation" -ForegroundColor Gray
Write-Host "    - See references/performance-optimization.md for code patterns" -ForegroundColor Gray
Write-Host "    - Use templates/perf_logging.py for instrumented function boilerplate" -ForegroundColor Gray
Write-Host ""

#endregion
