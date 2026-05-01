<#
.SYNOPSIS
    Extracts and evaluates DAX measures from a Power BI semantic model for common anti-patterns.

.DESCRIPTION
    Connects to the Power BI REST API, retrieves DAX measure definitions from a semantic model,
    and scans them for known performance anti-patterns. Outputs a report of findings with
    severity ratings and optimization recommendations.

.PARAMETER WorkspaceId
    The GUID of the Power BI workspace containing the dataset.

.PARAMETER DatasetId
    The GUID of the semantic model (dataset) to analyze.

.PARAMETER OutputPath
    Optional. Directory to save the analysis output. Defaults to current directory.

.EXAMPLE
    .\Get-DAXQueryMetrics.ps1 -WorkspaceId "xxx" -DatasetId "yyy"

.NOTES
    Requires: MicrosoftPowerBIMgmt PowerShell module
    Requires: XMLA endpoint access (F64/P1+ capacity)
    Install:  Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$DatasetId,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = (Get-Location).Path
)

#Requires -Modules MicrosoftPowerBIMgmt

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# DAX Anti-Pattern Definitions
$antiPatterns = @(
    @{
        Id          = 'AP-01'
        Name        = 'Iterator over large table with RELATED'
        Pattern     = '(?i)SUMX\s*\(\s*\w+\s*,.*RELATED\s*\('
        Severity    = 'Warning'
        Description = 'SUMX with RELATED() forces row-by-row relationship resolution. Pre-compute the value in the source or use a calculated column.'
    }
    @{
        Id          = 'AP-02'
        Name        = 'Nested CALCULATE'
        Pattern     = '(?i)CALCULATE\s*\(\s*CALCULATE\s*\('
        Severity    = 'Warning'
        Description = 'Nested CALCULATE calls add complexity. Flatten into a single CALCULATE with multiple filter arguments.'
    }
    @{
        Id          = 'AP-03'
        Name        = 'FILTER on entire table'
        Pattern     = '(?i)FILTER\s*\(\s*(?!ALL|VALUES|DISTINCT|ADDCOLUMNS|SUMMARIZE)\w+\s*,'
        Severity    = 'Warning'
        Description = 'FILTER() on an entire table materializes all rows in the Formula Engine. Use column predicates in CALCULATE instead.'
    }
    @{
        Id          = 'AP-04'
        Name        = 'Division without DIVIDE'
        Pattern     = '(?<!\w)(?:SUM|AVERAGE|COUNT|MIN|MAX)\s*\([^)]+\)\s*/\s*(?:SUM|AVERAGE|COUNT|MIN|MAX)\s*\([^)]+\)'
        Severity    = 'Info'
        Description = 'Use DIVIDE() instead of / operator for safe division with zero handling.'
    }
    @{
        Id          = 'AP-05'
        Name        = 'COUNTROWS(FILTER(...))'
        Pattern     = '(?i)COUNTROWS\s*\(\s*FILTER\s*\('
        Severity    = 'Warning'
        Description = 'Replace COUNTROWS(FILTER(...)) with CALCULATE(COUNTROWS(...), filter) for better performance.'
    }
    @{
        Id          = 'AP-06'
        Name        = 'IF without VAR caching'
        Pattern     = '(?i)IF\s*\(\s*\[.*?\]\s*[><=!]+\s*.*?,\s*\[.*?\]\s*,\s*\[.*?\]\s*\)'
        Severity    = 'Info'
        Description = 'IF() may evaluate both branches. Use VAR to cache measure references for better performance.'
    }
    @{
        Id          = 'AP-07'
        Name        = 'EARLIER function usage'
        Pattern     = '(?i)EARLIER\s*\('
        Severity    = 'Warning'
        Description = 'EARLIER() is a legacy function. Use VAR/RETURN pattern instead for clarity and performance.'
    }
    @{
        Id          = 'AP-08'
        Name        = 'LOOKUPVALUE in measure'
        Pattern     = '(?i)LOOKUPVALUE\s*\('
        Severity    = 'Info'
        Description = 'LOOKUPVALUE in measures can be slow. Consider using relationships with RELATED() or create a proper dimension join.'
    }
    @{
        Id          = 'AP-09'
        Name        = 'SELECTEDVALUE without fallback'
        Pattern     = '(?i)SELECTEDVALUE\s*\(\s*[^,)]+\s*\)'
        Severity    = 'Info'
        Description = 'SELECTEDVALUE without a fallback value returns BLANK when multiple values are selected. Add a default value parameter.'
    }
    @{
        Id          = 'AP-10'
        Name        = 'Complex SWITCH(TRUE())'
        Pattern     = '(?i)SWITCH\s*\(\s*TRUE\s*\(\s*\).*?(?:.*?,.*?){5,}'
        Severity    = 'Info'
        Description = 'SWITCH(TRUE()) with many branches may indicate overly complex logic. Consider simplifying or splitting into multiple measures.'
    }
)

function Write-Step {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan
}

try {
    # Ensure authenticated
    Write-Step "Checking Power BI authentication..."
    try {
        Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/me" -Method Get | Out-Null
    }
    catch {
        Write-Host "  Not authenticated. Connecting..." -ForegroundColor Yellow
        Connect-PowerBIServiceAccount
    }

    # Execute DAX query to retrieve measures
    Write-Step "Retrieving DAX measures from semantic model..."

    $daxQuery = @{
        queries = @(
            @{
                query = @"
EVALUATE
SELECTCOLUMNS(
    INFO.MEASURES(),
    "TableName", [TableID].[Name],
    "MeasureName", [Name],
    "Expression", [Expression],
    "Description", [Description],
    "DataType", [DataType],
    "IsHidden", [IsHidden]
)
"@
            }
        )
        serializerSettings = @{
            includeNulls = $true
        }
    }

    $body = $daxQuery | ConvertTo-Json -Depth 5
    $url = "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/datasets/$DatasetId/executeQueries"

    try {
        $response = Invoke-PowerBIRestMethod -Url $url -Method Post -Body $body | ConvertFrom-Json
    }
    catch {
        if ($_.Exception.Message -like '*Unauthorized*' -or $_.Exception.Message -like '*XMLA*') {
            Write-Warning "XMLA endpoint access required (F64/P1+ capacity). Falling back to metadata API..."

            # Fallback: use dataset metadata API
            Write-Step "Using REST API for basic measure metadata..."
            Write-Host "  Note: Expression analysis requires XMLA endpoint access." -ForegroundColor Yellow
            Write-Host "  Generating metadata-only report." -ForegroundColor Yellow

            $datasetInfo = Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/datasets/$DatasetId" -Method Get | ConvertFrom-Json
            $report = [ordered]@{
                AnalysisTimestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
                Dataset           = $datasetInfo.name
                DatasetId         = $DatasetId
                Note              = 'XMLA endpoint not available. Expression analysis requires F64/P1+ capacity with XMLA enabled.'
                Recommendation    = 'Use DAX Studio or Tabular Editor locally for measure expression analysis.'
            }

            $outputFile = Join-Path $OutputPath "dax-metrics_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
            $report | ConvertTo-Json -Depth 5 | Set-Content -Path $outputFile -Encoding UTF8
            Write-Host "`n  Metadata report saved to: $outputFile" -ForegroundColor Green
            return
        }
        throw
    }

    # Parse results
    $measures = $response.results[0].tables[0].rows
    Write-Host "  Found $($measures.Count) measure(s)" -ForegroundColor White

    # Analyze each measure
    Write-Step "Scanning for anti-patterns..."

    $allFindings = [System.Collections.Generic.List[PSObject]]::new()
    $measureStats = foreach ($measure in $measures) {
        $expression = $measure.'[Expression]'
        $measureName = $measure.'[MeasureName]'
        $tableName = $measure.'[TableName]'

        if ([string]::IsNullOrWhiteSpace($expression)) { continue }

        $measureFindings = foreach ($ap in $antiPatterns) {
            if ($expression -match $ap.Pattern) {
                $finding = [PSCustomObject]@{
                    MeasureName = $measureName
                    TableName   = $tableName
                    PatternId   = $ap.Id
                    PatternName = $ap.Name
                    Severity    = $ap.Severity
                    Description = $ap.Description
                }
                $allFindings.Add($finding)
                $finding
            }
        }

        # Measure complexity heuristics
        $lineCount = ($expression -split "`n").Count
        $hasVariables = $expression -match '(?i)\bVAR\b'
        $nestedFunctions = ([regex]::Matches($expression, '(?i)(CALCULATE|SUMX|FILTER|SWITCH|IF)\s*\(')).Count

        [PSCustomObject]@{
            TableName       = $tableName
            MeasureName     = $measureName
            LineCount       = $lineCount
            UsesVariables   = $hasVariables
            NestedFunctions = $nestedFunctions
            FindingsCount   = @($measureFindings).Count
            IsHidden        = $measure.'[IsHidden]'
            HasDescription  = -not [string]::IsNullOrWhiteSpace($measure.'[Description]')
        }
    }

    # Summary
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $report = [ordered]@{
        AnalysisTimestamp = $timestamp
        DatasetId         = $DatasetId
        WorkspaceId       = $WorkspaceId
        TotalMeasures     = $measures.Count
        MeasuresWithIssues = ($measureStats | Where-Object FindingsCount -gt 0).Count
        FindingsSummary   = [ordered]@{
            Critical = ($allFindings | Where-Object Severity -eq 'Critical').Count
            Warning  = ($allFindings | Where-Object Severity -eq 'Warning').Count
            Info     = ($allFindings | Where-Object Severity -eq 'Info').Count
        }
        ComplexMeasures   = @($measureStats | Where-Object { $_.LineCount -gt 20 -or $_.NestedFunctions -gt 5 } | Select-Object TableName, MeasureName, LineCount, NestedFunctions)
        MeasuresWithoutVars = @($measureStats | Where-Object { -not $_.UsesVariables -and $_.NestedFunctions -gt 2 } | Select-Object TableName, MeasureName, NestedFunctions)
        MeasuresMissingDesc = @($measureStats | Where-Object { -not $_.HasDescription -and -not $_.IsHidden } | Select-Object TableName, MeasureName)
        AllFindings       = $allFindings
        MeasureDetails    = $measureStats
    }

    # Save output
    $outputFile = Join-Path $OutputPath "dax-metrics_$timestamp.json"
    $report | ConvertTo-Json -Depth 10 | Set-Content -Path $outputFile -Encoding UTF8

    # Print summary
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " DAX MEASURE ANALYSIS SUMMARY" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Total Measures:       $($measures.Count)"
    Write-Host "  Measures with Issues: $($report.MeasuresWithIssues)"
    Write-Host "  Complex Measures:     $($report.ComplexMeasures.Count)"
    Write-Host "  Missing Descriptions: $($report.MeasuresMissingDesc.Count)"
    Write-Host "  Findings:"
    Write-Host "    Warning: $($report.FindingsSummary.Warning)" -ForegroundColor $(if ($report.FindingsSummary.Warning -gt 0) { 'Yellow' } else { 'Green' })
    Write-Host "    Info:    $($report.FindingsSummary.Info)" -ForegroundColor Green
    Write-Host "  Report saved to: $outputFile" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
}
catch {
    Write-Error "DAX analysis failed: $($_.Exception.Message)"
    Write-Host "`nStack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
