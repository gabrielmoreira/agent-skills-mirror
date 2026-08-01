#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    # Skip the Microsoft-internal Release Tracker and report public release data only.
    [switch] $PublicOnly
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot/ReleaseTrackerApi.ps1"

# Public .NET release metadata, used when the internal tracker isn't available so
# the skill still returns useful results for users outside the Microsoft tenant.
$PublicReleasesIndexUri = "https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json"

function Format-TrackerReleases {
    param([Parameter(Mandatory)] $Releases)

    # Format as Markdown headings and bullet points
    $md = @()
    foreach ($r in $Releases) {
        $security = if ($r.IsSecurity) { "Yes" } else { "No" }
        $date = if ($r.ReleaseDate) { ([datetime]$r.ReleaseDate).ToString("yyyy-MM-dd") } else { "N/A" }
        $md += "## $($r.Name)"
        $md += "- **Stage:** $($r.Stage)"
        $md += "- **Runtime Version:** $($r.RuntimeVersion)"
        $md += "- **SDK Version:** $($r.SdkVersion)"
        $md += "- **Release Date:** $date"
        $md += "- **Security:** $security"
        $md += "- **Stage Container:** $($r.BuildStageContainer)"
        $md += "- **Build Artifacts URL:** $($r.BuildArtifactsUrl)"
        $md += ""
    }

    $md -join "`n"
}

function Format-PublicReleases {
    param([string] $Reason)

    $channels = (Invoke-RestMethod -Uri $PublicReleasesIndexUri).'releases-index' |
        Where-Object { $_.'support-phase' -ne 'eol' }

    $md = @()
    $md += "> **Public release data** (builds.dotnet.microsoft.com) — shipped/announced releases only."
    if ($Reason) { $md += "> Internal Release Tracker not used: $Reason" }
    $md += "> Unshipped previews, **Stage Container**, and **Build Artifacts URL** are internal-only and unavailable here."
    $md += ""

    foreach ($c in $channels) {
        $security = if ($c.security) { "Yes" } else { "No" }
        $md += "## $($c.'latest-release')"
        $md += "- **Stage:** $($c.'support-phase')"
        $md += "- **Runtime Version:** $($c.'latest-runtime')"
        $md += "- **SDK Version:** $($c.'latest-sdk')"
        $md += "- **Release Date:** $($c.'latest-release-date')"
        $md += "- **Security:** $security"
        $md += "- **Channel:** $($c.'channel-version') ($($c.'release-type'))"
        $md += ""
    }

    $md -join "`n"
}

$releases = $null
$reason = $null

if ($PublicOnly) {
    $reason = "-PublicOnly was specified"
}
else {
    $access = Get-ReleaseTrackerAccess
    if ($access.Available) {
        try {
            $releases = Invoke-ReleaseTrackerRestMethod -Endpoint "releases/load/releases-view/active"
        }
        catch {
            $reason = $_.Exception.Message
        }
    }
    else {
        $reason = $access.Detail
    }
}

if ($null -ne $releases) {
    Format-TrackerReleases -Releases $releases
}
else {
    Format-PublicReleases -Reason $reason
}
