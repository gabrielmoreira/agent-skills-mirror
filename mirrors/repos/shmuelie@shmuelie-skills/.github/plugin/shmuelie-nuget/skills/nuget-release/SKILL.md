---
name: nuget-release
description: "Release one project-versioned NuGet library with SemVer, Keep a Changelog, tag validation, GitHub Actions trusted publishing, draft-first release assets, and explicit recovery. Use for release setup or an explicitly requested release, never ordinary PR CI."
---

# NuGet library releases

Publication is irreversible across NuGet and GitHub: there is no shared
transaction. Resolve repository policy and explicit release authority first.
The reference workflow releases one package to NuGet.org and GitHub, not an
independent-version monorepo or arbitrary feed system.

## Version and changelog contract

The project/shared build properties own the version. Do not let CI overwrite
that value from a tag or build counter. Evaluate effective `PackageVersion`
and inspect the produced `.nuspec`; imports and overrides matter.

Use SemVer: incompatible API/behavior is major, compatible additions minor,
compatible fixes patch. Prerelease labels use forms such as `1.2.0-rc.1`.
Do not compare versions lexically (`1.10.0` sorts incorrectly against `1.9.0`).

For a consuming library, use a changelog skeleton such as:

```markdown
# Changelog

Following Keep a Changelog and Semantic Versioning.

## [Unreleased]

## [1.2.0] - 2026-09-20

### Added
- Describe the consumer-visible addition.

[Unreleased]: https://github.com/OWNER/LIBRARY/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/OWNER/LIBRARY/releases/tag/v1.2.0
```

Replace the example identity/version/date and use only real release tags in a
production changelog. Use the applicable Added, Changed, Deprecated, Removed,
Fixed, and Security sections; a commit dump is not a consumer-facing changelog.

Keep a Changelog with `## [Unreleased]`, categorized entries, dated released
sections, and comparison links. When deliberately releasing:

1. Choose the version and update the project-owned value.
2. Move the relevant unreleased notes into `## [1.2.0] - YYYY-MM-DD`; keep
   `[Unreleased]` for subsequent work.
3. Review/commit the change and push the exact matching `v1.2.0` tag.
4. Let the configured workflow validate and publish; do not publish on every push.

The reference tag syntax is `vMAJOR.MINOR.PATCH[-prerelease]`. Build-metadata
release tags are rejected: NuGet removes `+metadata` for package identity.
Stable and prerelease tags must match the evaluated version, both package
archives, and exactly one nonempty dated changelog section.

## Copy and configure, do not activate the fixture

Copy `templates/release.yml` to `.github/workflows/release.yml` and these three
companions to `eng/release/`:

- `Release.Common.ps1`
- `New-ReleasePlan.ps1`
- `Publish-Release.ps1`

Also copy the package-authoring skill's `templates/Test-LibraryPackage.ps1`
to `eng/package/` and adapt the canonical example's `package-policy.json` at
repository root. Its content/provenance gates must pass before the release plan
is approved; a successful consumer test alone does not prove package completeness.

Configure `PACKAGE_PROJECT`, `TEST_PROJECT`, `CONSUMER_PROJECT`, and
`RELEASE_REPOSITORY` (`owner/repository`) as repository variables. Set
`RELEASE_BRANCH` only if the allowed release history is not the default branch.
The template checks the tag commit belongs to that branch history; enforce
protected tag/environment rules in GitHub as well.

Use a real package ID, metadata, repository, and consumer; publication of
`ShmuelieSkills.Fixture.*` or an `example/*` repository is rejected. Keep the
SDK pin consistent with `global.json`. The example requires both nupkg and
snupkg; deliberately redesign the artifact contract for a package without symbols.

## Trusted publishing and permissions

Register a NuGet.org Trusted Publishing policy for the intended owner/repository,
workflow **filename** (`release.yml`, not its full path), package scope, and the
`nuget` environment used by the template. Configure `NUGET_USER` with the
NuGet profile name, not an email address.

`NuGet/login` exchanges GitHub OIDC for a short-lived API key after validation,
just before the publication phase. Do not acquire it before lengthy builds.
Only the publish job has `id-token: write` and `contents: write`; normal
validation is read-only. Checkout credentials are not persisted.

If trusted publishing is not available, explicitly replace the login step with
an environment-secret key path and map `secrets.NUGET_API_KEY` to that single
step's environment. Scope the key to the package and required operation.
Never fall back silently after OIDC failure or expose keys in logs/source.
Honor protected-environment approval requirements; missing setup is a failure,
not a reason to widen permissions.

## Build once, stage, then publish

The validation job tests and packs the tagged commit once, runs a clean package
consumer, and creates a release plan with exact identity, commit, artifact
hashes, and changelog notes. The publish job downloads those artifacts from the
same workflow run; it never rebuilds the library.

`Publish-Release.ps1` verifies the job context and package bytes, then:

1. verifies the remote tag's peeled commit and absence of conflicting release/version;
2. creates a verified-tag draft;
3. uploads explicit package/symbol assets, notes, plan, and checksums;
4. downloads/checks the staged asset bytes;
5. pushes the package and symbols separately;
6. publishes the GitHub Release and checks its state/assets.

`--no-symbols` belongs only on the `.nupkg` phase to avoid an implicit symbol
push. Do not use it on the explicit `.snupkg` phase: it can suppress the symbol
upload while returning success.

Prereleases are explicitly marked prerelease and never latest stable. Stable
backports must not replace a newer stable version. Existing noncanonical release
tags require an explicit policy, not an invented sorting fallback.

`-WhatIf` validates local input but performs no publication transport calls.
It does not validate credentials. CI uses `-Confirm:$false` only after the
repository's release/tag/environment authorization gates have been configured.

## Recovery is explicit

The first version intentionally stops on an existing draft/release/package.
It does not blindly resume, use `--skip-duplicate`, replace assets with
`--clobber`, move tags, or rebuild a different archive for the same version.

| Failure | Recovery decision |
| --- | --- |
| Upload fails before package push | Retain draft and original CI artifact; verify checksums and upload only the missing assets under an approved recovery plan |
| Package push succeeded but symbol push failed | Do not repush the package; diagnose symbol ingestion and retry only the original symbol artifact when appropriate |
| NuGet succeeded; GitHub finalization failed | Verify the published package/provenance and original draft assets, then finalize that draft |
| Published immutable release is incomplete/conflicting | Do not delete/recreate or overwrite it; decide a corrective release/documentation action |
| Original artifacts expired or cannot be authenticated | Stop for maintainer action; do not label a fresh rebuild as the original package |

NuGet repository signing can change downloaded package bytes. A raw feed-package
hash mismatch with the original unsigned archive is not proof of different
source; verify provenance/content with signing-aware tooling during recovery.
NuGet indexing/validation may be asynchronous; a push response is not proof of
completed ingestion or symbol availability. Keep the failed phase and completed
steps visible. Never claim rollback of an already-published version.

Concurrency prevents overlapping publication without canceling in-flight work.
GitHub Actions retains at most one pending run in a concurrency group and may
replace an older pending run. Inspect displaced tag runs and rerun them
explicitly; this is not an unlimited release queue. Push release tags one at a
time rather than relying on a large bulk tag push.

## Validation and boundaries

`examples/Test-Release.ps1` exercises the core with synthetic zip packages,
fake transports, and per-step failures. The sibling canonical fixture exercises
real local build/pack/consumer and a no-transport `-WhatIf`.
Neither performs a live NuGet or GitHub publication. Live permissions,
environment rules, indexing, and symbol ingestion need a separately authorized
integration run.

References: [Trusted Publishing](https://learn.microsoft.com/nuget/nuget-org/trusted-publishing),
[NuGet versions](https://learn.microsoft.com/nuget/concepts/package-versioning),
[SemVer](https://semver.org/), [Keep a Changelog](https://keepachangelog.com/),
[GitHub release creation](https://cli.github.com/manual/gh_release_create).
