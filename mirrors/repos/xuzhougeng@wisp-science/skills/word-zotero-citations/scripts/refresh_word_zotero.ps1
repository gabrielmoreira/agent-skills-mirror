param(
    [Parameter(Mandatory = $true)][string]$Authorization,
    [string]$PythonExecutable = 'python',
    [int]$TimeoutSeconds = 600,
    [int]$StableSeconds = 5,
    [switch]$ValidateOnly
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$word = $null
$doc = $null
$started = [DateTime]::UtcNow
$before = $null
$after = $null
$lastSnapshot = $null
$macroCallCount = 0
$destinationCreated = $false
$wordVisibleBefore = $null
$wordAlertsBefore = $null

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-ZoteroFieldSnapshot {
    param([Parameter(Mandatory = $true)]$Document)

    $citationCount = 0
    $citationItemCount = 0
    $bibliographyCount = 0
    $bibliographyText = ''
    $citationResults = @()
    for ($index = 1; $index -le $Document.Fields.Count; $index++) {
        $field = $Document.Fields.Item($index)
        try {
            $code = [string]$field.Code.Text
            if ($code -match 'ZOTERO_ITEM') {
                $citationCount++
                $citationResults += [string]$field.Result.Text
                $start = $code.IndexOf('{')
                $end = $code.LastIndexOf('}')
                if (($start -lt 0) -or ($end -lt $start)) {
                    throw 'Citation field has no JSON payload'
                }
                $payload = $code.Substring($start, $end - $start + 1) | ConvertFrom-Json
                $citationItemCount += @($payload.citationItems).Count
            }
            elseif ($code -match 'ZOTERO_BIBL') {
                $bibliographyCount++
                $bibliographyText = [string]$field.Result.Text
            }
        }
        finally {
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($field)
        }
    }

    [pscustomobject]@{
        citation_count = $citationCount
        citation_item_occurrence_count = $citationItemCount
        citation_results = @($citationResults)
        bibliography_count = $bibliographyCount
        bibliography_length = $bibliographyText.Length
        bibliography_prefix = if ($bibliographyText.Length -gt 300) { $bibliographyText.Substring(0, 300) } else { $bibliographyText }
        bibliography_contains_pending = $bibliographyText.Contains('[Bibliography refresh pending]')
    }
}

function Assert-ExpectedSnapshot {
    param(
        [Parameter(Mandatory = $true)]$Snapshot,
        [Parameter(Mandatory = $true)]$Contract,
        [Parameter(Mandatory = $true)][string]$Phase,
        [switch]$RequireRefreshedBibliography
    )

    if ($Snapshot.citation_count -ne [int]$Contract.expected_citation_field_count) {
        throw "$Phase citation-field count differs from authorization"
    }
    if ($Snapshot.citation_item_occurrence_count -ne [int]$Contract.expected_citation_item_occurrence_count) {
        throw "$Phase citation-item occurrence count differs from authorization"
    }
    if ($Snapshot.bibliography_count -ne [int]$Contract.expected_bibliography_field_count) {
        throw "$Phase bibliography-field count differs from authorization"
    }
    if ($RequireRefreshedBibliography -and $Snapshot.bibliography_contains_pending) {
        throw "$Phase bibliography still contains the provisional Refresh marker"
    }
}

function Write-AtomicJsonReport {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Payload
    )

    if (Test-Path -LiteralPath $Path) {
        throw "Report already exists: $Path"
    }
    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        throw "Report directory does not exist: $directory"
    }
    $temporary = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Path) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        $json = $Payload | ConvertTo-Json -Depth 12
        [System.IO.File]::WriteAllText($temporary, $json, [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::Move($temporary, $Path)
    }
    finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force
        }
    }
}

function Copy-DiagnosticOnce {
    param(
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][string]$Diagnostic
    )

    if ((Test-Path -LiteralPath $Destination -PathType Leaf) -and -not (Test-Path -LiteralPath $Diagnostic)) {
        Copy-Item -LiteralPath $Destination -Destination $Diagnostic
    }
}

if ($TimeoutSeconds -lt 1) { throw 'TimeoutSeconds must be positive' }
if ($StableSeconds -lt 1) { throw 'StableSeconds must be positive' }
if (-not (Test-Path -LiteralPath $Authorization -PathType Leaf)) {
    throw "Refresh authorization does not exist: $Authorization"
}

$verificationJson = & $PythonExecutable -m zotero_mcp.word_citations.refresh --authorization $Authorization --check-zotero-visibility
if ($LASTEXITCODE -ne 0) {
    throw 'Python rejected the Refresh authorization before Word startup'
}
$contract = $verificationJson | ConvertFrom-Json
if ($contract.status -ne 'authorized') {
    throw 'Refresh authorization verifier did not return authorized status'
}
if (($null -eq $contract.zotero_visibility) -or -not [bool]$contract.zotero_visibility.ready) {
    throw 'Authorized Zotero Local API Collection is not fully visible'
}
if ($ValidateOnly) {
    $verificationJson
    return
}

$candidate = [string]$contract.candidate_path
$source = [string]$contract.source_path
$destination = [string]$contract.destination_path
$report = [string]$contract.report_path
$diagnostic = [string]$contract.diagnostic_path
$macro = [string]$contract.macro_name
$sourceHashBefore = Get-Sha256 -Path $source
$candidateHashBefore = Get-Sha256 -Path $candidate
if ($sourceHashBefore -ne [string]$contract.source_sha256) { throw 'Source SHA-256 changed after authorization verification' }
if ($candidateHashBefore -ne [string]$contract.candidate_sha256) { throw 'Candidate SHA-256 changed after authorization verification' }
if (Test-Path -LiteralPath $destination) { throw "Destination already exists: $destination" }
if (Test-Path -LiteralPath $report) { throw "Report already exists: $report" }
if (Test-Path -LiteralPath $diagnostic) { throw "Diagnostic already exists: $diagnostic" }

try {
    Copy-Item -LiteralPath $candidate -Destination $destination
    $destinationCreated = $true
    if ((Get-Sha256 -Path $destination) -ne $candidateHashBefore) {
        throw 'Destination copy differs from the authorized candidate'
    }

    $word = New-Object -ComObject Word.Application
    $wordVisibleBefore = [bool]$word.Visible
    $wordAlertsBefore = [int]$word.DisplayAlerts
    $word.Visible = $true
    $word.DisplayAlerts = 0
    $wordVersion = [string]$word.Version
    $doc = $word.Documents.Open($destination, $false, $false, $false)
    $before = Get-ZoteroFieldSnapshot -Document $doc
    Assert-ExpectedSnapshot -Snapshot $before -Contract $contract -Phase 'Pre-Refresh'

    $macroCallCount++
    $word.Run($macro)

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $stableSince = $null
    $stableFingerprint = $null
    do {
        Start-Sleep -Milliseconds 750
        try {
            $snapshot = Get-ZoteroFieldSnapshot -Document $doc
            $lastSnapshot = $snapshot
            Assert-ExpectedSnapshot -Snapshot $snapshot -Contract $contract -Phase 'Post-Refresh' -RequireRefreshedBibliography
            $fingerprint = $snapshot | ConvertTo-Json -Compress -Depth 6
            if ($fingerprint -ne $stableFingerprint) {
                $stableFingerprint = $fingerprint
                $stableSince = [DateTime]::UtcNow
            }
            elseif (([DateTime]::UtcNow - $stableSince).TotalSeconds -ge $StableSeconds) {
                $after = $snapshot
                break
            }
        }
        catch {
            $stableSince = $null
            $stableFingerprint = $null
        }
    } while ([DateTime]::UtcNow -lt $deadline)

    if ($null -eq $after) {
        throw "Timed out after $TimeoutSeconds seconds waiting for a stable Zotero Refresh snapshot"
    }
    if ($macroCallCount -ne [int]$contract.expected_formal_refresh_count) {
        throw 'Observed macro-call count differs from the authorization'
    }

    $doc.Save()
    $doc.Close($false)
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
    $doc = $null
    $word.DisplayAlerts = $wordAlertsBefore
    $word.Visible = $wordVisibleBefore
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    $word = $null

    $sourceHashAfter = Get-Sha256 -Path $source
    $candidateHashAfter = Get-Sha256 -Path $candidate
    if ($sourceHashAfter -ne $sourceHashBefore) { throw 'Source changed during Refresh' }
    if ($candidateHashAfter -ne $candidateHashBefore) { throw 'Pre-Refresh candidate changed during Refresh' }
    $output = Get-Item -LiteralPath $destination
    Write-AtomicJsonReport -Path $report -Payload ([ordered]@{
        schema_version = 1
        status = 'pass'
        task_id = [string]$contract.task_id
        attempt_id = [string]$contract.attempt_id
        authorization_path = [System.IO.Path]::GetFullPath($Authorization)
        authorization_sha256 = [string]$contract.authorization_sha256
        zotero_visibility = $contract.zotero_visibility
        source_path = $source
        source_sha256_before = $sourceHashBefore
        source_sha256_after = $sourceHashAfter
        candidate_path = $candidate
        candidate_sha256_before = $candidateHashBefore
        candidate_sha256_after = $candidateHashAfter
        destination_path = $output.FullName
        destination_sha256 = Get-Sha256 -Path $destination
        destination_size = $output.Length
        diagnostic_path = $diagnostic
        diagnostic_created = Test-Path -LiteralPath $diagnostic
        diagnostic_sha256 = if (Test-Path -LiteralPath $diagnostic -PathType Leaf) { Get-Sha256 -Path $diagnostic } else { $null }
        macro_name = $macro
        macro_call_count = $macroCallCount
        started_utc = $started.ToString('o')
        completed_utc = [DateTime]::UtcNow.ToString('o')
        word_version = $wordVersion
        timeout_seconds = $TimeoutSeconds
        stable_seconds = $StableSeconds
        before = $before
        after = $after
    })
}
catch {
    $errorRecord = $_
    if ($doc -ne $null) {
        try { $doc.Close($false) } catch {}
    }
    if ($word -ne $null) {
        try {
            if ($null -ne $wordAlertsBefore) { $word.DisplayAlerts = $wordAlertsBefore }
            if ($null -ne $wordVisibleBefore) { $word.Visible = $wordVisibleBefore }
        } catch {}
        try { $word.Quit() } catch {}
    }
    $diagnosticError = $null
    if ($destinationCreated) {
        try { Copy-DiagnosticOnce -Destination $destination -Diagnostic $diagnostic } catch { $diagnosticError = $_.Exception.Message }
    }
    $sourceHashAfter = $null
    $candidateHashAfter = $null
    try { $sourceHashAfter = Get-Sha256 -Path $source } catch {}
    try { $candidateHashAfter = Get-Sha256 -Path $candidate } catch {}
    $failure = [ordered]@{
        schema_version = 1
        status = 'error'
        task_id = [string]$contract.task_id
        attempt_id = [string]$contract.attempt_id
        authorization_path = [System.IO.Path]::GetFullPath($Authorization)
        authorization_sha256 = [string]$contract.authorization_sha256
        zotero_visibility = $contract.zotero_visibility
        source_path = $source
        source_sha256_before = $sourceHashBefore
        source_sha256_after = $sourceHashAfter
        candidate_path = $candidate
        candidate_sha256_before = $candidateHashBefore
        candidate_sha256_after = $candidateHashAfter
        destination_path = $destination
        destination_exists = Test-Path -LiteralPath $destination
        destination_sha256 = if (Test-Path -LiteralPath $destination -PathType Leaf) { Get-Sha256 -Path $destination } else { $null }
        diagnostic_path = $diagnostic
        diagnostic_created = Test-Path -LiteralPath $diagnostic
        diagnostic_sha256 = if (Test-Path -LiteralPath $diagnostic -PathType Leaf) { Get-Sha256 -Path $diagnostic } else { $null }
        diagnostic_error = $diagnosticError
        report_error = $null
        macro_name = $macro
        macro_call_count = $macroCallCount
        started_utc = $started.ToString('o')
        failed_utc = [DateTime]::UtcNow.ToString('o')
        timeout_seconds = $TimeoutSeconds
        stable_seconds = $StableSeconds
        before = $before
        last_snapshot = $lastSnapshot
        error = $errorRecord.Exception.Message
        error_type = $errorRecord.Exception.GetType().FullName
        retry_performed = $false
    }
    try {
        Write-AtomicJsonReport -Path $report -Payload $failure
    }
    catch {
        $failure.report_error = $_.Exception.Message
        [Console]::Error.WriteLine(($failure | ConvertTo-Json -Depth 12))
    }
    throw
}
finally {
    if ($doc -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    if ($word -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
