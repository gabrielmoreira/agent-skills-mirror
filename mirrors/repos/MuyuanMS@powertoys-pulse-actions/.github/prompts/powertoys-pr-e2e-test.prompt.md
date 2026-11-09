---
description: 'Prepare exact PR bits and verify PowerToys behavior using CI or a local Debug worktree.'
agent: 'agent'
---

# Prepare and test PowerToys PR <PRNumber>

Prepare and test microsoft/PowerToys PR <PRNumber> locally: <PRTitle>
https://github.com/microsoft/PowerToys/pull/<PRNumber>

Use a matching CI installer first where the affected feature supports it, avoiding a local build and the full CI artifact archive. Do not review the code, modify the upstream PR, push branches, or post comments. Use the powertoys-verification skill's PR-validation workflow when available.

CI installation is not itself E2E validation. Actual unsigned CI bits have worked for Color Picker activation, Image Resizer resizing, PowerRename renaming, and Registry Preview file rendering. FancyZones CLI/editor smoke checks do not prove snapping. Unsigned Release binaries can fail Settings IPC authentication, and unsigned MSIX packages can fail registration, including Command Palette and modern Explorer integration. Classify each affected feature rather than assuming every module works.

Required workflow:
1. Read the PR description and diff, record the current upstream head SHA, and derive concrete behavioral checks. Identify the host architecture, requested per-user or machine install scope, affected modules, and whether their signing, Settings IPC or shell integration is essential to the checks. Preserve existing source worktrees and do not install anything yet.
2. Locate a clean canonical main checkout of https://github.com/MuyuanMS/powertoys-pulse-actions (clone separately if absent). Read its current Get-PrCiInstaller.ps1 before running it:
   .\Get-PrCiInstaller.ps1 -PrNumber <PRNumber> -Architecture x64 -Scope User -Destination C:\Temp\pt-pr-<PRNumber>
   Substitute ARM64 or Machine only when appropriate. The helper uses public endpoints without a PAT, resolves a successful build matching the current source head, selects the exact installer from its CI logs, and downloads only the installer plus SHA256 manifest. It refuses to overwrite files. Use a fresh destination on a retry. Record download-receipt.json, verify the local hash and Authenticode status, and recheck the PR head. A synthetic merge build contains the source head plus its CI base; label that distinction. Do not fall back silently to an older-head build, download the multi-GB archive, execute a partial/hash-mismatched file, or treat a matching hash as a trusted signature.
3. If CI is missing, queued, expired, inaccessible, or signing/integration requirements prevent the intended test, record the exact condition and proceed to the local Debug source-build fallback below. Missing CI alone is not a reason to stop or ask the user to trigger CI. Wait only if the user explicitly requests waiting. Do not post /azp run yourself without approval; the dashboard offers a confirmed Trigger CI build action. Do not silently import certificates, disable authentication, register unsigned packages, or modify the PR to bypass trust checks. If the dashboard explicitly supplied an earlier build selection, inspect the comparison with the current head and report checks against that older source only; use the local current-head build for subsequent changes, never silently substitute an old installer.
4. Prefer a disposable test environment. Before installing, replacing an AppX package, or stopping the user's installed runner, explain the exact operation and obtain confirmation. Inventory and preserve the original version, install scope, runner/process identity, ordinary PowerToys settings, affected AppX LocalState and package registrations. Preserve both the original bootstrapper and full MSI outside the package cache; uninstall can delete cached installers. Establish a verified restoration path first. A per-user CI installer may refuse to coexist with an all-users install. Do not uninstall the existing product merely to get past this guard.
5. If testing an unpackaged module from an extracted MSI is appropriate, keep all bits in an owned isolated directory. Administrative extraction alone skips the dependency-copy custom action: inspect the exact-build CreateWinAppSDKHardlinksCA and WinUI3Apps\hardlinks.txt, reproduce only those file copies in that directory with path/hash validation, and attest actual running paths. Never overlay onto installed files. Direct executable/CLI smoke tests do not prove runner hotkeys, Settings IPC, Explorer menus or MSIX registration.
6. Launch the attested CI bits and exercise the changed feature with concrete expected/actual assertions: original failure, intended behavior and relevant edge cases. Verify outputs and actual UI behavior, not just process presence or installer exit 0. If the required chain does not work with the artifact, record FAIL/BLOCKED with evidence and move to source-built validation only where that resolves the dependency. Keep unsigned-package limitations explicit.
7. Close owned test processes normally, restore all touched settings/packages and the original installation, and verify restoration against the baseline. Do not claim completion with unresolved cleanup. Return the source head, CI build ID and merge SHA, installer filename/architecture/scope/hash/signature, exact module launch paths, per-scenario PASS/FAIL/BLOCKED results, evidence/log paths and restoration status. Recheck upstream head and label older-revision results accurately.

## Local Debug source-build fallback

1. Locate the existing PowerToys clone. Read AGENTS.md, .github\copilot-instructions.md, tools\build\Worktree-Guidelines.md and tools\build\BUILD-GUIDELINES.md at the PR revision. Create a separate clone if none exists. Preserve dirty work and existing branches; no reset, force push or modification of the installed binaries.
2. Fetch the actual upstream PR head even if origin points to a personal fork:
   git fetch https://github.com/microsoft/PowerToys.git pull/<PRNumber>/head
   git rev-parse FETCH_HEAD
   gh pr view <PRNumber> --repo microsoft/PowerToys --json headRefOid --jq .headRefOid
   Compare FETCH_HEAD with that live PR head. If it changed, repin and derive checks for the new revision. Choose a unique local branch name such as pr-test/<PRNumber>-<ShortHeadSha>. If it does not already exist:
   git branch pr-test/<PRNumber>-<ShortHeadSha> FETCH_HEAD
   .\tools\build\New-WorktreeFromBranch.ps1 -Branch pr-test/<PRNumber>-<ShortHeadSha> -NoFetch
   Read the helper's reported worktree path, verify git -C <WorktreePath> rev-parse HEAD equals the pinned SHA, and reuse only an already isolated exact-head worktree. If the helper cannot run, use git worktree add -b <UniqueBranch> <UnusedWorktreePath> <PinnedHeadSha>; never change the main checkout.
3. Enter the worktree, initialize submodules and run the first-build bootstrap in Debug:
   git submodule update --init --recursive
   .\tools\build\build-essentials.cmd -Platform x64 -Configuration Debug
   Use ARM64 on the appropriate host. Read the scripts' actual help at this revision. This bootstrap builds runner and Settings essentials; it is not proof that the affected module is built.
4. Identify every affected native/managed project and runtime dependency from the diff. Build their project directories using the worktree's scripts, for example:
   .\tools\build\build.ps1 -Platform x64 -Configuration Debug -Path .\src\modules\<AffectedModule>\<ProjectDirectory>
   Repeat for the required dependency chain. Keep the build-to-test flow in one terminal. Check each command's exit code before proceeding; nonzero is failure. Read build.Debug.x64.errors.log next to the project/solution, then the full log/binlog if needed. Do not launch or test on failed or stale output. Do not alter the PR code just to make it compile.
5. After successful builds, locate and verify the actual worktree output under x64\Debug (or ARM64\Debug). For runner-hosted scenarios, check the worktree's PowerToys.exe and required module DLL/Settings files exist, then launch that Debug runner from its output directory, for example:
   Start-Process -FilePath '<WorktreePath>\x64\Debug\PowerToys.exe' -WorkingDirectory '<WorktreePath>\x64\Debug'
   Confirm the executable name/layout from the actual project outputs before using this example. Use an affected module's own executable only when its documented entry path suffices; a standalone module smoke test cannot prove runner integration. First establish preservation and confirm any required stop of the user's installed runner as in step 4 of the CI workflow. Attest running executable paths/PIDs and module load paths from this exact worktree, not the installed release.
6. Run the derived behavioral assertions on the Debug bits, capture PASS/FAIL/BLOCKED evidence, close owned test processes normally, restore settings/packages and the original runner, and verify restoration. Source builds do not automatically solve signing or packaged-registration requirements; establish those explicitly without weakening trust. Record the pinned source SHA/worktree, Debug platform, commands, exit codes, launch paths and why CI could not cover the scenario. If local prerequisites/build/runtime genuinely fail, retain the exact error and remediation; do not label missing CI as the final blocker when the local path remains runnable.

Do not claim E2E readiness until the affected feature is exercised successfully on attested bits and the user's environment is restored.
