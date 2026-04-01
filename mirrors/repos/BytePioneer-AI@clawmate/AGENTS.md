# AGENTS.md

## Project Overview

ClawMate is an OpenClaw companion plugin distributed via the npm package `@clawmate/clawmate`.

## Common Commands

### Install
```bash
npx @clawmate/clawmate
```

Notes:
- This is the official npm install path.
- It uses the same installer flow as the earlier `npx github:BytePioneer-AI/clawmate` command, but pulls from published npm releases.
- Re-running it prompts before reinstalling/updating existing ClawMate config; it does not overwrite silently.

### Local Development
```bash
npm install
npm run clawmate:setup
npm run clawmate:plugin:check
```

### Release
```bash
# Bug fix release: x.y.z -> x.y.(z+1)
npm run release:patch

# Feature release: x.y.z -> x.(y+1).0
npm run release:minor

# Breaking release: x.y.z -> (x+1).0.0
npm run release:major

# Publish a specific version
npm run release -- 0.1.1 --publish

# Preview next patch version without changing files
npm run release -- patch --dry-run
```

The release script syncs versions across:

- `package.json`
- `packages/clawmate-companion/package.json`
- `packages/clawmate-companion/openclaw.plugin.json`

Then it runs:

- `npm install --package-lock-only`
- `npm run clawmate:plugin:check`
- `npm pack --dry-run`
- `npm publish --access public` (when `--publish` is used)
