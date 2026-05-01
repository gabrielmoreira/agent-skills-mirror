# GitHub Copilot Instructions

## Commands

- Install a skill from this workspace: `npx skills install .\azure-devops-changelog-generator`
- Run the Azure DevOps skill grader for a single eval case: `python .\azure-devops-changelog-generator\evals\grader.py --eval-id 1 --run-dir C:\path\to\outputs`
- Use `--eval-id <n>` to target one case from `azure-devops-changelog-generator\evals\evals.json`

## Repository Architecture

- This repository is a collection of Copilot skills. Each top-level directory is its own skill package rather than a shared application module.
- `SKILL.md` is the primary source of truth for a skill. It combines YAML front matter (name, description, inputs, outputs, tags) with the execution contract in markdown sections such as inputs, processing steps, outputs, and rules.
- `evals\evals.json` sits beside each skill and mirrors that contract with prompt-driven evaluation cases. When behavior changes, update the skill spec and the eval expectations together.
- Some skills are documentation-only (`angular-runtime-env-vars` currently has `SKILL.md` plus evals). Others also include executable helpers and supporting docs (`azure-devops-changelog-generator` adds `scripts\*.ps1`, `evals\grader.py`, and `README.md`).
- The Azure DevOps skill is a staged pipeline spread across multiple files: parse TFVC/Git input in the skill contract, fetch work items and comments in `scripts\fetch-workitems.ps1`, serialize `workitems.json`, render `cards.md` and `changelog.md` in separate PowerShell scripts, then verify outputs with the Python grader against `evals\evals.json`.

## Key Conventions

- Keep each skill self-contained inside its own folder. The existing repo does not use shared runtime libraries across skills.
- Preserve the current `SKILL.md` structure: YAML front matter first, then explicit operational sections with concrete prompts, required inputs, file names, and output formats. Favor imperative instructions over abstract guidance.
- Prefer Windows-first examples and PowerShell-compatible workflows. Existing scripts use PowerShell parameter blocks, `Write-Error`/`Write-Warning`/`Write-Host`, environment variables such as `$env:DEVOPS_PAT`, and Windows paths like `C:\Temp`.
- Match the current helper-script pattern: validate required inputs at the top, fail explicitly on missing required data, and write deterministic artifact files instead of hiding behavior in inline shell snippets.
- Keep output filenames stable when extending an existing skill. The Azure DevOps skill consistently uses `workitems.json`, `cards.md`, and `changelog.md` across the spec, README, scripts, and grader.
- Keep evaluation data declarative. Current eval files use objects with `id`, `prompt`, `expected_output`, `files`, and `expectations`; follow that schema when adding new cases.
- For the Azure DevOps skill specifically, keep responsibilities split across the three PowerShell scripts instead of merging fetch/render logic unless the surrounding structure changes everywhere that references those scripts.
