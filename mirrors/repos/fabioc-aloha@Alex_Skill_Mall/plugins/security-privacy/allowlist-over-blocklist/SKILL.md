---
type: skill
lifecycle: stable
inheritance: inheritable
name: allowlist-over-blocklist
description: Validate input against an allowlist of permitted values — reject everything else
tier: standard
applyTo: '**/*allowlist*,**/*over*,**/*blocklist*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Allowlist Over Blocklist

**Category**: Security
**Time Saved**: Prevents security incidents
**Battle-tested**: Yes — fundamental security principle

---

## The Problem

You need to validate user input — URLs, file paths, commands, or any constrained values. You think "I'll block the dangerous ones" and create a blocklist. Later, an attacker finds a format you didn't think of.

## Why Blocklists Fail

Blocklists are incomplete by definition. They only block what you anticipated. Attackers find edge cases, encodings, and variants you didn't consider.

**Example: URL validation blocklist**

```javascript
// ❌ BLOCKLIST APPROACH
const blocked = ['javascript:', 'data:', 'vbscript:'];
if (blocked.some(b => url.toLowerCase().startsWith(b))) {
  reject();
}
// Bypassed by: JAVASCRIPT:, java\nscript:, data\x00:text/html
```

## The Rule

**Enumerate what's permitted. Reject everything else.**

```javascript
// ✅ ALLOWLIST APPROACH
const allowed = ['https:', 'http:'];
const protocol = new URL(url).protocol;
if (!allowed.includes(protocol)) {
  reject();
}
// Only https: and http: pass. Everything else fails.
```

## When to Apply

| Domain | Allowlist | Not Blocklist |
|--------|-----------|---------------|
| URL schemes | `['https:', 'http:']` | Not `['javascript:', 'data:']` |
| File extensions | `['.jpg', '.png', '.pdf']` | Not `['.exe', '.sh']` |
| Commands | `['git', 'npm', 'node']` | Not `['rm', 'curl']` |
| API methods | `['GET', 'POST']` | Not `['DELETE', 'PATCH']` |
| User roles | `['admin', 'editor', 'viewer']` | Not `['banned', 'suspended']` |

## Implementation Patterns

### URL Validation

```javascript
const ALLOWED_PROTOCOLS = new Set(['https:', 'http:']);

function isValidUrl(input) {
  try {
    const url = new URL(input);
    return ALLOWED_PROTOCOLS.has(url.protocol);
  } catch {
    return false;
  }
}
```

### File Extension Validation

```javascript
const ALLOWED_EXTENSIONS = new Set(['.jpg', '.jpeg', '.png', '.gif', '.pdf']);

function isAllowedFile(filename) {
  const ext = path.extname(filename).toLowerCase();
  return ALLOWED_EXTENSIONS.has(ext);
}
```

### Command Execution

```javascript
const ALLOWED_COMMANDS = new Set(['git', 'npm', 'node', 'tsc']);

function safeExec(command, args) {
  if (!ALLOWED_COMMANDS.has(command)) {
    throw new Error(`Command not allowed: ${command}`);
  }
  return execFileSync(command, args);
}
```

### API Method Validation

```javascript
const ALLOWED_METHODS = new Set(['GET', 'POST', 'PUT']);

function validateMethod(method) {
  if (!ALLOWED_METHODS.has(method.toUpperCase())) {
    throw new Error(`Method not allowed: ${method}`);
  }
}
```

## Combining with Other Validations

Allowlists are your first gate, not your only gate:

```javascript
function validateUpload(file) {
  // Gate 1: Allowlist extension
  if (!ALLOWED_EXTENSIONS.has(path.extname(file.name).toLowerCase())) {
    throw new Error('File type not allowed');
  }
  
  // Gate 2: Check MIME type
  if (!ALLOWED_MIMES.has(file.mimetype)) {
    throw new Error('MIME type not allowed');
  }
  
  // Gate 3: Check magic bytes
  if (!verifyMagicBytes(file.buffer)) {
    throw new Error('File content mismatch');
  }
}
```

## Common Mistakes

| Mistake | Problem |
|---------|---------|
| Case-sensitive allowlist | `HTTPS:` bypasses `['https:']` |
| Partial matching | `https://evil.com` matches `http` |
| Mutable allowlist | Attackers modify at runtime |
| Empty string in allowlist | Matches falsy inputs |

## Verification Checklist

- [ ] All validation uses allowlist approach
- [ ] Allowlists are `const` or frozen
- [ ] Case normalization applied before check
- [ ] Default action is reject (not allow)
- [ ] No blocklist fallbacks

## Related Skills

- `shell-injection-prevention` — Command validation
- `path-traversal-prevention` — File path validation
