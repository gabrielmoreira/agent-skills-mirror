---
type: skill
lifecycle: stable
inheritance: inheritable
name: cloud-storage-paths
description: Cross-platform cloud storage path resolution — OneDrive, iCloud, Dropbox path discovery and normalization
tier: standard
applyTo: '**/*cloud*,**/*storage*,**/*paths*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Cloud Storage Paths

**Category**: Cross-Platform
**Time Saved**: 1-2 hours debugging path resolution
**Battle-tested**: Yes — iCloud, OneDrive, Dropbox variants

---

## The Problem

Your app needs to find the user's iCloud Drive (or OneDrive, Dropbox, Google Drive). You hardcode `~/iCloudDrive` and it works on your machine. Users report "folder not found" errors.

## Why It Happens

Cloud storage paths vary by:

1. **Provider** — Each has different naming conventions
2. **OS** — Same provider has different paths per OS
3. **Account type** — Personal vs Business often differ
4. **Installation method** — App Store vs direct download
5. **Version** — Paths change between app versions

## The Rule

**Use a candidate-list approach. Check all known paths in priority order. Return first that exists.**

## Path Variants by Provider

### iCloud Drive

| Platform | Possible Paths |
|----------|---------------|
| macOS | `~/Library/Mobile Documents/com~apple~CloudDocs/` |
| Windows | `%USERPROFILE%\iCloudDrive\` |
| Windows | `%USERPROFILE%\iCloud Drive\` (space) |
| Windows | `%USERPROFILE%\iCloud~com~apple~CloudDocs\` |

### OneDrive

| Account Type | Windows Path |
|--------------|-------------|
| Personal | `%USERPROFILE%\OneDrive\` |
| Business | `%USERPROFILE%\OneDrive - CompanyName\` |
| Education | `%USERPROFILE%\OneDrive - SchoolName\` |

macOS: `~/Library/CloudStorage/OneDrive-Personal/` or `~/Library/CloudStorage/OneDrive-CompanyName/`

### Dropbox

| Platform | Possible Paths |
|----------|---------------|
| Windows | `%USERPROFILE%\Dropbox\` |
| Windows | `%APPDATA%\Dropbox\` (older) |
| macOS | `~/Dropbox/` |
| macOS | `~/Library/CloudStorage/Dropbox/` (newer) |

### Google Drive

| Platform | Possible Paths |
|----------|---------------|
| Windows | `%USERPROFILE%\Google Drive\` |
| Windows | `G:\My Drive\` (mapped drive) |
| macOS | `~/Google Drive/` |
| macOS | `~/Library/CloudStorage/GoogleDrive-email/` |

## Implementation Pattern

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

function findCloudStorage(provider) {
  const home = os.homedir();
  const candidates = getCandidates(provider, home);
  
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  
  return null; // Not found
}

function getCandidates(provider, home) {
  const isWindows = process.platform === 'win32';
  
  switch (provider) {
    case 'icloud':
      return isWindows ? [
        path.join(home, 'iCloudDrive'),
        path.join(home, 'iCloud Drive'),
        path.join(home, 'iCloud~com~apple~CloudDocs'),
      ] : [
        path.join(home, 'Library/Mobile Documents/com~apple~CloudDocs'),
      ];
      
    case 'onedrive':
      return isWindows ? [
        path.join(home, 'OneDrive'),
        // Scan for business accounts
        ...findOneDriveBusinessPaths(home),
      ] : [
        path.join(home, 'Library/CloudStorage/OneDrive-Personal'),
        ...findOneDriveBusinessPaths(home),
      ];
      
    case 'dropbox':
      return isWindows ? [
        path.join(home, 'Dropbox'),
        path.join(process.env.APPDATA || '', 'Dropbox'),
      ] : [
        path.join(home, 'Dropbox'),
        path.join(home, 'Library/CloudStorage/Dropbox'),
      ];
      
    default:
      return [];
  }
}

function findOneDriveBusinessPaths(home) {
  // Scan for "OneDrive - *" folders
  const paths = [];
  try {
    const entries = fs.readdirSync(home);
    for (const entry of entries) {
      if (entry.startsWith('OneDrive - ')) {
        paths.push(path.join(home, entry));
      }
    }
  } catch { /* ignore */ }
  return paths;
}
```

## Environment Variable Hints

Some providers set environment variables:

```javascript
// OneDrive often sets these
process.env.OneDrive           // Personal
process.env.OneDriveCommercial // Business

// Use if available, fall back to scanning
const onedrive = process.env.OneDrive || findCloudStorage('onedrive');
```

## Verification Checklist

- [ ] Never hardcode a single cloud storage path
- [ ] Check all known variants for the provider
- [ ] Handle "not installed" case gracefully
- [ ] Test on multiple machines with different setups
- [ ] Log which path was found for debugging

## Common Symptoms

- "Works on my machine" with cloud storage
- "Folder not found" on user machines
- Different paths in bug reports

## Related Skills

- `vscode-cross-platform-paths` — VS Code config paths
- `line-ending-parsing` — Cross-platform file handling
