#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Resolve and download an Azure DevOps build artifact (or a single file within it):
  NuGet PackageArtifacts, shipping SDK installers, or VS Code VSIXes.

.DESCRIPTION
  One script for every "grab bits out of an AzDO build" need in the MAUI preview
  workflow. Resolves the artifact, then:

    * Whole-artifact zip download is anonymous on public orgs (e.g. dnceng-public).
    * Private orgs (e.g. devdiv) need an AAD token minted via `az account get-access-token`.
    * -List uses the AzDO container file service when a token is available (it can
      require auth even on public orgs) and otherwise falls back to downloading the
      artifact zip and scanning it locally, so it works for Container and
      PipelineArtifact types alike.
    * -SubPath downloads the artifact zip and extracts just the requested entry
      (robust across artifact types; no fragile single-file endpoint).

  Modes:
    -List                 List files inside the artifact (optionally -Filter'd), then exit.
    -SubPath <path>       Extract a single file from within the artifact.
    (neither)             Download the whole artifact as a .zip (optionally -Extract).

  Emits a one-line [SKILL_SUMMARY] {json} at the end.

.EXAMPLE
  # List the shipping installers in a build so the agent can pick the right os/arch one
  ./Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId 1479615 `
      -ArtifactName BlobArtifacts -List -Filter '*osx-arm64*'

.EXAMPLE
  # Download all NuGet packages from a public CI build and unzip them to a local source
  ./Get-AzdoArtifact.ps1 -Organization dnceng-public -Project public -BuildId 1479615 `
      -ArtifactName PackageArtifacts -Destination ~/NuGet/Source -Extract -FlattenNupkg

.EXAMPLE
  # Download one VSIX (single file) from a private DevDiv build
  ./Get-AzdoArtifact.ps1 -Organization devdiv -Project DevDiv -BuildId 14472388 `
      -ArtifactName VSIX -SubPath 'dotnet-maui-darwin-arm64-1.16.79-g961bf2613d.vsix' `
      -Destination /tmp
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$Organization,
  [Parameter(Mandatory)][string]$Project,
  [Parameter(Mandatory)][int]$BuildId,
  [Parameter(Mandatory)][string]$ArtifactName,
  [string]$SubPath,
  [string]$Destination,
  [string]$Filter,
  [switch]$List,
  [switch]$Extract,
  [switch]$FlattenNupkg,
  [switch]$RequireAuth,
  # AAD resource id for Azure DevOps (used to mint a token via `az` for private orgs).
  [string]$AdoResourceId = '499b84ac-1321-427f-aa17-267ca6975798',
  [string]$ApiVersion = '7.1'
)

$ErrorActionPreference = 'Stop'
function Info($m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "  ok $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  !! $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "error: $m" -ForegroundColor Red; exit 1 }

function Test-IsZip([string]$Path) {
  try {
    $fs = [System.IO.File]::OpenRead($Path)
    try { $b = New-Object byte[] 4; [void]$fs.Read($b, 0, 4) } finally { $fs.Dispose() }
    return ($b.Length -ge 2 -and $b[0] -eq 0x50 -and $b[1] -eq 0x4B)   # 'PK' zip magic
  } catch { return $false }
}

function Get-ArtifactZip([string]$Url, [hashtable]$Headers, [string]$Label) {
  $zip = Join-Path ([System.IO.Path]::GetTempPath()) "azdoart-$([guid]::NewGuid().ToString('N')).zip"
  try {
    Invoke-WebRequest -Headers $Headers -Uri $Url -OutFile $zip -UseBasicParsing
  } catch {
    Die "Artifact download failed for $Label ($($_.Exception.Message))."
  }
  if (-not (Test-IsZip $zip)) {
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Die "Downloaded content for $Label is not a zip (likely an auth redirect or error page). For private orgs run 'az login' with an account that can read '$Organization'."
  }
  return $zip
}

# --- Auth --------------------------------------------------------------------
# Whole-artifact zip downloads are anonymous on public orgs (e.g. dnceng-public).
# Private orgs (e.g. devdiv) always need an AAD token. The AzDO container file
# service used by -List can require a token even on public orgs, so mint one
# opportunistically when `az` is present and otherwise fall back to a zip scan.
$publicOrgs = @('dnceng-public')
$isPublic   = $Organization -in $publicOrgs
$hasAz      = [bool](Get-Command az -ErrorAction SilentlyContinue)
$mustAuth   = [bool]$RequireAuth -or (-not $isPublic)
$wantAuth   = $mustAuth -or ($List -and $hasAz)
$headers    = @{}
if ($wantAuth) {
  if (-not $hasAz) {
    if ($mustAuth) { Die "Azure CLI ('az') is required for private org '$Organization'. Install az and run 'az login', or target a public org/build." }
  } else {
    Info "Minting Azure DevOps token via az (resource $AdoResourceId)"
    $token = (az account get-access-token --resource $AdoResourceId --query accessToken -o tsv 2>$null)
    if ($token)        { $headers['Authorization'] = "Bearer $token" }
    elseif ($mustAuth) { Die "Could not get an AzDO token. Run 'az login' with a Microsoft account that can read '$Organization'." }
    else               { Warn "No az token; will download the artifact zip and scan it locally." }
  }
}

# --- Resolve the artifact ----------------------------------------------------
$artApi = "https://dev.azure.com/$Organization/$Project/_apis/build/builds/$BuildId/artifacts?artifactName=$ArtifactName&api-version=$ApiVersion"
Info "Resolving artifact '$ArtifactName' from $Organization/$Project build $BuildId"
try {
  $art = Invoke-RestMethod -Headers $headers -Uri $artApi
} catch {
  Die "Failed to resolve artifact '$ArtifactName' on build $BuildId ($($_.Exception.Message)). Check the org/project/build id and that the artifact name is exact (case-sensitive)."
}
$downloadUrl = $art.resource.downloadUrl
$data        = $art.resource.data      # e.g. '#/<containerId>/<ArtifactName>'
if (-not $downloadUrl) { Die "Artifact '$ArtifactName' had no downloadUrl (empty or access-denied)." }

# --- LIST mode ---------------------------------------------------------------
if ($List) {
  $files = $null
  $listVia = $null
  $containerId = $null
  if ($data -match '^#/(\d+)/') { $containerId = $Matches[1] }

  # Fast path: container file service. Needs a token (even on public orgs), an
  # explicit Accept: application/json (AzDO 404s otherwise), and a -preview
  # api-version. Only valid for Container-type artifacts.
  if ($containerId -and $headers['Authorization']) {
    $cHeaders = $headers.Clone()
    $cHeaders['Accept'] = 'application/json'
    # NB: build with concatenation, not "...$containerId?itemPath..." — PowerShell 7
    # mis-parses `$var?` in an interpolated string (ternary/null-conditional) and drops it.
    $cApi = "https://dev.azure.com/$Organization/_apis/resources/Containers/$containerId" +
            "?itemPath=$([uri]::EscapeDataString($ArtifactName))&isShallow=false&api-version=7.1-preview"
    Info "Listing files in artifact '$ArtifactName' (container $containerId)"
    try {
      $items = (Invoke-RestMethod -Headers $cHeaders -Uri $cApi).value |
        Where-Object { $_.itemType -eq 'file' -or $_.blob }
      $files = foreach ($it in $items) {
        $rel = $it.path -replace "^$([regex]::Escape($ArtifactName))/?", ''
        if ($Filter -and ($rel -notlike $Filter)) { continue }
        [pscustomobject]@{ subPath = $rel; sizeBytes = [int64]($it.fileLength ?? $it.blob.size ?? 0) }
      }
      $listVia = 'container'
    } catch {
      Warn "Container listing failed ($($_.Exception.Message)); falling back to a zip download+scan."
    }
  }

  # Fallback: download the artifact zip and enumerate entries. Works anonymously
  # and for PipelineArtifact artifacts (e.g. the public 'Packages' VSIX artifact).
  if ($null -eq $listVia) {
    $zip = Get-ArtifactZip $downloadUrl $headers "artifact '$ArtifactName'"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $za = [System.IO.Compression.ZipFile]::OpenRead($zip)
    try {
      $files = foreach ($e in $za.Entries) {
        if (-not $e.Name) { continue }   # skip directory entries
        $rel = $e.FullName -replace "^$([regex]::Escape($ArtifactName))/?", ''
        if ($Filter -and ($rel -notlike $Filter)) { continue }
        [pscustomobject]@{ subPath = $rel; sizeBytes = [int64]$e.Length }
      }
    } finally { $za.Dispose() }
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    $listVia = 'zip'
  }

  $files = @($files | Sort-Object subPath)
  foreach ($f in $files) { Write-Host ("  {0,12:n0}  {1}" -f $f.sizeBytes, $f.subPath) }
  Ok "$($files.Count) file(s) listed (via $listVia)"
  Write-Host ("[SKILL_SUMMARY] " + (@{ mode='list'; artifact=$ArtifactName; buildId=$BuildId; via=$listVia; count=$files.Count; files=$files } | ConvertTo-Json -Depth 5 -Compress))
  return
}

# --- Prepare destination -----------------------------------------------------
if (-not $Destination) { $Destination = (Get-Location).Path }
$Destination = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination)
New-Item -ItemType Directory -Force -Path $Destination | Out-Null

# --- SINGLE FILE (subPath) ---------------------------------------------------
# Download the artifact zip and extract just the requested entry. Works for both
# Container and PipelineArtifact types with no fragile single-file endpoint.
if ($SubPath) {
  $want = ($SubPath -replace '^/', '')
  $leaf = [System.IO.Path]::GetFileName($want)
  $outFile = Join-Path $Destination $leaf
  Info "Fetching '$leaf' from artifact '$ArtifactName'"
  $zip = Get-ArtifactZip $downloadUrl $headers "artifact '$ArtifactName'"
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $za = [System.IO.Compression.ZipFile]::OpenRead($zip)
  try {
    $entry = $za.Entries | Where-Object { $_.FullName -eq "$ArtifactName/$want" } | Select-Object -First 1
    if (-not $entry) { $entry = $za.Entries | Where-Object { $_.FullName -eq $want } | Select-Object -First 1 }
    if (-not $entry) { $entry = $za.Entries | Where-Object { ($_.FullName -replace "^$([regex]::Escape($ArtifactName))/?", '') -eq $want } | Select-Object -First 1 }
    if (-not $entry) { $entry = $za.Entries | Where-Object { $_.Name -eq $leaf } | Select-Object -First 1 }
    if (-not $entry) {
      Die "SubPath '$SubPath' not found in artifact '$ArtifactName'. Run with -List to see exact file names (case-sensitive)."
    }
    [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $outFile, $true)
  } finally { $za.Dispose() }
  Remove-Item $zip -Force -ErrorAction SilentlyContinue
  Ok "Saved $outFile"
  Write-Host ("[SKILL_SUMMARY] " + (@{ mode='file'; artifact=$ArtifactName; buildId=$BuildId; subPath=$SubPath; path=$outFile } | ConvertTo-Json -Depth 4 -Compress))
  return
}

# --- WHOLE ARTIFACT (zip) ----------------------------------------------------
Info "Downloading artifact '$ArtifactName' (zip)"
$zip = Get-ArtifactZip $downloadUrl $headers "artifact '$ArtifactName'"
$extractedTo = $null
$copied = 0
if ($Extract -or $FlattenNupkg) {
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) "$ArtifactName-$BuildId-$([guid]::NewGuid().ToString('N'))"
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  Info "Extracting"
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  if ($FlattenNupkg) {
    # Copy just the .nupkg files up to $Destination (a flat local NuGet source).
    foreach ($n in Get-ChildItem -Path $tmp -Recurse -Filter '*.nupkg') {
      Copy-Item $n.FullName -Destination $Destination -Force; $copied++
    }
    if ($copied -eq 0) { Warn "No .nupkg files found in artifact '$ArtifactName'." }
    Ok "Copied $copied .nupkg file(s) to $Destination"
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    $extractedTo = $Destination
  } else {
    # Move the extracted tree into $Destination.
    Copy-Item -Path (Join-Path $tmp '*') -Destination $Destination -Recurse -Force
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    $extractedTo = $Destination
    Ok "Extracted artifact to $Destination"
  }
  Remove-Item $zip -Force -ErrorAction SilentlyContinue
} else {
  $final = Join-Path $Destination "$ArtifactName.zip"
  Move-Item $zip $final -Force
  $zip = $final
  Ok "Saved $final"
}

Write-Host ("[SKILL_SUMMARY] " + (@{
  mode         = if ($FlattenNupkg) { 'nupkg' } elseif ($Extract) { 'extract' } else { 'zip' }
  artifact     = $ArtifactName; buildId = $BuildId
  destination  = $Destination
  extractedTo  = $extractedTo
  nupkgCopied  = $copied
  zipPath      = if ($Extract -or $FlattenNupkg) { $null } else { $zip }
} | ConvertTo-Json -Depth 4 -Compress))
