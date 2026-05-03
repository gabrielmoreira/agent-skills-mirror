---
type: skill
lifecycle: stable
inheritance: inheritable
name: path-traversal-prevention
description: When copying files or serving content, user-controlled paths can escape the intended directory:
tier: standard
applyTo: '**/*path*,**/*traversal*,**/*prevention*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Path Traversal Prevention

## The Problem

When copying files or serving content, user-controlled paths can escape the intended directory:

```javascript
// Vulnerable: attacker controls filename
const dest = path.join(uploadDir, req.body.filename);
// If filename is "../../../etc/passwd", dest escapes uploadDir
```

## The Solution

Validate that resolved paths stay within the intended root:

```javascript
function safeJoin(root, userPath) {
  const resolved = path.resolve(root, userPath);
  const normalized = path.normalize(resolved);
  
  // Ensure result is still within root
  if (!normalized.startsWith(path.normalize(root) + path.sep) && 
      normalized !== path.normalize(root)) {
    throw new Error('Path traversal attempt detected');
  }
  
  return normalized;
}

// Usage
try {
  const safePath = safeJoin('/uploads', userFilename);
  // Safe to use safePath
} catch (err) {
  res.status(400).json({ error: 'Invalid filename' });
}
```

## For Directory Trees

When recursively copying directories:

```javascript
async function safeCopyTree(src, dest, allowedRoot) {
  const entries = await fs.readdir(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    // Validate destination stays in bounds
    const resolvedDest = path.resolve(destPath);
    if (!resolvedDest.startsWith(path.resolve(allowedRoot))) {
      throw new Error(`Path escape: ${entry.name}`);
    }
    
    if (entry.isDirectory()) {
      await fs.mkdir(destPath, { recursive: true });
      await safeCopyTree(srcPath, destPath, allowedRoot);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}
```

## Common Attack Patterns

| Pattern | What It Does |
|---------|--------------|
| `../` | Parent directory |
| `..\\` | Parent on Windows |
| `....//` | Bypass naive `../` filter |
| `%2e%2e%2f` | URL-encoded `../` |
| `..%c0%af` | Overlong UTF-8 encoding |

## Verification

```javascript
const attacks = [
  '../etc/passwd',
  '..\\windows\\system32',
  'foo/../../bar',
  'normal/path/file.txt'  // Should pass
];

attacks.forEach(p => {
  try {
    const result = safeJoin('/uploads', p);
    console.log(`OK: ${p} -> ${result}`);
  } catch (e) {
    console.log(`BLOCKED: ${p}`);
  }
});
```

## When to Apply

- File upload handlers
- Static file servers
- Archive extraction (zip, tar)
- Template file loading
- Any path from user input

## Tags

`security` `path-traversal` `file-system` `input-validation`
