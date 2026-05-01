# Step 01 — Discover Project Structure

**Previous step:** (none — this is the first step)
**Next step:** `step-02-analyze.md`

---

## 1. Identify Project Root

Confirm the project root directory with the user:
> "I'll analyze the project at `{project-root}`. Is that the right directory, or should I look somewhere else?"

⏸️ **STOP** — wait for confirmation or correction.

---

## 2. Scan Top-Level Structure

List the top-level directories and files. Identify:
- Source code directories (e.g., `src/`, `lib/`, `app/`, `packages/`)
- Configuration files (`package.json`, `pom.xml`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.)
- Build/CI files (`.github/`, `Dockerfile`, `docker-compose.yml`, `Makefile`)
- Existing documentation (`docs/`, `README.md`, `ARCHITECTURE.md`, `CHANGELOG.md`)
- Test directories (`test/`, `tests/`, `spec/`, `__tests__/`)
- Infrastructure (`infra/`, `terraform/`, `k8s/`, `helm/`)

---

## 3. Detect Technology Stack

From configuration files and code, identify:
- **Primary language(s)** and version(s)
- **Runtime / framework** (e.g., Node.js + Express, Spring Boot, Django, Next.js)
- **Database(s)** and ORM/client (PostgreSQL + Prisma, MongoDB + Mongoose, etc.)
- **Key dependencies** — top 10 by significance
- **Build tooling** (Webpack, Vite, Gradle, Maven, etc.)
- **Testing framework(s)**
- **CI/CD system** (GitHub Actions, GitLab CI, Jenkins, Azure Pipelines)
- **Containerization and orchestration**

---

## 4. Identify Entry Points

Find:
- Main application entry points
- API surface (REST routes, GraphQL schema, gRPC services)
- CLI commands or scripts
- Background workers or queue consumers
- Scheduled jobs or cron tasks

---

## 5. Present Discovery Summary

Present findings as a concise summary table:

```
Project: {project_name}
Root: {project-root}

Technology Stack:
  Language: ...
  Framework: ...
  Database: ...
  
Structure:
  Source dirs: ...
  Test dirs: ...
  Docs: ...
  
Entry Points: ...

Key Dependencies: ...
```

⏸️ **STOP** — Ask: "Does this look right? Anything I missed or should adjust before I dive deeper?"

---

## 6. Save Progress

Update the output file frontmatter:
```yaml
stepsCompleted: ["step-01-discover"]
discoveredStack: "{detected stack}"
```

Then load and follow `./step-02-analyze.md`.
