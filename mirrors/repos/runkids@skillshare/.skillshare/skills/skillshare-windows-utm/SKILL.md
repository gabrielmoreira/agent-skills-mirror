---
name: skillshare-windows-utm
description: >-
  Verify skillshare on a real Windows guest running in local UTM: build a pinned
  commit in the devcontainer, push it into the VM, and either run the Windows E2E
  runbook with full and basic-user tokens or hand the maintainer a one-line
  hands-on setup. Use this whenever a change touches Windows links, junctions,
  file symlinks, Developer Mode, copy fallback, Windows paths, or the dashboard on
  Windows, or when the user asks to test or accept something on Windows / UTM.
argument-hint: "[auto | manual] [git-ref]"
metadata:
  targets: [claude, universal]
---

Linux tests cannot show Windows link behavior. This skill drives the local UTM guest with
`scripts/windows/utm.sh`. Before acting, run `python3 scripts/ai-context.py testing` and follow its
"Windows Verification" section; it is the source of truth for the rules below.

## Rules

- Build in the devcontainer from a **pinned commit** (`utm.sh build <ref>`), never from the working
  tree: other work may be editing it. Report the commit hash with every result.
- The host only drives the VM (`utmctl`). Never run `ss`, `go` or `pnpm` on the host.
- `utmctl exec` runs as SYSTEM, which can always create symlinks. Product behavior must run as the
  desktop user through `utm.sh task` (Interactive scheduled task). Use `--basic` for the basic-user
  token (`runas /trustlevel:0x20000`), which has no symlink right. Never switch to S4U: its token
  differs from a real user's.
- Isolate automated runs under `C:\Users\Public\sstest\`. Clean up with `utm.sh clean`, which uses
  `rmdir` (it does not follow junctions).
- Report which token (full or basic) and architecture each result came from.

## 1. Preflight

```sh
scripts/windows/utm.sh probe
```

| Output | Meaning and action |
|---|---|
| `stopped` | `utmctl start Windows`, then probe again after boot. |
| `OSStatus -1712` | macOS Automation permission for the terminal app is missing; ask the user to allow it. |
| `OSStatus -2700` / guest agent error | Guest still booting or agent not up. Wait, then retry. |
| `desktopUser=` empty | Nobody is logged in; Interactive tasks will not start. **Ask the user to log in** in the UTM window. Restarting the VM logs the user out. |
| `arch=ARM64` / `AMD64` | Use it as the build arch (`arm64` / `amd64`). |
| `devMode=1` | Developer Mode is on; the basic token may still create symlinks. Say so in the report. |

## 2. Build and push

```sh
scripts/windows/utm.sh build <ref> <arm64|amd64>   # ss.exe, ss-ui-dist.zip, ss-version.txt in $OUT
```

The UI zip is unpacked into `%APPDATA%\skillshare\ui\<version>` so `ss ui` never downloads it.
`utmctl file push` needs an existing guest folder; create one with `utm.sh ps` first, or push to
`C:\Users\Public\`.

## 3a. Automated acceptance (`auto`)

1. Create `C:\Users\Public\sstest\` (via `utm.sh ps`), push `ss.exe` and
   `scripts/windows/e2e-file-links.ps1` into it.
2. Run the runbook script once per token:
   ```sh
   scripts/windows/utm.sh task sstest-full  'C:\Users\Public\sstest\e2e-file-links.ps1' -- \
     -Exe C:\Users\Public\sstest\ss.exe -Root C:\Users\Public\sstest\run-full -Out C:\Users\Public\sstest\out-full.txt -Extended
   scripts/windows/utm.sh task sstest-basic 'C:\Users\Public\sstest\e2e-file-links.ps1' --basic -- \
     -Exe C:\Users\Public\sstest\ss.exe -Root C:\Users\Public\sstest\run-basic -Out C:\Users\Public\sstest\out-basic.txt -Extended
   ```
3. Poll `utm.sh pull 'C:\Users\Public\sstest\out-full.txt'` until the last line is `DONE`
   (`pull` exits 0 even when the file is missing).
4. For scenarios the script does not cover, write a small `.ps1`, push it, and run it with
   `utm.sh task`. Check reparse tags with `fsutil reparsepoint query` (`0xa0000003` junction,
   `0xa000000c` symlink) and read the file back.
5. `utm.sh clean`, then report per token: pass/fail, commit, arch, exact failing output.

## 3b. Hands-on test for the maintainer (`manual`)

```sh
scripts/windows/utm.sh push-manual
```

Give the user exactly one line to run in a **normal (non-admin) PowerShell** on the guest. A normal
shell tests the copy fallback that users without Developer Mode get; an admin shell can create
symlinks:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Public\ss-setup.ps1
```

It works in an isolated home, `C:\Users\Public\sstest\manual` (it overrides `USERPROFILE`, `HOME`,
`APPDATA`, `LOCALAPPDATA`), so the real profile is never touched. It installs `ss.exe` and the UI,
creates sample `.claude\CLAUDE.md` and `.codex\AGENTS.md` there, runs `init`, and opens the
dashboard. Tell the user which files to inspect under that folder, then list 4–6 things to try for
the change under test, each with what they should see. Cleanup removes only that folder:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Public\ss-setup.ps1 -Clean
```

Keep the instructions short. Do not paste multi-line setup blocks for the user to type.

## On a Windows host (no UTM)

The same scripts run natively; only the transport changes.

1. Build with the devcontainer (Docker Desktop) as in step 2, or run the `docker exec` part of
   `utm.sh build` directly, then copy `ss.exe`, `ss-ui-dist.zip` and `ss-version.txt` into one folder.
2. Hands-on: `powershell -ExecutionPolicy Bypass -File scripts\windows\manual-setup.ps1 -Dir <that folder>`.
   It stays isolated under `-Root`, so it is safe on a real profile.
3. Automated: run `scripts\windows\e2e-file-links.ps1` directly (it isolates under `-Root` too). For the
   basic-user token, launch it through `runas /trustlevel:0x20000 "powershell ..."` from a normal shell.
4. A developer machine often has Developer Mode on, which lets even the basic token create
   symlinks. Check `whoami /priv` and state it in the report; the no-symlink fallback needs it off.

## Gotchas

- Call `~/Applications/UTM.app/Contents/MacOS/utmctl` directly; the Homebrew symlink reports
  "Application not found". `utm.sh` does this.
- zsh `echo` eats backslashes in Windows paths; write guest scripts with a quoted heredoc.
- Under x64 emulation on ARM64, `$env:PROCESSOR_ARCHITECTURE` and .NET both say x64. `probe`
  reads the native value from the registry.
- A PowerShell 5 script without a BOM is read as the system code page; keep `.ps1` files ASCII.
