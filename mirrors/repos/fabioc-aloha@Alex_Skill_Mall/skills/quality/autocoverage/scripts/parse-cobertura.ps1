<#
.SYNOPSIS
    Parse Cobertura XML coverage reports and emit structured JSON.

.DESCRIPTION
    Supports coverage files produced by:
      - dotnet test --collect:"XPlat Code Coverage" (C#)
      - Jest/Vitest with cobertura reporter (TypeScript/JavaScript)
      - OpenCppCoverage --export_type=cobertura (C++)
      - pytest-cov --cov-report=xml (Python)

    Multiple XML files can be passed to produce a merged summary.
    No external dependencies -- uses only built-in PowerShell/.NET XML support.

.PARAMETER Files
    One or more paths to Cobertura XML files. Supports wildcards.

.PARAMETER Bottom
    Number of lowest-coverage files to highlight (default: 5).

.PARAMETER Output
    Write JSON to this file instead of stdout.

.PARAMETER Threshold
    Exit with code 1 if overall line coverage is below this percent.

.EXAMPLE
    .\parse-cobertura.ps1 coverage.cobertura.xml

.EXAMPLE
    .\parse-cobertura.ps1 coverage1.xml coverage2.xml -Bottom 10

.EXAMPLE
    .\parse-cobertura.ps1 .\coverage\**\coverage.cobertura.xml -Threshold 80
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Files,

    [int]$Bottom = 5,

    [string]$Output,

    [double]$Threshold = -1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Compress-LineRanges {
    param([int[]]$Lines)
    if (-not $Lines -or $Lines.Count -eq 0) { return @() }
    $sorted = @($Lines | Sort-Object -Unique)
    $ranges = [System.Collections.Generic.List[string]]::new()
    $start = $sorted[0]
    $prev = $sorted[0]
    for ($i = 1; $i -lt $sorted.Count; $i++) {
        if ($sorted[$i] -eq $prev + 1) {
            $prev = $sorted[$i]
        } else {
            if ($start -eq $prev) { $ranges.Add("$start") } else { $ranges.Add("$start-$prev") }
            $start = $sorted[$i]
            $prev = $sorted[$i]
        }
    }
    if ($start -eq $prev) { $ranges.Add("$start") } else { $ranges.Add("$start-$prev") }
    return $ranges.ToArray()
}

function Ensure-Array {
    # Force a value into an array -- handles PowerShell's single-element unwrapping
    param($Value)
    if ($null -eq $Value) { return @() }
    if ($Value -is [System.Array]) { return $Value }
    return @($Value)
}

function Parse-CoberturaFile {
    param([string]$FilePath)

    [xml]$xml = Get-Content -Path $FilePath -Raw
    $root = $xml.coverage

    # Read summary attributes (safe for missing attributes)
    $lineRate = if ($root.'line-rate') { [double]($root.'line-rate') } else { 0 }
    $branchRate = if ($root.'branch-rate') { [double]($root.'branch-rate') } else { 0 }
    $linesValid = if ($root.'lines-valid') { [int]($root.'lines-valid') } else { 0 }
    $linesCovered = if ($root.'lines-covered') { [int]($root.'lines-covered') } else { 0 }
    $branchesValid = if ($root.'branches-valid') { [int]($root.'branches-valid') } else { 0 }
    $branchesCovered = if ($root.'branches-covered') { [int]($root.'branches-covered') } else { 0 }

    # Aggregate by filename since some tools (dotnet-coverage) emit multiple
    # <class> entries per file (one per method/type). We merge them here.
    $fileMap = [ordered]@{}

    $packages = Ensure-Array $root.packages.package
    foreach ($package in $packages) {
        if (-not $package) { continue }
        $pkgName = $package.name

        $classes = Ensure-Array $package.classes.class
        foreach ($class in $classes) {
            if (-not $class) { continue }
            $filename = $class.filename
            if (-not $filename) { continue }

            # Initialize file entry if not seen
            if (-not $fileMap.Contains($filename)) {
                $fileMap[$filename] = [ordered]@{
                    package         = $pkgName
                    filename        = $filename
                    classes         = [System.Collections.Generic.List[string]]::new()
                    total_lines     = 0
                    covered_lines   = 0
                    uncovered_lines = [System.Collections.Generic.List[int]]::new()
                    _line_set       = [System.Collections.Generic.HashSet[int]]::new()  # dedup lines across classes
                }
            }
            $entry = $fileMap[$filename]

            $clsName = $class.name
            if ($clsName) { $entry.classes.Add($clsName) }

            $lines = Ensure-Array $class.lines.line
            foreach ($line in $lines) {
                if (-not $line) { continue }
                $lineNum = [int]($line.number)

                # Skip if we already counted this line from another class in the same file
                if (-not $entry._line_set.Add($lineNum)) { continue }

                $entry.total_lines++
                $hits = [int]($line.hits)
                if ($hits -gt 0) {
                    $entry.covered_lines++
                } else {
                    $entry.uncovered_lines.Add($lineNum)
                }
            }
        }
    }

    # Build file list with computed rates
    $fileList = [System.Collections.Generic.List[object]]::new()
    foreach ($key in $fileMap.Keys) {
        $entry = $fileMap[$key]
        $total = $entry.total_lines
        $covered = $entry.covered_lines
        $fileLR = if ($total -gt 0) { [math]::Round($covered / $total * 100, 2) } else { 0 }
        $fileList.Add([ordered]@{
            package         = $entry.package
            filename        = $entry.filename
            classes         = $entry.classes.ToArray()
            line_rate       = $fileLR
            total_lines     = $total
            covered_lines   = $covered
            uncovered_lines = Compress-LineRanges $entry.uncovered_lines.ToArray()
        })
    }

    # If the root attributes were missing/zero, recompute from parsed data
    if ($linesValid -eq 0 -and $fileList.Count -gt 0) {
        $linesValid = ($fileList | Measure-Object -Property total_lines -Sum).Sum
        $linesCovered = ($fileList | Measure-Object -Property covered_lines -Sum).Sum
        $lineRate = if ($linesValid -gt 0) { $linesCovered / $linesValid } else { 0 }
    }

    return [ordered]@{
        source_file = $FilePath
        summary     = [ordered]@{
            line_rate        = [math]::Round($lineRate * 100, 2)
            branch_rate      = [math]::Round($branchRate * 100, 2)
            lines_valid      = $linesValid
            lines_covered    = $linesCovered
            lines_uncovered  = $linesValid - $linesCovered
            branches_valid   = $branchesValid
            branches_covered = $branchesCovered
        }
        files       = $fileList.ToArray()
    }
}

function Merge-Results {
    param([object[]]$Results)

    if ($Results.Count -eq 1) { return $Results[0] }

    $totalLinesValid = 0; $totalLinesCovered = 0
    $totalBranchesValid = 0; $totalBranchesCovered = 0
    $allFiles = [System.Collections.Generic.List[object]]::new()
    $sourceFiles = [System.Collections.Generic.List[string]]::new()

    foreach ($r in $Results) {
        $totalLinesValid += $r.summary.lines_valid
        $totalLinesCovered += $r.summary.lines_covered
        $totalBranchesValid += $r.summary.branches_valid
        $totalBranchesCovered += $r.summary.branches_covered
        $sourceFiles.Add($r.source_file)
        foreach ($f in $r.files) { $allFiles.Add($f) }
    }

    $lineRate = if ($totalLinesValid -gt 0) { [math]::Round($totalLinesCovered / $totalLinesValid * 100, 2) } else { 0 }
    $branchRate = if ($totalBranchesValid -gt 0) { [math]::Round($totalBranchesCovered / $totalBranchesValid * 100, 2) } else { 0 }

    return [ordered]@{
        source_files = $sourceFiles.ToArray()
        summary      = [ordered]@{
            line_rate        = $lineRate
            branch_rate      = $branchRate
            lines_valid      = $totalLinesValid
            lines_covered    = $totalLinesCovered
            lines_uncovered  = $totalLinesValid - $totalLinesCovered
            branches_valid   = $totalBranchesValid
            branches_covered = $totalBranchesCovered
        }
        files        = $allFiles.ToArray()
    }
}

# Resolve wildcards and validate files
$resolvedFiles = [System.Collections.Generic.List[string]]::new()
foreach ($pattern in $Files) {
    $expanded = Resolve-Path -Path $pattern -ErrorAction SilentlyContinue
    if ($expanded) {
        foreach ($p in $expanded) { $resolvedFiles.Add($p.Path) }
    } else {
        Write-Host "Warning: no files matched: $pattern" -ForegroundColor Yellow
    }
}

if ($resolvedFiles.Count -eq 0) {
    Write-Error "Error: no valid Cobertura XML files found. Received: $($Files -join ', ')"
    exit 2
}

# Parse each file
$results = [System.Collections.Generic.List[object]]::new()
foreach ($filepath in $resolvedFiles) {
    Write-Host "Parsing: $filepath" -ForegroundColor Cyan
    $results.Add((Parse-CoberturaFile -FilePath $filepath))
}

# Merge and produce output
$merged = Merge-Results $results.ToArray()

# Add bottom N files
$bottomFiles = $merged.files | Sort-Object { $_.line_rate } | Select-Object -First $Bottom
$merged['bottom_files'] = @($bottomFiles)

$json = $merged | ConvertTo-Json -Depth 10

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
    $actual = $merged.summary.line_rate
    if ($actual -lt $Threshold) {
        Write-Host "FAIL: line coverage ${actual}% is below threshold ${Threshold}%" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "PASS: line coverage ${actual}% meets threshold ${Threshold}%" -ForegroundColor Green
    }
}
