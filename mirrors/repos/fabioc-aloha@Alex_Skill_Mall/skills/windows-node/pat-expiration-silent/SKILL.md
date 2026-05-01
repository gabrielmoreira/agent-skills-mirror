---
type: skill
lifecycle: stable
inheritance: inheritable
name: pat-expiration-silent
description: Personal Access Token expiration fails silently — 401 errors with no expiry message, pre-check pattern
tier: extended
applyTo: '**/*pat*,**/*expiration*,**/*silent*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# PAT Expiration Silent Failure

**Category**: Windows / Node.js
**Time Saved**: 30 minutes debugging publish failures
**Battle-tested**: Yes — VS Code Marketplace publishing

---

## The Problem

You run `vsce publish` or `npm publish` and it fails with a 401 error. Your `VSCE_PAT` or `NPM_TOKEN` environment variable is set. You just used it last week. What changed?

## Why It Happens

Personal Access Tokens (PATs) have expiration dates. When they expire:

- The environment variable still exists
- Preflight checks that look for "is variable set?" pass
- The actual API call fails with 401 Unauthorized
- Error messages often don't say "token expired"

## The Rule

**Token existence ≠ token validity. The 401 at publish time is the first signal that your PAT expired.**

## Common Tokens and Their Lifespans

| Token | Max Lifespan | Typical Setting |
|-------|-------------|-----------------|
| Azure DevOps PAT | 1 year | 90 days default |
| GitHub PAT (classic) | No expiry option | 30-90 days recommended |
| GitHub PAT (fine-grained) | 1 year max | Organization policy |
| npm token | No expiry | Until revoked |

## Detection Pattern

When you see a 401 during publish:

### Step 1: Identify the Token

```powershell
# Check which token is being used
echo $env:VSCE_PAT  # For VS Code Marketplace
echo $env:NPM_TOKEN  # For npm
echo $env:GH_TOKEN   # For GitHub CLI
```

### Step 2: Check Token Portal

| Service | Token Management URL |
|---------|---------------------|
| Azure DevOps | `https://dev.azure.com/{org}/_usersSettings/tokens` |
| GitHub | `https://github.com/settings/tokens` |
| npm | `https://www.npmjs.com/settings/~/tokens` |

### Step 3: Regenerate and Update

```powershell
# After creating new token, update env var
$env:VSCE_PAT = "new-token-value"

# Or set permanently
[Environment]::SetEnvironmentVariable("VSCE_PAT", "new-token-value", "User")

# Restart terminal to pick up changes
```

## Prevention: Calendar Reminders

Set calendar reminders before token expiry:

```
Token: VSCE_PAT
Created: 2026-01-15
Expires: 2026-04-15
Reminder: 2026-04-01 (2 weeks before)
```

## Token Scope Requirements

### VS Code Marketplace (VSCE)

Required scopes for Azure DevOps PAT:

- **Marketplace**: Manage (or Publish)
- Organization: All accessible organizations (or specific)

### npm

Required scope:

- **Automation** (for CI/CD) or **Publish** (for interactive)

### GitHub Packages

Required scopes:

- `write:packages`
- `read:packages`
- `delete:packages` (if needed)

## CI/CD Secret Rotation

For GitHub Actions secrets:

```yaml
# .github/workflows/publish.yml
env:
  VSCE_PAT: ${{ secrets.VSCE_PAT }}  # Update this secret when token rotates
```

**Reminder**: When you rotate a token, update:

1. Local environment variable
2. CI/CD secrets (GitHub, Azure DevOps, etc.)
3. Any shared credential stores

## Verification Checklist

- [ ] Check token expiration date in portal
- [ ] Set calendar reminder 2 weeks before expiry
- [ ] Update token in all locations when rotating
- [ ] Document which services use which tokens
- [ ] Test publish in dev environment after rotation

## Common Symptoms

- 401 Unauthorized during `vsce publish`
- 401 during `npm publish`
- "Authentication failed" with no further details
- Worked last month, fails now (no code changes)

## Preflight Script Idea

```javascript
// Add to your publish script
const { execSync } = require('child_process');

function checkVscePat() {
  const pat = process.env.VSCE_PAT;
  if (!pat) {
    console.error('VSCE_PAT not set');
    process.exit(1);
  }
  
  // PAT format: base64 encoded, typically 52+ chars
  if (pat.length < 50) {
    console.warn('VSCE_PAT looks short - might be truncated or invalid');
  }
  
  // Can't validate expiry without API call, but can warn
  console.log('VSCE_PAT is set. If publish fails with 401, check token expiry.');
}
```

## Related Skills

- `node-winget-collision` — Windows Node.js issues
