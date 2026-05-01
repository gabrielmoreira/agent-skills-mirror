# Step 04 — Identify Conventions, Patterns, and Health Signals

**Previous step:** `step-03-data-api.md`
**Next step:** `step-05-document.md`

---

## 1. Coding Conventions

Read a representative sample of source files (3–5 from different areas). Document observed conventions:

### Naming Conventions

```
Variables/Functions: {camelCase | snake_case | PascalCase}
Classes: {PascalCase}
Files: {kebab-case | camelCase | snake_case}
Constants: {UPPER_SNAKE | camelCase}
Database tables/columns: {snake_case | camelCase}
API endpoints: {kebab-case | camelCase | snake_case}
Test files: {*.test.ts | *.spec.ts | test_*.py | *_test.go}
```

### Error Handling Pattern

Describe how errors are handled:

```
Error pattern: {Exceptions thrown and caught at controller | Result types | Error first callbacks | ...}
  Service layer: throws domain exceptions (UserNotFoundError, ValidationError)
  Controller layer: catches exceptions, maps to HTTP status codes
  Unhandled errors: caught by global error middleware (src/middleware/errorHandler.ts)
  Error response format: { message: string, code: string, details?: object }
```

### Dependency Injection / Inversion of Control

```
DI pattern: {NestJS DI | InversifyJS | no DI (direct imports) | Spring IoC | Python DI library | ...}
```

### Logging

```
Logger: {Winston | Pino | console.log (none) | Loguru | log4j | zerolog}
  Format: {JSON structured | plain text}
  Levels used: {debug | info | warn | error}
  Request logging: {morgan | yes via middleware | no}
```

---

## 2. Testing Patterns

Read `package.json` test scripts or equivalent. Spot-read 2–3 test files.

```
Test framework: {Jest | Vitest | pytest | JUnit | Go testing | Mocha | ...}
Test types present:
  Unit tests: ✅/❌ (path: {tests/unit/})
  Integration tests: ✅/❌ (path: {tests/integration/})
  E2E tests: ✅/❌ (path: {tests/e2e/})
  Contract tests: ✅/❌

Mocking strategy: {jest.mock() | pytest fixtures | test doubles | database in-memory}
Coverage configured: ✅/❌ (target: {n}% if configured)
Test command: {npm test | pytest | go test ./... | mvn test}
```

---

## 3. Technical Debt Signals

Scan for debt markers. Terminal search if available:

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|TEMP\|@deprecated\|WORKAROUND" \
  --include="*.ts" --include="*.js" --include="*.py" --include="*.go" \
  --exclude-dir=node_modules --exclude-dir=.venv \
  . | wc -l
```

Categorize findings:
```
Technical Debt Summary:
  TODO comments: {n}
  FIXME markers: {n}
  HACK/workaround notes: {n}
  @deprecated usage: {n}
  Dead code signals: {unused exports, commented-out blocks}

Notable items:
  - {Specific significant TODO if found}
  - {Any large commented-out code blocks}
```

---

## 4. Security Patterns

Identify (do NOT flag as vulnerabilities unless obvious — Scout documents, not audits):

```
Security Observations:
  Input validation: {present at controller | service | both | none found}
  SQL injection protection: {ORM parameterized queries | raw queries (flagged) | no SQL}
  Secrets management: {env vars | .env file | vault | hardcoded (⚠️ flag)}
  CORS configuration: {src/...} — origins: {configured | wildcard ⚠️ | not found}
  Rate limiting: {present (middleware) | not found}
  Dependency audit: run `npm audit` / `pip audit` — {not checked}
```

⚠️ If any hardcoded secrets or credentials are found in source files, flag them prominently:
> "🔴 SECURITY: Hardcoded credential found in {file}:{line}. This must be moved to environment variables immediately."

---

## 5. Build and Deployment Config

Read and summarize:

```
Build:
  Build command: {npm run build | python -m build | go build | mvn package}
  Output: {dist/ | build/ | target/ | binary}
  Environment: {NODE_ENV | APP_ENV | GO_ENV}

Required Environment Variables:
  DATABASE_URL       required — PostgreSQL connection string
  JWT_SECRET         required — Token signing key
  REDIS_URL          optional — Defaults to localhost:6379
  SENDGRID_API_KEY   required — Email delivery
  PORT               optional — Defaults to 3000

Container:
  Dockerfile: ✅/❌
  Multi-stage build: ✅/❌
  Base image: {node:20-alpine | python:3.12-slim | ...}
  Exposed port: {3000}

Orchestration:
  docker-compose.yml: ✅/❌ — services: {list}
  Kubernetes manifests: ✅/❌ — path: {k8s/}
  Terraform / Bicep: ✅/❌ — path: {infra/}
```

---

## 6. Developer Experience

Document from observed config:

```
Dev Setup:
  Setup steps: {inferred from package.json scripts + README}
  Dev server: {npm run dev | uvicorn ... --reload | air | ...}
  Hot reload: ✅/❌
  Database seed: {npm run seed | inferred | not found}

Code Quality Tools:
  Linter: {ESLint | Ruff | golangci-lint | Checkstyle | none}
  Formatter: {Prettier | Black | gofmt | none}
  Type checker: {TypeScript strict | mypy | flow | none}
  Pre-commit hooks: ✅/❌ (.husky | pre-commit | lefthook)
  Config files: {.eslintrc | .prettierrc | pyproject.toml | ...}
```

---

## 7. Present Patterns and Health Summary

```
🔍 Patterns & Health — {project_name}
════════════════════════════════════════
Conventions: {consistent | mixed | unclear}
Testing: {unit + integration | unit only | minimal | none}
Tech debt markers: {n}
Security patterns: {present | partial | minimal}
Build: {containerized | bare | unclear}
DX tools: {linter, formatter, hooks}

Health Signal:
  🟢 {positive signal}
  🟡 {caution signal}
  🔴 {problem signal}
════════════════════════════════════════
```

⏸️ **STOP** — confirm observations. Ask: "Is there anything about the project's conventions or practices I should know before writing documentation?"

---

## 8. Save State

Update `{project-root}/_superml/relearn-state.yml`:
```yaml
step: "step-04-patterns"
status: "complete"
test_framework: "{jest|pytest|...}"
has_linter: true
tech_debt_count: {n}
env_vars_required: ["{list}"]
```

Load and follow `./step-05-document.md`.
