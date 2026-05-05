# Waza Agent Guide

## Project

Waza is a skill collection for engineering workflows. The repository contains eight skills: `think`, `design`, `check`, `hunt`, `write`, `learn`, `read`, and `health`.

## Repository Map

- `skills/RESOLVER.md` - trigger and routing table for the skill set.
- `skills/*/SKILL.md` - individual skill entrypoints.
- `skills/*/agents/` - specialist reviewer or inspector prompts.
- `skills/*/references/` - supporting references loaded only when needed.
- `skills/*/scripts/` - deterministic helper scripts.
- `rules/` - shared writing and behavior rules used by install and validation flows.
- `.claude-plugin/marketplace.json` - plugin marketplace metadata.
- `.github/workflows/` - public test and release automation.
- `scripts/package-skill.sh` - builds the Claude Desktop dispatcher ZIP.
- `scripts/` - verification and packaging helpers.
- `Makefile` - smoke tests and package workflow.

## Commands

```bash
make test
make package
./scripts/verify-skills.sh
```

Run `make test` before meaningful changes to skill behavior, packaging, scripts, or marketplace metadata.

## Skill Vs Script

Before adding a capability, decide the layer deliberately:

| Question | Yes | No |
|---|---|---|
| Does the user need judgment, adaptation, or follow-up questions? | Skill | Script or rule |
| Does the same input always produce the same output? | Script or rule | Skill |
| Is it a lookup, list, status check, or invariant check? | Script or rule | Skill |
| Does behavior shift with conversation context? | Skill | Script or rule |

Examples: `verify-skills.sh` is a script; `rules/english.md` and `rules/chinese.md` are rules; `/think`, `/hunt`, `/check`, and `/health` are skills.

## Skill Design Rules

- Put adaptive, judgment-heavy workflows in skills.
- Put deterministic checks, lookups, and table-driven validation in scripts.
- Keep `skills/RESOLVER.md` in sync when a skill description, trigger, or scope changes.
- Keep each `description` concrete enough for automatic routing.
- Avoid broad skills that mix unrelated workflows.
- Keep generic programmer capabilities in Waza. Project-specific constraints should be extracted from public repository context or user-provided task context.
- Treat `code-review` as an invocation alias for Waza `check`, not as a separate generic skill.
- Waza `check` must remain project-aware without depending on unpublished local files. It extracts commands, generated artifacts, risk areas, and release rules from the target diff, public docs, manifests, CI config, and user-provided context.
- Keep distribution files self-contained for Claude Desktop and plugin installs. The release ZIP may inline sub-skill bodies into a generated root `SKILL.md`; source-of-truth skill content remains under `skills/*/SKILL.md`.
- If a `templates/` directory is added, keep reusable public scaffolds there and include it in packaging/validation rules deliberately.

## Adding Or Changing A Skill

Use this path for any new skill or meaningful behavior change:

1. Create or update `skills/<name>/SKILL.md`; keep the description concrete, triggerable, and include a `Not for ...` exclusion.
2. Update `skills/RESOLVER.md` and `.claude-plugin/marketplace.json` so routing, descriptions, versions, and source paths agree.
3. Keep Waza public: extract project-specific details from public repo context at runtime instead of hardcoding private paths, credentials, or one-machine workflow.
4. Put deterministic enforcement in `scripts/` or `rules/`; keep only adaptive judgment in the skill body.
5. Run `./scripts/verify-skills.sh`, `make test`, and `make package` before release handoff.

## Distribution Rules

- `.claude-plugin/marketplace.json`, `skills/RESOLVER.md`, and every `skills/*/SKILL.md` must agree on skill names, descriptions, and source paths.
- `npx skills add tw93/Waza` should install the eight direct coding skills by default. Do not add a source-root `SKILL.md`; it prevents nested skill discovery.
- Claude Desktop uses the release ZIP built by `scripts/package-skill.sh`.
- `scripts/package-skill.sh` builds a public archive with exactly one generated root `SKILL.md`; nested `skills/*/SKILL.md` files are inlined for packaged installs.
- Do not make packaged skills resolve scripts or references through personal home-directory caches or machine paths. Resolve relative to the installed Waza directory.
- Rules under `rules/` are shared public behavior, not project-private memory.

## Verification

- Skill behavior changes: run `./scripts/verify-skills.sh` and the relevant smoke target.
- Packaging changes: run `make package` and inspect the generated archive.
- Marketplace, resolver, or root dispatcher changes: run `./scripts/verify-skills.sh` and confirm every marketplace source points at an existing skill directory.
- Non-trivial diffs: run the review workflow before release handoff.
- Documentation-only changes: check internal links and command names.

## Commit And Release

- Commit convention: `{type}: {description}` where type is `feat`, `fix`, `refactor`, `docs`, or `chore`.
- Release tags use lowercase `v{version}`.
- Release notes should be concise, engineer-facing, and bilingual only when needed.
- Rebuild packaged artifacts before publishing release assets.
- Release body structure: centered logo/title/tagline, English changelog, matching Chinese changelog, then update command and release asset links.
- Keep English and Chinese release items one-to-one by number. Use 5 to 8 items, one sentence each.
- Run `make package` before publishing; CI should upload the ZIP on published releases.
- After a GitHub release is published and assets are verified, add every positive release reaction with `gh api`: `+1`, `laugh`, `heart`, `hooray`, `rocket`, and `eyes`; resolve the release id from the tag, POST each reaction to `repos/<owner>/<repo>/releases/<id>/reactions`, then re-read reactions to confirm them.
