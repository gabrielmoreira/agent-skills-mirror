# Windows and WSL prerequisites

Spec153 installs claws in **WSL2 Ubuntu 24.04 or 26.04**, with the extension running in the WSL remote host. Native Windows runs only the prerequisite gate. Other Linux distributions, WSL1, SSH and container hosts are not new-installation targets in this workflow. Existing connection workflows retain their own compatibility rules.

The native gate issues only `wsl.exe --status` and `wsl.exe --list --verbose`. It accepts UTF-8 and UTF-16 output and fails closed on ambiguous results. It does not start a distribution, enable Windows features, install software, elevate or reboot. Missing/disabled WSL, WSL1-only, no distributions, errors and unknown output remain blocked.

Use the [Microsoft WSL installation guide](https://learn.microsoft.com/windows/wsl/install) to prepare Windows and a supported Ubuntu distribution yourself. Install the Microsoft WSL extension using the [VS Code WSL guide](https://code.visualstudio.com/docs/remote/wsl). The gate verifies that extension is available before probing WSL. The separate **Open in WSL** review names the distribution and existing Linux folder. This action can start that distribution, write a private non-secret handoff using its Python 3, and let VS Code install its WSL Server. These are handoff effects, separate from the read-only gate.

In the new WSL window, install/enable NetClaw there and reopen setup. The consumer verifies WSL2 and `/etc/os-release` before offering the one-use handoff. Handoffs expire after 15 minutes. Restored answers require review of host, source and paths; Windows paths are never silently treated as Linux paths. An expired or uncertain handoff is not replayed automatically.

The engine needs Python 3.10+, Git, uv and compatible runtime tooling. Prerequisites are checked again against the chosen source. HUD Node must satisfy the bundled policy: 24.19+ within 24.x, or 26.1+. Visible remedy commands preserve the user's version-manager choice. System package operations belong in the reviewed terminal; no `sudo npm` path is provided.

Parser/handoff fixtures are tested locally. Disposable native Windows snapshots and clean qualification of both Ubuntu releases remain pending in [Spec153 verification](../specs/153-ide-installer/verification.md). A passing parser fixture is not a completed Windows installation.
