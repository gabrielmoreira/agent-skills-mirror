# Step 01 — Scan Project Structure and Detect Tech Stack

**Previous step:** (none)
**Next step:** `step-02-architecture.md`

---

## 1. Top-Level Structure Scan

Read the project root directory listing. Identify and categorize:

**Entry Point Signals:**
- `package.json` / `package-lock.json` / `yarn.lock` → Node.js/TypeScript
- `pyproject.toml` / `setup.py` / `requirements.txt` / `Pipfile` → Python
- `go.mod` / `go.sum` → Go
- `pom.xml` / `build.gradle` / `*.gradle.kts` → Java/Kotlin
- `Cargo.toml` → Rust
- `*.csproj` / `*.sln` → .NET / C#
- `composer.json` → PHP
- `Gemfile` → Ruby

**Framework Signals** (read key manifests):
- Node: check `dependencies` / `devDependencies` in `package.json`
- Python: check `[tool.poetry.dependencies]` or `install_requires`
- Java: check `<dependencies>` in `pom.xml`

**Structure Signals:**
```
Scan for these directories and note presence/absence:
src/          app/          lib/          cmd/
test/         tests/        __tests__/    spec/
docs/         wiki/
.github/      .gitlab/      .circleci/    Jenkinsfile
k8s/          helm/         terraform/    infra/
docker/       Dockerfile    docker-compose.yml
scripts/      tools/        bin/
migrations/   db/
```

---

## 2. Determine Project Shape

Based on the scan, classify the project shape:

| Shape | Signals |
|-------|---------|
| **Monolith** | Single `src/` or `app/` with no sub-package manifests |
| **Modular Monolith** | Single repo, multiple internal packages/modules |
| **Monorepo** | `packages/`, `apps/`, `services/`, or `libs/` directories with sub-manifests |
| **Microservices** | Multiple Dockerfiles, service-specific directories, or API gateway config |
| **Library/SDK** | No server entry point, only exports |
| **CLI Tool** | `cmd/`, `bin/`, or `cli/` structure |
| **Data Pipeline** | DAG definitions, notebook files, ETL scripts |

---

## 3. Read Key Config Files

Read (in this order, stop when context fills up — prioritize top of list):
1. Root manifest (`package.json`, `pyproject.toml`, `pom.xml`, etc.) — version, description, scripts
2. `.env.example` or `config/` — environment variable names (NOT values)
3. `docker-compose.yml` — services, ports, dependencies
4. CI/CD config (`.github/workflows/*.yml` first file, `Jenkinsfile`, etc.)
5. Main entry point file (e.g., `src/index.ts`, `main.py`, `cmd/main.go`, `src/main/java/.../Application.java`)

---

## 4. Identify Key Directories

For each major directory found, write a one-line description of its likely purpose. Be explicit when inferring:

```
src/api/         → API route handlers (inferred from Express/FastAPI patterns)
src/services/    → Business logic layer (inferred from naming + import patterns)
src/models/      → Data models/entities
src/utils/       → Utility functions (confirmed — no domain logic found)
tests/unit/      → Unit tests
tests/integration/ → Integration tests
scripts/migrate/ → Database migration scripts
```

---

## 5. Count and Estimate

Gather rough metrics (use file count commands if terminal is available):

```bash
# File counts by type
find . -name "*.ts" -not -path "*/node_modules/*" | wc -l
find . -name "*.py" -not -path "*/.venv/*" | wc -l
find . -name "*.test.*" -o -name "*.spec.*" | grep -v node_modules | wc -l
```

Report:
```
Project Metrics (approximate):
  Total source files: {n}
  Test files: {n}
  Test coverage signal: {has tests | no tests found}
  Dependencies: {n direct dependencies}
  Age signal: earliest git commit date if available
```

---

## 6. Existing Documentation Audit

Check for existing docs and rate their quality:

| Document | Found? | Quality Signal |
|----------|--------|----------------|
| README.md | ✅/❌ | {Comprehensive / Minimal / Outdated / None} |
| ARCHITECTURE.md | ✅/❌ | ... |
| API docs | ✅/❌ | ... |
| CHANGELOG | ✅/❌ | ... |
| OpenAPI/Swagger spec | ✅/❌ | ... |
| Inline code comments | ✅/❌ | {Dense / Sparse / None} |
| JSDoc/docstrings | ✅/❌ | ... |

Flag: **"Existing docs found — I will verify accuracy against code before including any existing content in new docs."**

---

## 7. Present Scan Summary

```
🔍 Scan Complete — {project_name}
════════════════════════════════════════
Shape:      {Monolith | Monorepo | Microservices | ...}
Language:   {primary language(s)}
Framework:  {detected frameworks}
Runtime:    {Node 20 | Python 3.12 | Go 1.22 | ...}
Test suite: {Jest | pytest | JUnit | none found}
CI/CD:      {GitHub Actions | Jenkins | GitLab CI | none}
Deploy:     {Docker | K8s | Serverless | bare | unclear}

Source files: ~{n}
Test files:   ~{n}
Existing docs: {summary}

Key questions before going deeper:
1. {Any ambiguity found — e.g., "Is this a REST API or RPC? I see both patterns."}
2. {e.g., "There are 2 entry points. Which is the primary application?"}
════════════════════════════════════════
```

⏸️ **STOP** — confirm findings and answer questions before proceeding to architecture step.

---

## 8. Save State

Write to `{project-root}/_superml/relearn-state.yml`:
```yaml
step: "step-01-scan"
status: "complete"
project_shape: "{shape}"
primary_language: "{language}"
framework: "{framework}"
entry_points: ["{list}"]
key_directories: ["{list}"]
existing_docs: "{summary}"
```

Load and follow `./step-02-architecture.md`.
