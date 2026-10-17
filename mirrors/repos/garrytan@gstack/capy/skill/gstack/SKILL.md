---
name: gstack
description: Install and use gstack in Capy and Claude Code. Load at session start to check this machine, and for gstack planning, code review, debugging, QA, design, security, documentation, and shipping workflows.
---

# gstack for Capy and Claude Code

## Session start: check, then install only when needed

Resolve `scripts/install.sh` relative to this SKILL.md, not the working repository. It is a frozen bootstrapper: it prints `gstack-capy-skill: wrapper <n> (<path>)` first, learns the supported minimum from gstack's remote, and hands over to the checkout's own wrapper (`bin/gstack-capy-session`).

1. At session start run `bash scripts/install.sh --check`, adding `--for <skill>` when you know the workflow (`--for autoplan`, `--for review`, `--for qa`). It prints one `PASS|FAIL|SKIP|WARN <component>` row per component (`WARN` is an owner action), a `GSTACK_LAUNCH:` line, and exactly one trailer as the last line: `gstack: ok <revision> for=<skill>[ (<notes>)]` (exit 0) or `gstack: fail <ids> …` (exit 1). Read the exit status and grep `^gstack: ` directly; never pipe the check through `tail`, `head` or `grep` alone. `--check` never moves the checkout.
2. If the trailer names `revision`, `runtime` or `pins` (`gstack: fail revision …`, `gstack: fail runtime,pins`, `gstack: fail pins`) and a checkout exists, or an ok trailer carries `behind=<n> (latest: <v>); fix: <command>` (the checkout is <n> commits behind origin; the output also has a `gstack-capy-session: behind origin/<branch>: …` line), run the same command without `--check` (900-second timeout), or the `fix:` command when it names another. Report the trailer verbatim, `behind=` included: a lane that is behind says so. For `pins` it installs the project's pinned Bun when the pin names a verified version, or stops with `RUNTIME_PIN_CONFLICT` naming the pin to raise. Any clean, unpinned checkout behind origin is fast-forwarded in install mode (below the `GSTACK_MIN_REVISION` floor by the bootstrapper, `gstack-capy-skill: upgraded <old> -> <new>`; above it by the checkout, `SELF_UPGRADE: done <old> -> <new>`), reinstalled and rechecked in one locked step. A pinned (`--revision`, detached), dirty or diverged checkout, or one another live session holds a lease on (`UPGRADE_BUSY`), is never moved: the trailer names the cause and the exact commands (above the floor it is a `fail behind` trailer after `SELF_UPGRADE: skipped (<reason>)`, with `UPGRADE_BUSY` or `UPGRADE_REFUSED`). A lease whose pid was reused after a wake is reclaimed on its own. `GSTACK_CAPY_AUTO_UPGRADE=0` disables every fast-forward, `GSTACK_CAPY_SELF_UPGRADE=off` only the above-floor one.
3. If the trailer is `gstack: fail not-installed …` and this session runs no gstack workflow, record that line and continue; nothing is installed. Install right before the first workflow with `bash scripts/install.sh --for <skill>` (about 30 s cold: clone, a SHA-256-verified Bun when none installed fits, both host profiles without Chromium, and a `~/.local/bin/bun` shim so fresh shells get the recorded Bun).
4. Any other `FAIL` row carries a `fix:` command and a reason code with a troubleshooting anchor; run the fix, then `--check` again. `SKIP codex-cli (optional; …)`, `SKIP browser (lazy; …)`, `SKIP pins (planning-only; …)` and `SKIP pins (helper runtime; …)` are not failures.

**The trailer rule.** No `^gstack: ok` line from this machine in this session means gstack is not installed here: do not run a workflow, and do not claim the skills work. One machine's install never covers another.

**Subagents.** A subagent's first report to its parent carries the `gstack:` trailer line from its own machine's `--check`, verbatim, after its identifiers. A parent treats a missing line as `gstack: fail not-installed`. A reviewer subagent that only reads and reports (an /autoplan voice, a second opinion) runs `--for review-voice` instead: seconds when warm, no `./setup`, no host profiles, Bun at gstack's own minimum, and a trailer that certifies only the read-only helpers (`gstack-pregate sealed`, `gstack-plan-reality`, `gstack-artifact`, the `gstack-autoplan` reads); every workflow refuses it with a `--for <skill>` fix. Never brief a reviewer that no install is needed. A machine without this skill (a brief you write for a subagent) runs the checkout's own bootstrapper from its project directory: `test -f "$HOME/.local/share/gstack/setup" || git clone --quiet --single-branch --depth 1 https://github.com/garrytan/gstack.git "$HOME/.local/share/gstack" && GSTACK_CAPY_ROOT="$HOME/.local/share/gstack" bash "$HOME/.local/share/gstack/capy/skill/gstack/scripts/install.sh" --for <skill>`.

`gstack-capy-skill: owner action — Drive copy is wrapper <n>, minimum <m>; copy <root>/capy/skill/gstack/ (CAPY_WRAPPER_STALE)` means this skill folder is older than the checkout wants. The run still works; tell the owner, who copies that directory over the skill folder. Never write the skill folder yourself.

## Launch every gstack command with the GSTACK_LAUNCH line

Every successful run, `--check` included, prints `GSTACK_LAUNCH: PATH=<dir>:$PATH GSTACK_SESSION_KIND=unattended GSTACK_STATE_ROOT=<path> GSTACK_EPHEMERAL=1 GSTACK_CAPY=1 GSTACK_INSTALL_VERDICT=<file>` (the `PATH=` part only when the verified Bun is not first on PATH) and, then, `GSTACK_LAUNCH_PATH: <dir>` for callers that do not evaluate shell syntax. Prefix each gstack command with those assignments, or export them once in the shell that runs it; a child shell's export cannot configure the parent's later commands. The PATH part is what makes gstack's `#!/usr/bin/env bun` commands run the Bun the trailer certified; the Capy image's `/usr/local/bin/bun` is 1.3.14, below gstack's minimum.

With `GSTACK_CAPY=1`, a workflow started in an unattended or spawned session checks the install verdict the last run wrote for this checkout, HEAD and workflow, and the Bun on PATH. When either fails it prints an `INSTALL: fail …` row with its fix and `GSTACK_RESULT: skill=<s> status=refused run=-` and exits 3: stop, run the fix, start again. An ok whose pins row was `SKIP pins (planning-only; …)` does not admit a workflow that runs the repo's tests (`review`, `ship`, `qa`), and a verdict that did not check a component the workflow needs does not admit it either; run `--for <that skill>` first.

## Load the right workflow

For Capy running GPT-6 Astra, read `${CODEX_HOME:-$HOME/.codex}/skills/gstack/SKILL.md` for routing, then `${CODEX_HOME:-$HOME/.codex}/skills/gstack-<skill>/SKILL.md` for the selected workflow. These are the generated GPT-6 Astra instructions, not the Claude source files.

For Claude Code, read `~/.claude/skills/gstack/SKILL.md` for routing and `~/.claude/skills/<skill>/SKILL.md` for the selected workflow. When launching a Claude Code session, tell it to load gstack and name the intended workflow. For Capy running a Claude model, the Claude instruction files can be read directly with the Capy adaptations below; that does not turn Capy into the Claude Code harness.

If no specific skill was requested, use the router's task-to-skill mapping. Read only the selected workflow and its referenced files. For other models, use the closest applicable instruction profile without claiming a model-specific profile was generated or evaluated for them.

## Unattended runs for a parent agent

For `/autoplan` driven from Capy, read `autoplan/DRIVER.md` in the checkout (`~/.local/share/gstack/autoplan/DRIVER.md`): the compact phase loop, artifact contract and gate protocol, without the interactive preamble. A checkout without that file predates it; follow its `autoplan/SKILL.md` instead. Run every command with the `GSTACK_LAUNCH` assignments and read outputs as files, not prose: the run directory holds `run.json`, `decisions.jsonl`, `findings.jsonl`, `tasks.jsonl`, `timing.json`, `plan.md` and `review-record.md`, and the run ends with `GSTACK_RESULT: skill=autoplan status=gate_pending run=<dir>`. `~/.local/share/gstack/bin/gstack-artifact validate <dir>/run.json` is the completion check. The gate is answered through `gstack-autoplan answer` (or `gstack-gate parse`) with the printed `gate_rev`; an unattended run never approves its own gate. `docs/unattended.md` in the checkout is the contract.

Capy checklist for `/autoplan`: drive `gstack-autoplan`, never a hand adaptation presented as a run. Relay `gstack-gate render <dir>/gate.json --all` with `rec` (every recommendation, plan changes included) as the one-word default; answer with `--by agent:<id> --owner-reply "<their words>"`. Set `GSTACK_AUTOPLAN_CHECKPOINT_DIR` to a private project-user Drive folder; after machine replacement, `gstack-autoplan resume --out <new dir> --from <that dir>` restores the newest valid checkpoint.

## Before any push or pull request

In a repository with a sealed configuration (a `sealed` key in its `.gstack/pregate.json`), run `~/.local/share/gstack/bin/gstack-pregate sealed` before every push and before creating a pull request: Capy's pull-request tool may not run local git hooks, so this is the check that keeps sealed or eval output out of a public repository. A refusal names the file, line and rule; do not push until it passes.

## Adapt host-specific instructions to Capy

- An instruction to invoke `Skill` means read and follow the selected SKILL.md with the available file-reading tool. Do not call a nonexistent Skill tool or assume slash commands were registered in Capy's UI.
- Use Capy's user-visible messaging and question tools for output and decisions. Plain assistant text is not a delivered message in Capy. Use Capy's task and pull-request workflows rather than unavailable Claude or Codex host tools.
- Capy has no native gstack host target. Claude hooks do not become enforced Capy hooks; safety skills are advisory here, and `/autoplan` prints `autoplan guard: not enforced by this host` once to say so. Report missing capabilities instead of silently claiming equivalent enforcement.
- Selecting GPT-6 Astra or Claude in Capy does not install or authenticate the Codex or Claude Code CLI. For cross-model reviews, a subagent on another model family is a full outside voice; record the model that reviewed. Do not report a missing Codex CLI as degraded coverage when another runner reviewed.
- Preserve the user's requested scope, decisions, and consent. Do not enable telemetry or remote artifact sharing on their behalf. Installing gstack does not authorize merging, deploying, destructive operations, or bypassing approvals.

## Maintenance

`bash scripts/install.sh --check` is the health check; `bash scripts/install.sh` installs or repairs and fast-forwards a checkout below the supported minimum. Between minimums, `~/.local/share/gstack/bin/gstack-upgrade --check` says whether the checkout is behind, and `~/.local/share/gstack/bin/gstack-upgrade` fast-forwards it to the tip of the default branch and reinstalls (it refuses dirty, diverged or pinned checkouts and never stashes or resets). The installer is for Capy's Ubuntu cloud machines with Git, curl, Node.js, flock and timeout; do not run it on a personal device without permission.
