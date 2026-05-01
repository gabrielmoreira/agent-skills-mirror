---
name: repo-structure-conventions
description: Enforce file organization, naming conventions, and app-type-specific project layouts. Use when creating, restructuring, or onboarding a repository.
argument-hint: "[app-type: vscode-extension|node-library|shell-tool|static-site|web-app|python-project|monorepo] [mode: audit|scaffold|remediate]"
user-invocable: true
disable-model-invocation: false
---

# Repo Structure Conventions

## Purpose

Ensure every managed repository has a consistent, navigable, industry-standard file organization. This skill is the **primary owner** for structural layout, naming, and build-artifact isolation.

## When to invoke

- Creating a new repository.
- Restructuring an existing repository.
- Onboarding a repo that lacks clear organization.
- After `repo-onboarding-standards` classifies the app type.

## Scope boundary

### Owns (primary authority)

- Root-level file layout and ordering.
- Directory naming conventions.
- App-type-specific directory structures.
- Build artifact isolation (.gitignore, .vscodeignore, .npmignore).
- CODEOWNERS patterns by project size and structure.

### Delegates (do NOT duplicate)

| Concern | Owner |
|---|---|
| Community health files (README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT) | `repo-profile-governance` |
| Discoverability metadata (description, topics, social preview, homepage) | `repo-profile-governance` |
| GitHub Actions security (SHA pinning, token permissions, OIDC) | `github-actions-security-hardening` |
| Secret hygiene (.env, credentials, artifact leaks) | `secret-exposure-prevention` |
| Documentation content quality and drift detection | `docs-drift-maintenance` |
| Release versioning, tags, and publish integrity | `release-version-integrity` |
| CI/CD workflow design and merge gates | `github-review-merge-admin` |

## Hard constraints

1. No unbounded loops or recursive retries.
2. Maximum one full repository audit per invocation.
3. No silent file creation; produce explicit proposals for review.
4. Never move or rename files without confirming the change won't break imports, CI, or published paths.
5. Prefer the smallest structural change that achieves the convention.

## Modes

- **audit**: Detect structural gaps and deviations. Return findings ranked by severity.
- **scaffold**: Generate the initial directory structure for a new project given an app type.
- **remediate**: Propose minimal file moves/renames to bring an existing repo into compliance.

---

## A) Universal file layout

### Root minimalism principle

A file belongs at the repository root **only** if at least one of these conditions is true:

| Condition | Examples |
|---|---|
| **Tool enforcement** — a tool will not find the file elsewhere | `package.json`, `Cargo.toml`, `go.mod`, `.gitignore` |
| **Platform convention** — GitHub/GitLab renders or processes it from root | `README.md`, `LICENSE`, `CHANGELOG.md`, `CODEOWNERS` |
| **Ecosystem standard name** — the ecosystem's toolchain expects it at root | `tsconfig.json`, `pyproject.toml`, `.editorconfig`, `Makefile` |
| **Primary entry point** — the project has ≤ 3 source files and no `src/` dir | `mem-watchdog.sh`, `install.sh`, `main.py` |

All other files belong in a purpose-named directory (`docs/`, `scripts/`, `test/`, `src/`, `.github/`).

**Audit behavior**: Root files failing this test are flagged at `low` severity (informational). The finding recommends which directory the file should move to, but does not block merges.

**Cross-ecosystem consensus**: Rust (`src/`, `tests/`), Go (`cmd/`, `internal/`, `test/`), Python (`src/<pkg>/`, `tests/`), JS/TS (`src/`, `test/`), .NET (`src/`, `test/`), and the kriasoft Folder-Structure-Conventions standard (2k★, 5.8k forks) all converge on this layout: source and tests in subdirectories, root contains only files that must be there.

Every repository must have this root-level structure (files may be absent if N/A):

```
README.md                  ← required (content owned by repo-profile-governance)
LICENSE                    ← required when distributing
CHANGELOG.md               ← required; Keep a Changelog format
.gitignore                 ← required
.github/
  copilot-instructions.md  ← repo-specific Copilot context
  instructions/            ← stack-specific Copilot rules
  ISSUE_TEMPLATE/          ← issue forms + config.yml
  pull_request_template.md ← PR checklist
  workflows/               ← CI/CD pipelines
  CODEOWNERS               ← ownership mapping
docs/                      ← long-form documentation (architecture, guides, references)
scripts/                   ← build, deploy, and maintenance scripts
test/                      ← test suites (or tests/ — pick one, be consistent)
```

### Root-level file ordering convention

When listing or organizing root files, follow this precedence:
1. Community/metadata: README, LICENSE, CHANGELOG, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT
2. Configuration: .gitignore, .editorconfig, package.json / pyproject.toml / Makefile
3. Entry points: main source files at root only for simple projects
4. Dot-directories: .github/, .vscode/ (if committed)

## B) Naming conventions

| Rule | Convention | Example |
|---|---|---|
| Directories | kebab-case, lowercase, no spaces | `test-fixtures/`, `docs/technical/` |
| Source files | Language convention (camelCase for JS/TS, snake_case for Python/Shell) | `configWriter.js`, `mem_watchdog.sh` |
| Config files | Ecosystem standard name | `package.json`, `tsconfig.json`, `.eslintrc.json` |
| Scripts | kebab-case or snake_case, descriptive verb-noun | `prepare.js`, `docs-integrity-check.sh` |
| Test files | Match source name with `.test.` or `_test.` suffix | `utils.test.js`, `test_watchdog.sh` |
| Documentation | UPPER_SNAKE for community files, kebab-case for guides | `CONTRIBUTING.md`, `system-stability.md` |

### Naming anti-patterns (flag in audit mode)

- Spaces in file or directory names.
- Mixed case in directory names (`Tests/` vs `test/`).
- Generic names without context (`utils/`, `helpers/`, `misc/`).
- Numbered prefixes for ordering (`01-setup/`, `02-config/`).

## C) App-type-specific structures

### VS Code Extension

```
package.json               ← manifest (publisher, contributes, activationEvents)
extension.js (or src/)     ← activation entry point
commands.js, utils.js ...  ← feature modules
lifecycle.js               ← vscode:uninstall hook (plain Node.js)
resources/                 ← bundled non-JS assets (BUILD ARTIFACT — gitignored)
scripts/
  prepare.js               ← vscode:prepublish build step
test/
  unit/                    ← node:test or mocha unit tests
  helpers/                 ← test mocks (e.g., mockVscode.js)
  bench/                   ← benchmarks
  stress/                  ← stress/load tests
.vscodeignore              ← exclude test/, scripts/, .env from .vsix
```

Key rules:
- `resources/` is a build artifact: listed in `.gitignore`, NOT in `.vscodeignore`.
- `test/` is listed in `.vscodeignore` but NOT in `.gitignore`.
- `.env` and `.env.example` must be in BOTH `.gitignore` and `.vscodeignore`.
- `extensionKind: ["ui"]` and `scope: "machine"` in `package.json` for local-only extensions.

### Node Library / CLI Tool

```
src/                       ← source code
dist/ or lib/              ← build output (gitignored)
test/                      ← test suites
bin/                       ← CLI entry points (referenced in package.json "bin")
package.json
tsconfig.json              ← if TypeScript
```

Key rules:
- `dist/` or `lib/` in `.gitignore` but included in npm package via `"files"` in `package.json`.
- Lock file (`package-lock.json`) committed for applications, optional for libraries.
- `engines` field in `package.json` specifies minimum Node.js version.

### Shell Tool / Daemon

```
mem-watchdog.sh            ← main script at root (simple projects)
mem-watchdog.service       ← systemd unit file
install.sh                 ← installer
test-watchdog.sh           ← test suite at root
test-pressure.sh           ← specialized test suites
scripts/                   ← auxiliary scripts (only if >3 scripts)
docs/
  technical/               ← architecture, postmortems
  workflow/                ← process docs, learnings
scratch/                   ← ephemeral test output (gitignored or auto-pruned)
```

Key rules:
- Main scripts live at root when there are ≤3 of them.
- `scratch/` for ephemeral test output — auto-pruned via `tmpfiles.d` or test cleanup.
- No `/tmp` writes from daemon scripts (testable constraint).
- Config files follow XDG: `${XDG_CONFIG_HOME:-$HOME/.config}/<tool>/`.

### Static Site / Web App

```
src/                       ← source (components, pages, styles)
public/                    ← static assets served as-is
dist/ or build/            ← build output (gitignored)
test/ or __tests__/        ← test suites (framework convention)
```

Key rules:
- Build output directory in `.gitignore`.
- Framework config at root (`next.config.js`, `vite.config.ts`, etc.).
- Environment files: `.env.example` committed, `.env` and `.env.local` gitignored.

### Python Project

```
src/<package_name>/        ← source package (src layout preferred)
tests/                     ← test suites
docs/                      ← documentation
pyproject.toml             ← project metadata and build config (preferred over setup.py)
```

Key rules:
- `src/` layout prevents accidental imports from the working directory.
- `__pycache__/`, `*.pyc`, `.eggs/`, `*.egg-info/` in `.gitignore`.
- Virtual environment directory (`venv/`, `.venv/`) in `.gitignore`.

## D) Build artifact isolation

### Ignore file strategy

| File | Purpose | Scope |
|---|---|---|
| `.gitignore` | Exclude from version control | Build outputs, caches, secrets, env files, IDE settings |
| `.vscodeignore` | Exclude from .vsix package | Tests, scripts, dev configs, .env |
| `.npmignore` | Exclude from npm package | Tests, docs, CI configs, .env |
| `"files"` in `package.json` | Allowlist for npm package | Preferred over `.npmignore` for libraries |

### Mandatory .gitignore entries (all projects)

```
# Environment and secrets
.env
.env.local
.env.*.local

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/settings.json      ← if contains user-specific paths
*.code-workspace            ← unless shared intentionally
```

### Audit check: no build artifacts in git history

Flag any committed files matching: `dist/`, `build/`, `node_modules/`, `*.vsix`, `resources/` (for VS Code extensions), `__pycache__/`, `*.pyc`.

## E) CODEOWNERS patterns

### Solo maintainer (1 person)

```
# Single owner for everything
* @username
```

### Small team (2–5 people)

```
# Default
* @org/core-team

# Specialized paths
.github/workflows/ @org/devops
docs/ @org/docs-team
```

### Monorepo

```
# Package-level ownership
/packages/api/ @org/backend
/packages/web/ @org/frontend
/packages/shared/ @org/core-team

# Cross-cutting
.github/ @org/devops
```

---

## Output format (audit mode)

```text
STRUCTURE_AUDIT_REPORT
app_type: <detected or specified>
mode: <audit|scaffold|remediate>

findings:
- id: S1
  severity: <low|medium|high>
  area: <layout|naming|artifact-isolation|codeowners>
  observation: <what exists>
  expected: <what should exist>
  fix: <specific change>

actions:
1) priority: <P1|P2|P3>
   change: <specific file/directory operation>
   rationale: <why>
   risk: <what could break>

decision: <apply|defer|NO_CHANGE>
```

## Stop conditions

Return `NO_CHANGE` when:
- Structure already matches conventions for the detected app type.
- Proposed moves would break published paths, imports, or CI.
- Insufficient context to determine the correct app type.
