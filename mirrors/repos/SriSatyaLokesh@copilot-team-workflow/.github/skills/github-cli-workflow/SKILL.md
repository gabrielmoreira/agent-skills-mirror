---
name: github-cli-workflow
description: Complete GitHub CLI and Git workflow knowledge for automated issue tracking, branch management, and PR creation. Use when handles GitHub-specific operations like creating issues, PRs, or managing branches with gh.
---

# GitHub CLI Workflow

## Overview
Provides complete GitHub CLI and Git workflow knowledge for automated issue tracking, branch management, and PR creation.

## GitHub Message Size Limits & Conventions

**Critical**: GitHub has strict character limits. Keep messages compact.

| Field | Max Chars | Convention | Example |
|-------|-----------|-----------|---------|
| Issue title | 255 | Keep under 60 | `bug: Post completion not saving` |
| Issue body | ~64KB | Keep under 2000 | Use bullet lists, minimal formatting |
| PR title | 255 | Keep under 60 | `fix: Reading time parsing error` |
| PR body | ~64KB | Keep under 1000 | Compact: `Fixes #42. Root cause: X. Fix: Y.` |
| Commit msg subject | 72 | Keep under 50 (conventional) | `fix: Correct filter in post layout` |
| Commit msg body | 72 chars per line | Bullet format w/ blank lines | Use `-` for bullets, 2 blank lines between |

**Format Guidelines**:
- Issue/PR titles: `<type>: <what> <why if critical>`
- Issue body: Start with 1-2 sentences, then bullet points
- PR body: Start with `Fixes #X`, then bullets (max 500 chars)
- Commits: Subject 50 chars max, body bullets with blank lines

---

## GitHub CLI Setup

### Installation & Verification

```powershell
# Try simple command first
gh --version

# If that fails, GitHub CLI may not be in PATH. Use full path:
& "C:\Program Files\GitHub CLI\gh.exe" --version

# Verify installation path exists
Test-Path "C:\Program Files\GitHub CLI\gh.exe"  # Should return True
```

### Authentication

```powershell
# Try simple command first
gh auth login

# If not working, use full path:
& "C:\Program Files\GitHub CLI\gh.exe" auth login

# Check authentication status (try gh first, then full path if needed)
gh auth status
# OR: & "C:\Program Files\GitHub CLI\gh.exe" auth status

# Refresh to update scopes
gh auth refresh -s read:project
# OR: & "C:\Program Files\GitHub CLI\gh.exe" auth refresh -s read:project
```

### Common Auth Issues

| Issue | Solution |
|-------|----------|
| `gh: command not found` | Use full path: `& "C:\Program Files\GitHub CLI\gh.exe"` |
| `authentication token is missing required scopes [read:project]` | Run: `gh auth refresh -s read:project` (or with full path) |
| `Review: Can not approve your own pull request` | This is normal - you can't approve your own PR |
| `permission denied` | Check: `gh auth status` (must show authenticated) |

---

## Detecting GitHub Repository

Before offering GitHub CLI automation, **always check if this is a GitHub repo**:

```powershell
# Check if git repo exists
git rev-parse --git-dir 2>$null
if ($LASTEXITCODE -eq 0) {
    # Check if remote is GitHub
    $remote = git config --get remote.origin.url
    if ($remote -match 'github\.com') {
        Write-Host "✅ GitHub repository detected"
        # Offer GitHub CLI automation
    } else {
        Write-Host "ℹ️ Git repo but not GitHub - manual workflow"
    }
} else {
    Write-Host "ℹ️ Not a git repository - skipping GitHub automation"
}
```

**When to ask**:
- After creating issue doc
- Before starting implementation
- When user says `/finish-branch`

**What to offer**:
```
🤖 This is a GitHub repository. I can:
1. Create a GitHub issue for tracking
2. Create a feature branch automatically
3. Create and merge PR when complete

Would you like me to automate this? (yes/no)
```

---

## Complete 10-Step Git Workflow

### Step 1: Create GitHub Issue

**Purpose**: Track the work and get an issue number for branching

```powershell
# Try simple command first
gh issue create --title "fix: Image paths missing baseurl" `
  --body "Image paths need baseurl prefix for GitHub Pages"

# If 'gh' command not found, use full path:
& "C:\Program Files\GitHub CLI\gh.exe" issue create --title "fix: Image paths missing baseurl" `
  --body "Image paths need baseurl prefix for GitHub Pages"

# Issue with labels (try gh first)
gh issue create --title "fix: Something broken" `
  --body "Description here" `
  --label bug,enhancement

# ⚠️ Note: If any gh command fails with 'command not found',
# replace 'gh' with '& "C:\Program Files\GitHub CLI\gh.exe"' throughout
```

**Output**: Returns issue number (e.g., `https://github.com/owner/repo/issues/42`)

**Parse issue number**:
```powershell
$issueUrl = gh issue create --title "Title" --body "Body"
if ($issueUrl -match '#(\d+)') {
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
# fix/    - Bug fixes
# feature/ - New features
# docs/   - Documentation
# refactor/ - Code refactoring
# style/  - CSS/styling changes
# test/   - Tests
# chore/  - Dependencies, build config
```

**Output**: `Switched to a new branch 'fix/42-image-paths-baseurl'`

**Automated branch creation from issue**:
```powershell
# Extract issue info
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
- Images now load on GitHub Pages

Resolves #42"

# Or shorter
git commit -m "fix: Add baseurl to image paths (Resolves #42)"

# Keywords that auto-close issues:
# - Fixes #42
# - Resolves #42
# - Closes #42
# - Fixed #42
```

**Automated commit**:
```powershell
$issueNumber = 42
$commitMessage = @"
fix: Add baseurl to image paths

- Updated all placeholder.png paths
- Fixed off.jpg fallbacks
- Images now load on GitHub Pages

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
# Check if branch exists on remote
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

### Step 6: Create Pull Request with "Fixes #X"

**⚠️ CRITICAL**: PR body MUST start with `Fixes #<issue-number>` for auto-closure

```powershell
# Try simple command first
gh pr create `
  --title "fix: Add baseurl prefix to all image paths" `
  --body "Fixes #42

## Changes
- Updated all placeholder.png paths in home.html
- Fixed off.jpg fallback images
- Images now resolve correctly on GitHub Pages

## Testing
✅ Local build passes
✅ No console errors" `
  --base main

# If 'gh' not found, use full path:
& "C:\Program Files\GitHub CLI\gh.exe" pr create `
  --title "fix: Add baseurl prefix to all image paths" `
  --body "Fixes #42

## Changes
- Updated all placeholder.png paths
- Testing passed" `
  --base main

# ⚠️ MUST include "Fixes #42" or issues won't auto-close
```

**Automated PR creation from work folder**:
```powershell
$issueNumber = 42
$workDir = "work/ISSUE-042-feature-name"

# Read plan.md and result.md
$plan = Get-Content "$workDir/plan.md" -Raw
$result = Get-Content "$workDir/result.md" -Raw

# Extract title from plan
$title = "fix: Feature implementation"  # Parse from plan

# Build compact PR body (under 1000 chars)
$prBody = @"
Fixes #$issueNumber

## Implementation
$(($result -split "`n" | Select-Object -First 10) -join "`n")

## Testing
✅ All tests pass
✅ Requirements met
"@

# Create PR
gh pr create --title $title --body $prBody --base main
```

**Why "Fixes #X" is Critical**:
- GitHub detects this keyword and auto-links issue
- When PR merges → issue automatically closes
- Without it → issue stays open even after code is merged

---

### Step 7: Merge Pull Request (Optional Auto-merge)

```powershell
# Get PR number from current branch
$prNumber = gh pr view --json number -q .number

# Squash merge (recommended for smaller PRs)
gh pr merge $prNumber --squash --delete-branch

# Auto-merge when checks pass (if configured)
gh pr merge $prNumber --squash --delete-branch --auto

# Other merge options:
# --merge     - Standard merge commit
# --rebase    - Rebase merge
# --squash    - Squash merge (recommended)
```

**Output**:
```
✓ Merged pull request #3 (fix: Add baseurl to image paths)
   Commit: 38ba60e
   Deleted fix/3-image-paths-baseurl branch
```

---

## GitHub CLI Commands Reference

### Issues

```bash
# Create issue
gh issue create --title "Title" --body "Body" --label bug

# List issues
gh issue list --state open

# View issue
gh issue view 42

# Close issue manually (if not auto-closed by PR)
gh issue close 42 --comment "Fixed in PR #3"

# Reopen issue
gh issue reopen 42
```

### Pull Requests

```bash
# Create PR with auto-link to issue
gh pr create --title "Title" --body "Fixes #42

Details..." --base main

# View current PR
gh pr view

# View specific PR
gh pr view 3

# List PRs
gh pr list --state open

# Merge PR
gh pr merge 3 --squash --delete-branch

# Close PR without merge
gh pr close 3

# Check PR status
gh pr status
```

### Repository

```bash
# View repo info
gh repo view

# Get current remote URL
git config --get remote.origin.url

# Clone repo with SSH
gh repo clone owner/repo
```

---

## Error Handling

### Error: "No commits yet on this branch"
**Cause**: Pushed empty branch without changes  
**Fix**: Make changes, commit, push again

### Error: "cannot parse 'n' in multiline body"
**Cause**: Multi-line string in PowerShell without proper escaping  
**Fix**: Use proper PowerShell multi-line strings with @" "@ syntax

### Error: "Review: Can not approve your own pull request"
**Cause**: You created the PR, can't approve it yourself  
**Fix**: This is normal - skip approval or have teammate approve

### Error: "authentication token is missing required scopes"
**Cause**: GitHub CLI authenticated but missing project scopes  
**Fix**: Run `gh auth refresh -s read:project`

### Error: "gh: command not found"
**Cause**: GitHub CLI not in system PATH  
**Fix**: Use full path: `& "C:\Program Files\GitHub CLI\gh.exe"`

---

## Integration Pattern for Agents

### When starting an issue:

```
1. Check if GitHub repo:
   - Run: git config --get remote.origin.url
   - If contains 'github.com' → offer automation

2. Ask user: "Create GitHub issue for tracking? (yes/no)"

3. If yes:
   - Create GitHub issue with title and description
   - Parse issue number from response
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

3. Ask user: "Create PR and auto-merge? (yes/no)"

4. If yes:
   - Read work/ISSUE-XXX/result.md for summary
   - Create PR with "Fixes #<number>" in body
   - Optionally: gh pr merge --squash --delete-branch --auto
```

---

## Best Practices for Agents

### ✅ DO

- **Always check if GitHub repo first** before offering automation
- **Parse issue numbers** from GitHub CLI responses
- **Include "Fixes #X"** in PR body (not just title)
- **Keep PR bodies compact** (under 1000 chars)
- **Use squash merge** for cleaner history
- **Delete branch after merge** automatically
- **Handle gh command not found** gracefully (try full path)

### ❌ DON'T

- **Never assume GitHub CLI is in PATH** (always try, then fallback to full path)
- **Don't create PR without "Fixes #X"** in body
- **Don't merge without user confirmation** (unless explicitly requested)
- **Don't create issues without user approval**
- **Don't push to main branch** (always use feature branches)

---

## PowerShell Helper Functions

### Check if GitHub repo:

```powershell
function Test-IsGitHubRepo {
    try {
        $remote = git config --get remote.origin.url 2>$null
        return $remote -match 'github\.com'
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

### Parse issue number from URL:

```powershell
function Get-IssueNumber {
    param([string]$IssueUrl)
    if ($IssueUrl -match '#(\d+)') {
        return $matches[1]
    }
    return $null
}
```

---

## Complete Automation Example

```powershell
# Step 1: Check if GitHub repo
if (Test-IsGitHubRepo) {
    Write-Host "🤖 GitHub repository detected. Automating workflow..."
    
    # Step 2: Create issue
    $title = "fix: Add new feature"
    $body = "Implementing new feature as requested"
    $issueUrl = gh issue create --title $title --body $body
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
    Write-Host "📝 GitHub Issue: #$issueNumber"
    Write-Host "🌿 Branch: $branchName"
}
```