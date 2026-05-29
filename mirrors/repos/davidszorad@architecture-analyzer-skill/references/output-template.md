# Output Template — Architecture Document

This is the reference template for the architecture document. Each section below describes what to include, the format to use, and why the section matters for LLM code generation.

The template is **technology-agnostic**. Code snippets and naming examples shown below happen to use .NET/C# syntax for brevity, but every section applies to any stack — substitute the equivalent constructs from the codebase under analysis (TypeScript classes, Python modules, Spring beans, Go packages, etc.). Use the **actual language and idioms** of the target codebase in the final document. The level of detail must match a stack-specialized analyzer regardless of language.

Write every section in the order shown. Skip sections that genuinely don't apply (e.g., no ORM, no cross-cutting tenancy). Don't pad with "N/A".

---

## Section 1: Project Identity

**Purpose**: Orient the model on what this codebase is and who it serves. Without this, the model generates code in a vacuum.

**Format**:
```markdown
# {ProjectName} — Architecture Prompt

> **Purpose**: Feed this prompt to an LLM so it completely understands how to build, extend, debug, and test the {ProjectName} codebase.

---

## 1. Project Identity

**{ProjectName}** is a **{one-line description}** built by {organization}. It provides {list of key capabilities} — all governed by {key cross-cutting concern if any, e.g., "country-specific configurations"}.
```

Keep it to one paragraph. Focus on what the system *does*, not how.

---

## Section 2: Tech Stack

**Purpose**: The model needs to know exact technologies and versions to generate correct imports, API calls, and dependency declarations.

**Format**: A table with three columns — Category, Technology, Version.

```markdown
## 2. Tech Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Runtime | {Node.js / .NET / Python / JVM / Go / ...} | {version from lockfile or pin} |
| Language | {C# / TypeScript / Python / Kotlin / Go / ...} | {version} |
| Web Framework | {ASP.NET Core / NestJS / FastAPI / Spring Boot / ...} | {version} |
| ORM / Data Access | {EF Core / Prisma / SQLAlchemy / JPA / GORM / ...} | {version} |
| Primary Database | {PostgreSQL / MySQL / DynamoDB / ...} | — |
| Auth | {provider} | — |
| Testing | {framework} + {mocking lib} | x.x.x |
| ... | ... | ... |
```

**What to include** (only if actually used):
- Runtime & language (with version pin from lockfile / `global.json` / `.nvmrc` / `.python-version` / `go.mod`)
- Web/API framework
- ORM / data access
- Primary database (and secondary if any)
- Cloud provider & key services (compute, storage, secrets, messaging)
- Auth provider and method
- UI framework (if any)
- Serialization library
- HTTP client strategy
- External API integrations (as a group)
- PDF/Excel/QR or other specialty libs
- Testing framework + mocking library + assertion library
- Package / dependency management strategy
- API versioning approach
- API docs tooling

Use `—` for version when version doesn't matter or isn't pinned. Only include technologies actually used.

---

## Section 3: Solution Architecture

**Purpose**: This is the single highest-value section. Models reference it constantly when deciding where to place new code.

### 3.1 Project Map

**Format**: ASCII box diagram grouping projects/modules/packages by layer.

```markdown
### 3.1 Project Map ({N} projects)

┌─────────────── PRESENTATION ───────────────┐
│  {Project}.Api              (Web API)       │  ← {brief description}
│  {Project}.Admin.Api        (Web API)       │  ← {brief description}
└─────────────────────────────────────────────┘
         ↓ depends on
┌─────────────── APPLICATION ────────────────┐
│  {Project}.Application                      │  ← {brief description}
└─────────────────────────────────────────────┘
         ↓ depends on
┌─────────────── CORE ───────────────────────┐
│  {Project}.Core                             │  ← {brief description}
└─────────────────────────────────────────────┘
         ↓ depends on
┌─────────────── DATA ───────────────────────┐
│  {Project}.Database                         │  ← {brief description}
└─────────────────────────────────────────────┘

┌─────────────── INFRASTRUCTURE ─────────────┐
│  {Project}.Infrastructure                   │  ← {brief description}
└─────────────────────────────────────────────┘

┌─────────────── TESTS ──────────────────────┐
│  {Project}.Tests                            │  ← {brief description}
└─────────────────────────────────────────────┘
```

Rules for the diagram:
- Use `↓ depends on` arrows only for the primary dependency chain
- Group projects by layer using box-drawing characters (`┌ ┐ └ ┘ │ ─`)
- Add a one-line description after each project (← comment style)
- Include project type in parentheses — adapt to the stack: (Web API), (Lambda), (Console), (Razor Lib), (Blazor Web), (NestJS app), (CLI), (Worker), (Library/Package), (Frontend SPA), (Lambda Handler), (Spring Boot service), etc.
- Separate standalone groups (Infrastructure, Workers, Tests) without arrows if they sit outside the main chain
- Mark legacy projects clearly: `← Being phased out → use {Replacement}`

### 3.2 Dependency Rules

**Format**: Numbered list of hard rules about what can reference what.

```markdown
### 3.2 Dependency Rules

1. **Application** → Core → Database (downward only)
2. **Infrastructure** → Core (implements Core interfaces)
3. **API projects** → Application + Infrastructure (wiring)
4. **Slices/feature modules within Application MUST NOT reference each other**
5. ...
```

These rules prevent the model from introducing circular dependencies or violating architectural boundaries.

---

## Section 4: Core Design Patterns

**Purpose**: This section teaches the model *how* to write code in this codebase. Each subsection covers one pattern with a real extracted code example.

### 4.1 through 4.N: One subsection per major pattern

Common patterns to document (include only those present):

- **CQRS / Mediator / Use-Case dispatch** — command/query definitions, handler signatures, pipeline behaviors, how handlers are discovered
- **Result / Either / Error monad** — type definitions, error types, factory methods, conversion helpers
- **Validation Framework** — sync validators, async business validators, how they're wired (decorator chain, middleware, framework hooks)
- **Domain Events + Outbox** — event definitions, handlers, outbox message flow
- **Repository Pattern** (if used instead of direct ORM context/session)
- **Specification Pattern** (if present)

**Format for each pattern**:

```markdown
### 4.1 {Pattern Name}

{One paragraph explaining what it is and where it lives in the codebase.}

#### {Sub-aspect, e.g., "Commands (write operations)"}

{Code snippet — real, extracted, trimmed to essentials, in the codebase's actual language}

#### {Sub-aspect, e.g., "Queries (read operations)"}

{Code snippet}
```

**Code snippet guidelines**:
- Extract from real files — use actual class/function names, namespaces/modules, and types
- Use the codebase's actual language — TypeScript decorators, Python type hints, Go struct tags, Java annotations, etc.
- Include comments that explain conventions: `// concrete for writes`, `// NO CancellationToken here`, `# async handler — do not block`
- Keep each snippet under 25 lines
- Show the canonical/recommended way, not edge cases
- If a command + handler are in the same file (or module), show that pattern

**Pipeline / interceptor chain**: Document the execution order as a clear pipeline diagram:
```
Request → LoggingDecorator → ValidationDecorator → BusinessValidationDecorator → Handler
```

For each link in the chain, capture details that affect how a model writes code:
- **Concurrency model**: Does business validation run validators sequentially or concurrently (`Task.WhenAll`, `Promise.all`, `asyncio.gather`, goroutines)?
- **Error aggregation**: First-error-wins, or collects all validation errors?
- **DI lifetime / scope**: State the lifetime of handlers, validators, and decorators (e.g., ".NET handlers auto-registered with **scoped** lifetime via assembly scanning"; "NestJS providers default to singleton unless `Scope.REQUEST`"; "FastAPI dependencies resolve per-request"). Getting this wrong causes DI resolution failures or concurrency bugs.

---

## Section 5: Data Layer

**Purpose**: Data access is where most subtle bugs live — wrong context/session usage, missing auditing, wrong transaction scope. Be thorough.

### Subsections to include:

**5.1 DbContext / Session / Client** — the entry point class for data access (EF `DbContext`, SQLAlchemy `Session` factory, Prisma client, Hibernate `EntityManager`, etc.). Document signature, save behavior, auditing, naming conventions.

**Read interface vs write concrete**: if the codebase splits reads and writes via an interface that hides `SaveChanges`/`commit` (e.g., .NET `IDbContext` exposing `DbSet<T>` but NOT `SaveChangesAsync`; a Prisma read-only wrapper; a SQLAlchemy read-only session factory; JPA `@Transactional(readOnly = true)` repositories; separate GORM read-replica `*gorm.DB`), document:
- The interface name and which members it exposes (and which it deliberately omits)
- Which classes depend on the read interface (query handlers) vs the write concrete (command handlers)
- The rule: **do NOT inject both the read interface and the write concrete into the same class**. If a class needs to write, it depends on the write concrete and uses it for reads too. Query handlers depend on the read interface only.
Show one real query-handler constructor and one real command-handler constructor to illustrate.

**5.2 Schemas / Namespaces** — table of schema/namespace names and their purposes (or collections for NoSQL).

**5.3 Base Entity / Mixin** — the base class or mixin with audit fields (if any), with code.

**5.4 Entity Configuration Pattern** — how entities and their configurations are organized (same file? separate? declarative annotations vs fluent config vs schema file?). Show a real example. Include:
- **Seed data patterns**: If configurations use seed mechanisms (EF `HasData()`, Prisma seed scripts, Django fixtures, Rails seeds, Alembic data migrations), show a real example. This is a common pattern that models need to replicate when adding new entities.
- **Check constraints / domain constraints**: If defined inline (EF `HasCheckConstraint()`, Postgres CHECK in migrations, JPA `@Check`), show the naming convention and a real example (e.g., `"ck_country_country_code_uppercase"`).
- **Builder / fluent / decorator conventions**: Note recurring API patterns beyond basic schema/key (EF `IsFixedLength()`, `HasMaxLength()`, `HasConversion()`; Prisma `@db.VarChar(...)`, `@map(...)`; SQLAlchemy `Column(..., server_default=...)`; JPA `@Column(columnDefinition=...)`).

**5.5 Enum ↔ Lookup-Table Pattern** — if the codebase uses enum-backed lookup tables, show the pattern with code.

**5.6 Key Domain Entities** — table of major entities with schema and description.

**5.7 Transactions** — the pattern for explicit transactions, with code (`using var transaction = ...`, `@Transactional`, `with db.session.begin():`, `unitOfWork`, `tx.Run(...)`).

**Format for entity table**:
```markdown
| Entity | Schema | Description |
|--------|--------|-------------|
| `User` : AuditableEntity | tc | HCP user (Email, Roles, Countries) |
```

---

## Section 6: Application Layer / Modules

**Purpose**: Tell the model what business domains exist and how they're organized.

### 6.1 Module Catalog

**Format**: Table of all modules/slices/features with domain and complexity.

```markdown
| Module | Domain | Complexity |
|--------|--------|-----------|
| `MaterialOrders` | Full CRUD material ordering | Very High |
| `Countries` | Country/state reference data | Low |
```

Complexity is based on file count, sub-feature depth, and number of commands/queries (or endpoints).

### 6.2 Folder Convention

Show the folder structure of one complex module as a tree, annotating what goes where. Use the codebase's actual layout (slice-per-feature, MVC, layered, hexagonal, etc.).

### 6.3 DI / Module Registration

Explain how modules/handlers are registered — assembly scanning, decorator-based discovery, explicit module imports (NestJS `imports`), framework auto-discovery (Spring component scan), or manual wiring.

---

## Section 7: Infrastructure Layer

**Purpose**: The model needs to know how external services are integrated so it can add new ones correctly.

### 7.1 DI Lifetime / Scope Conventions

Table mapping lifetime/scope (Singleton, Scoped/Request, Transient, per-invocation) to what uses it and why. Use the terminology of the stack (e.g., `Scope.REQUEST` in NestJS, `@RequestScope` in Spring, `scoped` in EF Core, `Depends(...)` per-request in FastAPI).

### 7.2 API Client Pattern

One real code example showing how an HTTP client is registered and configured (`IHttpClientFactory` + `DelegatingHandler`, axios instance + interceptors, `httpx.AsyncClient` with custom transport, Feign client, etc.).

### 7.3 External Integrations

Table mapping: Integration → Interface (Core) → Implementation (Infrastructure).

---

## Section 8: API Layer

### 8.1 Controller / Route Handler Pattern

Real code example of a controller or route handler module showing: base class (if any), routing, auth attribute/guard, handler injection pattern, action methods. Use the codebase's actual framework idioms.

### 8.2 Result → HTTP Mapping

Table showing how Result/error states map to HTTP status codes.

### 8.3 Authentication

Table of API projects and their auth method. **Check each API project's bootstrap file individually** — different projects in the same repo often use different auth providers or methods.

```markdown
| API Project | Auth Method | Identity Provider |
|-------------|------------|-------------------|
| {Project}.Api | JWT Bearer | {actual provider, e.g., Microsoft Entra ID} |
| {Project}.Admin.Api | ALB OIDC / Lambda Authorizer | {provider} |
| {Project}.Consent | OIDC (cookie) | {provider} |
```

**Important**: Report the ACTUAL identity provider found in the bootstrap configuration (`Program.cs`/`Startup.cs`, `main.ts`, `main.py`, `Application.java`), not what legacy config files or comments suggest. If an `OktaConfiguration.cs` exists but `Startup.cs` wires `EntraConfiguration`, the active provider is Entra.

### 8.4 Middleware, Interceptors & Filters

This subsection is high-value for LLM code generation. Go beyond a simple bullet list.

**User context middleware**: For middleware (or NestJS interceptors, FastAPI dependencies, Spring filters) that extracts user identity/context from JWT claims or headers, document the complete claim-to-property mapping:

```markdown
**`CurrentUserMiddleware`** — extracts JWT claims and populates scoped `CurrentUser` service:
| Claim/Header | Property |
|-------------|----------|
| `country` | `CurrentUser.Country` |
| `email` | `CurrentUser.Email` |
| `customerId` | `CurrentUser.CustomerId` |
| ... | ... |
```

**Delegation / impersonation middleware**: If the system supports acting on behalf of another user, document:
- The header name and format (e.g., `Delegation` header with JSON payload)
- How delegate claims override or supplement the original user's claims
- How service permissions are scoped for delegates

**Action filters / decorators / guards**: For each custom filter, decorator, or guard, document:
- What it does (input sanitization, service availability check, rate limiting, etc.)
- Approximate usage count across endpoints (e.g., "used on 16+ controller actions")
- Whether it's applied globally or per-action

```markdown
- **`[SanitizeInputStrings]`** — sanitizes string inputs; applied per-action on ~16 endpoints
- **`[ValidateServiceAvailabilityFilter]`** — checks country-level service availability; per-action
- **`HttpResponseExceptionFilter`** — global; catches `HttpResponseException` → `ObjectResult`
```

**Exception handling**: How unhandled exceptions become HTTP responses (exception filters, error middleware, framework defaults, problem-details).

### 8.5 Caching & CORS

**CORS**: Document per-project CORS policies. Different API projects often have different CORS rules:

```markdown
| API Project | CORS Policy |
|-------------|-------------|
| {Project}.Api | AllowAny (permissive) |
| {Project}.Admin.Api | Restricted to `localhost:4200` |
```

**Caching**: Cache profiles, response caching middleware, cache headers strategy, distributed cache configuration (Redis, in-memory).

---

## Section 9: Testing Conventions

### 9.1 Framework

What test framework, mocking library, assertion library, and coverage tool.

### 9.2 Test Base Classes / Fixtures

Table of **ALL** shared test setup mechanisms found — base classes, pytest `conftest.py` fixtures, RSpec shared contexts, JUnit extensions, Go test helpers. Not just database test bases. Include controller test bases, service test bases, integration test bases, and any custom fixtures.

Document inheritance chains where they exist (e.g., `ServicesTestBase : DatabaseTestBase`, pytest fixture composition).

```markdown
| Base Class / Fixture | Inherits From | Purpose |
|-----------|--------------|----------|
| `DatabaseTestBase` | — | Wraps each test in DB transaction (auto-rollback). Provides `Context`. |
| `TransactionalCodeDatabaseTestBase` | — | For code managing own transactions. No wrapping. Auto-cleans. `[NonParallelizable]`. |
| `ControllersTestBase` | — | Shared mock services and DTOs for controller tests. |
| `ServicesTestBase` | `DatabaseTestBase` | Shared test data for legacy service tests. |
| `DatabaseTestFixture` | — | Shared fixture for DB connection/lifecycle. |
```

For each, note:
- What setup it provides (mock initialization, DB seeding, HTTP context, container startup)
- Any special framework attributes it requires (`[NonParallelizable]`, `[Collection]`, `@Execution(SAME_THREAD)`, pytest `serial` markers)
- The setup override pattern (e.g., `OnSetUp()` virtual method, `setUp`/`tearDown`, pytest fixture `yield`)

### 9.3 Handler / Endpoint Test Pattern

One real test example showing: fixture setup, arrange/act/assert, naming convention. Use the codebase's actual test framework.

### 9.4 Test Naming

Explain the naming pattern with formula: `MethodName_WhenCondition_ExpectedBehavior` (or `test_should_<behavior>_when_<condition>`, `it("should ...", () => ...)`, etc.).

---

## Section 10: Coding Conventions

### 10.1 Language / Style

Bullet list of observed conventions. Adapt to the language:
- **.NET / C#**: sealed by default, handler visibility, record types for commands, collection types, field naming, serialization preference, `CancellationToken` rules, extension method syntax.
- **TypeScript**: strictness flags, `interface` vs `type`, readonly conventions, branded types, async/await rules, decorator usage.
- **Python**: type-hint coverage, dataclass/Pydantic preference, async conventions, naming (snake_case), docstring style.
- **Java/Kotlin**: nullability conventions, sealed classes, record/data class usage, Optional handling, immutability patterns.
- **Go**: error wrapping conventions, context propagation, interface placement (consumer-side), naming.

### 10.2 Data Access

Bullet list: read interface vs write concrete (e.g., `IDbContext` for reads vs `DbContext` for writes — never inject both in the same class; if writes are needed, use the write concrete for reads too), save/commit rules, transaction pattern, naming convention, ORM-specific idioms.

### 10.3 Infrastructure

Rules for adding API clients, cloud SDK registration, external call conventions.

### 10.4 Commit Messages (if discoverable)

Format with examples — check `.gitmessage`, contributing guidelines, or recent git log patterns.

---

## Section 11: Build & Run Commands

**Format**: Table of Action → Command. Use the stack's actual commands.

```markdown
| Action | Command |
|--------|---------|
| Build solution | `dotnet build` |
| Run all tests | `dotnet test` |
| Run specific tests | `dotnet test --filter "FullyQualifiedName~ClassName"` |
| Run main API locally | `dotnet run --project {Project}.Api` |
| Add EF migration | `dotnet ef migrations add <Name> --project {Db} --startup-project {Api}` |
```

Examples in other stacks: `npm run build`, `pnpm test`, `pytest tests/unit -k <pattern>`, `uvicorn app.main:app --reload`, `alembic revision --autogenerate -m "<msg>"`, `./gradlew bootRun`, `go run ./cmd/api`, `bundle exec rspec`.

Source these from: README, Makefile, `package.json` scripts, `pyproject.toml`, `justfile`, `taskfile.yml`, CI config, or infer from project structure.

---

## Section 12: How to Add a New Feature

**Purpose**: This is the "teach a model to fish" section. Walk through adding a realistic feature step by step, with code for each step.

**Format**:

```markdown
## 12. How to Add a New Feature (Step-by-Step)

### Example: Adding a new "{Feature}" query to the Application layer

1. **Create the slice folder** (if new):
   {path}

2. **Define the DTO**:
   {real code pattern in the codebase's language}

3. **Define the Query**:
   {real code pattern}

4. **Implement the Handler**:
   {real code pattern}

5. **Add validation (if needed)**:
   {real code pattern}

6. **Add the controller / route endpoint**:
   {real code pattern}

7. **Write tests**:
   {real code pattern}

8. **DI / module registration**:
   {how it's handled — manual, auto-discovered, decorator-based, module import}
```

Use a realistic but simple feature name. The code should use the project's actual types (`Result<T>`, `IQuery<T>`, `@QueryHandler`, etc.) so a model can copy the pattern directly.

---

## Section 13: Multi-Tenancy / Cross-Cutting Concerns

**Purpose**: If the system has a cross-cutting concern (multi-tenancy, country config, feature flags), document it here. This prevents the model from generating code that ignores these concerns.

Include: how tenancy/context is determined, where configuration lives, how it gates features, middleware/interceptor that extracts it.

Skip this section if no significant cross-cutting concern exists.

---

## Section 14: Key Business Flows

**Purpose**: Help the model understand the domain so it can make sensible decisions about error handling, validation, and data flow.

**Format**: 3-5 key flows, each as a numbered list of 3-5 steps.

```markdown
### {Flow Name}
1. {Actor} does {action} via {API/UI}
2. {Processing step}
3. {External system interaction}
4. {Result/side effect}
```

Keep it high-level — this is domain orientation, not a sequence diagram.

---

## Section 15: Legacy Code Guidance

**Purpose**: Prevent the model from extending deprecated code.

**Format**: Table of legacy project → replacement.

```markdown
| Legacy Project | Replacement |
|---------------|-------------|
| `{Project}.Services` | → `{Project}.Application` (vertical slices) |
```

Add a clear instruction: "When working on features that touch legacy code, prefer refactoring into the new architecture rather than extending legacy patterns."

Skip if there's no legacy code.

---

## Section 16: Quick Reference — Where Does This Go?

**Purpose**: A routing table the model can scan instantly when starting any task.

**Format**:

```markdown
| I need to... | Put it in... |
|-------------|-------------|
| Define a new command/query | `{Project}.Application/<Slice>/<Feature>/` |
| Define a new DTO | `{Project}.Application/<Slice>/Dto/` |
| Define a new entity | `{Project}.Database/Entities/` |
| Add a new API endpoint | `{Project}.Api/Controllers/` |
| Write a unit test | `{Project}.Tests/Application/<Slice>/` |
| ... | ... |
```

Cover at least: command/query, DTO, entity/model, enum, infrastructure interface, infrastructure implementation, API endpoint, migration, unit test, cross-slice shared logic, background job, scheduled task.
