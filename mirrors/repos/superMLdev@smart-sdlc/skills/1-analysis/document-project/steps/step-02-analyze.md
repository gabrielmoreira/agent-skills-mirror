# Step 02 — Deep Analysis

**Previous step:** `step-01-discover.md`
**Next step:** `step-03-document.md`

---

## 1. Architecture Analysis

Examine the source code structure and identify:
- **Architectural pattern** (MVC, Clean Architecture, Hexagonal, Microservices, Monolith, etc.)
- **Layer boundaries** — how is the code organized? (controllers, services, repositories, domain models)
- **Module / package structure** — is there clear separation of concerns?
- **Cross-cutting concerns** — logging, authentication, error handling, validation
- **Communication patterns** — REST, GraphQL, events, queues, gRPC

---

## 2. Data Model

Identify the core data entities:
- Primary domain models / entities
- Relationships between entities
- Database schema (if migration files or ORM models are present)
- External data sources or third-party APIs consumed

---

## 3. API Surface

Map the public interface:
- REST endpoints with methods, paths, request/response shapes (sample 5–10 most important)
- Authentication / authorization mechanism
- Rate limiting or API versioning
- Public vs internal endpoints

---

## 4. Dependency Health Check

Review key dependencies:
- Are there any obviously outdated or deprecated packages?
- Any security-sensitive dependencies worth flagging?
- Any unusual or opinionated choices that need documenting?

---

## 5. Code Quality Signals

From visible patterns, note:
- Test coverage presence (unit, integration, e2e)
- Linting and formatting setup
- Type safety level (TypeScript strictness, mypy, etc.)
- Notable technical debt signals (TODOs, FIXMEs, large files)

---

## 6. Integration Points

Identify external integrations:
- Third-party APIs or SDKs
- Cloud services (AWS, Azure, GCP)
- Message queues or event buses
- Authentication providers (OAuth, SSO)
- Feature flags, analytics, monitoring

---

## 7. Present Analysis Summary

Present a structured analysis summary. Highlight the 3–5 most important things someone new to this codebase must know.

⏸️ **STOP** — Ask: "Anything to add or correct before I write the documentation?"

---

## 8. Save Progress

Update output file frontmatter:
```yaml
stepsCompleted: ["step-01-discover", "step-02-analyze"]
```

Then load and follow `./step-03-document.md`.
