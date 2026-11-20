# Motion releases: build, test, publish

> Repository installation defaults to the [source guide](install.md). Published npm installation is an explicit alternative through the [application guide](install.md). Candidate builds, publication and snapshot recovery use the manual [release workflow](release-workflows.md); merging changes does not publish an npm application package or update hosted application installation guides.

Use **Motion package and release** in `nexu-io/openmotion` on `main`. Its `prepublish` mode builds and validates a candidate. Its `publish` mode can build a new candidate in the same run or select one from an earlier successful run. Snapshot-only recovery remains an independent maintenance entry. Daily development branches from the latest `origin/main` and PRs target `main`.

The optional [DSH workspace plugin](../integrations/dsh/README.md#distribution-maintenance) follows the same candidate/publication flow. Candidate builds check, pack and scan a plugin at the frozen source and application version, then seal it with the application. Publication uploads those exact bytes and advances the matching `integrations/dsh/stable/latest.json` or `integrations/dsh/test/latest.json` only after application publication succeeds. The independent **DSH integration** workflow retains PR artifacts and updates only the main development entry. The plugin still needs a built source runtime; this does not publish a separate npm plugin package. Existing candidates without DSH retain their original release behavior.

| Mode | Result |
| --- | --- |
| `prepublish` (default) | Freeze the main source SHA, build and scan once, then validate the same tgz on macOS ARM64 and Windows x64 while checking the template snapshot. Retain the tgz, SHA256, package size, notes and native reports in Actions. |
| `publish` | Build and validate in this run, or pick a completed candidate by its exact version and `candidate_run_id`. A selected candidate retains its original bytes and receives fresh scans and native verification. Prepare immutable hosted resources before publishing npm. |

Selecting `publish` in the manual dispatch authorizes that exact publication. There is no acceptance checkbox. The operator receipt binds the triggering account, run and package hash. Use `candidate-install.md` for optional isolated local testing and retain completed `acceptance.md` privately.

New public test packages use **DEV templates**; stable packages use prod. The `dev` URL path selects the test software channel, whose newly built packages now embed DEV configuration. Package visibility does not grant DEV network access or authorization; no private catalog snapshot or credential is embedded. Existing prod-based test versions are immutable and remain unchanged. Stable uses an explicit version and prod configuration in these same entries. Skills marketplace/platform upload remains outside this flow; the release manifest's Skills are included in the npm application and registered locally.

## First-time administrator setup

The default `main` contains OpenMotion; the former HTML Anything application remains on `legacy`. For candidate build, npm publication and snapshot recovery, select **Use workflow from: main**. Selecting `feature/motion`, `legacy`, a tag or another feature/fix branch fails before new release work. Application source must be a reviewed commit integrated into `main`. Frozen candidates produced before the repository rename/main cutover retain their original receipt identity and remain readable; new builds seal only the current repository/main identity. See [GitHub's manual workflow requirements](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Keep these control files together:

- `.github/workflows/motion-candidate.yml`, `motion-publish-test.yml`, `motion-publication-recovery.yml` and `motion-install-check.yml` (read-only manual rechecks).
- `.github/scripts/motion-release.mjs`, `motion-scan.mjs`, `motion-registry.mjs`, `motion-registry-smoke.mjs`, `motion-release-notes.mjs`, `publish-install-guide.mjs` and `.github/gitleaks.toml`.
- `scripts/runtime-assets.mjs`, `release-version.mjs`, `install-guide.mjs`, `docs/install.md`, `docs/templates/release-record.md` and `docs/templates/candidate-install.md`.

`docs/install.md` is the single maintained source for source setup, the main Skill installation, npm setup and onboarding. `scripts/install-guide.mjs` omits its marked source-only blocks and fills the released npm identity before publication. The root `install.md` and former onboarding URL only forward to this guide; they contain no separate installation rules.

Protect changes to the trusted control files and `main`; keep default-branch registration aligned. There is no `motion-test-publish` GitHub Environment prerequisite or Review deployments step in this version.

For `@openmotion/app`, open npm **Settings → Trusted publishing → Add trusted publisher → GitHub Actions**. After the repository rename, verify or update npm's external trusted-publisher configuration; source changes do not update it automatically. Set owner **`nexu-io`**, repository **`openmotion`**, workflow filename **`motion-publish-test.yml`** (no directory), **leave Environment blank**, and allow **npm publish** plus **Allow npm dist-tag**. The latter is separately required to advance `test` or `latest` after registry propagation; enabling publish alone is insufficient. If an older entry names an environment, it must be updated to match this workflow before publication. GitHub-hosted runners use Node 26.11.1; credentialed npm jobs explicitly install npm 11.21.2 for OIDC dist-tag support and `id-token: write`; no stored npm token is needed. The recovery caller never calls npm publish or dist-tag. npm does not support a dist-tag dry-run; do not test that command against the real registry without channel-write authorization. See [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/).

Reuse the existing R2 settings. Manual release workflows scope credentials to template staging and final snapshot uploads. Automatic main template synchronization scopes them to its upload step.

| Setting | Role |
| --- | --- |
| Secrets `CLOUDFLARE_R2_RELEASES_AK`, `CLOUDFLARE_R2_RELEASES_SK` | Bucket-scoped S3 write credentials |
| Variable `CLOUDFLARE_R2_RELEASES_BUCKET` | `open-design-releases` |
| Variable `CLOUDFLARE_R2_RELEASES_URL` | Approved R2 S3 HTTPS origin |
| Variable `CLOUDFLARE_R2_RELEASES_PUBLIC_ORIGIN` | `https://releases.open-design.ai` |

## Automatic template synchronization

Merging template catalog/source or publisher changes into `main` automatically runs **Publish hosted template catalog**. It uploads template resources and snapshot metadata, then updates `https://releases.open-design.ai/open-motion/templates/main/catalog.json`. NPM users receive catalog updates independently of application releases. A manual rerun on `main` is also available; the website continues using CMS.

This automatic workflow is an explicitly authorized exception to the manual release boundary in [AGENTS.md](../AGENTS.md#candidate-and-publication-controls). It reuses the existing R2 configuration, with credentials present only in the final upload step. The credentials have shared release-bucket access: there is no storage-enforced template-only isolation. Changes to the publisher and workflow therefore require the same trusted main review as other release control files. The script writes template objects, snapshots and the main catalog pointer; it does not publish npm, move tags or update installation guides. The shared release catalog continues to use the manual release workflow; snapshot-only recovery does not move it.

## 1. Build

Open **Actions → Motion package and release → Run workflow**, select **`main`**, `mode=prepublish`, and a channel. For `test`, normally leave **version** empty. For `stable`, enter an explicit new version such as `0.0.1` (no suffix); empty or mismatched versions fail before building. Use this same branch for publication and recovery; `main` registers the manual Actions entries; release operations still execute from `main`.

Publication ordering explicitly reserves the historical **0.6.x** namespace (including its test versions). The active series starts at **0.0.1** and always follows that historical line. Within either line, normal numeric/prerelease ordering still applies. This lets a separately authorized stable publication move historical npm `latest=0.6.7` and its default guide to `0.0.1`, while a stale 0.6.x candidate can never replace an active-series version. New active versions must skip the reserved 0.6.x namespace when they eventually reach it; 0.7.0 and later remain available. Package version validation and standard SemVer comparison are unchanged. npm itself does not know this repository policy: existing `^0.6.x` ranges and lockfiles do not migrate to 0.0.1. Use the explicit `@latest` guide or pin the new exact version.

An empty test version starts from the frozen source's next patch and a short `-test.N`, then reads npm `latest`, `test` and `candidate` using this publication order. For source `0.0.1`, historical tags such as `0.6.7` and `0.6.8-test.21` do not raise the core version: the result is **0.0.2-test.N**. A current-series tag that is not older advances its core's patch, for example `0.0.2-test.20` can advance to `0.0.3-test.N`; the run number keeps concurrent candidates distinct. Registry errors or invalid tags still stop automatic selection. `N` remains `GITHUB_RUN_NUMBER + 5`; gaps are expected and retries add an attempt suffix. Full run ID, attempt and source SHA remain in the candidate records. Explicit stable `0.0.1` is never automatically published or substituted by a test version.

The checkout version is a development baseline, not the last published package version. Packaging stamps the resolved version into the output package, application, lock and plugin metadata without rewriting source manifests. Thus source `0.6.3` and the historical npm `0.6.4-test.6` can coexist; no stable `0.6.4` is implied. With `source_sha` empty, source is frozen to `GITHUB_SHA` of the selected `main` dispatch, even if the branch advances while the run queues. The legacy `main` package version is never used for automatic Motion numbering. Source development versions and published package versions remain separate; automatic candidate numbering respects the source and active publication-series registry baselines.

To override numbering, enter a new `MAJOR.MINOR.PATCH-test.N[.N]`. Do not reuse an existing candidate/published version or choose one older than the current npm `test` channel. Never change bytes under an existing published version. The successful summary and artifact name show the resolved version; copy that exact version into the publication form after accepting its bytes. Publication never generates a new number.

Normally leave **source_sha** empty. The build fetches `main`, resolves its current full SHA once, records it and checks out exactly that SHA. To test a particular reviewed integrated commit, supply its full 40-character SHA. A later branch update cannot silently change this candidate. Confirm the chosen source has completed the required integration review.

The build scans tracked source before dependency installation, runs the technical checks/Studio regression/public Tool ZIP E2E, builds the final channel-specific npm tgz once and scans its outer and inner archives. It has no npm OIDC or R2 credentials. Successful output is retained as **`motion-candidate-<version>` for 30 days**. Wait for the whole build run to succeed before publication.

The artifact contains: `openmotion-app-<version>.tgz`, `release-npm.json`, `source-scan.json`, `package-scan.json`, `install.md`, `install-record.json`, **`candidate-install.md`**, `acceptance.md`, `release-notes.md` and `candidate.json`. New schema-3 candidates record source/control SHA, producer run/attempt and file hashes, including Notes. Retained schema-2 candidates remain readable with their original identity. Its acceptance state remains `not-performed`. The generated checklist fills machine identity only; human results start at `NOT RUN`.

`candidate-install.md` installs the exact **local tgz**. The sibling frozen `install.md` pins the registry version for **after publication** and cannot install an unpublished version. The candidate guide template is a CI helper, not an addition to the product distribution list.

## 2. Download and accept

1. Open the successful build summary, download `motion-candidate-<version>` and extract the ZIP.
2. Give that directory to your Agent and copy this instruction:

   > Read candidate-install.md in this folder. Read candidate.json, verify the local tgz SHA256, and install this exact local OpenMotion candidate. Use a separate test host profile/configuration, application home, data directory and Skills directory; preserve my daily environment. Verify actual MCP/Skills loading without waiting for background video-component preparation. Run prepare only when explicitly asked to wait or before requested media/capture/export acceptance checks. Record actual results in a private copy of acceptance.md; mark unrun checks NOT RUN. Do not publish.

3. Follow the actual supported host/platform isolation recipe in [npm installation](npm-installation.md). Setup starts video-component preparation in the background; MCP connection, project creation/editing and ordinary preview do not wait for it. When prepare is needed, reuse setup's explicit application home; `--home` alone does not isolate the host profile. The application is embedded: no source checkout or sidecar application/manifest download is needed. Native dependencies still need network access. Report installation/host loading separately from video-component readiness; installation alone does not authorize video creation or export.
4. Complete **`acceptance.md` privately** with PASS / FAIL / NOT RUN, supported OS/host, template/catalog identity, existing-data preservation, real Agent creation/edit/export, normal-speed human audio/video playback, known issues and recovery. [The acceptance guide](release-guide.md) defines the checks. Build success cannot fill human results.

Keep completed evidence against the generated candidate identity. Do not edit/re-upload the frozen candidate artifact or place private test results in public Actions artifacts. Record failed and unrun checks honestly; they are not a manual workflow gate. Code changes need a new candidate version. To publish an existing candidate, copy its run ID and exact version from the summary. The workflow reads and verifies its tgz hash.

## 3. Publish the candidate version

Select **`main`** and **`mode=publish`** in **Motion package and release**. For a candidate you already reviewed, enter its exact version and `candidate_run_id`. A blank run ID builds and validates a new package in the same run. Stable and retained-candidate runs require an explicit version. A new test run can allocate a version. Supply `source_sha` only for a fresh build, using a full reviewed SHA integrated into main. The npm Trusted Publisher filename remains `motion-publish-test.yml`.

1. Verify source integration and the sealed package. A retained candidate must come from a successful registered run in this repository. The exact run lookup checks its GitHub ZIP digest and every sealed file; same-run consumers use the producing job's artifact ID and SHA256.
2. Run isolated installation on macOS ARM64 and Windows x64 from the sealed local tgz. Verify repeat setup, Skills, MCP resources, native components and supported hosted template behavior. In parallel, prepare immutable R2 template and Skill resources for the frozen source. Any failed check stops before npm.
3. Publish the exact tgz with trusted publishing under the public `candidate` tag (test) or `stage` tag (stable), or verify identical existing bytes. An unauthenticated readback compares the public tarball's SHA256 and integrity before advancing `test` or `latest`. Existing version bytes are immutable.
4. Archive the versioned guide and release evidence, advance the default guide and prepared catalog pointer, publish the matching DSH download if present, and publish the exact-source GitHub Release Notes.

For stable, complete the [human acceptance checks](release-guide.md#stable-acceptance) against the frozen prod candidate when required by the release. Test/DEV bytes cannot be promoted into stable/prod. Platform runs do not establish real model creation or human playback. OIDC authenticates the trusted publisher; packaged source and provenance remain recorded separately.

Npm and R2 are separate services. If a later step fails, retry failed jobs to reuse the retained producer artifact IDs. An identical npm package does not require a new upload. If the package bytes change after publishing, use a new version.

## Independent installation rechecks

Use **Motion installation check** (`motion-install-check.yml`) to check an existing public test or stable version without starting publication. After its manual entry is registered on the default branch, select `main`, enter the exact version, and run. This entry has only `contents: read` and `actions: read`; it has no npm OIDC or R2 credentials and cannot publish, move tags or write install.md. Only candidate resolution receives the read-only GitHub token; installed consumer processes receive an allowlisted environment and isolated application/data/Skills/host directories.

The workflow verifies the original successful candidate's ZIP/file hashes and integrated source, then downloads the exact npm bytes on macOS ARM64 and Windows x64. It checks fresh/repeated setup, unrelated MCP-setting preservation, the version’s DEV/prod configuration, Chromium/FFmpeg/ffprobe preparation, registered Tools/Skills and resources. Hosted-catalog packages additionally run the same live-template and Chromium checks as publication; screenshots and `result.json` are retained with each platform report. Both platforms complete independently (`fail-fast: false`). Metadata/tarball requests retry 404/408/429/5xx and transient network errors for up to 15 minutes per request. Authorization errors, malformed metadata and hash mismatches fail immediately. A failed retry cannot retain an old successful download report.

Read each platform's job summary and `installation-<platform>-<run>-<attempt>` artifacts. Failure stays visible in this independent run and cannot resume publishing. Reports record the tested package source/SHA256 separately from the check-code SHA; registry download alone does not certify native installation. Real model creation, Windows 11 desktop behavior and human audiovisual acceptance remain separate checks. Legacy CMS packages still require separate template-service verification.

A same-repository PR changing this workflow, registry helpers or their tests runs the fixed test.7 regression case without publication; fork PRs are skipped. This PR regression must be refreshed before its original candidate artifact expires. Production operation requires the separately reviewed default-branch entry registration; this change does not register or run anything on main.

## Versions and records

| Channel | Moving guide, updated last | Immutable guide |
| --- | --- | --- |
| Test software, DEV templates | `/open-motion/dev/install.md` | `/open-motion/dev/<version>/install.md` |
| Stable software, prod templates | `/open-motion/install.md` | `/open-motion/<version>/install.md` |

Stable uses the prod paths above and npm `latest`; test keeps the DEV paths and npm `test`. Existing legacy `/versions/<version>/install.md` objects remain immutable.

Successful test and stable publication update the same fixed URL, `https://releases.open-design.ai/open-motion/templates/releases/catalog.json`, without an npm version in its path. Each new promoted release replaces that catalog after all its source objects and snapshot metadata upload successfully. The snapshot step checks out the verified candidate's `sourceCommit` and fetches only catalog LFS objects. Content-addressed resources and commit snapshots remain immutable internally. Snapshot-only recovery and superseded releases upload/verify snapshots without changing the shared release catalog. Release publication does not move `templates/main/catalog.json`: NPM runtime discovery continues to follow that latest main catalog independently of the installed software version. The website retains its CMS source.

New candidates containing DSH use schema 4 and also archive the matching `openmotion-dsh-<version>.tgz`, `dsh-plugin.json` and `dsh-package-scan.json`. Plugin metadata records the exact source commit, version, checksum, byte length and supported host. Archive-only recovery and superseded publication verify immutable plugin objects without changing stable/test pointers. Schema-2/3 candidates remain readable; no plugin is rebuilt for them.

Each version archives the exact tgz, manifests, generated blank acceptance checklist, both installation guides, scans, sealed candidate notes when present, candidate identity, the schema-2 release record; later platform reports are retained as Actions artifacts. The release record contains package/source identity and the manual operator authorization; it does not claim independent review or attest private test results. Completed private acceptance material is never uploaded. `test-promotion.json` retains the prior tag, exact package, promotion outcome. The immutable release record includes channel verification and template environment. Both channels record the matching candidate-install reports and their hashes before updating the channel. Separate registry readback records verify the public package. These reports explicitly retain unrun model/human checks. Snapshot recovery preserves a prior immutable release record while retaining its own fresh operator authorization in its attempt artifact.

Builds have no publication lock, so another version can build during acceptance. Test/stable publication and snapshot recovery share one workflow-wide concurrency group with cancellation disabled. GitHub concurrency is not a durable FIFO: it retains one running and one newest pending run; do not enqueue a batch. Publish one accepted version at a time. A superseded candidate can retain version snapshots without moving the default. Default-guide version comparison plus ETag conditional writes prevent late older completion from rolling a newer entry back; unrecognized or conflicting same-version guide bytes require inspection.

Actions artifacts and attempt records expire after **30 days**. R2 snapshots follow the separately managed bucket lifecycle. Acceptance does not extend artifact retention. The explicit run ID distinguishes candidates of the same unpublished version. Lookups by version alone require a unique match. Expired/deleted artifacts fail closed; retain internal evidence before expiry and build a new version when necessary.


## Failure and snapshot recovery

- Before clicking publish: building, downloading and testing publish nothing. Discard an unwanted candidate. Fix code under a new version when bytes change.
- After npm publication: the exact version under `candidate` or `stage` is public. If activation or R2 finalization fails, inspect the npm receipt and retry the failed jobs with the same package.
- Use **Re-run failed jobs** for a partial publication failure. Consumers use successful producer artifact IDs rather than guessing their own attempt. Re-running publication reuses the existing candidate and original accepted version; it does not rebuild. A candidate build rerun is different: a successful new artifact must be accepted again, and selecting a specific run disambiguates repeated candidate builds.
- **Motion snapshot recovery** is a separate maintenance entry. Select `main`, choose the channel, enter the existing candidate version and start snapshot-only recovery. It requires an already published identical npm version. Test fills missing immutable snapshots. Stable checks both exact public installations before filling snapshots. Use the optional candidate run ID if multiple artifacts share the version. It never builds, publishes npm, moves npm tags or accesses the moving guide. Missing/expired/ambiguous candidates stop.
- Version writes use conditional create and byte comparison. Same bytes resume; different immutable bytes stop. A public readback error blocks promotion. A failure after `fixed-write-attempted` may mean the moving write completed: inspect storage and its canonical URL before retrying.
- An unexpected npm tag change stops promotion; a newer accepted stable version is preserved and only the older version snapshot is archived. This workflow does not silently repair tags. Channel rollback is a separate reviewed operation and does not downgrade installed clients or restore their data.

Source/package scans are not a scan of every historical Git object or business classification of all binary assets; reviewers still check content, dependencies, licenses and telemetry boundaries. The historical `0.6.4-test.6` predates these candidate records: do not invent a trusted run for it or republish it to fill this format.

## Validation before activation

Run the repository's release/scanner/guide tests and actionlint. The no-publication rehearsal uses temporary candidate files and simulated GitHub/npm/R2 responses to test the transition and failure cases. It does **not** exercise npm OIDC, hosted native installation or CDN routing.

After separately authorized default-branch/npm setup, build a new candidate and verify that building alone publishes nothing. Rehearse both a selected candidate and a same-run build. Any automated validation failure must stop before npm publication. A positive hosted publication rehearsal is a real publication and needs explicit release authorization. Ordinary PR CI remains credential-free. This implementation PR enables none of those administrative actions by itself.

## GitHub Release notes

Both test/DEV and stable/prod candidate builds prepare `release-notes.md` before sealing the candidate. The ZIP includes it, and the Actions Summary displays it. Notes bind the version, environment, frozen source SHA and tgz checksum. Schema-3 candidates require their identity and SHA256; schema-2 candidates remain readable without a draft. No Release or tag is created by a build.

Stable descriptions are maintained through the [Changelog index](https://github.com/nexu-io/openmotion/blob/main/CHANGELOG.md) and [authoring guide](https://github.com/nexu-io/openmotion/blob/main/docs/CHANGELOG/README.md). Review the English/Chinese Unreleased drafts, select the version and archive them as `docs/CHANGELOG/v{version}/en.md` and `zh-CN.md` through a PR to main before building. Candidate preparation reads those files using the exact **application source SHA**, never current main or the control checkout. It requires an exact version heading and a nonempty UTF-8 body. English is required when supplied copy exists; Chinese is recommended. Missing both warns and retains an explicit automatic draft; English-only warns. Invalid supplied content and GitHub access errors stop preparation rather than disguising a broken source as missing copy. Unreleased and other-version files are never substituted. These sources are repository/publication documents, excluded from all application/npm/plugin bundles.

Test candidates, and stable candidates without authored descriptions, use read-only same-channel published GitHub Release/tag/commit history. The previous baseline is the highest lower-version published GitHub Release in that channel, not an unpublished candidate or an npm tag with no GitHub Release. A first-channel draft discloses its limited 100-commit history; comparisons paginate up to 1,000 commits. Short/empty or repeated pages retain unique rows with explicit shown/total counts and a full comparison link. Missing metadata or diverged history stops preparation. Automatic drafts mark acceptance focus and known issues NOT PROVIDED; authored descriptions must state the actual remaining issues and checks without claiming private acceptance from CI.

Review the sealed Notes before publication and keep actual test results private. Changing source copy does not amend an existing candidate: use a new candidate/version, since duplicate retained version artifacts are ambiguous. After confirmed stable publication, update the root index with its actual date and Release link through a PR. Maintainers can correct published Release prose; retries preserve those edits and the frozen candidate bytes. No new manual entry, approval environment or editorial acceptance checkbox is introduced.

Publication reuses the schema-3 candidate's exact draft and only adds final installation links and verified publication identity. It writes the final display body to `github-release-notes.md`, preserving the sealed `release-notes.md` for retries and immutable snapshots. Older schema-2 candidates retain the GitHub-generated publication-time fallback.

This extension requires the manual npm entry points to be enabled; their restoration is tracked in [PR #444](https://github.com/nexu-io/openmotion/pull/444). It does not change the repository source-installation default or enable those roots itself.

After the matching test or stable snapshot succeeds, **Publish GitHub Release notes** prepares a draft and publishes it at `v<exact npm version>`, targeting the candidate's source commit rather than the publication workflow SHA. Test releases are marked **Pre-release** and never become GitHub Latest. Stable releases become Latest only when this publication was not superseded. No GitHub Release is created for candidate builds, PR checks or snapshot-only recovery.

The final note includes the exact npm version, DEV/prod environment, immutable and moving installation links, tgz SHA256, source commit and publication run around the sealed authored description or automatic draft. Installation checks, live service access, actual Agent creation and human audiovisual acceptance remain separate evidence. Maintainers may edit the published prose in GitHub Releases.

The implementation follows Open Design's draft-before-publication pattern in `.github/workflows/release-stable.yml` and `.github/scripts/release/github/stable-notes.sh`, scaled to this npm application. It does not copy desktop signing, updater feeds or multilingual website publication.

The notes job alone executes with `contents: write`; it receives neither npm OIDC nor R2 secrets and never executes candidate application code. The recovery caller grants the reusable workflow a contents-write permission ceiling so GitHub can validate its conditional notes job, but archive-only always skips that job and its running jobs retain contents-read. Existing conflicting tags or release identities stop instead of being overwritten. An already published matching Release is preserved on retry, including maintainer edits. A draft left by a partial failure can finish with the same identity. Notes failures produce a warning without rolling back delivered npm packages or guides; inspect the retained `release-notes.md`/`github-release-notes.md`/`github-release.json` artifact and rerun the same publication version to retry. GitHub Release creation may require repository/organization Actions policy to permit the scoped write token. That permission and live publication need independent verification.

These workflows remain specific to OpenMotion. A later organization template can expose project-specific build/package/storage inputs and reuse the proven controls; npm trust and repository secrets must still be configured for each caller. No organization template or repository setting is created by this change.
