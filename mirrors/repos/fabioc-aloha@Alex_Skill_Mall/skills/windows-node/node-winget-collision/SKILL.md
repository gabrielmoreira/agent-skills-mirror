---
type: skill
lifecycle: stable
inheritance: inheritable
name: node-winget-collision
description: Node.js installed via winget collides with nvm — path priority, shim conflicts, resolution steps
tier: extended
applyTo: '**/*node*,**/*winget*,**/*collision*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Node.js Winget Collision

**Category**: Windows / Node.js
**Time Saved**: 30-60 minutes debugging
**Battle-tested**: Yes — occurred during Node.js upgrade

---

## The Problem

You install Node.js 22 via winget. It works. Later you uninstall the old Node.js 20 version. Suddenly `node --version` gives an error or shows the wrong version. Your terminal can't find node at all.

## Why It Happens

Multiple winget Node.js packages share the same installation directory:

```
OpenJS.NodeJS.22    →  C:\Program Files\nodejs\
OpenJS.NodeJS.LTS   →  C:\Program Files\nodejs\
OpenJS.NodeJS       →  C:\Program Files\nodejs\
```

When you uninstall ANY of them, winget removes the shared binaries — even if another package is still "installed."

## The Rule

**When upgrading Node.js via winget: Install new first, verify, THEN uninstall old.**

## Safe Upgrade Procedure

### Step 1: Install New Version First

```powershell
# Install Node 22 (don't uninstall old yet!)
winget install OpenJS.NodeJS --version 22.x.x

# Or use the versioned package
winget install OpenJS.NodeJS.22
```

### Step 2: Verify Installation

```powershell
# Close and reopen terminal, then:
node --version
# Should show v22.x.x

npm --version
# Should work
```

### Step 3: Only Then Uninstall Old

```powershell
# NOW it's safe to remove old version
winget uninstall OpenJS.NodeJS.LTS

# Or uninstall by exact ID from winget list
winget list nodejs  # Find the exact ID
winget uninstall OpenJS.NodeJS --version 20.x.x
```

### Step 4: Verify Again

```powershell
node --version
# Still v22.x.x — good!
```

## If You Already Broke It

### Recovery Steps

```powershell
# 1. Check what winget thinks is installed
winget list nodejs

# 2. Uninstall all Node entries
winget uninstall OpenJS.NodeJS
winget uninstall OpenJS.NodeJS.LTS
winget uninstall OpenJS.NodeJS.22

# 3. Clean up PATH (if needed)
# Remove stale C:\Program Files\nodejs entries

# 4. Fresh install
winget install OpenJS.NodeJS.22

# 5. Restart terminal and verify
node --version
```

### Manual PATH Cleanup

```powershell
# Check current PATH
$env:PATH -split ';' | Where-Object { $_ -like '*nodejs*' }

# If it shows paths that don't exist:
# System Properties → Environment Variables → Path → Remove bad entries
```

## Alternative: Use NVM for Windows

Avoid the problem entirely with Node Version Manager:

```powershell
# Install nvm-windows
winget install CoreyButler.NVMforWindows

# Then manage versions safely
nvm install 22
nvm install 20
nvm use 22
nvm list
```

## Package ID Reference

| Package ID | Description |
|------------|-------------|
| `OpenJS.NodeJS` | Latest stable |
| `OpenJS.NodeJS.LTS` | Latest LTS |
| `OpenJS.NodeJS.22` | Specific v22 |
| `OpenJS.NodeJS.20` | Specific v20 |
| `OpenJS.NodeJS.18` | Specific v18 |

## Verification Checklist

- [ ] Never uninstall old Node before installing new
- [ ] Verify `node --version` after install
- [ ] Check `npm --version` works
- [ ] Only then uninstall old version
- [ ] Consider nvm-windows for version management

## Common Symptoms

- "'node' is not recognized" after uninstalling old version
- Wrong Node version showing after upgrade
- npm commands fail after Node.js changes
- PATH contains nonexistent nodejs folder

## Related Skills

- `pat-expiration-silent` — Silent failures in Windows tools
