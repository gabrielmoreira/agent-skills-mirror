---
name: git-hooks-automation
description: "Sets up versioned Git hooks with Husky + lint-staged, the Python pre-commit framework, or core.hooksPath: pre-commit lint/format, commitlint, pre-push tests. Use when the user mentions pre-commit, commit-msg, Husky, lint-staged, commitlint, or githooks. Not for day-to-day git commit/branch/rebase/PR (git-workflow) or CI pipeline YAML unrelated to local hooks."
version: 1.0.1
risk: safe
source: community
date_added: "2026-03-07"
---

# Git Hooks Automation

Automate code quality enforcement at the Git level. Set up hooks that lint, format, test, and validate before commits and pushes ever reach your CI pipeline — catching issues in seconds instead of minutes.

## When to Use

- User asks to "set up git hooks" or "add pre-commit hooks"
- Configuring Husky, lint-staged, or the pre-commit framework
- Enforcing commit message conventions (Conventional Commits, commitlint)
- Automating linting, formatting, or type-checking before commits
- Setting up pre-push hooks for test runners
- Migrating from Husky v4 to v9+ or adopting hooks from scratch
- User mentions "pre-commit", "commit-msg", "pre-push", "lint-staged", or "githooks"

## Prerequisites

- Git installed and available on PATH (`git --version` to verify)
- For Husky + lint-staged: Node.js 18+ and npm (`node --version`, `npm --version`)
- For pre-commit framework: Python 3.8+ (`python --version`)
- An existing Git repository (`git init` already run) or willingness to initialize one
- **Windows host (primary):** PowerShell is the default shell. Use `npx` commands directly in PowerShell. For shell-based hook scripts, ensure Git Bash is installed (bundled with Git for Windows). Line endings: configure `.gitattributes` with `* text=auto` to avoid CRLF issues in hook scripts.

## Procedure

### 1. Understand Git Hook Types

Git hooks are scripts that run automatically at specific points in the Git workflow. They live in `.git/hooks/` and are not version-controlled by default — which is why tools like Husky exist.

| Hook | Fires When | Common Use |
|---|---|---|
| `pre-commit` | Before commit is created | Lint, format, type-check staged files |
| `prepare-commit-msg` | After default msg, before editor | Auto-populate commit templates |
| `commit-msg` | After user writes commit message | Enforce commit message format |
| `post-commit` | After commit is created | Notifications, logging |
| `pre-push` | Before push to remote | Run tests, check branch policies |
| `pre-rebase` | Before rebase starts | Prevent rebase on protected branches |
| `post-merge` | After merge completes | Install deps, run migrations |
| `post-checkout` | After checkout/switch | Install deps, rebuild assets |

### 2. Choose Your Approach

| Approach | Best For | Language |
|---|---|---|
| Husky + lint-staged | JavaScript/TypeScript projects | Node.js |
| pre-commit framework | Python or polyglot projects | Any |
| Custom shell hooks + `core.hooksPath` | No Node/Python, or full control | Any |

### 3. Husky + lint-staged (Node.js Projects)

The modern standard for JavaScript/TypeScript projects. Husky manages Git hooks; lint-staged runs commands only on staged files for speed.

#### 3a. Install and Initialize (Husky v9+)

```bash
# Install
npm install --save-dev husky lint-staged

# Initialize Husky (creates .husky/ directory)
npx husky init

# The init command creates a pre-commit hook — edit it:
echo "npx lint-staged" > .husky/pre-commit
```

> **Windows (PowerShell):** The `echo` command above works in Git Bash. In PowerShell, use:
> ```powershell
> Set-Content -Path .husky\pre-commit -Value "npx lint-staged" -NoNewline
> ```
> Or simply open `.husky\pre-commit` in your editor and type the command.

#### 3b. Configure lint-staged in `package.json`

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix --max-warnings=0",
      "prettier --write"
    ],
    "*.{css,scss}": [
      "prettier --write",
      "stylelint --fix"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ]
  }
}
```

#### 3c. Add Commit Message Linting with commitlint

```bash
# Install commitlint
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# Create commitlint config
cat > commitlint.config.js << 'EOF'
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'build', 'ci', 'chore', 'revert'
    ]],
    'subject-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100]
  }
};
EOF

# Add commit-msg hook
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg
```

> **Windows (PowerShell):** Use `Set-Content` for the commit-msg hook:
> ```powershell
> Set-Content -Path .husky\commit-msg -Value "npx --no -- commitlint --edit `$1" -NoNewline
> ```

#### 3d. Add Pre-Push Hook

```bash
# Run tests before pushing
echo "npm test" > .husky/pre-push
```

#### 3e. Verify Directory Structure

```
project/
├── .husky/
│   ├── pre-commit        # npx lint-staged
│   ├── commit-msg        # npx --no -- commitlint --edit $1
│   └── pre-push          # npm test
├── commitlint.config.js
├── package.json          # lint-staged config here
└── ...
```

### 4. pre-commit Framework (Python / Polyglot)

Language-agnostic framework that works with any project. Hooks are defined in YAML and run in isolated environments.

#### 4a. Install and Create Config

```bash
# Install (Python required)
pip install pre-commit

# Create config
cat > .pre-commit-config.yaml << 'EOF'
repos:
  # Built-in checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key

  # Python formatting
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black

  # Python linting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: ['--fix']
      - id: ruff-format

  # Shell script linting
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
      - id: shellcheck

  # Commit message format
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.2.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
EOF
```

#### 4b. Install Hooks and Run First Check

```bash
# Install hooks into .git/hooks/
pre-commit install
pre-commit install --hook-type commit-msg

# Run against all files (first time)
pre-commit run --all-files
```

#### 4c. Key Commands Reference

```bash
pre-commit install              # Install hooks
pre-commit run --all-files      # Run on everything (CI or first setup)
pre-commit autoupdate           # Update hook versions
pre-commit run <hook-id>        # Run a specific hook
pre-commit clean                # Clear cached environments
```

### 5. Custom Hook Scripts (Any Language)

For projects not using Node or Python, write hooks directly in shell and share them via `core.hooksPath`.

#### 5a. Create a Portable Pre-Commit Hook

Create `.githooks/pre-commit`:

```sh
#!/bin/sh
# .githooks/pre-commit — Team-shared hooks directory
set -e

echo "=== Pre-Commit Checks ==="

# 1. Prevent commits to main/master
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "detached")
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "❌ Direct commits to $BRANCH are not allowed. Use a feature branch."
  exit 1
fi

# 2. Check for debugging artifacts
if git diff --cached --diff-filter=ACM | grep -nE '(console\.log|debugger|binding\.pry|import pdb)' > /dev/null 2>&1; then
  echo "⚠️  Debug statements found in staged files:"
  git diff --cached --diff-filter=ACM | grep -nE '(console\.log|debugger|binding\.pry|import pdb)'
  echo "Remove them or use git commit --no-verify to bypass."
  exit 1
fi

# 3. Check for large files (>1MB)
LARGE_FILES=$(git diff --cached --name-only --diff-filter=ACM | while read f; do
  size=$(wc -c < "$f" 2>/dev/null || echo 0)
  if [ "$size" -gt 1048576 ]; then echo "$f ($((size/1024))KB)"; fi
done)
if [ -n "$LARGE_FILES" ]; then
  echo "❌ Large files detected:"
  echo "$LARGE_FILES"
  exit 1
fi

# 4. Check for secrets patterns
if git diff --cached --diff-filter=ACM | grep -nEi '(AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{48}|github_pat_[A-Za-z0-9_]{20,}|password\s*=\s*["\x27][^"\x27]+["\x27])' > /dev/null 2>&1; then
  echo "🚨 Potential secrets detected in staged changes! Review before committing."
  exit 1
fi

echo "✅ All pre-commit checks passed"
```

#### 5b. Share Custom Hooks via `core.hooksPath`

```bash
# In your repo, set a shared hooks directory
git config core.hooksPath .githooks

# Add to project setup docs or Makefile
# Makefile
setup:
	git config core.hooksPath .githooks
	chmod +x .githooks/*
```

> **Windows (PowerShell):** `chmod` is not available in PowerShell. Use Git Bash for the `chmod +x` step, or rely on `core.hooksPath` which does not require the executable bit on Windows.

### 6. CI Integration

Hooks are a first line of defense, but CI is the source of truth.

#### 6a. Run pre-commit in CI (GitHub Actions)

```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: pre-commit/action@v3.0.1
```

#### 6b. Run lint-staged Validation in CI

```yaml
# Validate that lint-staged would pass (catch bypassed hooks)
name: Lint Check
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx eslint . --max-warnings=0
      - run: npx prettier --check .
```

### 7. Migration: Husky v4 → v9+

```bash
# 1. Remove old Husky
npm uninstall husky
rm -rf .husky

# 2. Remove old config from package.json
# Delete "husky": { "hooks": { ... } } section

# 3. Install fresh
npm install --save-dev husky
npx husky init

# 4. Recreate hooks
echo "npx lint-staged" > .husky/pre-commit
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg

# 5. Clean up — old Husky used package.json config,
#    new Husky uses .husky/ directory with plain scripts
```

### 8. Gradual Adoption Strategy

For existing projects, adopt hooks incrementally to reduce team friction:

1. **Week 1:** Start with formatting only — `{ "*.{js,ts}": ["prettier --write"] }`
2. **Week 2-3:** Add linting — `{ "*.{js,ts}": ["eslint --fix", "prettier --write"] }`
3. **Week 4:** Add commit message linting with commitlint
4. **Week 5+:** Add pre-push test runner

## Pitfalls

### Hooks Not Running

| Symptom | Cause | Fix |
|---|---|---|
| Hooks silently skipped | Not installed in `.git/hooks/` | Run `npx husky init` or `pre-commit install` |
| "Permission denied" | Hook file not executable | `chmod +x .husky/pre-commit` (Git Bash on Windows) |
| Hooks run but wrong ones | Stale hooks from old setup | Delete `.git/hooks/` contents, reinstall |
| Works locally, fails in CI | Different Node/Python versions | Pin versions in CI config |

### Performance Issues

```json
// ❌ Slow: runs on ALL files every commit
{
  "scripts": {
    "precommit": "eslint src/ && prettier --write src/"
  }
}

// ✅ Fast: lint-staged runs ONLY on staged files
{
  "lint-staged": {
    "*.{js,ts}": ["eslint --fix", "prettier --write"]
  }
}
```

### Bypassing Hooks (When Needed)

```bash
# Skip all hooks for a single commit
git commit --no-verify -m "wip: quick save"

# Skip pre-push only
git push --no-verify

# Skip specific pre-commit hooks (pre-commit framework only)
SKIP=eslint git commit -m "fix: update config"
```

> **Warning:** Bypassing hooks should be rare. If your team frequently bypasses, the hooks are too slow or too strict — fix the hooks, not the workflow.

### Windows-Specific Pitfalls

- **CRLF line endings:** Hook scripts with CRLF endings fail silently on some Git versions. Add `* text=auto` to `.gitattributes` and run `git add --renormalize .`
- **PowerShell vs Git Bash:** Husky hooks execute via Git Bash, not PowerShell. Shell scripts in `.husky/` must use POSIX syntax, not PowerShell cmdlets.
- **`$1` in commit-msg:** In PowerShell, backtick-escape the dollar sign when writing the file: `` `$1 ``. In Git Bash, use `\$1`.

### Key Principles

- **Staged files only** — Never lint the entire codebase on every commit
- **Auto-fix when possible** — `--fix` flags reduce developer friction
- **Fast hooks** — Pre-commit should complete in < 5 seconds
- **Fail loud** — Clear error messages with actionable fixes
- **Team-shared** — Use Husky or `core.hooksPath` so hooks are version-controlled
- **CI as backup** — Hooks are convenience; CI is the enforcer
- **Gradual adoption** — Start with formatting, add linting, then testing

## Verification

### Verify Husky + lint-staged Setup

```bash
# 1. Confirm .husky directory exists with hooks
ls -la .husky/
# Expected: pre-commit, commit-msg, pre-push files present

# 2. Confirm lint-staged config in package.json
cat package.json | grep -A 10 "lint-staged"
# Expected: JSON block with file glob patterns and commands

# 3. Test pre-commit hook by making a trivial change
echo "// test" >> src/index.js
git add src/index.js
git commit -m "test: verify hooks"
# Expected: lint-staged runs, eslint/prettier execute on staged files

# 4. Test commit-msg hook
git commit -m "bad message format" --allow-empty
# Expected: commitlint rejects with "type-enum" error

git commit -m "feat: valid conventional commit" --allow-empty
# Expected: commit succeeds
```

### Verify pre-commit Framework Setup

```bash
# 1. Confirm hooks are installed
pre-commit install
# Expected: "pre-commit installed at .git/hooks/pre-commit"

# 2. Run all hooks against all files
pre-commit run --all-files
# Expected: each hook reports "Passed" or "Failed"

# 3. Test commit-msg hook
pre-commit install --hook-type commit-msg
git commit -m "bad message" --allow-empty
# Expected: conventional-pre-commit rejects

git commit -m "fix: valid message" --allow-empty
# Expected: commit succeeds
```

### Verify Custom core.hooksPath Setup

```bash
# 1. Confirm hooksPath is set
git config core.hooksPath
# Expected: .githooks

# 2. Confirm hook files are executable (Git Bash)
ls -la .githooks/
# Expected: -rwxr-xr-x for each hook file

# 3. Test the hook
git commit --allow-empty -m "test: verify custom hooks"
# Expected: "=== Pre-Commit Checks ===" output, then "✅ All pre-commit checks passed"
```

## Related Skills

- `codebase-audit-pre-push` — Deep audit before GitHub push
- `verification-before-completion` — Verification before claiming work is done
- `bash-pro` — Advanced shell scripting for custom hooks
- `github-actions-templates` — CI/CD workflow templates

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
