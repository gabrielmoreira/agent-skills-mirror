---
type: skill
lifecycle: stable
inheritance: inheritable
name: parity-guard-test-pattern
description: When checking that all callers of a contract implement it correctly, you get false positives from wrapper delegators:
tier: standard
applyTo: '**/*parity*,**/*guard*,**/*test*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Parity Guard Test Pattern

## The Problem

When checking that all callers of a contract implement it correctly, you get false positives from wrapper delegators:

```javascript
// Contract: "All files that call exec() must handle exit code 2"

// Direct caller — MUST implement contract
execFileSync('node', [script]); // Must handle exit code

// Delegator — calls wrapper that already handles contract
runMuscle(script); // runMuscle handles exit code internally
```

Testing both the same way creates noise.

## The Solution

Split tests into DIRECT callers and DELEGATION callers.

```javascript
// parity-guard.test.js

const directCallers = findFiles((content) => 
  content.includes("child_process") && 
  /exec(File)?Sync|spawn/.test(content)
);

const wrapperCallers = findFiles((content) =>
  /runMuscle|muscleAndPrompt|executeScript/.test(content)
);

describe('Contract: exit code handling', () => {
  describe('Direct callers (must implement)', () => {
    directCallers.forEach(file => {
      it(`${file} handles exit code 2`, () => {
        const content = fs.readFileSync(file, 'utf8');
        expect(content).toMatch(/exitCode|status|code.*===?\s*2/);
      });
    });
  });

  describe('Delegators (exempt — wrapper handles)', () => {
    wrapperCallers.forEach(file => {
      it(`${file} uses contract-compliant wrapper`, () => {
        const content = fs.readFileSync(file, 'utf8');
        // Just verify they use the wrapper, not raw exec
        expect(content).not.toMatch(/execFileSync|execSync/);
      });
    });
  });
});
```

## Classification Rules

| Pattern | Category | Contract Obligation |
|---------|----------|-------------------|
| `require('child_process')` + `exec*` | Direct | Must implement |
| `import { spawn }` + `spawn()` | Direct | Must implement |
| `runMuscle()` | Delegator | Exempt |
| `shellExecute()` (if contract-compliant) | Delegator | Exempt |

## Verification

1. Direct callers all implement the contract
2. Delegators use compliant wrappers
3. No false positives from wrapper usage
4. New callers are automatically classified

## When to Apply

- Any "all X must do Y" contract
- Error handling requirements
- Logging requirements
- Security patterns (sanitization, auth checks)

## Tags

`quality` `testing` `contracts` `parity`
