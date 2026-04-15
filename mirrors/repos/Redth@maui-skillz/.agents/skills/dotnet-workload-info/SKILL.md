---
name: dotnet-workload-info
description: >-
  Discover .NET SDK versions, workload sets, workload manifest versions, and
  platform dependencies from live .NET metadata and NuGet feeds. USE FOR:
  Xcode or JDK requirements, Android SDK packages, MAUI package versions,
  prerelease workloads, custom NuGet sources, pinned workload set versions, and
  manifest version lookups. DO NOT USE FOR: writing release-notes markdown
  itself (use maui-release-notes), app troubleshooting, or binding work.
  FOR SINGLE OPERATIONS: answer the version/dependency question directly without
  producing docs. INVOKES: curl, dotnet, unzip, jq.
---

# .NET Workload Info Discovery

Query live .NET release metadata and NuGet feeds to discover authoritative SDK
versions, workload sets, manifest versions, and dependency requirements.

Prefer user-provided NuGet sources and exact versions when supplied. This is
important for pre-publication scenarios where the packages are not yet available
on NuGet.org.

## When to Use This Skill

Use this skill when you need to:
- find the latest or requested workload set for a .NET release
- resolve Xcode, JDK, or Android SDK requirements from workload manifests
- inspect prerelease or private-feed workload packages
- honor a specific workload set or workload manifest version provided by the user
- compare implicit MAUI versions with the latest published package versions

## Inputs

| Parameter | Required | Example | Notes |
|-----------|----------|---------|-------|
| dotnetVersion | yes | 9.0, 10.0 | Major.minor format |
| prerelease | no | true/false | Default false |
| workload | no | ios, android, maui | Alias or full id |
| sdkVersion | no | 10.0.103 | Use this instead of latest-sdk discovery when pinned |
| nugetSources | no | `https://pkgs.dev.azure.com/.../index.json`, `myfeed` | Search these sources in the supplied order before NuGet.org |
| nugetConfig | no | `NuGet.config` | Use this to resolve named/custom sources |
| localPackages | no | `/tmp/*.nupkg` | Inspect local packages directly when provided |
| workloadSetVersion | no | 10.103.0 or 10.0.103 | Use the exact requested workload set version |
| manifestVersions | no | `ios=26.2.11425`, `maui=10.0.30` | Per-workload exact version overrides |

## Source Handling Rules

1. If the user provides `nugetSources`, treat them as authoritative and check
   them in the order given.
2. If the user provides a `NuGet.config`, source name, service-index URL, or
   local `.nupkg`, treat that input as authoritative and use it directly.
3. If a source is a name instead of a URL, resolve it from local NuGet config
   or `dotnet nuget list source`.
4. If an exact `workloadSetVersion` or `manifestVersions` override is supplied,
   do not substitute a different version just because a newer one exists.
5. Reuse the source that provided the workload set when looking up the related
   manifest packages, then fall through the remaining sources only if needed.
6. Stop searching once the requested package/version is found, and report which
   source was used.

## Workload Aliases

| Alias | Full ID |
|-------|---------|
| ios | microsoft.net.sdk.ios |
| android | microsoft.net.sdk.android |
| maccatalyst | microsoft.net.sdk.maccatalyst |
| macos | microsoft.net.sdk.macos |
| tvos | microsoft.net.sdk.tvos |
| maui | microsoft.net.sdk.maui |

---

## Discovery Process

### Step 1: Determine SDK Version and Feature Band

If `sdkVersion` is provided, use it directly.

If an exact `workloadSetVersion` is provided, preserve that version and derive
the corresponding CLI format and SDK band from it.

Otherwise, get the latest SDK version from the .NET release metadata:

```bash
curl -s "https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/releases-index.json" | \
  jq '.["releases-index"][] | select(.["channel-version"]=="{MAJOR}.0")'
```

Extract `latest-sdk` and derive SDK band:
- `10.0.103` → band `10.0.100` (hundreds digit)
- `10.0.205` → band `10.0.200`

### Step 2: Resolve Feed Endpoints

For each custom source, resolve the NuGet V3 service index and extract the
package base/search endpoints from that source instead of hardcoding
`api.nuget.org` or `azuresearch-usnc.nuget.org`.

```bash
curl -s "{SOURCE_INDEX}" | jq -r '
  .resources[] |
  select(
    (."@type" | tostring | contains("PackageBaseAddress")) or
    (."@type" | tostring | contains("SearchQueryService"))
  ) | ."@id"'
```

If no custom sources are supplied, use NuGet.org as the fallback/default source.

### Step 3: Find Workload Set Package / Version

Use the dotnet workload search version command to discover the latest workload set version:

```
dotnet workload search version --format json --take 1
# Returns: [{"workloadVersion":"10.0.103"}]
```

```
dotnet workload search version --format json --take 1 | ConvertFrom-Json
```

The returned workloadVersion is the CLI version to use with --version flag.

**Version conversion**:
To convert this to the NuGet package version used in the later package lookups:

CLI 10.0.103 → NuGet 10.103.0 (remove middle .0., combine)
The NuGet package is: Microsoft.NET.Workloads.{band} where band = CLI version (e.g., Microsoft.NET.Workloads.10.0.100)

If the user provided an exact `workloadSetVersion`, use that version instead of
searching for latest and try the custom sources first.

### Step 4: Download Workload Set Manifest

```bash
curl -o workloadset.nupkg "{PACKAGE_BASE}/microsoft.net.workloads.{band}/{version}/microsoft.net.workloads.{band}.{version}.nupkg"
unzip -p workloadset.nupkg data/microsoft.net.workloads.workloadset.json
```

Format: `"{workload_id}": "{manifestVersion}/{sdkBand}"`

### Step 5: Download Workload Manifest

Build package id: `{WorkloadId}.Manifest-{sdkBand}` (e.g., `Microsoft.NET.Sdk.iOS.Manifest-10.0.100`)

```bash
curl -o manifest.nupkg "{PACKAGE_BASE}/{packageid}/{version}/{packageid}.{version}.nupkg"
unzip -p manifest.nupkg data/WorkloadDependencies.json
```

Use the version from `microsoft.net.workloads.workloadset.json` unless the user
provided an explicit `manifestVersions` override. Try the workload set source
first so pre-release/private-feed manifests resolve correctly.

### Step 6: Parse Dependencies

**Android** (`microsoft.net.sdk.android`):
```json
{
  "jdk": { "version": "[17.0,22.0)", "recommendedVersion": "17.0.14" },
  "androidsdk": {
    "packages": ["build-tools;35.0.0", "platform-tools", "platforms;android-35"],
    "apiLevel": "35", "buildToolsVersion": "35.0.0"
  }
}
```

**iOS/macOS** (`microsoft.net.sdk.ios`):
```json
{
  "xcode": { "version": "[26.2,)", "recommendedVersion": "26.2" },
  "sdk": { "version": "26.2" }
}
```

**Version ranges**: `[17.0,22.0)` = >=17.0 AND <22.0; `[26.2,)` = >=26.2

---

## MAUI NuGet Packages

MAUI packages may be newer than workload versions. Query the selected
`SearchQueryService` (or NuGet.org if no custom source was supplied) for the
latest compatible version:

```bash
curl -s "{SEARCH_QUERY_SERVICE}?q=packageid:Microsoft.Maui.Controls&prerelease=false" | \
  jq '.data[0].versions | map(select(.version | startswith("{MAJOR}."))) | last'
```

Key packages: `Microsoft.Maui.Controls`, `Microsoft.Maui.Essentials`, `Microsoft.Maui.Graphics`

To use newer version than workload:
```xml
<PackageReference Include="Microsoft.Maui.Controls" Version="10.0.30" />
```

---

## Output Format

```json
{
  "dotnetVersion": "10.0",
  "latestSdk": "10.0.102",
  "sdkBand": "10.0.100",
  "workloadSet": {
    "packageId": "...",
    "nugetVersion": "10.102.0",
    "cliVersion": "10.0.102",
    "source": "https://api.nuget.org/v3/index.json"
  },
  "workloads": [{
    "workloadId": "microsoft.net.sdk.ios",
    "manifestVersion": "26.2.10191",
    "sdkBand": "10.0.100",
    "source": "https://pkgs.dev.azure.com/...",
    "dependencies": { "xcode": { "versionRange": "[26.2,)", "recommendedVersion": "26.2" } }
  }],
  "mauiNugets": [{ "packageId": "Microsoft.Maui.Controls", "latestVersion": "10.0.30" }]
}
```

---

## Stop Signals

- Stop once the requested workload set, relevant manifest versions, and
  dependencies have been resolved.
- If an exact requested package/version is missing from the supplied sources,
  stop and report the missing package plus the sources checked.
- Do not keep searching additional feeds once the needed packages are found.

## Error Handling

- Exact version not found → report the package id, version, and sources checked
- No results → retry with `prerelease=true` only when the user did not pin an exact version
- Missing WorkloadDependencies.json → report explicitly
- Missing dependency key → note which keys absent

## Best Practices

- ALWAYS fetch live data; never hardcode versions
- ALWAYS include sdkBand with manifest versions
- Show the source/feed used for each workload set and manifest lookup
- Use public NuGet.org links only when the selected version exists publicly

## Reference

See `references/workload-discovery-process.md` for detailed NuGet API documentation and complete examples.
