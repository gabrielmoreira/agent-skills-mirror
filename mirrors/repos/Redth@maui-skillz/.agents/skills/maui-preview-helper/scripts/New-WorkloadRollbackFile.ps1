#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Construct a .NET workload rollback file from a dotnet/maui branch's version files.

.DESCRIPTION
    Reads the authoritative rollback template
    (src/Workload/Microsoft.NET.Sdk.Maui.Manifest/Rollback.in.json) and eng/Versions.props
    from a dotnet/maui branch, substitutes each @Property@ placeholder with its value, and
    writes a flat rollback JSON of the form { "manifest.id": "version/sdk-band", ... } suitable
    for `dotnet workload install maui --from-rollback-file <file>`.

    The template is the source of truth for WHICH manifest IDs exist (this differs by branch),
    so the output stays correct across net9.0 / main / PR branches without hard-coding a list.

    NOTE: the microsoft.net.sdk.maui version (@VERSION@) is the MAUI package's own build version
    and is NOT statically knowable from the repo. Supply it with -MauiVersion (from the CI build
    you are dogfooding) or via -Override. Anything the script can't resolve is reported so the
    caller can fill it in.

.PARAMETER Repo
    owner/name of the MAUI repo. Default: dotnet/maui.

.PARAMETER Branch
    Branch (or tag / commit sha) to read version files from. Default: main.

.PARAMETER OutFile
    Path to write the rollback JSON. If omitted, JSON is written to stdout.

.PARAMETER Band
    Force the SDK feature band (the part after '/') for every entry, e.g. '9.0.100' or
    '10.0.100-preview.5'. Overrides whatever band the template properties resolve to. Useful
    when a band property is computed in MSBuild and can't be read literally.

.PARAMETER MauiVersion
    Explicit version for the microsoft.net.sdk.maui manifest (the @VERSION@ placeholder), e.g.
    '9.0.80-ci.net9.12345'. Strongly recommended — see NOTE above.

.PARAMETER Override
    One or more 'manifest.id=version' or 'manifest.id=version/band' entries applied LAST — after
    -MauiVersion — so an explicit -Override always wins. Example:
    -Override 'microsoft.net.sdk.ios=18.2.9000'

.PARAMETER AllowUnresolved
    Write the rollback file even if some entries still contain unresolved @tokens@ or $(refs).
    By default the script fails fast (nothing is written) so a broken file never reaches
    `dotnet workload install`.

.PARAMETER RollbackTemplateUrl
    Override the raw URL of Rollback.in.json (advanced).

.PARAMETER VersionsPropsUrl
    Override the raw URL of Versions.props (advanced).

.EXAMPLE
    pwsh New-WorkloadRollbackFile.ps1 -Branch net9.0 -MauiVersion 9.0.80-ci.net9.9999 -OutFile ./rollback.json

.EXAMPLE
    pwsh New-WorkloadRollbackFile.ps1 -Branch main -Band 10.0.100 -Override 'microsoft.net.sdk.ios=26.0.11017' -OutFile ./rollback.json
#>
[CmdletBinding()]
param(
    [string]$Repo = 'dotnet/maui',
    [string]$Branch = 'main',
    [string]$OutFile,
    [string]$Band,
    [string]$MauiVersion,
    [string[]]$Override = @(),
    [switch]$AllowUnresolved,
    [string]$RollbackTemplateUrl,
    [string]$VersionsPropsUrl
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }

if (-not $RollbackTemplateUrl) {
    $RollbackTemplateUrl = "https://raw.githubusercontent.com/$Repo/$Branch/src/Workload/Microsoft.NET.Sdk.Maui.Manifest/Rollback.in.json"
}
if (-not $VersionsPropsUrl) {
    $VersionsPropsUrl = "https://raw.githubusercontent.com/$Repo/$Branch/eng/Versions.props"
}

Write-Info "Rollback template: $RollbackTemplateUrl"
Write-Info "Versions.props:    $VersionsPropsUrl"

try {
    $templateText = (Invoke-WebRequest -Uri $RollbackTemplateUrl -UseBasicParsing).Content
} catch {
    throw "Failed to download rollback template from $RollbackTemplateUrl : $($_.Exception.Message)"
}
try {
    $propsText = (Invoke-WebRequest -Uri $VersionsPropsUrl -UseBasicParsing).Content
} catch {
    throw "Failed to download Versions.props from $VersionsPropsUrl : $($_.Exception.Message)"
}

# --- Parse Versions.props into a name -> raw value map (last definition wins) ---
$props = @{}
$conditionalProps = New-Object System.Collections.Generic.HashSet[string]
try {
    [xml]$xml = $propsText
    foreach ($pg in $xml.Project.PropertyGroup) {
        $pgCond = $pg.Condition
        foreach ($node in $pg.ChildNodes) {
            if ($node.NodeType -eq [System.Xml.XmlNodeType]::Element) {
                if ($pgCond -or $node.Condition) { [void]$conditionalProps.Add($node.Name) }
                $props[$node.Name] = $node.InnerText
            }
        }
    }
} catch {
    throw "Failed to parse Versions.props as XML: $($_.Exception.Message)"
}

# Resolve a property value, expanding simple $(Other) references. Returns $null if the property
# is unknown; leaves unresolved MSBuild function calls ($([...])) intact and flags them.
$script:unresolved = New-Object System.Collections.Generic.List[string]

# Evaluate the handful of MSBuild property-function expressions MAUI uses to compute SDK bands,
# e.g. $([System.Text.RegularExpressions.Regex]::Match(10.0.100-rtm.25523.113, `^\d+\.\d+\.\d`)).
# Handles ::Match and ::Replace; leaves anything else intact (it will be flagged as unresolved).
function Invoke-MSBuildExpr([string]$val) {
    for ($i = 0; $i -lt 25; $i++) {
        $before = $val
        # ::Match(input, `pattern`)
        $val = [regex]::Replace($val, '\$\(\[System\.Text\.RegularExpressions\.Regex\]::Match\(([^,`]*),\s*`([^`]*)`\)\)', {
            param($m)
            try { return [regex]::Match($m.Groups[1].Value.Trim(), $m.Groups[2].Value).Value } catch { return $m.Value }
        })
        # ::Replace(input, `pattern`, `replacement`)
        $val = [regex]::Replace($val, '\$\(\[System\.Text\.RegularExpressions\.Regex\]::Replace\(([^,`]*),\s*`([^`]*)`,\s*`([^`]*)`\)\)', {
            param($m)
            try { return [regex]::Replace($m.Groups[1].Value.Trim(), $m.Groups[2].Value, $m.Groups[3].Value) } catch { return $m.Value }
        })
        if ($val -eq $before) { break }
    }
    return $val
}

function Resolve-PropValue([string]$name, [int]$depth = 0) {
    if ($depth -gt 20) { return $null }
    if (-not $props.ContainsKey($name)) { return $null }
    $val = $props[$name]
    # Expand $(Simple) references we know about.
    $val = [regex]::Replace($val, '\$\(([A-Za-z0-9_]+)\)', {
        param($m)
        $inner = $m.Groups[1].Value
        $r = Resolve-PropValue $inner ($depth + 1)
        if ($null -eq $r) { return $m.Value } else { return $r }
    })
    # Evaluate MSBuild band-computation expressions once inner props are expanded.
    $val = Invoke-MSBuildExpr $val
    return $val
}

# --- Substitute @Token@ placeholders in the template text ---
$missing = New-Object System.Collections.Generic.List[string]
$usedConditional = New-Object System.Collections.Generic.HashSet[string]
$result = [regex]::Replace($templateText, '@([A-Za-z0-9_]+)@', {
    param($m)
    $token = $m.Groups[1].Value
    if ($token -eq 'VERSION') {
        if ($MauiVersion) { return $MauiVersion }
        # Best-effort: some branches expose the maui version as a property.
        foreach ($cand in 'PackageReferenceVersion','MauiVersion','MauiPackageVersion') {
            $v = Resolve-PropValue $cand
            if ($v) { return $v }
        }
        $missing.Add('@VERSION@ (microsoft.net.sdk.maui) — supply -MauiVersion') | Out-Null
        return '@VERSION@'
    }
    $v = Resolve-PropValue $token
    if ($null -eq $v) {
        $missing.Add("@$token@") | Out-Null
        return "@$token@"
    }
    if ($conditionalProps.Contains($token)) { [void]$usedConditional.Add($token) }
    if ($v -match '\$\(' -or $v -match '\$\[') {
        # Contains an unresolved reference or MSBuild function call.
        $missing.Add("@$token@ (=> '$v')") | Out-Null
    }
    return $v
})

# --- Safety net: if a band segment is still an unresolved expression and -Band was given,
#     replace every entry's band (text of value after the first '/') before parsing. ---
if ($Band -and ($result -match '\$\(' )) {
    $result = [regex]::Replace($result, ':\s*"([^"/]+)/[^"]*"', ': "$1/' + $Band + '"')
}

# --- Parse the substituted JSON ---
$map = $null
try {
    $map = $result | ConvertFrom-Json -AsHashtable
} catch {
    Write-Warn "Substituted template is not valid JSON (likely unresolved @tokens). Raw output below:"
    Write-Host $result
    throw "Could not parse substituted rollback JSON. Resolve the missing tokens (see warnings), or pass -Band <sdk-band> to force the feature band, and retry."
}

# --- Force band on every entry if requested ---
if ($Band) {
    foreach ($k in @($map.Keys)) {
        $ver = ($map[$k] -split '/', 2)[0]
        $map[$k] = "$ver/$Band"
    }
}

# --- Set microsoft.net.sdk.maui from -MauiVersion (BEFORE overrides, so an explicit
#     -Override for that manifest still wins) ---
if ($MauiVersion -and $map.ContainsKey('microsoft.net.sdk.maui')) {
    $curBand = if ($map['microsoft.net.sdk.maui'] -match '/') { ($map['microsoft.net.sdk.maui'] -split '/',2)[1] } else { $Band }
    if ($MauiVersion -match '/') { $map['microsoft.net.sdk.maui'] = $MauiVersion }
    elseif ($curBand) { $map['microsoft.net.sdk.maui'] = "$MauiVersion/$curBand" }
    else { $map['microsoft.net.sdk.maui'] = $MauiVersion }
}

# --- Apply explicit overrides last (id=version or id=version/band) ---
foreach ($o in $Override) {
    $eq = $o.IndexOf('=')
    if ($eq -lt 1) { Write-Warn "Ignoring malformed -Override '$o' (expected id=version)"; continue }
    $id = $o.Substring(0, $eq).Trim().ToLowerInvariant()
    $val = $o.Substring($eq + 1).Trim()
    if ($val -notmatch '/' ) {
        # No band given in the override: keep the existing band, else the forced/-Band, else none.
        if ($map.ContainsKey($id) -and ($map[$id] -match '/')) {
            $existingBand = ($map[$id] -split '/', 2)[1]
            $val = "$val/$existingBand"
        } elseif ($Band) {
            $val = "$val/$Band"
        }
    }
    $map[$id] = $val
}

# --- Emit ordered JSON ---
$ordered = [ordered]@{}
foreach ($k in ($map.Keys | Sort-Object)) { $ordered[$k] = $map[$k] }
$json = $ordered | ConvertTo-Json

# --- Detect anything still unresolved AFTER overrides/-MauiVersion were applied ---
$stillUnresolved = @(
    $ordered.GetEnumerator() |
        Where-Object { $_.Value -match '@[A-Za-z0-9_]+@' -or $_.Value -match '\$\(' } |
        ForEach-Object { "$($_.Key) => $($_.Value)" }
)

foreach ($mp in ($missing | Select-Object -Unique)) {
    Write-Warn "Unresolved placeholder: $mp"
}
if ($usedConditional.Count -gt 0 -and -not $Band) {
    Write-Warn "$($usedConditional.Count) resolved value(s) came from a Versions.props property with an MSBuild Condition ($([string]::Join(', ', $usedConditional))). This flat parser is last-definition-wins; if a version/band looks wrong, pass -Band or -Override."
}

# Structured summary for the agent to reason over (emitted even on failure).
$summary = [ordered]@{
    repo            = $Repo
    branch          = $Branch
    outFile         = $OutFile
    written         = $false
    manifestCount   = $ordered.Count
    manifests       = $ordered
    unresolved      = @($stillUnresolved)
    conditionalUsed = @($usedConditional)
    bandForced      = $Band
    mauiVersion     = $MauiVersion
    overrides       = $Override
}

# --- Fail fast: never write a broken rollback file ---
if ($stillUnresolved.Count -gt 0 -and -not $AllowUnresolved) {
    Write-Host "[SKILL_SUMMARY] $($summary | ConvertTo-Json -Depth 5 -Compress)"
    throw "Rollback file NOT written: $($stillUnresolved.Count) manifest(s) still unresolved [$([string]::Join('; ', $stillUnresolved))]. Supply -MauiVersion / -Band / -Override, or pass -AllowUnresolved to write anyway."
}

# --- Write the file (resolved, or -AllowUnresolved) ---
if ($OutFile) {
    $dir = Split-Path -Parent $OutFile
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $json | Set-Content -Path $OutFile -Encoding utf8
    Write-Info "Wrote rollback file: $OutFile ($($ordered.Count) manifests)"
} else {
    Write-Host $json
}
$summary['written'] = $true
Write-Host "[SKILL_SUMMARY] $($summary | ConvertTo-Json -Depth 5 -Compress)"

if ($stillUnresolved.Count -gt 0 -and $AllowUnresolved) {
    Write-Warn "Wrote file with $($stillUnresolved.Count) unresolved manifest(s) because -AllowUnresolved was set. Fill them before running `dotnet workload install`."
}
