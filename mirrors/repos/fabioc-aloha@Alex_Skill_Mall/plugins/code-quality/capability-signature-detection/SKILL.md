---
type: skill
lifecycle: stable
inheritance: inheritable
name: capability-signature-detection
description: Code-scanning regex that looks for literal strings misses real usage:
tier: standard
applyTo: '**/*capability*,**/*signature*,**/*detection*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Capability Signature Detection

## The Problem

Code-scanning regex that looks for literal strings misses real usage:

```javascript
// First attempt: find files that use ".github/muscles/"
grep -rn '\.github/muscles/' . // Misses most actual usage!

// Because real code uses variables:
const musclePath = path.join(brainDir, 'muscles', name);
execFileSync('node', [musclePath]); // No literal string!
```

## The Solution

Detect the **capability signature**, not the literal text.

```javascript
// Instead of: "files containing '.github/muscles/'"
// Detect: "files that import child_process AND call execFileSync/spawn"

const hasCapability = (content) => {
  const importsChildProcess = /require\(['"]child_process['"]\)|from ['"]child_process['"]/.test(content);
  const callsExec = /exec(File)?Sync|spawn(Sync)?/.test(content);
  return importsChildProcess && callsExec;
};
```

## Pattern Design

Ask: **"If a developer renames a path constant, would the test still find them?"**

| Approach | Survives Rename? | Use When |
|----------|------------------|----------|
| Literal string match | No | String IS the contract |
| Import + call pattern | Yes | Behavior IS the contract |
| AST parsing | Yes | Complex patterns |

## Examples

### Find Files That Execute Node Scripts

```javascript
// Bad: misses variable paths
const bad = /execFileSync\(['"]node['"],\s*\[['"]\.github/;

// Good: finds capability
const good = (content) => {
  const hasChildProcess = /child_process/.test(content);
  const executesNode = /exec(File)?Sync\(\s*['"]node['"]/.test(content);
  return hasChildProcess && executesNode;
};
```

### Find Files That Make HTTP Requests

```javascript
// Bad: misses axios, got, node-fetch, etc.
const bad = /fetch\(/;

// Good: covers common HTTP libraries
const good = (content) => {
  return /require\(['"](?:axios|got|node-fetch|undici)['"]\)|fetch\(|http\.request/.test(content);
};
```

## Verification

1. Rename a path variable → test still finds the file
2. Add new caller with different variable name → test finds it
3. False positives are acceptable if they're related capability

## When to Apply

- Finding callers of internal APIs
- Security audits (who can exec, who can write files)
- Contract enforcement
- Dependency analysis

## Tags

`quality` `testing` `regex` `code-analysis`
