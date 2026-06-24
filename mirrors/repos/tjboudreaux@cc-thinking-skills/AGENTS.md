# Agent Guidelines

This repository packages 39 Claude Code thinking skills. Treat it as a plugin marketplace project first and an eval research project second.

## Default Workflow

- Preserve the public skill count at 39 unless a change intentionally adds/removes a shipped skill and updates README, plugin metadata, routing cases, and eval docs together.
- Keep skill frontmatter descriptions situation-named and under 200 characters.
- Prefer agent-native instructions over human facilitation language.
- Add explicit "When NOT to Use" boundaries for every non-router skill.
- Do not commit local backups, downloaded third-party datasets, transient logs, or scratch eval runs.

## Verification

- Run `node scripts/validate-skills.js` after skill edits.
- Run `EVAL_RUN=<name> node evals/run-structural.js` after catalog edits.
- Run routing or behavioral evals only when the changed surface warrants the cost.
- Use current post-edit evidence only; historical pre-edit results are context, not proof.

## Local Backups

Global Claude assets may be backed up under `backups/` for safety. The directory is gitignored. Do not add backup archives to commits.

## Images

README and marketing images live in `assets/`. Keep generated source paths out of README links; copy selected assets into the repo and leave generator cache files untouched.
