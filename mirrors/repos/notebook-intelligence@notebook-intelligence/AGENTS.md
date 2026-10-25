# Agent notes for notebook-intelligence

Guidance for coding agents working in this repository. [CONTRIBUTING.md](CONTRIBUTING.md) covers the full development setup.

## Before pushing

Run all four and make sure they pass:

```bash
pytest tests/ -q
jlpm tsc --noEmit
jlpm lint:check
jlpm jest
```

If you added or changed a user-visible string, also run `jlpm i18n:extract` (CI's `jlpm i18n:check` fails on a stale translation template). It needs `pip install -e ".[i18n]"`.

If `jlpm lint:check` reports formatting problems, run `jlpm lint` to auto-fix them with the repo's Prettier (this covers Markdown too).

## JavaScript tooling

- Use `jlpm` for every frontend command (install, build, lint, test). Do not use a system `yarn` or `npm`. `jlpm` is the Yarn bundled with JupyterLab, and CI installs with it.
- Do not add a `packageManager` field to `package.json`. `jlpm` ignores it, so it only changes which Yarn a plain `yarn` command runs. A lockfile written by a different Yarn version gets a different TypeScript builtin patch hash, and CI's immutable `jlpm` install then fails with `YN0028`.
- After changing dependencies or `resolutions`, regenerate the lockfile with `jlpm install`, then confirm `jlpm install --immutable` passes. The `yarn.lock` diff should touch only the packages you meant to change.

## Code conventions

- Adding an admin policy touches seven places. The comment above `FEATURE_POLICY_SPEC` in `notebook_intelligence/extension.py` lists them all; update every one, or the policy silently stops working in one direction.
- Every user-visible string goes through JupyterLab's translator: `const trans = getTrans();` (or `useTrans()` in a component) from `src/i18n.ts`, then `trans.__('Saved %1', name)`. The local must be named `trans` or the extractor misses it. Use placeholders instead of concatenation, and do not translate at module load. Prompts sent to a model, tool results returned to it, logs and product names stay English, and so do strings in `schema/plugin.json` and Python, which NBI's catalogs cannot reach yet. [CONTRIBUTING.md](CONTRIBUTING.md#translations) has the details.
- Import `react-icons` icons from `src/icons.ts`, not directly from `react-icons/vsc` or `react-icons/md`. That module re-types the icons so they compile under `@types/react` 18.
