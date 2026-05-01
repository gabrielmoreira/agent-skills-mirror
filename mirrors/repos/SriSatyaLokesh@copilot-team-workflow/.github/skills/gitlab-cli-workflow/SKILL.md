---
name: gitlab-cli-workflow
description: Complete GitLab CLI (glab) and Git workflow knowledge for automated issue tracking, branch management, and MR creation. Use when handles GitLab-specific operations like creating issues, MRs, or managing branches with glab.
---

# GitLab CLI Workflow

## Overview
Provides complete GitLab CLI (`glab`) and Git workflow knowledge for automated issue tracking, branch management, and MR creation.

## GitLab Message Size Limits & Conventions

**Critical**: Keep messages compact for readability.

| Field | Max Chars | Convention | Example |
|-------|-----------|-----------|---------|
| Issue title | 255 | Keep under 60 | `bug: Post completion not saving` |
| Issue description | ~1MB | Keep under 2000 | Use bullet lists, minimal formatting |
| MR title | 255 | Keep under 60 | `fix: Reading time parsing error` |
| MR description | ~1MB | Keep under 1000 | Compact: `Closes #42. Root cause: X. Fix: Y.` |
| Commit msg subject | 72 | Keep under 50 (conventional) | `fix: Correct filter in post layout` |
| Commit msg body | 72 chars per line | Bullet format w/ blank lines | Use `-` for bullets, 2 blank lines between |

**Format Guidelines**:
- Issue/MR titles: `<type>: <what> <why if critical>`
- Issue description: Start with 1-2 sentences, then bullet points
- MR description: Start with `Closes #X`, then bullets (max 500 chars)
- Commits: Subject 50 chars max, body bullets with blank lines

---

## GitLab CLI Setup

### Installation & Verification

```powershell
# Try simple command first
glab --version

# Windows install via winget
winget install Gitlab.glab

# If glab not in PATH, use full path (adjust version as needed):
& "$env:LOCALAPPDATA\Programs\glab\glab.exe" --version

# Verify installation path exists
Test-Path "$env:LOCALAPPDATA\Programs\glab\glab.exe"  # Should return True
```

### Authentication

```powershell
# Try simple command first
glab auth login

# If that fails, use full path:
& "$env:LOCALAPPDATA\Programs\glab\glab.exe" auth login

# Self-hosted GitLab instance
glab auth login --hostname gitlab.example.com

# Check authentication status
glab auth status

# Refresh token if needed
glab auth refresh
```

### Common Auth Issues

| Issue | Solution |
|-------|----------|
| `glab: command not found` | Use full path: `& "$env:LOCALAPPDATA\Programs\glab\glab.exe"` |
| `GITLAB_TOKEN not set` | Run: `glab auth login` again |
| `404 Not Found` on self-hosted | Add `--hostname your.gitlab.instance` to all commands |
| `Review: Can not approve your own merge request` | Normal — have a teammate approve |

---

## Detecting GitLab Repository

Before offering GitLab CLI automation, **always check if this is a GitLab repo**:

```powershell
# Check if git repo exists
git rev-parse --git-dir 2>$null
if ($LASTEXITCODE -eq 0) {
    # Check if remote is GitLab
    $remote = git config --get remote.origin.url
    if ($remote -match 'gitlab\.') {
        Write-Host "✅ GitLab repository detected"
        # Offer GitLab CLI automation
    } else {
        Write-Host "ℹ️ Git repo but not GitLab - manual workflow"
    }
} else {
    Write-Host "ℹ️ Not a git repository - skipping GitLab automation"
}
```

**When to ask**:
- After creating issue doc
- Before starting implementation
- When user says `/finish-branch`

**What to offer**:
```
🤖 This is a GitLab repository. I can:
1. Create a GitLab issue for tracking
2. Create a feature branch automatically
3. Create and merge MR when complete

Would you like me to automate this? (yes/no)
```

---

## Complete 10-Step Git Workflow

### Step 1: Create GitLab Issue

**Purpose**: Track the work and get an issue number for branching

```powershell
# Try simple command first
glab issue create --title "fix: Image paths missing baseurl" `
  --description "Image paths need baseurl prefix for GitLab Pages"

# If 'glab' command not found, use full path:
& "$env:LOCALAPPDATA\Programs\glab\glab.exe" issue create `
  --title "fix: Image paths missing baseurl" `
  --description "Image paths need baseurl prefix for GitLab Pages"

# Issue with labels
glab issue create --title "fix: Something broken" `
  --description "Description here" `
  --label "bug"

# ⚠️ Note: If any glab command fails with 'command not found',
# replace 'glab' with '& "$env:LOCALAPPDATA\Programs\glab\glab.exe"' throughout
```

**Output**: Returns issue URL (e.g., `https://gitlab.com/namespace/repo/-/issues/42`)

**Parse issue number**:
```powershell
$issueUrl = glab issue create --title "Title" --description "Body"
if ($issueUrl -match 'issues/(\d+)') {
    $issueNumber = $matches[1]
    Write-Host "Created issue #$issueNumber"
}
```

---

### Step 2: Create Feature Branch

**Naming Convention**: `<type>/<issue-number>-<description>`

```bash
# Standard format
git checkout -b fix/42-image-paths-baseurl

# Type prefixes:
# fix/      - Bug fixes
# feature/  - New features
# docs/     - Documentation
# refactor/ - Code refactoring
# style/    - CSS/styling changes
# test/     - Tests
# chore/    - Dependencies, build config
```

**Output**: `Switched to a new branch 'fix/42-image-paths-baseurl'`

**Automated branch creation from issue**:
```powershell
$issueNumber = 42
$issueTitle = "Image paths missing baseurl"
$type = "fix"  # Determine from title or ask user

# Sanitize title for branch name
$description = $issueTitle.ToLower() -replace '[^a-z0-9]+', '-' -replace '^-|-$', ''
$branchName = "$type/$issueNumber-$description"

# Create and checkout branch
git checkout -b $branchName
Write-Host "✅ Created branch: $branchName"
```

---

### Step 3: Implement Changes

```bash
# Work happens here
# Agents write code, tests, etc.
```

---

### Step 4: Commit with Issue Reference

**Critical**: Include issue number in commit message

```bash
# Format
git add .
git commit -m "fix: Add baseurl to image paths

- Updated all placeholder.png paths
- Fixed off.jpg fallbacks
- Images now load on GitLab Pages

Resolves #42"

# Or shorter
git commit -m "fix: Add baseurl to image paths (Resolves #42)"

# Keywords that auto-close issues when MR merges:
# - Fixes #42
# - Resolves #42
# - Closes #42
```

**Automated commit**:
```powershell
$issueNumber = 42
$commitMessage = @"
fix: Add baseurl to image paths

- Updated all placeholder.png paths
- Fixed off.jpg fallbacks
- Images now load on GitLab Pages

Resolves #$issueNumber
"@

git add .
git commit -m $commitMessage
```

---

### Step 5: Push Branch to Remote

```bash
# Push feature branch
git push origin fix/42-image-paths-baseurl

# Or push current branch
git push origin HEAD
```

**Check if push needed**:
```powershell
$currentBranch = git branch --show-current
$remoteBranch = git ls-remote --heads origin $currentBranch

if (-not $remoteBranch) {
    Write-Host "Pushing branch to remote..."
    git push origin $currentBranch
} else {
    Write-Host "Branch already on remote, pushing updates..."
    git push origin $currentBranch
}
```

---

### Step 6: Create Merge Request with "Closes #X"

**⚠️ CRITICAL**: MR description MUST contain `Closes #<issue-number>` for auto-closure

```powershell
# Try simple command first
glab mr create `
  --title "fix: Add baseurl prefix to all image paths" `
  --description "Closes #42

## Changes
- Updated all placeholder.png paths in home.html
- Fixed off.jpg fallback images
- Images now resolve correctly on GitLab Pages

## Testing
✅ Local build passes
✅ No console errors" `
  --target-branch main

# If 'glab' not found, use full path:
& "$env:LOCALAPPDATA\Programs\glab\glab.exe" mr create `
  --title "fix: Add baseurl prefix to all image paths" `
  --description "Closes #42

## Changes
- Updated all placeholder.png paths
- Testing passed" `
  --target-branch main

# ⚠️ MUST include "Closes #42" or issues won't auto-close
```

**Automated MR creation from work folder**:
```powershell
$issueNumber = 42
$workDir = "work/ISSUE-042-feature-name"

# Read plan.md and result.md
$plan = Get-Content "$workDir/plan.md" -Raw
$result = Get-Content "$workDir/result.md" -Raw

# Build compact MR description (under 1000 chars)
$mrDescription = @"
Closes #$issueNumber

## Implementation
$(($result -split "`n" | Select-Object -First 10) -join "`n")

## Testing
✅ All tests pass
✅ Requirements met
"@

# Create MR
glab mr create --title "fix: Feature implementation" --description $mrDescription --target-branch main
```

**Why "Closes #X" is Critical**:
- GitLab detects this keyword and auto-links the issue
- When MR merges → issue automatically closes
- Without it → issue stays open even after code is merged

---

### Step 7: Merge Merge Request (Optional Auto-merge)

```powershell
# Get MR number from current branch
$mrNumber = glab mr view --json iid | ConvertFrom-Json | Select-Object -ExpandProperty iid

# Squash merge (recommended for smaller MRs)
glab mr merge $mrNumber --squash --remove-source-branch

# Other merge options:
# --merge                 - Standard merge commit
# --rebase                - Rebase merge
# --squash                - Squash merge (recommended)
# --remove-source-branch  - Delete branch after merge (equivalent to --delete-branch)
```

**Output**:
```
✓ Merged merge request !3 (fix: Add baseurl to image paths)
   Deleted fix/3-image-paths-baseurl branch
```

---

## GitLab CLI Commands Reference

### Issues

```bash
# Create issue
glab issue create --title "Title" --description "Body" --label "bug"

# List issues
glab issue list --state opened

# View issue
glab issue view 42

# Close issue manually (if not auto-closed by MR)
glab issue close 42

# Reopen issue
glab issue reopen 42
```

### Merge Requests

```bash
# Create MR with auto-link to issue
glab mr create --title "Title" --description "Closes #42

Details..." --target-branch main

# View current branch's MR
glab mr view

# View specific MR
glab mr view 3

# List MRs
glab mr list --state opened

# Merge MR
glab mr merge 3 --squash --remove-source-branch

# Close MR without merge
glab mr close 3

# Approve MR (from a reviewer)
glab mr approve 3
```

### Repository

```bash
# View repo info
glab repo view

# Get current remote URL
git config --get remote.origin.url

# Clone repo
glab repo clone namespace/repo
```

---

## Error Handling

### Error: "No commits yet on this branch"
**Cause**: Pushed empty branch without changes  
**Fix**: Make changes, commit, push again

### Error: "cannot parse 'n' in multiline body"
**Cause**: Multi-line string in PowerShell without proper escaping  
**Fix**: Use proper PowerShell multi-line strings with `@" "@` syntax

### Error: "Review: Can not approve your own merge request"
**Cause**: You created the MR, can't approve it yourself  
**Fix**: This is normal — skip approval or have teammate approve

### Error: "404 Not Found"
**Cause**: Wrong GitLab hostname (self-hosted) or missing permissions  
**Fix**: Add `--hostname your.gitlab.instance` or check project permissions

### Error: "glab: command not found"
**Cause**: GitLab CLI not in system PATH  
**Fix**: Use full path: `& "$env:LOCALAPPDATA\Programs\glab\glab.exe"` or install via `winget install Gitlab.glab`

---

## Integration Pattern for Agents

### When starting an issue:

```
1. Check if GitLab repo:
   - Run: git config --get remote.origin.url
   - If contains 'gitlab.' → offer automation

2. Ask user: "Create GitLab issue for tracking? (yes/no)"

3. If yes:
   - Create GitLab issue with title and description
   - Parse issue number from response URL (issues/\d+)
   - Create branch: <type>/<number>-<description>
   - Create work folder: work/ISSUE-<number>-<description>/
   - Create files: plan.md, result.md
```

### When finishing implementation:

```
1. Commit all changes:
   - Message includes "Resolves #<number>"

2. Push branch to remote:
   - git push origin HEAD

3. Ask user: "Create MR and auto-merge? (yes/no)"

4. If yes:
   - Read work/ISSUE-XXX/result.md for summary
   - Create MR with "Closes #<number>" in description
   - Optionally: glab mr merge --squash --remove-source-branch
```

---

## Best Practices for Agents

### ✅ DO

- **Always check if GitLab repo first** before offering automation
- **Parse issue numbers** from GitLab CLI response URLs
- **Include "Closes #X"** in MR description (not just title)
- **Keep MR descriptions compact** (under 1000 chars)
- **Use squash merge** for cleaner history
- **Delete branch after merge** using `--remove-source-branch`
- **Handle glab command not found** gracefully (try full path)

### ❌ DON'T

- **Never assume glab is in PATH** (always try, then fallback to full path)
- **Don't create MR without "Closes #X"** in description
- **Don't merge without user confirmation** (unless explicitly requested)
- **Don't create issues without user approval**
- **Don't push to main branch** (always use feature branches)

---

## PowerShell Helper Functions

### Check if GitLab repo:

```powershell
function Test-IsGitLabRepo {
    try {
        $remote = git config --get remote.origin.url 2>$null
        return $remote -match 'gitlab\.'
    } catch {
        return $false
    }
}
```

### Get current branch:

```powershell
function Get-CurrentBranch {
    return git branch --show-current
}
```

### Parse issue number from GitLab URL:

```powershell
function Get-IssueNumber {
    param([string]$IssueUrl)
    if ($IssueUrl -match 'issues/(\d+)') {
        return $matches[1]
    }
    return $null
}
```

### Parse MR number from GitLab URL:

```powershell
function Get-MRNumber {
    param([string]$MrUrl)
    if ($MrUrl -match 'merge_requests/(\d+)') {
        return $matches[1]
    }
    return $null
}
```

---

## Complete Automation Example

```powershell
# Step 1: Check if GitLab repo
if (Test-IsGitLabRepo) {
    Write-Host "🤖 GitLab repository detected. Automating workflow..."
    
    # Step 2: Create issue
    $title = "fix: Add new feature"
    $description = "Implementing new feature as requested"
    $issueUrl = glab issue create --title $title --description $description
    $issueNumber = Get-IssueNumber $issueUrl
    
    # Step 3: Create branch
    $branchName = "fix/$issueNumber-add-new-feature"
    git checkout -b $branchName
    
    # Step 4: Create work folder
    $workDir = "work/ISSUE-$($issueNumber.PadLeft(3, '0'))-add-new-feature"
    New-Item -ItemType Directory -Force -Path $workDir
    New-Item -ItemType File -Force -Path "$workDir/plan.md"
    New-Item -ItemType File -Force -Path "$workDir/result.md"
    
    Write-Host "✅ Setup complete. Start implementing in $workDir"
    Write-Host "📝 GitLab Issue: #$issueNumber"
    Write-Host "🌿 Branch: $branchName"
}
```

---

## GitHub CLI vs GitLab CLI Reference

| Action | GitHub CLI (`gh`) | GitLab CLI (`glab`) |
|:-------|:-----------------|:--------------------|
| Auth | `gh auth login` | `glab auth login` |
| Create issue | `gh issue create --body` | `glab issue create --description` |
| View issue | `gh issue view <n>` | `glab issue view <n>` |
| List issues | `gh issue list` | `glab issue list` |
| Close issue | `gh issue close <n>` | `glab issue close <n>` |
| Create PR/MR | `gh pr create --base` | `glab mr create --target-branch` |
| List PRs/MRs | `gh pr list` | `glab mr list` |
| View PR/MR | `gh pr view <n>` | `glab mr view <n>` |
| Merge PR/MR | `gh pr merge <n> --delete-branch` | `glab mr merge <n> --remove-source-branch` |
| List labels | `gh label list` | `glab label list` |
| Clone repo | `gh repo clone` | `glab repo clone` |
| Auto-close keyword | `Fixes #42` in PR body | `Closes #42` in MR description |
| Issue URL pattern | `…/issues/42` | `…/-/issues/42` |
| MR URL pattern | `…/pull/3` | `…/-/merge_requests/3` |