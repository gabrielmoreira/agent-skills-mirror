---
type: skill
lifecycle: stable
inheritance: inheritable
name: repository-readiness-eval
description: Evaluate a repository's readiness for AI-assisted development across 4 axes: code understanding, dependency restore, build success, and test execution. Use when onboarding to a new repo, assessing CI readiness, or validating that an AI agent can work effectively in a codebase.
tier: standard
applyTo: '**/*repository*,**/*readiness*,**/*eval*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Repository Readiness Evaluation

Systematic 4-axis assessment of whether a repository is ready for productive AI-assisted development — from code comprehension through successful test execution.

## When to Use

- Onboarding to an unfamiliar repository
- Assessing if a codebase is AI-agent-ready
- Validating CI/CD pipeline health
- Pre-engagement quality check before committing to a project
- Measuring improvement after fixing build/test issues

---

## The 4 Axes

| Axis | Question | Score Range |
| ---- | -------- | ----------- |
| **A: Code Understanding** | Can you comprehend the project structure, tech stack, and architecture? | 0–5 |
| **B: Dependency Restore** | Can you install/restore all dependencies successfully? | 0–5 |
| **C: Build Success** | Does the project compile/build without errors? | 0–5 |
| **D: Test Execution** | Do tests run and pass? | 0–5 |

**Total**: 0–20 points → Tier classification (below)

---

## Phase 1: Code Understanding (Axis A)

### Investigation Steps

1. **Read README** — does it explain setup, architecture, and conventions?
2. **Identify tech stack** — languages, frameworks, build system, package manager
3. **Map project structure** — entry points, module boundaries, config files
4. **Find build/run commands** — documented or discoverable from manifests
5. **Identify test framework** — what runs tests, where are they located

### Scoring Rubric

| Score | Criteria |
| ----- | -------- |
| 5 | Clear docs, standard structure, obvious entry points, well-organized |
| 4 | Minor gaps but navigable — missing some docs, non-standard naming |
| 3 | Understandable with effort — sparse docs, complex structure |
| 2 | Confusing — unclear entry points, mixed concerns, minimal docs |
| 1 | Barely comprehensible — no docs, non-standard everything |
| 0 | Cannot determine project purpose or structure |

---

## Phase 2: Dependency Restore (Axis B)

### Investigation Steps

1. **Identify package manager** — npm, pip, dotnet, cargo, maven, etc.
2. **Run restore command** — `npm install`, `pip install -r requirements.txt`, `dotnet restore`, etc.
3. **Check for lock files** — `package-lock.json`, `poetry.lock`, `Cargo.lock`
4. **Identify private registries** — `.npmrc`, `nuget.config`, `pip.conf`
5. **Record failures** — classify per taxonomy below

### Common Restore Commands

| Ecosystem | Command |
| --------- | ------- |
| Node.js | `npm install` or `yarn install` or `pnpm install` |
| Python | `pip install -r requirements.txt` or `poetry install` |
| .NET | `dotnet restore` |
| Go | `go mod download` |
| Rust | `cargo fetch` |
| Java | `mvn dependency:resolve` or `gradle dependencies` |

### Scoring Rubric

| Score | Criteria |
| ----- | -------- |
| 5 | All dependencies restore cleanly on first attempt |
| 4 | Minor warnings but functional — deprecated packages, peer dep warnings |
| 3 | Partial success — some packages fail but core works |
| 2 | Significant failures — private registry auth, version conflicts |
| 1 | Most dependencies fail — broken lock file, missing registry |
| 0 | Cannot restore any dependencies |

---

## Phase 3: Build Success (Axis C)

### Investigation Steps

1. **Find build command** — from README, `package.json` scripts, `Makefile`, etc.
2. **Run build** — `npm run build`, `dotnet build`, `cargo build`, `make`, etc.
3. **Capture output** — record warnings and errors
4. **Classify failures** — per taxonomy below
5. **Attempt fixes** — if simple (missing env var, config), fix and retry

### Common Build Commands

| Ecosystem | Command |
| --------- | ------- |
| Node.js/TS | `npm run build` or `tsc` |
| .NET | `dotnet build` |
| Go | `go build ./...` |
| Rust | `cargo build` |
| Python | `python -m build` or `python setup.py build` |
| Java | `mvn compile` or `gradle build` |

### Scoring Rubric

| Score | Criteria |
| ----- | -------- |
| 5 | Clean build, zero warnings |
| 4 | Builds successfully with minor warnings |
| 3 | Builds with significant warnings or non-critical errors suppressed |
| 2 | Build fails but fixable (missing config, env vars, minor code issues) |
| 1 | Build fails with deep issues (incompatible deps, missing system libs) |
| 0 | Cannot determine how to build, or catastrophic failure |

---

## Phase 4: Test Execution (Axis D)

### Investigation Steps

1. **Find test command** — `npm test`, `dotnet test`, `pytest`, `cargo test`
2. **Run tests** — capture pass/fail/skip counts
3. **Classify failures** — infrastructure vs logic vs flaky
4. **Calculate pass rate** — passing / (passing + failing)
5. **Note coverage** if available

### Common Test Commands

| Ecosystem | Command |
| --------- | ------- |
| Node.js | `npm test` or `npx jest` or `npx vitest` |
| .NET | `dotnet test` |
| Python | `pytest` or `python -m unittest` |
| Go | `go test ./...` |
| Rust | `cargo test` |
| Java | `mvn test` or `gradle test` |

### Scoring Rubric

| Score | Criteria |
| ----- | -------- |
| 5 | All tests pass, good coverage, fast execution |
| 4 | >95% pass rate, minor flaky tests |
| 3 | >80% pass rate, some infrastructure failures |
| 2 | 50–80% pass rate, significant issues |
| 1 | <50% pass rate or tests barely run |
| 0 | No tests exist, or test framework cannot execute |

---

## Failure Taxonomy

Tag every failure encountered during evaluation:

| Tag | Definition | Example |
| --- | ---------- | ------- |
| `MISSING_TOOL` | Required tool/runtime not installed | Node 18 needed, only 16 available |
| `AUTH_REQUIRED` | Credentials needed for private resource | Private npm registry, Azure artifact feed |
| `ENV_CONFIG` | Missing environment variable or config file | `.env` not present, `appsettings.local.json` missing |
| `VERSION_CONFLICT` | Dependency version incompatibility | Peer dep mismatch, lockfile drift |
| `PLATFORM_SPECIFIC` | Works on one OS but not another | Linux paths on Windows, missing system lib |
| `FLAKY_TEST` | Test passes/fails non-deterministically | Timing-dependent, external service dependency |

---

## Scoring & Tier Classification

### Compute Total Score

```text
Total = A + B + C + D  (range: 0–20)
```

### Tier Mapping

| Tier | Score | Interpretation |
| ---- | ----- | -------------- |
| **Excellent** | 18–20 | Ready for immediate productive work |
| **Good** | 14–17 | Minor friction, workable with small fixes |
| **Fair** | 10–13 | Significant setup needed before productive work |
| **Poor** | 6–9 | Major blockers — investment required before engagement |
| **Critical** | 0–5 | Not ready — fundamental issues must be resolved first |

---

## Output Artifact

```markdown
# Repository Readiness Report

**Repository:** <name>
**Date:** <date>
**Evaluator:** <who/what>

## Summary

| Axis | Score | Notes |
| ---- | ----- | ----- |
| A: Code Understanding | X/5 | <brief> |
| B: Dependency Restore | X/5 | <brief> |
| C: Build Success | X/5 | <brief> |
| D: Test Execution | X/5 | <brief> |
| **Total** | **X/20** | **Tier: <tier>** |

## Failures Encountered

| # | Phase | Tag | Description | Resolution |
| - | ----- | --- | ----------- | ---------- |
| 1 | B | AUTH_REQUIRED | Private npm registry needs token | Set NPM_TOKEN env var |
| 2 | C | ENV_CONFIG | Missing DATABASE_URL | Added to .env from .env.example |

## Recommendations

### Immediate (blocks productive work)
1. <fix>

### Short-term (improves experience)
1. <improvement>

### Nice-to-have
1. <suggestion>
```

---

## Intervention Tracking

When you fix issues during evaluation, track them:

| Intervention | Classification | Impact on Score |
| ------------ | -------------- | --------------- |
| Filled missing env var from example | Config fix | Score reflects post-fix state |
| Installed missing tool | Setup fix | Score reflects post-fix state |
| Fixed code to make build pass | Code change | **Deduct 1 point from that axis** |
| Skipped failing tests | Workaround | Score reflects skip (not pass) |

**Autonomy penalty**: If you had to modify source code (not config) to achieve a passing build/test, deduct 1 point from that axis. The repo should work without code changes for a new developer.

---

## Troubleshooting Common Blockers

| Symptom | Likely Cause | Resolution |
| ------- | ------------ | ---------- |
| `ENOENT` on install | Wrong working directory | Check for monorepo, find correct root |
| `401 Unauthorized` on restore | Private registry | Check `.npmrc`, `nuget.config`, set auth token |
| `Cannot find module` after install | Missing build step | Run build before test |
| Tests pass locally but timeout | External service dependency | Mock or skip integration tests |
| Build warns "deprecated" | Old dependencies | Usually safe to ignore for eval |
| `ENOMEM` during build | Large project, low memory | Increase memory or build in parts |

---

## Integration with Other Skills

| Skill | Relationship |
| ----- | ------------ |
| `architecture-audit` | Use readiness score to prioritize audit targets |
| `tech-debt-discovery` | Low readiness scores indicate tech debt |
| `testing-strategies` | Axis D failures feed test improvement planning |
| `bootstrap-learning` | Phase 1 aligns with bootstrap's Orient step |
