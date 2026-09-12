---
name: windows-self-hosted-runner
description: Prepare and verify a Windows GitHub Actions self-hosted runner on a clean released VM image. Use when bootstrapping the runner, selecting SDK/native build prerequisites, diagnosing service-account permission failures, or proving queued-job readiness.
---

# Windows Self-Hosted Runner Bootstrap

Treat the VM, toolchain, runner files, GitHub registration, Windows service, and queued-job validation as separate resources. A clean released Windows image may
have Windows PowerShell 5.1 but no PowerShell 7, .NET SDK, Windows SDK, Visual Studio Build Tools, or native compiler.

## Safety and approval boundary

- Use only public Windows images, public vendor downloads, and first-party documentation. Do not depend on private images or provisioning frameworks.
- Inventory read-only state first. Before provisioning a VM, elevating, changing ACLs, installing a machine-wide toolchain, or installing, starting, stopping, or
  removing a service, show the exact operation and require the user's explicit approval.
- Never route an untrusted public-fork pull request to a privileged persistent self-hosted runner. GitHub warns that forked code can compromise it. Prefer a
  GitHub-hosted runner or a disposable, isolated runner with no durable secrets or privileged network access.
- Never place registration or removal credentials in a repository, workflow YAML, bootstrap script, command example, transcript, or runner label.

## 1. Inventory before changing the machine

Record the following in a non-secret bootstrap log:

1. Windows edition, version/build, patch state, pending reboot, and whether the selected runner release supports the OS.
2. OS and process architecture (`x64` or `arm64`), plus the architecture required by the jobs. Select the matching runner archive and SDK/native tools.
3. Available shells (`powershell.exe` 5.1 and, only if already present, `pwsh`), free disk space, writable staging/log roots, proxy settings, certificate trust,
   outbound HTTPS 443 access, and required GitHub/action/package domains.
4. Planned runner root, work directory, labels, runner group/repository scope, and whether the runner is persistent or disposable. GitHub recommends a
   system-account-accessible root such as `C:\actions-runner` for a Windows service.
5. The account intended for the service and its least required rights: log on as a service, read/execute the runner and toolchain, modify runner work/temp
   directories, and access required network resources. Do not assume it is the logged-on user, `NETWORK SERVICE`, or any other built-in account.

Derive build prerequisites from repository evidence rather than copying the `windows-latest` software list:

- Read `global.json`, target frameworks/RIDs, solution and project files,
  packaging manifests, and workflow commands.
- For SDK-style managed builds, install the compatible .NET SDK. Prefer `actions/setup-dotnet` or `dotnet-install.ps1` in a service-writable, job-scoped directory
  when persistence is unnecessary.
- For .NET Framework or builds requiring full Visual Studio MSBuild, select
  the matching Build Tools workload and targeting packs. Modern SDK-style WPF
  and Windows Forms may build with the .NET SDK alone; use the actual project
  targets to decide rather than requiring Visual Studio for every desktop app.
- For C++, Native AOT, or native dependencies, add the compatible C++ build workload/toolset and Windows SDK for the project's target version and architecture.
- For MSIX or Windows packaging, include the Windows SDK packaging/signing tools
  and the required MSBuild packaging targets. Do not assume `dotnet build`
  substitutes for full Visual Studio MSBuild.
- Use Microsoft's workload/component IDs and install only what the workload requires. Confirm that the chosen Visual Studio release supports the selected .NET
  SDK. Record installer exit codes and any reboot requirement.

Verify tools by their real entry points, for example `dotnet --info`,
`MSBuild.exe`, `cl.exe`, `makeappx.exe`, and `signtool.exe`; a successful
installer exit alone is not proof that the service account can find or run them.

## 2. Bootstrap with the shell the image actually has

Do not require `pwsh` merely to download the runner. Windows PowerShell 5.1 can perform the small bootstrap. For endpoints requiring TLS 1.2, preserve existing
protocols and add TLS 1.2; `-UseBasicParsing` avoids legacy web-rendering dependencies:

```powershell
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol =
    [Net.ServicePointManager]::SecurityProtocol -bor
    [Net.SecurityProtocolType]::Tls12

Invoke-WebRequest -UseBasicParsing -Uri $RunnerArchiveUri -OutFile $ArchivePath
if ((Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash -ne $ExpectedHash) {
    throw 'Runner archive checksum did not match the trusted value.'
}
Expand-Archive -LiteralPath $ArchivePath -DestinationPath $RunnerRoot
```

Obtain the archive URL and checksum from GitHub's current add-runner
instructions. Keep the bootstrap log in an operator-selected durable directory,
outside the runner root, and start it before download. Record paths, versions,
hashes, exit codes, and created resources, but no credentials. Stop or suspend
transcription before registration; runner `_diag` logs are separate and do not
replace the bootstrap log.

## 3. Prove each lifecycle stage

Do not collapse these checks into "installed":

| Stage | Required evidence |
| --- | --- |
| Downloaded | Archive exists, expected size/hash matches, and extraction has not been assumed. |
| Extracted | Expected runner files exist in the intended root and are executable by the planned account. |
| Registered | GitHub lists the intended runner with the expected scope, name, group, and labels. |
| Service installed | The exact service recorded by the runner exists and its configured logon identity is known. |
| Service running | That exact service reports `Running`; no wildcard start/stop is used. |
| Connected | GitHub reports `Idle` and runner diagnostics show `Connected to GitHub` / `Listening for Jobs`. |
| Job ready | A deliberately queued diagnostic job matches the labels, is accepted, and succeeds under the service identity. |

On Windows, service installation is selected during `config.cmd`; it requires an
elevated shell. Registration succeeding does not prove service installation,
service `Running` does not prove GitHub connectivity, and `Idle` does not prove
the workload toolchain or filesystem permissions.

After service installation, read the exact service name from the runner's
`.service` file and inspect `Win32_Service.StartName`:

```powershell
$ErrorActionPreference = 'Stop'
$serviceName = (Get-Content (Join-Path $RunnerRoot '.service') -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($serviceName)) { throw 'Runner service name is missing.' }
$services = @(Get-CimInstance Win32_Service |
    Where-Object { $_.Name -eq $serviceName })
if ($services.Count -ne 1) { throw 'Expected exactly the recorded runner service.' }
$services |
    Select-Object Name, StartName, State, StartMode, PathName
```

If the file is absent or several runner services exist, stop and resolve the
intended runner; never pick the first wildcard match. ACL inspection is useful,
but only a queued job proves the effective identity, environment, and access.

## 4. Recover from service-account SDK denial

A common clean-image failure is `actions/setup-dotnet` attempting to create or
write under `C:\Program Files\dotnet` while the runner service account lacks
permission. Do not grant broad write access to Program Files. Scope the install
to the job's writable temp directory and define `DOTNET_INSTALL_DIR` before the
action runs:

```yaml
jobs:
  service-account-probe:
    runs-on: [self-hosted, windows, x64]
    steps:
      - uses: actions/setup-dotnet@v4
        env:
          DOTNET_INSTALL_DIR: ${{ runner.temp }}\dotnet
        with:
          dotnet-version: '8.0.x'
      - name: Verify effective identity and SDK
        shell: powershell
        env:
          DOTNET_INSTALL_DIR: ${{ runner.temp }}\dotnet
        run: |
          $ErrorActionPreference = 'Stop'
          whoami
          if ($LASTEXITCODE -ne 0) { throw 'Identity probe failed.' }
          "RUNNER_TEMP=$env:RUNNER_TEMP"
          "DOTNET_INSTALL_DIR=$env:DOTNET_INSTALL_DIR"
          dotnet --info
          if ($LASTEXITCODE -ne 0) { throw 'SDK probe failed.' }
```

This excerpt only demonstrates a per-job .NET SDK install and identity probe.
`runner.temp` is available in step `env`, not job-level `env`; keep this
override on the installation step and any diagnostic step that reads it.
Choose the SDK from repository requirements, use an action ref allowed by the
repository's pinning policy, and install native/Windows SDK prerequisites
separately with explicit elevation. `runner.temp` is job-scoped; use a dedicated
persistent tool root only when caching is intentional, ACL it to the discovered
service identity, and set machine/service environment deliberately before
restarting the exact service.

Also test creating, reading, and deleting a uniquely named probe file under the
actual runner work/temp root. Report the failing path and identity when denied;
do not silently fall back to an administrator account.

## 5. Credentials, logs, readiness, and rollback

- Fetch GitHub's automatically generated registration credential immediately
  before configuration. GitHub documents a one-hour lifetime. Use it once and
  let it expire; obtain a fresh short-lived credential if registration is
  delayed or fails.
- Unattended configuration commonly passes the credential through the
  documented `--token` argument. A sufficiently privileged local observer, process audit, or shell
  history may capture that command line. Avoid transcripts and command echo,
  minimize the exposure window, and restrict machine access. Deleting a file or
  clearing history afterward does not prove every trace is gone.
- Preserve the independent bootstrap log and the runner's `_diag\Runner_*` and
  `_diag\Worker_*` logs according to a defined ACL and retention policy. Review
  and redact them before sharing; GitHub secret masking is not guaranteed for
  every transformation.
- Queue a minimal diagnostic workflow only after the runner is connected. Prove
  label routing, `whoami`, selected environment variables (never dump all
  environment variables), temp/workspace write access, network access, and each
  required tool version. The run must complete successfully before declaring
  the runner ready.
- On failure, remove registration with GitHub's current removal procedure and a
  fresh time-limited removal credential if registration completed. Let that
  procedure remove its configuration and service, then verify the exact recorded
  runner and service are gone.
- Delete only the archive, extracted directory, probe files, service, and
  installer-owned resources recorded as created by this bootstrap. Use vendor
  uninstall/modify support for a system-wide toolchain. Never broadly kill
  processes, remove all `actions.runner.*` services, delete shared tool caches,
  or recursively clean an unverified parent directory.
- If removal cannot be completed, leave logs intact, revoke/expire credentials,
  disable assignment to the runner, and report the exact residual resources and
  manual action required. Do not claim cleanup erased prior exposure.

## First-party references

- [GitHub: Adding self-hosted runners](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners)
- [GitHub: Self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)
- [GitHub: Monitor and troubleshoot self-hosted runners](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/monitor-and-troubleshoot)
- [GitHub: Removing self-hosted runners](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/remove-runners)
- [GitHub: Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [`actions/setup-dotnet` environment variables](https://github.com/actions/setup-dotnet#environment-variables)
- [GitHub Actions context availability](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability)
- [Microsoft: Visual Studio command-line installation](https://learn.microsoft.com/visualstudio/install/use-command-line-parameters-to-install-visual-studio)
- [Microsoft: Build Tools workload and component IDs](https://learn.microsoft.com/visualstudio/install/workload-component-id-vs-build-tools)
- [Microsoft: `dotnet-install` scripts](https://learn.microsoft.com/dotnet/core/tools/dotnet-install-script)
- [Microsoft: `Win32_Service` and `StartName`](https://learn.microsoft.com/windows/win32/cimwin32prov/win32-service)
