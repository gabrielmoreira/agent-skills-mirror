param(
    [Parameter(Mandatory = $true)][string]$Authorization,
    [Parameter(Mandatory = $true)][ValidateSet('citation', 'bibliography')][string]$Mode,
    [Parameter(Mandatory = $true)][string]$WorkingCopy,
    [Parameter(Mandatory = $true)][string]$Report,
    [int]$OpenTimeoutSeconds = 180,
    [int]$DialogObserveSeconds = 8,
    [int]$CloseTimeoutSeconds = 30,
    [string]$PythonExecutable = 'python'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$word = $null
$doc = $null
$started = [DateTime]::UtcNow
$dialogWindow = $null
$cleanupWarning = $null

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Write-AtomicJsonReport {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)]$Payload)
    if (Test-Path -LiteralPath $Path) { throw "Report already exists: $Path" }
    $directory = Split-Path -Parent $Path
    $temporary = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Path) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        $json = $Payload | ConvertTo-Json -Depth 12
        [System.IO.File]::WriteAllText($temporary, $json, [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::Move($temporary, $Path)
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
}

if (-not ('WispUiWindowInfo' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Collections.Generic;

public sealed class WispUiWindowInfo {
    public long Handle { get; set; }
    public uint ProcessId { get; set; }
    public string Title { get; set; }
    public string ClassName { get; set; }
}

public static class WispUiNativeWindow {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    static extern int GetClassName(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    public const uint WM_CLOSE = 0x0010;

    public static WispUiWindowInfo[] GetVisibleWindows() {
        var rows = new List<WispUiWindowInfo>();
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (!IsWindowVisible(hWnd)) return true;
            var title = new StringBuilder(2048);
            var className = new StringBuilder(512);
            GetWindowText(hWnd, title, title.Capacity);
            GetClassName(hWnd, className, className.Capacity);
            if (title.Length == 0) return true;
            uint processId;
            GetWindowThreadProcessId(hWnd, out processId);
            rows.Add(new WispUiWindowInfo {
                Handle = hWnd.ToInt64(),
                ProcessId = processId,
                Title = title.ToString(),
                ClassName = className.ToString()
            });
            return true;
        }, IntPtr.Zero);
        return rows.ToArray();
    }

    public static bool CloseWindow(long handle) {
        return PostMessage(new IntPtr(handle), WM_CLOSE, IntPtr.Zero, IntPtr.Zero);
    }
}
'@
}

function Get-WindowSnapshot {
    $rows = @()
    foreach ($window in [WispUiNativeWindow]::GetVisibleWindows()) {
        $process = Get-Process -Id $window.ProcessId -ErrorAction SilentlyContinue
        if ($null -eq $process) { continue }
        $rows += [pscustomobject]@{
            handle = [long]$window.Handle
            process_id = [int]$window.ProcessId
            process_name = [string]$process.ProcessName
            class_name = [string]$window.ClassName
            title = [string]$window.Title
        }
    }
    return @($rows)
}

function Get-ZoteroWindows {
    return @(Get-WindowSnapshot | Where-Object {
        $_.process_name -eq 'zotero' -and
        ($_.class_name -like 'Mozilla*' -or $_.class_name -like '*Zotero*')
    })
}

function Get-FieldSnapshot {
    param([Parameter(Mandatory = $true)]$Document)

    $citationCount = 0
    $bibliographyCount = 0
    $bibliographyLength = 0
    $citationIds = New-Object System.Collections.Generic.List[string]
    $uriKeys = New-Object System.Collections.Generic.List[string]
    $citationItemOccurrenceCount = 0
    $userPrefix = 'http://zotero.org/users/' + $script:USER_ID + '/items/'

    for ($index = 1; $index -le $Document.Fields.Count; $index++) {
        $field = $Document.Fields.Item($index)
        try {
            $code = [string]$field.Code.Text
            if ($code -match 'ZOTERO_ITEM') {
                $citationCount++
                $citationMatch = [regex]::Match($code, '"citationID"\s*:\s*"([^"]+)"')
                if ($citationMatch.Success) {
                    [void]$citationIds.Add($citationMatch.Groups[1].Value)
                }
                $uriMatches = [regex]::Matches($code, [regex]::Escape($userPrefix) + '([A-Z0-9]+)', 'IgnoreCase')
                $citationItemOccurrenceCount += $uriMatches.Count
                foreach ($uriMatch in $uriMatches) {
                    [void]$uriKeys.Add($uriMatch.Groups[1].Value.ToUpperInvariant())
                }
            }
            elseif ($code -match 'ZOTERO_BIBL') {
                $bibliographyCount++
                $bibliographyLength = ([string]$field.Result.Text).Length
            }
        }
        finally {
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($field)
        }
    }

    return [pscustomobject]@{
        citation_count = $citationCount
        citation_item_occurrence_count = $citationItemOccurrenceCount
        bibliography_count = $bibliographyCount
        bibliography_length = $bibliographyLength
        unique_citation_id_count = @($citationIds | Sort-Object -Unique).Count
        unique_item_key_count = @($uriKeys | Sort-Object -Unique).Count
    }
}

function Assert-ExpectedSnapshot {
    param([Parameter(Mandatory = $true)]$Snapshot, [Parameter(Mandatory = $true)]$Contract, [Parameter(Mandatory = $true)][string]$Phase)
    if ($Snapshot.citation_count -ne [int]$Contract.expected_citation_field_count) { throw "$Phase citation-field count differs" }
    if ($Snapshot.citation_item_occurrence_count -ne [int]$Contract.expected_citation_item_occurrence_count) { throw "$Phase citation-item occurrence count differs" }
    if ($Snapshot.bibliography_count -ne [int]$Contract.expected_bibliography_field_count) { throw "$Phase bibliography-field count differs" }
    if ($Snapshot.unique_citation_id_count -ne [int]$Contract.expected_citation_field_count) { throw "$Phase unique citation-id count differs" }
    $expectedUniqueKeys = @($Contract.item_keys | Sort-Object -Unique).Count
    if ($Snapshot.unique_item_key_count -ne $expectedUniqueKeys) { throw "$Phase unique item-key count differs" }
}

function Wait-ForDocumentReady {
    param([Parameter(Mandatory = $true)]$Document, [Parameter(Mandatory = $true)]$Contract, [int]$TimeoutSeconds)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        Start-Sleep -Milliseconds 500
        try {
            $snapshot = Get-FieldSnapshot -Document $Document
            Assert-ExpectedSnapshot -Snapshot $snapshot -Contract $Contract -Phase 'Word-open'
            return $snapshot
        }
        catch {}
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "Timed out waiting for Word to expose the authorized field snapshot"
}

if (-not (Test-Path -LiteralPath $Authorization -PathType Leaf)) { throw "Authorization does not exist: $Authorization" }
$contractJson = & $PythonExecutable -m zotero_mcp.word_citations.refresh --authorization $Authorization --allow-existing-outputs
if ($LASTEXITCODE -ne 0) { throw 'Python rejected the Refresh authorization before UI validation' }
$contract = $contractJson | ConvertFrom-Json
if ($contract.status -ne 'authorized') { throw 'Refresh authorization verifier did not return authorized status' }

$script:USER_ID = [string]$contract.library_id
$destination = [string]$contract.destination_path
$source = [string]$contract.source_path
if ([System.IO.Path]::GetFullPath($destination) -eq [System.IO.Path]::GetFullPath($WorkingCopy)) { throw 'Working copy must differ from the destination' }
if ([System.IO.Path]::GetFullPath($source) -eq [System.IO.Path]::GetFullPath($WorkingCopy)) { throw 'Working copy must differ from the source' }
if (Test-Path -LiteralPath $WorkingCopy) { throw "Working copy already exists: $WorkingCopy" }
if (Test-Path -LiteralPath $Report) { throw "Report already exists: $Report" }
if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) { throw "Destination does not exist: $destination" }

$destinationHashBefore = Get-Sha256 -Path $destination
$sourceHashBefore = Get-Sha256 -Path $source
Copy-Item -LiteralPath $destination -Destination $WorkingCopy
$copyHashBefore = Get-Sha256 -Path $WorkingCopy
if ($copyHashBefore -ne $destinationHashBefore) { throw 'Working copy differs from the authorized destination' }

$macroError = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $true
    $word.DisplayAlerts = 0
    $wordVersion = [string]$word.Version
    $doc = $word.Documents.Open($WorkingCopy, $false, $false, $false)
    $doc.Activate()
    $fieldBefore = Wait-ForDocumentReady -Document $doc -Contract $contract -TimeoutSeconds $OpenTimeoutSeconds

    if ($Mode -eq 'citation') {
        $targetField = $null
        for ($index = 1; $index -le $doc.Fields.Count; $index++) {
            $candidateField = $doc.Fields.Item($index)
            if ([string]$candidateField.Code.Text -match 'ZOTERO_ITEM') {
                $targetField = $candidateField
                break
            }
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($candidateField)
        }
        if ($null -eq $targetField) { throw 'No ZOTERO_ITEM field was exposed by Word' }
        try { $targetField.Result.Select() } finally { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($targetField) }
        $macro = 'ZoteroAddEditCitation'
    }
    else {
        $macro = 'ZoteroAddEditBibliography'
    }

    $baselineHandles = @((Get-ZoteroWindows).handle)
    try { $word.Run($macro) } catch { $macroError = $_.Exception.Message }

    $dialogDeadline = [DateTime]::UtcNow.AddSeconds($OpenTimeoutSeconds)
    do {
        Start-Sleep -Milliseconds 250
        $candidates = @(Get-ZoteroWindows | Where-Object { $baselineHandles -notcontains $_.handle })
        if ($candidates.Count -gt 0) { $dialogWindow = $candidates[0] }
    } while ($null -eq $dialogWindow -and [DateTime]::UtcNow -lt $dialogDeadline)
    if ($null -eq $dialogWindow) { throw "No new Zotero integration window appeared for $macro. Macro error: $macroError" }

    Start-Sleep -Seconds $DialogObserveSeconds
    $fieldWhileOpen = Get-FieldSnapshot -Document $doc
    Assert-ExpectedSnapshot -Snapshot $fieldWhileOpen -Contract $contract -Phase 'Dialog-open'
    $dialogSnapshot = [pscustomobject]@{
        handle = $dialogWindow.handle
        process_id = $dialogWindow.process_id
        process_name = $dialogWindow.process_name
        class_name = $dialogWindow.class_name
        title = $dialogWindow.title
    }

    [void][WispUiNativeWindow]::CloseWindow([long]$dialogWindow.handle)
    $stillOpen = $true
    $closeDeadline = [DateTime]::UtcNow.AddSeconds($CloseTimeoutSeconds)
    do {
        Start-Sleep -Milliseconds 250
        $stillOpen = @(Get-WindowSnapshot | Where-Object { $_.handle -eq $dialogWindow.handle }).Count -gt 0
    } while ($stillOpen -and [DateTime]::UtcNow -lt $closeDeadline)
    if ($stillOpen) { throw "The Zotero integration window did not close within $CloseTimeoutSeconds seconds" }

    Start-Sleep -Seconds 2
    $fieldAfterCancel = Get-FieldSnapshot -Document $doc
    Assert-ExpectedSnapshot -Snapshot $fieldAfterCancel -Contract $contract -Phase 'After-cancel'
    $savedState = [bool]$doc.Saved
    try {
        $doc.Close(0)
        $doc = $null
        $word.Quit()
        $word = $null
    }
    catch {
        $cleanupException = $_.Exception
        $isRpcUnavailable = $false
        while ($null -ne $cleanupException) {
            if ($cleanupException.HResult -eq -2147023174) { $isRpcUnavailable = $true; break }
            $cleanupException = $cleanupException.InnerException
        }
        if (-not $isRpcUnavailable) { throw }
        $cleanupWarning = 'Word COM disconnected with RPC_S_SERVER_UNAVAILABLE after the Zotero dialog was recognized and closed; unchanged file hashes remain mandatory'
        $doc = $null
        $word = $null
    }

    $copyHashAfter = Get-Sha256 -Path $WorkingCopy
    $destinationHashAfter = Get-Sha256 -Path $destination
    $sourceHashAfter = Get-Sha256 -Path $source
    $copyUnchanged = $copyHashAfter -eq $copyHashBefore
    $destinationUnchanged = $destinationHashAfter -eq $destinationHashBefore
    $sourceUnchanged = $sourceHashAfter -eq $sourceHashBefore

    $result = [ordered]@{
        schema_version = 1
        status = if ($copyUnchanged -and $destinationUnchanged -and $sourceUnchanged) { 'pass' } else { 'fail' }
        task_id = [string]$contract.task_id
        attempt_id = [string]$contract.attempt_id
        authorization_sha256 = [string]$contract.authorization_sha256
        mode = $Mode
        recognition_signal = if ($Mode -eq 'citation') { 'Zotero citation editor window opened while the first existing ZOTERO_ITEM field result was selected' } else { 'Zotero bibliography editor window opened while the document already contained one ZOTERO_BIBL field' }
        destination = [System.IO.Path]::GetFullPath($destination)
        destination_sha256_before = $destinationHashBefore
        destination_sha256_after = $destinationHashAfter
        destination_unchanged = $destinationUnchanged
        working_copy = [System.IO.Path]::GetFullPath($WorkingCopy)
        working_copy_sha256_before = $copyHashBefore
        working_copy_sha256_after = $copyHashAfter
        working_copy_unchanged = $copyUnchanged
        source = [System.IO.Path]::GetFullPath($source)
        source_sha256_before = $sourceHashBefore
        source_sha256_after = $sourceHashAfter
        source_unchanged = $sourceUnchanged
        ui_copy_disposable = $true
        ui_edits_cancelled = $true
        macro = $macro
        macro_error = $macroError
        dialog = $dialogSnapshot
        field_snapshot_before = $fieldBefore
        field_snapshot_while_dialog_open = $fieldWhileOpen
        field_snapshot_after_cancel = $fieldAfterCancel
        document_saved_property_before_close = $savedState
        word_version = $wordVersion
        started_utc = $started.ToString('o')
        completed_utc = [DateTime]::UtcNow.ToString('o')
        dialog_observe_seconds = $DialogObserveSeconds
        close_method = 'WM_CLOSE followed by Word close with wdDoNotSaveChanges'
        cleanup_warning = $cleanupWarning
    }

    if (-not $copyUnchanged) { throw 'The UI validation working copy changed despite cancelling and closing without save' }
    if (-not $destinationUnchanged) { throw 'The authorized destination changed during UI validation' }
    if (-not $sourceUnchanged) { throw 'The protected source changed during UI validation' }
    Write-AtomicJsonReport -Path $Report -Payload $result
    $result | ConvertTo-Json -Depth 12
}
catch {
    $failure = [ordered]@{
        schema_version = 1
        status = 'fail'
        task_id = if ($contract) { [string]$contract.task_id } else { $null }
        attempt_id = if ($contract) { [string]$contract.attempt_id } else { $null }
        authorization_sha256 = if ($contract) { [string]$contract.authorization_sha256 } else { $null }
        mode = $Mode
        macro = if ($Mode -eq 'citation') { 'ZoteroAddEditCitation' } else { 'ZoteroAddEditBibliography' }
        error = $_.Exception.Message
        started_utc = $started.ToString('o')
        completed_utc = [DateTime]::UtcNow.ToString('o')
    }
    try { Write-AtomicJsonReport -Path $Report -Payload $failure } catch {}
    if ($dialogWindow -ne $null) { try { [void][WispUiNativeWindow]::CloseWindow([long]$dialogWindow.handle) } catch {} }
    if ($doc -ne $null) { try { $doc.Close(0) } catch {} }
    if ($word -ne $null) { try { $word.Quit() } catch {} }
    throw
}
finally {
    if ($doc -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    if ($word -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
