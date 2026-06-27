# Contributing to OpenKnowledge

OpenKnowledge is developed in Inkeep's internal monorepo and mirrored to this public repository with Copybara. Public contributions should still start here: open a pull request against `inkeep/open-knowledge`.

## How Public PRs Flow

1. Open a PR against this repository.
2. Automation mirrors the PR into `inkeep/agents-private` under `public/open-knowledge/`.
3. Maintainers review and merge the internal PR.
4. Copybara syncs the accepted change back to this repository and your public PR is closed automatically (not merged — the change lands via the mirror sync, not via the public PR).

Review and merge decisions happen in the internal mirror so that public and internal development stay on the same history.

## What to Expect After Opening a PR

A short orientation, because the flow is unusual:

- **Within ~1 minute** a bot will post a sticky comment on your PR indicating that an internal mirror PR has been opened. The link in that comment points to a private repo and won't be accessible to you; that's expected.
- **Automated review** runs on every public PR via an LLM-based code review (Claude). Full lint, type checks, and tests run internally after the bridge mirrors your changes — results are not surfaced back to your public PR.
- **Maintainer review happens in the internal mirror.** Reviewer comments are **not auto-mirrored back to your PR**. If you don't hear back within a few business days, please comment on your PR to nudge — that's the right thing to do, not annoying.
- **Your PR will be closed (not merged)** once the change has been merged internally and synced back. The mirrored commit on `main` is attributed to our sync bot for technical reasons, but the PR history and internal commit preserve your original authorship.

## Development Setup

```bash
bun install
bun run check
```

Run the app locally:

```bash
bun run --filter @inkeep/open-knowledge-app dev
```

Run the docs site locally:

```bash
cd docs
bun run dev
```

### Environment Variables

OpenKnowledge requires no environment variables for development — `bun install && bun run check` works in a fresh clone. To start the dev server, see the commands above. See `.env.example` for optional dev/observability env vars (OpenTelemetry, custom dev server port).

### Toolchain

The repository pins `Bun 1.3.13+` and `Node.js 24+` via `.bun-version`, `.node-version`, and `package.json` `engines`. If you use a version manager:

- `fnm install` (reads `.node-version`)
- `volta install node@24`
- `mise install` (reads `.node-version`)

If you're on a different Node version, `bun install` will warn about `EBADENGINE`. The install usually succeeds anyway, but tests and builds may not — pin Node 24+ before reporting issues.

## Useful Commands

```bash
bun run format       # Format with Biome
bun run lint         # Lint with Biome
bun run typecheck    # TypeScript checks through Turbo
bun run test         # Test through Turbo
bun run build        # Build all workspaces
bun run check        # Public PR gate: lint, typecheck, and tests
```

For targeted work, run package commands from the package directory:

```bash
cd packages/app
bun run test
```

## Contribution Guidelines

- Keep PRs focused and small enough to review.
- Include tests or a clear manual verification note for behavior changes.
- Run `bun run check` before requesting review.
- Commit `bun.lock` when dependency changes require it.
- Run `bun run notices` and include `THIRD_PARTY_NOTICES.md` changes when dependency changes affect third-party notices.
- Do not include secrets, credentials, customer data, local machine paths, or generated debug artifacts.

## Force-Push and Maintainer Iteration

If a maintainer needs to push fixes to your PR during review, they may either ask you to make the changes or push directly to your fork branch (if you've enabled "allow edits from maintainers" on your PR). Force-pushing to your own branch after a maintainer commit may discard their work — please coordinate via the PR thread before force-pushing if a maintainer has been actively iterating. Since maintainer comments in the internal mirror are not auto-mirrored, a maintainer who is actively iterating will typically post directly on your public PR when coordination is needed.

## Public Export Boundary

Only source code, public docs, and build or development scripts are exported here. Internal planning notes, reports, specs, and agent workspace files are intentionally not part of the public mirror.

## License

OpenKnowledge is licensed under the [GNU General Public License v3.0 or later](./LICENSE) (`GPL-3.0-or-later`). By submitting a contribution, you agree that it is licensed under the same terms.
