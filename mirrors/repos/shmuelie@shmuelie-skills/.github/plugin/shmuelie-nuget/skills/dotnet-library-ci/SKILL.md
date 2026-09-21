---
name: dotnet-library-ci
description: "Create credential-free GitHub Actions CI for .NET libraries with build/test/pack, metadata inspection, and isolated consumption of the produced NuGet package. Use for PR/branch CI and library validation, not release publication."
---

# .NET library CI

Separate ordinary validation from release publishing. PR/branch jobs restore,
build, test, pack, inspect, and consume packages without feed credentials or
`id-token: write`. Never use `pull_request_target` to build untrusted PR code
with privileged tokens.

## Adopt the template

Copy [templates/ci.yml](templates/ci.yml) to `.github/workflows/ci.yml` in the
consuming repository. Configure repository variables `PACKAGE_PROJECT`,
`TEST_PROJECT`, and `CONSUMER_PROJECT` as repository-relative project paths.
Choose the actual branch trigger and SDK pin; keep `global.json` consistent.
The template uses Windows and Linux with .NET 10.0.401.

Also copy `nuget-package-authoring/templates/Test-LibraryPackage.ps1` to
`eng/package/Test-LibraryPackage.ps1` and adapt the canonical example's
`package-policy.json` at repository root. The policy is reviewed source, not
inferred from the archive: specify the real package/repository/license, exact
framework assembly set, and expected dependency IDs/ranges/include/exclude
attributes. Both CI and release templates run this gate before approving artifacts.

Copy/adapt the [canonical example](../dotnet-library-projects/examples/README.md),
not a second divergent library. The consumer's exact PackageReference must
match the project-owned library version. The template's local-only consumer
restore is for this dependency-free example; adapt source mapping for real
transitive dependencies as described by `nuget-package-authoring`.

The action revisions are pinned to immutable commits with version comments.
Update them deliberately and rerun the fixture rather than switching to a
floating action branch. Normal CI uploads workflow artifacts, not GitHub Release
assets or packages to NuGet.org.

## Validation gates

- SDK/test-runner selection is explicit and reproducible.
- Restore/audit errors remain visible; do not suppress them to obtain a green run.
- All matrix jobs must pass; a failed or canceled job is not release readiness.
- Inspect package ID/version, framework assemblies, README/license metadata,
  XML docs, dependency groups, source commit, and intended symbols.
- Use a separate consumer cache and local feed so a cached package cannot
  conceal missing or invalid output. Run the consumer, not just its restore.
- Keep artifacts named per matrix entry; never let two jobs overwrite the same
  artifact name.

The reusable inspector enforces required metadata, README/license, framework
assemblies, public XML docs, dependency groups, matching portable PDBs, and
Source Link URLs for the reviewed commit. Its initial contract targets ordinary
pure-managed `lib/<tfm>` packages on GitHub, not native/RID/analyzer packages.
Extend that policy deliberately for other package shapes rather than bypassing
the gate. The canonical fixture exercises negative archive mutations as well as
valid content.

Release publishing is a separate tag-triggered workflow. A green PR job does
not authorize a release, and artifacts from an arbitrary PR run are not trusted
release inputs.

## Local reproduction

```powershell
pwsh -NoProfile -File ..\dotnet-library-projects\examples\Test-Fixture.ps1 -ScratchRoot $env:TEMP
pwsh -NoProfile -File ..\nuget-release\examples\Test-Release.ps1 -ScratchRoot $env:TEMP
```

Decision tests use synthetic packages and fake transports with no network.
Restoring/building the actual example may access NuGet. Passing those tests
does not prove workflow permissions, protected environments, or publication.
