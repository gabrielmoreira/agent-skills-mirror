---
name: powershell-gallery-publishing
description: Publish PowerShell modules to the PowerShell Gallery from GitHub Actions on a tag push, cut releases, and avoid the multi-tag trigger gotcha. Use when asked to publish a module to PSGallery, set up a module release pipeline, cut a module release, or reserve a module name.
---

When publishing a PowerShell module to the PowerShell Gallery via GitHub Actions, or cutting a module release, apply this domain knowledge.

# PowerShell Gallery Publishing — Domain Knowledge

## Tag-triggered publish workflow

Drive publishing off a **release tag** rather than every push, so a release is an explicit, auditable act. A workflow that triggers on a versioned tag (and optionally `workflow_dispatch` for manual re-runs):

```yaml
on:
  push:
    tags:
      - '<Module>-v*'          # e.g. MyModule-v1.2.3
  workflow_dispatch:
    inputs:
      module: { description: Module to publish, required: true, type: choice, options: [ ... ] }

jobs:
  publish:
    runs-on: windows-latest
    environment: powershell-gallery      # gate the secret behind a named environment
    steps:
      - uses: actions/checkout@v5
      - name: Validate
        shell: pwsh
        run: ./build/Test-Modules.ps1
      - name: Resolve module + verify tag matches manifest
        shell: pwsh
        env: { REF_NAME: "${{ github.ref_name }}" }
        run: |
          if ($env:REF_NAME -notmatch '^(?<module>[\w.]+)-v(?<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)$') { throw "Invalid tag: $env:REF_NAME" }
          $manifest = Test-ModuleManifest "./modules/$($Matches.module)/$($Matches.module).psd1"
          if ("$($manifest.Version)" -ne $Matches.version) { throw "Tag version $($Matches.version) != manifest $($manifest.Version)." }
      - name: Publish
        shell: pwsh
        env: { PSGALLERY_API_KEY: "${{ secrets.PSGALLERY_API_KEY }}" }
        run: Publish-PSResource -Path ./out/<Module> -Repository PSGallery -ApiKey $env:PSGALLERY_API_KEY
```

- **Encode the module name AND version in the tag** (`<Module>-vX.Y.Z`) so one workflow serves a multi-module repo — parse the tag to pick which module to publish.
- **Fail the run if the tag version does not equal the manifest `ModuleVersion`.** This catches the classic "tagged v1.2.3 but forgot to bump the `.psd1`" mistake before a wrong-versioned package reaches the Gallery.
- **Gate the API key behind a GitHub Actions *environment*** (`environment: powershell-gallery`), not a bare repo secret — you get environment protection rules and a clear audit surface.

## PowerShell Gallery API key

1. Sign in at the Gallery, then avatar, then **API Keys, then Create**.
2. **Scope:** *Push new packages and package versions*.
3. **Glob pattern:** restrict the key to just your module family (e.g. `MyModule.*`) so a leaked key cannot push arbitrary package names.
4. Store it as the environment secret the workflow reads (e.g. `PSGALLERY_API_KEY`). With the GitHub CLI: `gh secret set PSGALLERY_API_KEY --env powershell-gallery`.

## Cutting a release

1. Bump the version in the module manifest (`.psd1` `ModuleVersion`), the README version line, and the changelog.
2. **Promote `## [Unreleased]`** notes into a dated/versioned section and leave an empty `[Unreleased]` behind (keeps a CI "changelog updated" gate happy).
3. Commit, then create and push the tag:
   ```powershell
   git tag MyModule-v1.2.3
   git push origin MyModule-v1.2.3
   ```
   The tag push triggers the publish workflow, then validation, then the Gallery publish.

## Gotcha — GitHub does NOT fire tag workflows when you push more than three tags at once

**If a single `git push` delivers more than three tags, GitHub dispatches _no_ `push` events for them, so tag-triggered workflows never run.** This bites a multi-module repo that tags several modules and pushes them together (e.g. `git push --tags` after creating four `*-vX.Y.Z` tags) — the publish pipeline silently does nothing.

Fixes:
- **Push tags one at a time** (or in batches of three or fewer): `git push origin MyModule-v1.2.3` per tag.
- Or trigger the missed publishes manually via `workflow_dispatch`.
- Never rely on a bulk `git push --tags` to fire per-tag release automation.

## Reserving a module name

- **PowerShell Gallery names are first-come-first-served**, and your first successful publish reserves the name to your account.
- Check availability *before* the first release with the Gallery OData API or `Find-PSResource -Name MyModule -Repository PSGallery` (no result means available).
- If a name matters, publish an initial `0.1.0` to claim it rather than risk someone else taking it.
