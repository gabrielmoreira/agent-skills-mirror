---
type: skill
lifecycle: stable
inheritance: inheritable
name: build-script-path-rot
description: Hardcoded paths in build scripts break when directory structure changes:
tier: standard
applyTo: '**/*build*,**/*script*,**/*path*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Build Script Path Rot

## The Problem

Hardcoded paths in build scripts break when directory structure changes:

```javascript
// Bad: hardcoded path
const srcDir = './src/components';
const outDir = './dist/components';

// After restructure: src/components → packages/ui/src
// Script breaks silently or with confusing errors
```

## The Solution

### Option 1: Resolve Relative to Manifest

```javascript
const path = require('path');
const pkg = require('./package.json');

// Paths defined in package.json
const srcDir = path.resolve(__dirname, pkg.directories?.src || 'src');
const outDir = path.resolve(__dirname, pkg.directories?.dist || 'dist');
```

```json
// package.json
{
  "directories": {
    "src": "packages/ui/src",
    "dist": "dist"
  }
}
```

### Option 2: Config File

```javascript
// build.config.js
module.exports = {
  srcDir: './packages/ui/src',
  outDir: './dist',
  assets: './assets'
};
```

```javascript
// build.cjs
const config = require('./build.config.js');
const srcDir = path.resolve(__dirname, config.srcDir);
```

### Option 3: Auto-Discover

```javascript
// Find src directory by looking for markers
function findSrcDir() {
  const candidates = ['src', 'packages/ui/src', 'lib'];
  for (const dir of candidates) {
    if (fs.existsSync(path.join(dir, 'index.ts'))) {
      return dir;
    }
  }
  throw new Error('Could not find source directory');
}
```

## Red Flags

| Pattern | Risk |
|---------|------|
| `'./src/'` hardcoded | Will break on restructure |
| `process.cwd() + '/src'` | Breaks if script run from different dir |
| Relative paths without `path.resolve` | Platform-specific issues |

## Safe Patterns

```javascript
// Always resolve from script location
const scriptDir = __dirname;
const projectRoot = path.resolve(scriptDir, '..');
const srcDir = path.resolve(projectRoot, 'src');

// Or from package.json location
const pkgPath = require.resolve('./package.json');
const projectRoot = path.dirname(pkgPath);
```

## Verification

1. Move a directory → script still works (reads from config)
2. Run script from different working directory → still works
3. Paths in config match actual structure

## When to Apply

- Any build script with file paths
- After directory restructure
- When script "mysteriously" breaks in CI

## Tags

`build` `paths` `configuration` `portability`
