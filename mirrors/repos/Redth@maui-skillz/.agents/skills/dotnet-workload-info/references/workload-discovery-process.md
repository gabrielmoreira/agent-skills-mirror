# .NET Workload Discovery - Detailed Reference

This reference provides comprehensive documentation for the NuGet APIs and data structures used in workload discovery. Consult this when you need deeper understanding of the discovery process.

## Table of Contents

1. [NuGet API Reference](#nuget-api-reference)
2. [Source Discovery and Custom Feeds](#source-discovery-and-custom-feeds)
3. [Package Naming Conventions](#package-naming-conventions)
4. [Version Format Conversions](#version-format-conversions)
5. [Package File Structures](#package-file-structures)
6. [Complete Discovery Example](#complete-discovery-example)

---

## NuGet API Reference

NuGet lookups should be driven from the source's V3 service index whenever
possible. Do not assume NuGet.org endpoints when the user provided custom feeds.

### Search API

**Endpoint**: Source-specific `SearchQueryService` URL from the feed's
service index.

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Search query | `Microsoft.NET.Workloads.10.0` |
| `prerelease` | Include prereleases | `true` or `false` |
| `semVerLevel` | SemVer compatibility | `2.0.0` |

**Response structure**:
```json
{
  "totalHits": 5,
  "data": [{
    "id": "Microsoft.NET.Workloads.10.0.100",
    "version": "10.102.0",
    "versions": [
      { "version": "10.100.0", "@id": "..." },
      { "version": "10.102.0", "@id": "..." }
    ]
  }]
}
```

### Package Content API (Flat Container)

**Download package**: 
```
{packageBaseAddress}/{id}/{version}/{id}.{version}.nupkg
```

**List versions**:
```
{packageBaseAddress}/{id}/index.json
```

**Important**:
- Package IDs must be lowercase in flat-container URLs
- The base address comes from the source's `PackageBaseAddress/3.0.0` resource
- Some private feeds may require exact version lookup rather than fuzzy search

### .NET Releases API

**Releases index**:
```
https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/releases-index.json
```

**Per-channel releases**:
```
https://builds.dotnet.microsoft.com/dotnet/release-metadata/{major}.0/releases.json
```

**Response fields**:
| Field | Description |
|-------|-------------|
| `channel-version` | Major.minor (e.g., "10.0") |
| `latest-sdk` | Current stable SDK version |
| `latest-release` | Current runtime version |
| `support-phase` | "active", "maintenance", "eol" |
| `release-type` | "lts" or "sts" |

---

## Source Discovery and Custom Feeds

### Feed resolution order

1. Use the `nugetSources` the user supplied, in the exact order given
2. If a source is a name, resolve it from `NuGet.config` / `dotnet nuget list source`
3. Use NuGet.org only as a fallback when no custom source was provided or the
   user did not pin an exact package/version

### Resolve endpoints from a V3 service index

```bash
curl -s "{SOURCE_INDEX}" | jq -r '
  .resources[] |
  select(
    (."@type" | tostring | contains("PackageBaseAddress")) or
    (."@type" | tostring | contains("SearchQueryService")) or
    (."@type" | tostring | contains("RegistrationsBaseUrl"))
  ) | { type: ."@type", url: ."@id" }'
```

Use the discovered `PackageBaseAddress` for exact package download/version-list
operations. Use `SearchQueryService` only when you need to find the latest
compatible version.

### Exact version behavior

If the user provides a specific workload set or manifest version:

- try that exact version on the custom sources first
- do not substitute a newer or different version
- if it is missing, report the failure and the feeds checked

This is especially important when release notes are being generated before the
packages are published publicly.

---

## Package Naming Conventions

### Workload Set Packages

**Pattern**: `Microsoft.NET.Workloads.{major}.{band}`

| Example | Description |
|---------|-------------|
| `Microsoft.NET.Workloads.10.0.100` | .NET 10, 100-band |
| `Microsoft.NET.Workloads.9.0.200` | .NET 9, 200-band |

**Exclusions**: Ignore `.Msi.x64`, `.Msi.arm64` variants.

### Workload Manifest Packages

**Pattern**: `{WorkloadId}.Manifest-{sdkBand}`

| Workload | Package Example |
|----------|-----------------|
| iOS | `Microsoft.NET.Sdk.iOS.Manifest-10.0.100` |
| Android | `Microsoft.NET.Sdk.Android.Manifest-9.0.100` |
| MAUI | `Microsoft.NET.Sdk.Maui.Manifest-10.0.100` |

---

## Version Format Conversions

### SDK Band Derivation

From SDK version, extract the feature band (hundreds digit):

| SDK Version | Band |
|-------------|------|
| `10.0.102` | `10.0.100` |
| `10.0.205` | `10.0.200` |
| `9.0.309` | `9.0.300` |

### NuGet ↔ CLI Version

| NuGet Format | CLI Format | Conversion |
|--------------|------------|------------|
| `10.102.0` | `10.0.102` | `{parts[0]}.0.{parts[1]}` |
| `9.309.0` | `9.0.309` | Swap middle segments |

---

## Package File Structures

### Workload Set Package

**File**: `data/microsoft.net.workloads.workloadset.json`

```json
{
  "microsoft.net.sdk.android": "35.0.50/9.0.100",
  "microsoft.net.sdk.ios": "26.2.10191/10.0.100",
  "microsoft.net.sdk.maccatalyst": "26.2.10191/10.0.100",
  "microsoft.net.sdk.macos": "26.2.10191/10.0.100",
  "microsoft.net.sdk.tvos": "26.2.10191/10.0.100",
  "microsoft.net.sdk.maui": "10.0.10/10.0.100"
}
```

**Format**: `"{workload_id}": "{manifestVersion}/{sdkBand}"`

### Workload Manifest Package

**Files**:
- `data/WorkloadManifest.json` - Workload definition and packs
- `data/WorkloadDependencies.json` - External tool requirements

### WorkloadDependencies.json Structures

**Android workload**:
```json
{
  "microsoft.net.sdk.android": {
    "jdk": {
      "version": "[17.0,22.0)",
      "recommendedVersion": "17.0.14"
    },
    "androidsdk": {
      "packages": [
        "build-tools;35.0.0",
        "platform-tools",
        "platforms;android-35",
        "cmdline-tools;13.0"
      ],
      "apiLevel": "35",
      "buildToolsVersion": "35.0.0",
      "cmdLineToolsVersion": "13.0"
    }
  }
}
```

**iOS/macOS workload**:
```json
{
  "microsoft.net.sdk.ios": {
    "workload": {
      "alias": ["ios"],
      "version": "26.2.10191"
    },
    "xcode": {
      "version": "[26.2,)",
      "recommendedVersion": "26.2"
    },
    "sdk": {
      "version": "26.2"
    }
  }
}
```

### Version Range Notation

Uses NuGet/Maven interval notation:

| Notation | Meaning |
|----------|---------|
| `[17.0,22.0)` | >= 17.0 AND < 22.0 |
| `[26.2,)` | >= 26.2 (no upper bound) |
| `(1.0,2.0]` | > 1.0 AND <= 2.0 |

**Brackets**: `[` = inclusive, `(` = exclusive

---

## Complete Discovery Example

### Goal: Find iOS requirements for .NET 10

**Step 1**: Get latest SDK
```bash
curl -s "https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/releases-index.json" | \
  jq '.["releases-index"][] | select(.["channel-version"]=="10.0") | .["latest-sdk"]'
# Result: "10.0.102"
```

**Step 2**: Derive band → `10.0.100`

**Step 3**: Find workload set
```bash
curl -s "{SEARCH_QUERY_SERVICE}?q=Microsoft.NET.Workloads.10.0&prerelease=false" | \
  jq '.data[] | select(.id=="Microsoft.NET.Workloads.10.0.100") | {id, version}'
# Result: { "id": "Microsoft.NET.Workloads.10.0.100", "version": "10.102.0" }
```

**Step 4**: Download and extract workload set
```bash
curl -so workloadset.nupkg "{PACKAGE_BASE}/microsoft.net.workloads.10.0.100/10.102.0/microsoft.net.workloads.10.0.100.10.102.0.nupkg"
unzip -p workloadset.nupkg data/microsoft.net.workloads.workloadset.json | jq '."microsoft.net.sdk.ios"'
# Result: "26.2.10191/10.0.100"
```

**Step 5**: Download iOS manifest
```bash
curl -so ios.nupkg "{PACKAGE_BASE}/microsoft.net.sdk.ios.manifest-10.0.100/26.2.10191/microsoft.net.sdk.ios.manifest-10.0.100.26.2.10191.nupkg"
unzip -p ios.nupkg data/WorkloadDependencies.json | jq '.["microsoft.net.sdk.ios"].xcode'
# Result: { "version": "[26.2,)", "recommendedVersion": "26.2" }
```

### Final Output

```yaml
.NET Version: 10.0
Latest SDK: 10.0.102
SDK Band: 10.0.100

Workload Set:
  Package: Microsoft.NET.Workloads.10.0.100
  NuGet Version: 10.102.0
  CLI Version: 10.0.102

iOS Workload:
  Manifest: Microsoft.NET.Sdk.iOS.Manifest-10.0.100
  Version: 26.2.10191
  Xcode Range: "[26.2,)"
  Xcode Recommended: 26.2
```
