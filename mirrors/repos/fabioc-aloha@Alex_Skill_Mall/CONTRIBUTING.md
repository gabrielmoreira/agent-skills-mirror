# Contributing to Alex ACT Plugin Mall

Contributions are welcome.

Contract: you prepare the plugin payload in your fork, automation validates it, CODEOWNER `@fabioc-aloha` reviews and approves, and merge publishes the accepted change. Passing checks is required but is not acceptance.

## What Is Accepted

Submissions must be:

- Battle-tested in real project use.
- Specific and actionable.
- Current with upstream behavior.
- Licensed with clear provenance.
- Non-overlapping with existing Mall entries, unless you provide a clear rationale.
- Free of PII, client-private data, private business data, or credentials.

## Prerequisites

- Node.js 24 or newer.
- `npm ci` completed in the Mall repo.
- A fork of this repo and a feature branch.

## Source Plugin Requirements

Your source plugin must meet these requirements before preparation:

- `plugin.json` is present and valid.
- `plugin.json` uses a kebab-case `name`.
- `plugin.json` has `version`.
- `plugin.json` has `description`.
- `plugin.json` has an `author` object.
- `plugin.json` declares at least one component path such as `skills`, `agents`, `commands`, `hooks`, `mcpServers`, or `lspServers`.
- Every skill has `SKILL.md` with frontmatter that includes `name` and `description`.
- Every command markdown file has a `description` field in frontmatter.
- `README.md` is recommended.
- `LICENSE` is recommended.
- Total vendored payload size stays at or below the platform limit of 100 files.
- No secrets, credential files, or symlinks.

Forbidden content examples include `.env`, private keys, OAuth secrets, token exports, and symlinked files.

## Canonical Contributor Flow

Run from your fork of the Mall repo.

Dry run first:

```bash
npm run submit:prepare -- --source ../my-plugin --category productivity --repository https://github.com/you/my-plugin --ref v1.0.0 --submitted-by @you --evidence "Used in a real project"
```

Apply after dry-run output looks correct:

```bash
npm run submit:prepare -- --source ../my-plugin --category productivity --repository https://github.com/you/my-plugin --ref v1.0.0 --submitted-by @you --evidence "Used in a real project" --apply
```

Optional include mappings:

```bash
npm run submit:prepare -- --source ../my-plugin --category productivity --repository https://github.com/you/my-plugin --ref v1.0.0 --submitted-by @you --evidence "Used in a real project" --include .github/config=config,.github/scripts/shared=scripts/shared --apply
```

Validate and run checks:

```bash
npm run submit:validate -- --plugin productivity/my-plugin
npm test
npm run validate
```

### What `submit:prepare` Does

`submit:prepare`:

- Normalizes source component paths into Mall-root component paths such as `skills/`, `agents/`, and `commands/`.
- Renames `*.prompt.md` command files to `*.md` in the vendored payload.
- Writes `.mall-metadata.json`.
- Regenerates `.github/plugin/marketplace.json` deterministically.

`submit:prepare` never commits, never pushes, and never merges.

## Branch, Commit, and PR Steps

1. Create and switch to your feature branch.
2. Run the canonical flow above.
3. Review only intended changes.
4. Commit with severity tag `[behaviour]` in the commit subject.
5. Open a PR using `.github/PULL_REQUEST_TEMPLATE/plugin-submission.md`.

Your PR should include:

- The plugin payload folder under `plugins/<category>/<name>/`.
- The generated `.github/plugin/marketplace.json` update.

Your PR should not include:

- Catalog outputs.
- Scoring outputs.
- README refresh outputs.

Maintainer refresh owns those outputs.

## Automated Review

Automation checks:

- Changed plugin path and payload integrity.
- 100-file platform limit.
- Secret and symlink rejection.
- Required frontmatter and component declarations.
- Relative Markdown links remain inside the payload and resolve.
- Marketplace determinism.
- `npm test` pass.
- `npm run validate` pass.

The workflow never auto-merges. CODEOWNER approval is required.

Repository administrators must configure `main` branch protection to require
the **Validate proposed plugins** status check and CODEOWNER approval.
CODEOWNERS requests the review; branch protection makes it mandatory.
The validation workflow runs on every PR. Generated catalog refresh paths are
not CODEOWNED and may auto-merge after the check; plugin-related paths are
CODEOWNED and wait for maintainer approval.

Preview and apply the canonical protection payload:

```bash
npm run admin:configure-approval
npm run admin:configure-approval -- --apply
```

## Editorial Review

Even with green checks, maintainers review:

- Value and practical usefulness.
- Overlap with existing entries.
- Evidence quality.
- License and provenance clarity.
- Safety and data handling.
- Maintenance burden.
- Category fit.

Admin review can request revisions or decline despite passing checks.

## Updating an Existing Plugin

Contributors can open a normal PR to update an existing plugin they own, but `submit:prepare` intentionally refuses overwrite behavior.

If overwrite is needed:

- Ask an admin, or
- Manually update only your owned plugin payload with a clear upstream ref in metadata and PR notes.

Canonical vendored refreshes are admin-owned:

```bash
npm run vendor -- --replace --apply
```

## Maintainer Commands (Concise)

Vendor refresh, review, and maintenance:

```bash
npm run vendor -- --source ../my-plugin --category productivity --repository https://github.com/you/my-plugin --ref v1.0.0 --submitted-by @you --evidence "Used in a real project"
npm run vendor -- --source ../my-plugin --category productivity --repository https://github.com/you/my-plugin --ref v1.0.0 --submitted-by @you --evidence "Used in a real project" --apply
npm run vendor -- --source ../my-plugin --category productivity --repository https://github.com/you/my-plugin --ref v1.0.0 --submitted-by @you --evidence "Used in a real project" --replace --apply
npm run maintain -- --curated
npm run admin:configure-approval
```

Full network maintenance mode:

```bash
npm run maintain -- --full
```

`--full` requires `SOURCES_DIR` and either `GH_TOKEN` or `GITHUB_TOKEN`.
Review diffs before commit.

## Security Disclosure

Report security issues using `SECURITY.md`. Never submit secrets in a PR.

## Would Revise If

Revise this guide if the GitHub Copilot CLI plugin schema changes, if the 100-file platform limit changes, or if the approval model changes. Re-evaluate on 2026-11-01.
