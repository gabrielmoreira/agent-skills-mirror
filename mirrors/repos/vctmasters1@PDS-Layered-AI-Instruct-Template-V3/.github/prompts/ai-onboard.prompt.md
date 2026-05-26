---
mode: agent
description: Interactive onboarding wizard — walks the user through filling in every [PLACEHOLDER] in this freshly-cloned template (project identity, dev specs, license, dates, modules) and finishes by rebuilding the master index.
---

# Onboard a New Project

Convert this template from a generic scaffold into a live project. Walk the user through each block of unknowns, **ask one focused question (or small group) at a time**, write the answers into the right files, and finish by rebuilding the index.

> **→ [Read Project Specs First](../copilot-instructions.md#read-project-specs-first)** — `.github/dev-specs.md` is authoritative for platform questions and is filled in during Step 2.
> **→ [Versioning](../../.ai/conventions.md#versioning)** — fill `Last Updated` with today's date. Never leave `[DATE]` as a literal placeholder in a live file.
> **→ [AI Enforcement](../../.ai/conventions.md#ai-enforcement)** — reject non-conforming names (kebab-case for directories, etc.) and suggest a fix instead of accepting them silently.

## Guardrails

- **Never overwrite without asking** when a placeholder is already filled in (e.g., the user re-runs `/ai-onboard` on a partially-onboarded project — diff and confirm).
- **Never invent values.** Inference is allowed only when grounded in explicit repo/session evidence (file detection, git metadata, environment info) and must be surfaced for user confirmation.
- If the user says "skip" or "I don't know yet", leave the placeholder as-is and add the file to the "still needs your input" list at the end.
- **Use today's date** (the assistant's session date) for every `Last Updated` field touched, formatted `YYYY-MM-DD`.
- Run all edits in the workspace root unless the user has explicitly opened a subdirectory.
- Do **not** delete `.example-module/` without explicit confirmation — it is a working reference, not dead weight.

---

## Steps

### 1. Detect onboarding state and auto-fillable values

Before asking anything, scan the project to see what's already been onboarded AND collect every value that can be inferred without user input.

**Onboarding state checks** (what is still a placeholder):

- Does `.ai/instruct.md` still contain `[PROJECT_NAME]`?
- Does `LICENSE` still contain `[YEAR]` or `[COPYRIGHT_HOLDER]`?
- Does `.github/dev-specs.md` still have *zero* checked boxes (`[x]`)?
- Does `README.md` still contain `[PROJECT_NAME]` / `[repo-url]`?
- Does `.example-module/` still exist?
- Run [.github/scripts/validate-instructions.ps1](../scripts/validate-instructions.ps1) and capture its findings.

**Auto-detect defaults** (gather *before* asking any questions; present as pre-filled answers):

| Field | Detect from |
|---|---|
| `[PROJECT_NAME]` default | Workspace folder name (Title Case if kebab/snake) |
| `[repo-url]` | `git remote get-url origin` (if a remote exists) |
| `[project-name]` (clone path) | Tail of the repo URL, or the workspace folder name |
| `[YEAR]` | Current year from the session date |
| `[COPYRIGHT_HOLDER]` | `git config user.name` (fall back to GitHub org/user from the remote URL) |
| `Last Updated` | Session date in `YYYY-MM-DD` |
| Developer OS | Session `environment_info` / shell |
| Language / framework / package manager | Presence of `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `CMakeLists.txt`, `pom.xml`, `Gemfile`, `composer.json` |
| Top-level modules | Existing non-hidden, non-dot directories in workspace root that already contain source code |

**Auto-apply policy**: any field above whose detected value is unambiguous (workspace folder name, current year, git user.name, session date) is **filled immediately**, not asked. Mention what you filled in the opening summary so the user can correct any wrong guess in one message.

Tell the user what state the project is in, then ask if they want a **full onboarding** (every step below) or a **targeted** pass (only the unfilled sections).

### 2. Project identity

Ask the user (one prompt, multiple fields acceptable):

- **Project name** (used as `[PROJECT_NAME]` throughout — accept any human-readable form; do not enforce kebab-case here, that's for directories)
- **One-sentence description** — what does the project do?
- **Primary purpose** — who is it for, what problem does it solve?
- **Repo URL** (if known yet; otherwise leave `[repo-url]`)

Then update:

- [.ai/instruct.md](../../.ai/instruct.md) — replace `[PROJECT_NAME]`, the one-sentence description, the "Purpose" line, and bump `Last Updated`.
- [README.md](../../README.md) — replace `[PROJECT_NAME]`, the description quote, and `[repo-url]` / `[project-name]` in the Quick Start block.

### 3. License

Ask:

- **Copyright year** (default to the current year)
- **Copyright holder** (individual name or organization)
- **License** — keep MIT (the shipped default), or switch? If switch, name it; do **not** generate the replacement text yourself — tell the user to paste it in and offer to update the README license link.

Then update [LICENSE](../../LICENSE): replace `[YEAR]` and `[COPYRIGHT_HOLDER]`. If switching license, ask the user to confirm before overwriting the MIT body.

### 4. Development & target platform — `dev-specs.md`

Walk through [.github/dev-specs.md](../dev-specs.md) section by section. For each section, present the available checkboxes and ask the user which apply. Do not ask one checkbox at a time — group by section (Developer OS, Shell, Editor, Target, Language, etc.).

Detect hints where possible *before* asking, and present them as the suggested default:

- **Developer OS**: the assistant runs in a known environment — use that as the prefilled guess (the current session's `environment_info`/OS).
- **Shell**: infer from the active terminal type if it's visible in the session context.
- **Editor**: the project is being onboarded inside VS Code — pre-check VS Code unless told otherwise.
- **Language / Frameworks / Package Manager**: check for telltale files in the workspace root (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `CMakeLists.txt`, `pom.xml`, etc.) and pre-check matches.

For each section:
1. Show the user the inferred defaults.
2. Ask "Anything to add or change?"
3. Apply `[x]` to chosen lines and fill freeform fields (version numbers, distro, etc.).

Finish by updating `Last Updated` at the top of `dev-specs.md`.
If any section remains ambiguous, explicitly prompt the user to edit/confirm `.github/dev-specs.md` before closing onboarding.

### 5. Root architecture — `.ai/instruct.md`

Ask:

- **Tech stack** — list the main pieces (the answers from Step 4 give a head start; confirm with the user before writing).
- **Environments** — does the project have local/staging/production? Capture URLs or `localhost:PORT` for each, or mark "not applicable yet".
- **Architecture diagram** — ask for the top-level module list with one-line descriptions. If the user can't answer yet, leave the ASCII diagram block as a TODO and note it in the final summary.
- **Data flow** — one or two sentences. Skippable.
- **External dependencies** — payment, email, storage, etc. Skippable.

Fill these into [.ai/instruct.md](../../.ai/instruct.md). Keep the `Key Directories` table for Step 6.

### 6. Modules

Ask the user to enumerate their top-level modules (directories that should each have their own `.ai/instruct.md`).

For each module the user names:
- Confirm the directory name is `kebab-case` (reject and suggest a fix otherwise).
- If the directory does not exist yet, **do not create source files** — only ask whether to scaffold the `.ai/` + `.dev-docs/` skeleton now via `/ai-new-module`, or defer.
- If the directory exists, run the equivalent of `/ai-new-module` against it (without overwriting any existing `instruct.md`).
- Add a row to the Key Directories table in [.ai/instruct.md](../../.ai/instruct.md).

Then ask about [.example-module/](../../.example-module/):
- **Keep it** as a reference (no change).
- **Rename it** to a real module (move directory, update root key-directories table, rebuild index).
- **Archive it** via `/ai-archive` once the user has at least one real module.

Default: keep, with a note in the final summary that it can be archived later.

### 7. Environment variables

Ask which secrets/config the project will need at the root level. Add a stub line for each in [.env.example](../../.env.example) with a `# description` comment and an empty value. Do not write real values.

Remind the user (link, do not restate): [.env File Convention](../../.ai/credentials.md#env-file-convention).

### 7b. Host isolation strategy

Invoke `/ai-env-check` (or perform its detection inline — see [.github/prompts/ai-env-check.prompt.md](ai-env-check.prompt.md)) to determine the current shell's containment and the workspace's per-stack markers.

Then ask the user which isolation strategy the project should adopt — present only options that fit the stacks chosen in Step 4:

- **Project-local only** (`node_modules`, `.venv`, out-of-tree `build/`) — minimum bar, suitable for single-stack projects.
- **Add `docker-compose.yml`** for runtime services (database, broker, cache) so nothing runs directly on the host.
- **Add `.devcontainer/devcontainer.json`** so VS Code / Codespaces opens the workspace in a container by default. Recommended for multi-language projects, embedded projects, or teams with >2 contributors.
- **Already containerized elsewhere** (skip — the project is built and run inside a VM, remote dev box, or CI-only).

Do not scaffold anything in this step. Record the user's choice and add a one-line note to [.ai/instruct.md](../../.ai/instruct.md) under a new `Host Isolation Strategy` row, plus a follow-up in the final summary (Step 11) telling the user the exact next command to run if they picked a scaffold option.

### 8. Git hooks

Ask whether the user wants to install the pre-commit credential-leak hook now. If yes, instruct them to run:

```pwsh
bash .github/hooks/install-hooks.sh        # macOS / Linux / WSL / Git Bash
pwsh .github/hooks/install-hooks.ps1       # Windows PowerShell
```

(Each installer just runs `git config core.hooksPath .github/hooks`. Check `.github/dev-specs.md` to know which one applies.)

Do **not** run the installer yourself — it's a per-clone operation the developer should run on their machine.

### 9. CHANGELOG

Add a new `## [0.1.0] — YYYY-MM-DD` (or `## [Unreleased]`) section to [CHANGELOG.md](../../CHANGELOG.md) with a single bullet: "Initial project setup from PDS-Layered-AI-Instruct-Template-V3." Leave the template's own changelog history above untouched if the user wants to keep it for reference; otherwise ask.

### 10. Validate & rebuild

1. Run [.github/scripts/validate-instructions.ps1](../scripts/validate-instructions.ps1) — or invoke `/ai-validate`. Fix any reported issues before continuing (most likely a missed `[DATE]`).
2. Invoke `/ai-update-index` to rebuild [.ai/index.md](../../.ai/index.md) so the new modules and bumped dates are reflected.

### 11. Final report

Print a summary to the user:

- **Filled in**: bulleted list of placeholders resolved, by file.
- **Inferred and confirmed**: bulleted list of values auto-detected (especially in `.github/dev-specs.md`) and confirmed or edited by the user.
- **Still needs your input**: any placeholders the user said "skip" on, or any TODOs left in the diagram/data-flow sections.
- **Suggested next steps**: e.g., "run `bash .github/hooks/install-hooks.sh`", "archive `.example-module/` when ready", "fill in module rules in `[module]/.ai/instruct.md`".

---

## Interaction style

- **Group related questions.** Don't ping-pong one field at a time.
- **Show inferred defaults** before asking — make the easy path "press Enter to accept".
- **Confirm destructive moves** (renames, archive, license swap) before executing them.
- **Never silently skip** a step the user didn't explicitly defer.
