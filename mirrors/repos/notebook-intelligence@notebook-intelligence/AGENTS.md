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

If `jlpm lint:check` reports formatting problems, run `jlpm lint` to auto-fix them with the repo's Prettier (this covers Markdown too).

## JavaScript tooling

- Use `jlpm` for every frontend command (install, build, lint, test). Do not use a system `yarn` or `npm`. `jlpm` is the Yarn bundled with JupyterLab, and CI installs with it.
- Do not add a `packageManager` field to `package.json`. `jlpm` ignores it, so it only changes which Yarn a plain `yarn` command runs. A lockfile written by a different Yarn version gets a different TypeScript builtin patch hash, and CI's immutable `jlpm` install then fails with `YN0028`.
- After changing dependencies or `resolutions`, regenerate the lockfile with `jlpm install`, then confirm `jlpm install --immutable` passes. The `yarn.lock` diff should touch only the packages you meant to change.

## Code conventions

- Adding an admin policy touches seven places. The comment above `FEATURE_POLICY_SPEC` in `notebook_intelligence/extension.py` lists them all; update every one, or the policy silently stops working in one direction.
- Import `react-icons` icons from `src/icons.ts`, not directly from `react-icons/vsc` or `react-icons/md`. That module re-types the icons so they compile under `@types/react` 18.
