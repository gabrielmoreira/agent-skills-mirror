---
name: svgo
description: "Runs SVGO v3 with ESM config to strip Inkscape/Illustrator namespaces, clean paths, and batch-compress SVG folders while keeping viewBox and interactive IDs. Trigger on optimize-svg, icon minification, or a CI dry-run gate. Do not use for PNG/JPEG/WebP rasters or CSS layout work."
version: 1.0.1
domain: UI-UX
risk: safe
last_verified: '2026-05-30'
self_updating: true
---

# SVG Optimization via SVGO

Optimize SVG (Scalable Vector Graphics) assets using the SVGO CLI tool. Strip editor metadata, clean paths, compress data segments, and configure plugins for responsive layout behavior.

## When to Use

- You need to optimize or compress one or more SVG vector files before committing them to a frontend codebase.
- You are cleaning inline graphic styles, stripping editor metadata (Inkscape, Illustrator, Figma namespaces), or reducing SVG file sizes.
- You are scripting batch SVG compression across a directory of icon or illustration assets.
- You are setting up a CI/CD gate to verify that SVGs in a pull request are already optimized.
- **Trigger keywords**: svg, svgo, optimize svg, compress svg, vector optimization, strip svg metadata, clean svg, batch svg compression, viewBox preservation.

**Route elsewhere for**: General raster image optimization (PNG, JPEG, WebP) or CSS integration — use `frontend-design` or `ui-ux-pro-max`.

## Prerequisites

- Node.js and npm installed and available on `PATH`.
- SVGO CLI installed globally or as a project dev dependency.

```powershell
# Global installation (Windows PowerShell)
npm install -g svgo

# Project dependency installation
npm install --save-dev svgo
```

- A configuration file (`svgo.config.js` or `svgo.config.mjs`) using **ESM syntax** is strongly recommended for reproducible optimization. SVGO v3+ requires ESM `export default` in config files.

## Procedure

### 1. Create or Verify the SVGO Configuration File

Create `svgo.config.js` in the project root. Use ESM syntax (required for SVGO v3+):

```javascript
// svgo.config.js - SVG Optimization Configuration
export default {
  multipass: true, // Run optimization pass multiple times for maximum compression
  js2svg: {
    indent: 2,     // Pretty print SVG structure for code review
    pretty: true,
  },
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // HARD RULE: Never remove viewBox — it breaks responsive scaling
          removeViewBox: false,
          // Keep IDs if referenced in external CSS or JavaScript
          cleanupIds: false,
        },
      },
    },
    'removeRasterImages', // Strip embedded PNG/JPG assets
    'sortAttrs',          // Sort attributes for cleaner diffs
    {
      name: 'cleanupNumericValues',
      params: {
        floatPrecision: 2, // Limit decimal precision; do not drop below 2
      },
    },
  ],
};
```

**Decision: pretty print vs. minify**
- Use `pretty: true` with `indent: 2` in workspace libraries to keep Git diffs readable.
- Use `pretty: false` with no indents inside build pipelines to minimize production file sizes.

### 2. Optimize a Single SVG File

```powershell
# In-place (only on git-tracked assets where changes can be reverted)
svgo logo.svg

# Output to a new file
svgo logo.svg -o src/assets/logo.optimized.svg --config svgo.config.js
```

### 3. Batch Compress a Directory of SVGs

```powershell
svgo -f src/assets/raw-icons -o src/assets/icons --config svgo.config.js
```

### 4. Optimize SVG from stdin

```powershell
# PowerShell: pipe file content into svgo
Get-Content input.svg -Raw | svgo --string - -o output.svg
```

### 5. CI/CD Dry-Run Gate

Verify that SVGO would not modify already-optimized files without writing changes:

```powershell
# PowerShell: iterate all SVGs and dry-run each
Get-ChildItem -Path src/assets -Recurse -Filter *.svg | ForEach-Object {
  svgo --dry-run $_.FullName
}
```

## Configuration Reference

| Flag / Option       | Purpose                                                      |
|---------------------|--------------------------------------------------------------|
| `input.svg`         | Target file to optimize (in-place if no `-o`).               |
| `-o output.svg`     | Write optimized output to a specific path.                   |
| `-f folder`         | Optimize all SVGs in a folder.                               |
| `--config file`     | Use a custom configuration file.                             |
| `--string -`        | Read SVG from stdin.                                         |
| `--dry-run`         | Report what would change without writing files.              |

## Pitfalls

- **HARD RULE — Never enable `removeViewBox`**: Stripping the `viewBox` attribute prevents SVGs from scaling dynamically in fluid CSS grids and breaks responsive layout designs. Always override `removeViewBox: false` in `preset-default`.
- **`cleanupIds` breaks animated/interactive SVGs**: SVGO's `cleanupIds` plugin strips or renames element IDs. If CSS variables or JavaScript reference specific element IDs (e.g. `<path id="star-path">`), optimization will break styles and animations. Disable `cleanupIds` when optimizing animated or interactive SVGs.
- **Embedded raster images inflate file size**: SVGs can contain base64-encoded PNG/JPG images (`<image href="data:image/png;base64,...">`). This defeats the purpose of vector code. Enable `removeRasterImages` to strip these payloads.
- **SVGO v3+ requires ESM config**: Config files must use `export default` in `.js` or `.mjs` files. CommonJS `module.exports` will fail on v3+.
- **Default presets may strip needed namespaces**: Default presets can remove namespace nodes needed by external tooling (e.g. Inkscape tags, React-specific properties). Review plugin overrides before batch runs.
- **Coordinate precision below 2 warps paths**: Setting `floatPrecision` below 2 can cause visible path distortion. Keep it at 2 or higher.
- **In-place edits on untracked files are irreversible**: Only run in-place optimization (`svgo file.svg`) on git-tracked assets. Use `-o` for build artifacts.
- **Broken XML input fails silently or produces invalid output**: Validate XML well-formedness before running SVGO on hand-edited SVGs.

## Verification

After optimization, run these checks:

### 1. Confirm `viewBox` is preserved

```powershell
# Should output the viewBox attribute for every optimized SVG
Select-String -Path src/assets/icons/*.svg -Pattern 'viewBox' | Select-Object Filename, LineNumber, Line
```

If any file is missing `viewBox`, re-run with `removeViewBox: false` in the config.

### 2. Confirm no raster image payloads remain

```powershell
# Should return no matches
Select-String -Path src/assets/icons/*.svg -Pattern 'data:image/(png|jpeg|jpg)'
```

### 3. Confirm float precision is adequate

Visually inspect optimized paths or diff against the original. If path coordinates warp, increase `floatPrecision` in the `cleanupNumericValues` plugin params.

### 4. Confirm interactive IDs are preserved

```powershell
# List all id attributes in optimized files
Select-String -Path src/assets/icons/*.svg -Pattern 'id="' | Select-Object Filename, Line
```

Cross-reference with any CSS or JS that targets those IDs.

### 5. Check compression metrics

SVGO reports saved bytes and percentage on each run. Verify the output shows non-zero savings (or zero if already optimized).

## Quality Bar

- [ ] `viewBox` attributes preserved on all optimized files.
- [ ] Coordinate `floatPrecision` is 2 or higher.
- [ ] Nested `<image>` raster nodes removed or flagged for replacement.
- [ ] All vector IDs used in interactive styling are preserved.
- [ ] Config file uses ESM `export default` syntax (SVGO v3+).
- [ ] In-place edits only performed on git-tracked assets.

## Failure Handling

- **Path coordinates warp after optimization**: Increase `floatPrecision` inside the `cleanupNumericValues` params block (e.g. from 2 to 3 or 4).
- **Broken SVG tags after optimization**: Check XML validity of the source file before running SVGO. Use an XML validator or `xmllint --noout input.svg`.
- **Config file not loaded**: Ensure the file is named `svgo.config.js` or `svgo.config.mjs` and uses `export default`. Pass `--config <path>` explicitly if it is not in the project root.
- **`cleanupIds` broke animations**: Re-run with `cleanupIds: false` and restore the original IDs from git.

## Source Anchors

- [SVGO GitHub Repository](https://github.com/svg/svgo)
- [W3C SVG Specification](https://www.w3.org/TR/SVG2/)
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design](https://m3.material.io/)

## Changelog

- **2026-05-30**: Modernized frontmatter schema, set domain to UI-UX, converted instructions to imperative structures, updated configurations to v3 ESM requirements, introduced responsive layout verification guidelines.
- **2026-05-31**: Rewritten to production-grade agent skill format with numbered procedures, PowerShell-native commands, expanded pitfalls, and checkable verification steps.
