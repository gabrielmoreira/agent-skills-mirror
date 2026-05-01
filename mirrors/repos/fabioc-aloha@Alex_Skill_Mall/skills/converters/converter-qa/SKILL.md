---
type: skill
lifecycle: stable
inheritance: inheritable
name: "converter-qa"
description: Test harness for validating converter outputs with 284 assertions across all converter muscles
tier: standard
applyTo: '**/*converter*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Converter QA Framework


> Trust your converters -- 284 assertions prove they work

Test harness that validates all converter outputs: md-to-word regression tests, md-to-eml structure validation, shared module unit tests, file size bounds, and output format verification.

## When to Use

- After modifying any converter muscle or shared module
- Before releasing a new version of the converter pipeline
- When adding new features to md-to-word, md-to-eml, or shared modules
- As part of the pre-publish quality gate

## Test Suites

| Suite | Covers | Assertions |
|-------|--------|-----------|
| Shared module tests | All 8 shared modules (preprocessor, mermaid, config, etc.) | ~120 |
| md-to-word smoke | End-to-end Word conversion with multiple style presets | ~40 |
| md-to-word OOXML | Visual regression (XML structure, table styling) | ~30 |
| md-to-eml structure | Email HTML, CID images, frontmatter mapping | ~20 |
| markdown-lint | All 19 lint rules with positive and negative cases | ~30 |
| md-scaffold | Template generation for all 5 template types | ~15 |
| nav-inject | Navigation injection, dry-run, init | ~10 |
| CLI flag parsing | All CLI flags for md-to-word (new flags) | ~15 |
| Lua filter syntax | Pandoc Lua filter validation | ~4 |

## Usage

```bash
# Run all tests
node .github/muscles/converter-qa.cjs

# Run a specific suite
node .github/muscles/converter-qa.cjs --suite=word
node .github/muscles/converter-qa.cjs --suite=shared

# Verbose output (show passing tests)
node .github/muscles/converter-qa.cjs --verbose
```

## Adding Tests

Tests use a minimal zero-dependency framework:

```javascript
suite('My test suite', () => {
  assert(condition, 'description of what is being tested');
  skip('description of skipped test');  // for known issues
});
```

## Quality Gate Integration

This muscle is part of the pre-publish quality gate:

1. `converter-qa.cjs` runs all 284 assertions
2. Zero failures required to pass
3. Skips are tracked but don't block (used for environment-dependent tests)

## Test Patterns

### Assertion Style

Tests use direct boolean assertions with descriptive messages:

```javascript
suite('preprocessor', () => {
  const result = preprocessMarkdown(input);
  assert(result.includes('expected'), 'preprocessor should transform X to Y');
  assert(!result.includes('bad'), 'preprocessor should strip bad patterns');
});
```

### Regression Testing

OOXML tests compare generated Word document XML structure against known-good snapshots:

1. Generate a `.docx` from a known markdown input
2. Unzip the `.docx` and extract `document.xml`
3. Assert specific XML elements exist (table styles, heading formats, image references)
4. Assert element counts match expected values

### Environment-Dependent Skips

Some tests depend on external tools (Pandoc, Mermaid CLI). Use `skip()` when the tool is unavailable:

```javascript
if (!hasPandoc()) {
  skip('Pandoc Lua filter syntax (pandoc not installed)');
} else {
  suite('Lua filter', () => { /* ... */ });
}
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Assertion count mismatch | New tests added — update the expected count in docs |
| OOXML regression failure | Intentional style change — regenerate snapshot |
| Pandoc tests skipped | Install Pandoc: `winget install JohnMacFarlane.Pandoc` |
| Mermaid render tests fail | Install `@mermaid-js/mermaid-cli` globally |
