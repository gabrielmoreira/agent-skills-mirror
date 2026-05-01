<#
.SYNOPSIS
    Parse text-based coverage output from pytest-cov, Jest, or Vitest into JSON.

.DESCRIPTION
    Reads coverage text from a file or stdin and emits structured JSON to stdout.
    Supports three formats:
      - pytest: output from pytest --cov --cov-report=term-missing
      - jest:   output from npx jest --coverage (text table)
      - vitest: output from npx vitest run --coverage (same table format as jest)

    The parser auto-detects the format when -Format is 'auto' (default).
    No external dependencies -- uses only built-in PowerShell.

.PARAMETER Input
    File containing coverage text output. Reads from stdin if omitted.

.PARAMETER Format
    Coverage output format: auto, pytest, jest, vitest (default: auto).

.PARAMETER Bottom
    Number of lowest-coverage files to highlight (default: 5).

.PARAMETER Output
    Write JSON to this file instead of stdout.

.PARAMETER Threshold
    Exit with code 1 if overall line coverage is below this percent.

.EXAMPLE
    pytest --cov=src --cov-report=term-missing | pwsh scripts/parse-coverage-text.ps1

.EXAMPLE
    .\parse-coverage-text.ps1 -Input pytest-output.txt -Format pytest

.EXAMPLE
    npx jest --coverage 2>&1 | pwsh scripts/parse-coverage-text.ps1 -Format jest
#>
[CmdletBinding()]
param(
    [string]$Input,

    [ValidateSet('auto', 'pytest', 'jest', 'vitest')]
    [string]$Format = 'auto',

    [int]$Bottom = 5,

    [string]$Output,

    [double]$Threshold = -1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Parse-Pytest {
    param([string]$Text)

    $files = [System.Collections.Generic.List[object]]::new()
    $total = $null

    # Match: src/foo.py  120  15  88%  45-50, 102
    $linePattern = '^\s*(\S+\.py)\s+(\d+)\s+(\d+)\s+(\d+)%\s*(.*)?$'
    $totalPattern = '^\s*TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%'

    foreach ($line in $Text -split "`n") {
        $line = $line.Trim()

        if ($line -match $totalPattern) {
            $total = [ordered]@{
                statements = [int]$Matches[1]
                missing    = [int]$Matches[2]
                line_rate  = [int]$Matches[3]
            }
            continue
        }

        if ($line -match $linePattern) {
            $missingStr = if ($Matches[5]) { $Matches[5].Trim() } else { '' }
            $uncovered = if ($missingStr) {
                @($missingStr -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
            } else { @() }

            $files.Add([ordered]@{
                filename        = $Matches[1]
                statements      = [int]$Matches[2]
                missing         = [int]$Matches[3]
                line_rate       = [int]$Matches[4]
                uncovered_lines = $uncovered
            })
        }
    }

    if (-not $total -and $files.Count -gt 0) {
        $totalStmts = ($files | Measure-Object -Property statements -Sum).Sum
        $totalMiss = ($files | Measure-Object -Property missing -Sum).Sum
        $rate = if ($totalStmts -gt 0) { [math]::Round(($totalStmts - $totalMiss) / $totalStmts * 100, 2) } else { 0 }
        $total = [ordered]@{ statements = $totalStmts; missing = $totalMiss; line_rate = $rate }
    }

    if (-not $total) { $total = [ordered]@{ statements = 0; missing = 0; line_rate = 0 } }

    return [ordered]@{
        format  = 'pytest'
        summary = [ordered]@{
            line_rate  = $total.line_rate
            statements = $total.statements
            missing    = $total.missing
        }
        files   = $files.ToArray()
    }
}

function Parse-JestVitest {
    param([string]$Text)

    $files = [System.Collections.Generic.List[object]]::new()
    $summary = $null

    # Match: name | stmts | branch | funcs | lines | uncovered
    $rowPattern = '^\s*(.+?)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(.*?)\s*$'

    foreach ($line in $Text -split "`n") {
        # Skip separator lines
        if ($line -match '^\s*[-|]+\s*$') { continue }
        # Skip header
        if ($line -match '% Stmts|% Branch') { continue }

        if ($line -match $rowPattern) {
            $name = $Matches[1].Trim()
            $stmts = [double]$Matches[2]
            $branch = [double]$Matches[3]
            $funcs = [double]$Matches[4]
            $lines = [double]$Matches[5]
            $uncoveredStr = $Matches[6].Trim()
            $uncovered = if ($uncoveredStr) {
                @($uncoveredStr -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
            } else { @() }

            $entry = [ordered]@{
                stmts_pct       = $stmts
                branch_pct      = $branch
                funcs_pct       = $funcs
                line_rate       = $lines
                uncovered_lines = $uncovered
            }

            if ($name -match '^(All files|All)$') {
                $summary = $entry
            } else {
                $entry['filename'] = $name
                $files.Add($entry)
            }
        }
    }

    if (-not $summary) {
        $summary = [ordered]@{ stmts_pct = 0; branch_pct = 0; funcs_pct = 0; line_rate = 0; uncovered_lines = @() }
    }

    return [ordered]@{
        format  = 'jest/vitest'
        summary = [ordered]@{
            line_rate  = $summary.line_rate
            stmts_pct  = $summary.stmts_pct
            branch_pct = $summary.branch_pct
            funcs_pct  = $summary.funcs_pct
        }
        files   = $files.ToArray()
    }
}

function Detect-Format {
    param([string]$Text)
    if ($Text -match '% Stmts|% Branch') { return 'jest' }
    if ($Text -match 'Stmts\s+Miss|TOTAL') { return 'pytest' }
    return 'unknown'
}

# Read input
$text = $null
if ($Input) {
    if (-not (Test-Path $Input)) {
        Write-Error "Error: file not found: $Input"
        exit 2
    }
    Write-Host "Reading: $Input" -ForegroundColor Cyan
    $text = Get-Content -Path $Input -Raw
} else {
    # Read from pipeline/stdin
    $pipeInput = @($input)
    if ($pipeInput.Count -gt 0) {
        $text = $pipeInput -join "`n"
        Write-Host "Reading from stdin" -ForegroundColor Cyan
    } else {
        Write-Error "Error: no input. Pipe coverage output or use -Input."
        Write-Host "Usage: pytest --cov=src --cov-report=term-missing | pwsh parse-coverage-text.ps1" -ForegroundColor Yellow
        exit 2
    }
}

# Detect format
$fmt = $Format
if ($fmt -eq 'auto') {
    $fmt = Detect-Format $text
    if ($fmt -eq 'unknown') {
        Write-Error "Error: could not auto-detect format. Use -Format to specify. Supported: pytest, jest, vitest"
        exit 2
    }
    Write-Host "Detected format: $fmt" -ForegroundColor Cyan
} elseif ($fmt -eq 'vitest') {
    $fmt = 'jest'  # same table format
}

# Parse
$result = switch ($fmt) {
    'pytest' { Parse-Pytest $text }
    'jest'   { Parse-JestVitest $text }
    default  { Write-Error "Error: unsupported format: $fmt"; exit 2 }
}

if ($result.files.Count -eq 0) {
    Write-Host "Warning: no coverage data found in input." -ForegroundColor Yellow
}

# Add bottom N files
$bottomFiles = $result.files | Sort-Object { $_.line_rate } | Select-Object -First $Bottom
$result['bottom_files'] = @($bottomFiles)

$json = $result | ConvertTo-Json -Depth 10

if ($Output) {
    $parentDir = Split-Path -Path $Output -Parent
    if ($parentDir -and -not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }
    $json | Set-Content -Path $Output -Encoding UTF8
    Write-Host "Report written to: $Output" -ForegroundColor Green
} else {
    Write-Output $json
}

# Threshold check
if ($Threshold -ge 0) {
    $actual = $result.summary.line_rate
    if ($actual -lt $Threshold) {
        Write-Host "FAIL: line coverage ${actual}% is below threshold ${Threshold}%" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "PASS: line coverage ${actual}% meets threshold ${Threshold}%" -ForegroundColor Green
    }
}
