---
name: maui-release-notes
description: >-
  Generate or update .NET MAUI workload release notes markdown from live
  workload and manifest data. USE FOR: MAUI workload release notes, version
  rollup docs, custom NuGet feeds, prerelease or unpublished workload packages,
  pinned workload set or manifest versions, and release-note index updates. DO
  NOT USE FOR: simple workload/version questions without documentation output
  (use dotnet-workload-info), app release notes, or non-MAUI release summaries.
  FOR SINGLE OPERATIONS: if the user only needs version/package data, use
  dotnet-workload-info and do not edit the notes. INVOKES: dotnet-workload-info
  skill.
---

# MAUI Release Notes Generator

Generate formatted markdown for .NET MAUI workload releases using live workload
data from the `dotnet-workload-info` skill.

When custom NuGet sources or exact package versions are provided, use them for
workload set and workload manifest discovery instead of assuming the packages
already exist on NuGet.org.

## When to Use This Skill

Use this skill when:
- generating new `release-notes/maui-release-notes-YYYYMMDD.md` entries
- updating `release-notes/maui-release-notes.md` after a workload release
- documenting a pre-release or internal MAUI workload build from a private feed
- producing notes for a specific workload set or manifest version the user provided
- checking whether a new release-note entry is needed

## Skill Boundary

`dotnet-workload-info` owns source selection, package/version resolution, and
manifest dependency extraction.

This skill owns change detection and markdown authoring. Pass feed/version
overrides through unchanged, and avoid separate feed lookups unless the returned
data is incomplete.

## File Structure

```
release-notes/
├── maui-release-notes.md              # Index page with all releases
└── maui-release-notes-YYYYMMDD.md     # Dated release notes (one per update)
```

## Workflow

### Step 1: Gather workload data
Use `dotnet-workload-info` to fetch live data for the **two most recent .NET
versions** (e.g., .NET 10 and .NET 9), unless the user explicitly asked for a
different set of versions.

Pass through any user-provided overrides, especially:
- custom `nugetSources`
- exact `workloadSetVersion`
- per-workload `manifestVersions`
- `includePrerelease=true`

Capture:
- Workload set versions (NuGet + CLI format)
- Individual workload versions (MAUI, iOS, Mac Catalyst, Android, tvOS, macOS)
- MAUI NuGet package versions (implicit from workload vs latest on NuGet)
- Apple dependencies (Xcode version, SDK)
- Android dependencies (JDK, SDK packages)
- Source/feed used for each workload set and manifest lookup

### Step 2: Check for version changes
Compare fetched data against most recent `maui-release-notes-YYYYMMDD.md`:

```bash
ls -1 release-notes/maui-release-notes-*.md | sort -r | head -1
```

Key versions to compare per .NET version:
- Workload set version
- MAUI version
- iOS version  
- Android version

If no prior `maui-release-notes-*.md` file exists, treat the requested versions
as changed and generate the first entry.

**If any changed → proceed.**

**If unchanged → report "versions are up to date"** unless the user explicitly
requested notes for a pinned version, private feed, or forced regeneration. In
those cases, still generate/update the note for the requested build.

### Step 3: Generate dated release notes
Create `release-notes/maui-release-notes-{YYYYMMDD}.md` using templates from [references/templates.md](references/templates.md).

For link construction (NuGet URLs, GitHub release tags), see [references/links.md](references/links.md).

Source-specific rules:
- Record the actual source summary in the header (NuGet.org, custom feeds, or both)
- Even when a package version is discovered from a private/internal feed, keep
  the package links pointed at the equivalent `nuget.org` URL so the notes will
  resolve correctly once the packages are published publicly
- Keep the package/version data authoritative to the selected feed/version set

### Step 4: Update index page
Add new entry at **top** of `release-notes/maui-release-notes.md`:
- Only include .NET version sections that had actual changes
- Update "Last Updated" date

## Index Entry Format

Each release entry includes:
1. Date heading (e.g., `### January 19, 2026`)
2. Link to full notes
3. Per-.NET version summary (only for versions with changes):
   - Workload set version
   - Workload versions table with Requirements column
   - MAUI NuGet packages (implicit vs latest)

**Requirements column:**
- Apple platforms: `Xcode ≥ {version}`
- Android: `API {level}, JDK {version}`
- MAUI: (empty)

## Stop Signals

- Stop once the requested versions are resolved and the dated note plus index
  update are complete.
- Stop early with an informational response when nothing changed and the user
  did not request a specific build/version.
- Do not continue scanning additional feeds once the needed workload set and
  manifest packages have been found.

## Detailed Templates

See [references/templates.md](references/templates.md) for:
- Complete index page template
- Full dated release notes template with all sections

## Link Construction

See [references/links.md](references/links.md) for:
- NuGet package URL patterns
- GitHub release tag formats (including Apple platform tag algorithm)
- Formatting conventions

## Inputs

| Parameter | Required | Default |
|-----------|----------|---------|
| dotnetVersions | no | Two most recent stable versions |
| includePrerelease | no | false |
| nugetSources | no | none |
| workloadSetVersion / workloadSetVersions | no | auto-discovered |
| manifestVersions | no | derived from workload set |
| forceGenerate | no | false |

## Output

**Versions changed:**
1. New `release-notes/maui-release-notes-{YYYYMMDD}.md`
2. Updated `release-notes/maui-release-notes.md` with new entry at top

**Versions current:** Informational message only

## Dependencies

Requires `dotnet-workload-info` for live feed/package data. Never use
cached/hardcoded versions, and never assume NuGet.org is the correct source
when the user provided a custom feed.
