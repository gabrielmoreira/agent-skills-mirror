Build and test microsoft/PowerToys PR <PRNumber> locally: <PRTitle>
https://github.com/microsoft/PowerToys/pull/<PRNumber>

Prepare this PR for local end-to-end testing. Do not review the code, modify the upstream PR, push branches, or post comments.

Required workflow:
1. Locate the existing PowerToys clone and verify Visual Studio 2022 or Build Tools has the Desktop C++ and .NET desktop workloads. Preserve all existing branches, changes, and worktrees.
2. Check whether an isolated worktree for PR <PRNumber> already exists and reuse it when safe. Otherwise fetch the exact PR head without changing the main checkout:
   git fetch origin pull/<PRNumber>/head:pr-test/<PRNumber>
   .\tools\build\New-WorktreeFromBranch.ps1 -Branch pr-test/<PRNumber>
3. Enter the worktree and initialize dependencies:
   git submodule update --init --recursive
   Confirm HEAD matches the current upstream PR head SHA. Do not rebase or change the PR code merely to make the build pass.
4. Inspect the changed files to identify every affected PowerToys module, native module interface, managed application, plugin, and dependency project.
5. Build from the worktree using the repository scripts, not ad-hoc MSBuild:
   $env:POWERTOYS_DISABLE_SPECTRE = "1"
   .\tools\build\build-essentials.cmd
   Then build the full affected chain in dependency order with tools\build\build.cmd: dependency projects, native module interface DLL, managed module application, and the specific changed project or plugin.
6. Verify every build exits successfully, x64\Debug\PowerToys.exe exists, the affected module binaries exist under x64\Debug, and the runner log contains no "Failed to load" entry for the target module.
7. Launch the exact built executable from this worktree. Exercise the changed feature end to end with 2-4 concrete scenarios, including the main behavior and relevant edge cases from the PR description.
8. Return a concise test handoff containing:
   - PR head SHA and worktree path
   - exact PowerToys.exe launch path
   - projects and commands built
   - concrete steps to access the feature
   - expected result for each test scenario
   - any build/runtime failure with the relevant log path and error

Do not claim the PR is ready for testing until the full affected module chain builds and the feature can be launched from the isolated worktree.
