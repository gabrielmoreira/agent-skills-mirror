---
type: skill
lifecycle: stable
inheritance: inheritable
name: vscode-cross-platform-paths
description: VS Code path handling across Windows, macOS, and Linux — URI schemes, path separators, workspace folders
tier: standard
applyTo: '**/*vscode*,**/*cross*,**/*platform*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# VS Code Cross-Platform Paths

**Category**: Cross-Platform
**Time Saved**: 30 minutes debugging path resolution
**Battle-tested**: Yes — VS Code extension development

---

## The Problem

Your VS Code extension or script needs to find VS Code's user settings, extensions, or data folders. You use `process.env.APPDATA + '/Code/User'` and it works on Windows. Mac and Linux users report errors.

## Why It Happens

VS Code stores user data in different locations on each OS, and the paths don't follow a consistent pattern:

| OS | User Settings Path |
|----|-------------------|
| Windows | `%APPDATA%\Code\User` |
| macOS | `~/Library/Application Support/Code/User` |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/Code/User` |

## The Rule

**Use `os.platform()` switch to resolve VS Code paths. Never hardcode a single platform's path.**

## Implementation Pattern

```javascript
const os = require('os');
const path = require('path');

function getVSCodeUserPath() {
  const platform = os.platform();
  const home = os.homedir();
  
  switch (platform) {
    case 'win32':
      return path.join(process.env.APPDATA || '', 'Code', 'User');
      
    case 'darwin':
      return path.join(home, 'Library', 'Application Support', 'Code', 'User');
      
    case 'linux':
      const configHome = process.env.XDG_CONFIG_HOME || path.join(home, '.config');
      return path.join(configHome, 'Code', 'User');
      
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}
```

## All VS Code Paths

### User Data

```javascript
function getVSCodeUserDataPath() {
  const platform = os.platform();
  const home = os.homedir();
  
  switch (platform) {
    case 'win32':
      return path.join(process.env.APPDATA || '', 'Code');
    case 'darwin':
      return path.join(home, 'Library', 'Application Support', 'Code');
    case 'linux':
      const configHome = process.env.XDG_CONFIG_HOME || path.join(home, '.config');
      return path.join(configHome, 'Code');
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}
```

### Extensions

```javascript
function getVSCodeExtensionsPath() {
  const home = os.homedir();
  // Same on all platforms!
  return path.join(home, '.vscode', 'extensions');
}
```

### Common Subpaths

| Subpath | Contains |
|---------|----------|
| `User/settings.json` | User settings |
| `User/keybindings.json` | Keyboard shortcuts |
| `User/snippets/` | Custom snippets |
| `User/globalStorage/` | Extension global state |
| `User/workspaceStorage/` | Per-workspace extension state |

## VS Code Insiders

VS Code Insiders uses different folder names:

```javascript
function getVSCodePath(insider = false) {
  const folderName = insider ? 'Code - Insiders' : 'Code';
  const platform = os.platform();
  const home = os.homedir();
  
  switch (platform) {
    case 'win32':
      return path.join(process.env.APPDATA || '', folderName);
    case 'darwin':
      return path.join(home, 'Library', 'Application Support', folderName);
    case 'linux':
      const configHome = process.env.XDG_CONFIG_HOME || path.join(home, '.config');
      return path.join(configHome, folderName);
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}
```

## Using VS Code APIs (When Available)

In extension context, prefer VS Code APIs:

```typescript
import * as vscode from 'vscode';

// Global storage (extension-specific)
const globalStoragePath = context.globalStorageUri.fsPath;

// Workspace storage
const workspaceStoragePath = context.storageUri?.fsPath;

// Log path
const logPath = context.logUri.fsPath;
```

## Verification Checklist

- [ ] Never use raw `process.env.APPDATA` for VS Code paths
- [ ] Handle all three platforms (win32, darwin, linux)
- [ ] Use `path.join()` for all path construction
- [ ] Test on actual machines or VMs, not just path strings
- [ ] Consider VS Code Insiders variant

## Common Symptoms

- "Extension works on Windows, crashes on Mac"
- "Can't find settings file on Linux"
- "APPDATA is undefined" (non-Windows)

## Related Skills

- `cloud-storage-paths` — Other app data locations
- `line-ending-parsing` — Cross-platform file handling
