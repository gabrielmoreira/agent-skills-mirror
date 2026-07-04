---
name: architecture-analyzer
description: Deeply analyze a software codebase (any language or framework) and produce a comprehensive architecture document optimized for LLM consumption - so any AI can build, extend, debug, and test the codebase. Outputs a single Markdown file covering tech stack, project map, design patterns, data layer, modules, infrastructure, API layer, testing, coding conventions, build commands, feature walkthrough, business flows, and legacy guidance - all with real extracted code snippets. USE FOR - generate architecture doc, analyze codebase, document codebase for AI, create codebase context, onboard AI to repo, solution overview, reverse-engineer architecture, map the codebase, understand this project, explain this codebase structure, create LLM prompt for codebase, extract project patterns, codebase knowledge base, architecture.md. Even if the user just says "document this repo" or "help me understand this codebase" or "create a context file for AI", this skill applies. Works with any stack - .NET, Node.js/TypeScript, Python, Java/Kotlin, Go, Ruby, PHP, Rust, etc. - and adapts depth of analysis to the conventions of the detected stack.
---

# Architecture Analyzer

Analyze a software codebase and produce a single comprehensive Markdown document that gives an LLM everything it needs to build, extend, debug, and test the codebase.

The output is not documentation for humans — it's an **LLM context document**. Every section exists because it helps a model write correct code on the first try: knowing which patterns to follow, which conventions to respect, where new code goes, and what to avoid.

This skill is **stack-agnostic**. It works on .NET, Node.js/TypeScript, Python, Java/Kotlin, Go, Ruby, PHP, Rust, and polyglot repos. The exploration steps describe *what* to discover; the per-stack hints describe *where* to look for it. When analyzing a .NET solution, the depth and precision must match a .NET-specialized analyzer — the generality of this skill is a layer on top, not a reduction in rigor.

## Before You Start

Read the output template at [references/output-template.md](references/output-template.md). It defines the exact sections, ordering, and format of the final document. Keep it open as your guide throughout the analysis.

## Workflow Overview

The analysis has three phases:

1. **Detect** — identify the primary stack(s) so subsequent steps use the right vocabulary and file patterns
2. **Explore** — systematically scan the codebase to gather raw facts
3. **Synthesize** — assemble those facts into the output template with real code snippets

Do NOT start writing the document until you've completed exploration. Premature writing leads to incomplete sections and backtracking.

---

## Phase 0: Detect the Stack

Before deep exploration, identify the primary language(s), runtime(s), and build system(s). This determines which file patterns and conventions to look for in every later step.

Run these checks in parallel:

| Stack | Manifest / Marker Files |
|-------|------------------------|
| .NET | `*.sln`, `*.csproj`, `*.fsproj`, `*.vbproj`, `global.json`, `Directory.Build.props`, `Directory.Packages.props` |
| Node.js / TypeScript | `package.json`, `tsconfig.json`, `pnpm-workspace.yaml`, `nx.json`, `turbo.json`, `lerna.json` |
| Python | `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `Pipfile`, `poetry.lock`, `uv.lock` |
| Java / Kotlin | `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`, `gradlew` |
| Go | `go.mod`, `go.sum`, `go.work` |
| Ruby | `Gemfile`, `*.gemspec`, `Rakefile` |
| PHP | `composer.json`, `composer.lock` |
| Rust | `Cargo.toml`, `Cargo.lock` |
| Other | `Dockerfile`, `Makefile`, `BUILD.bazel`, `flake.nix` |

If multiple stacks coexist, classify each top-level module/service by its manifest and analyze each one with the appropriate conventions. Note the polyglot structure explicitly in the output document.

Record the detected stack(s); every later step has stack-specific guidance you'll consult.

---

## Phase 1: Explore

Work through these steps in order. Each step builds context for the next. Use search tools aggressively — `file_search`, `grep_search`, `read_file`, and `semantic_search` are your primary instruments.

### Step 1: Repository Structure & Project Map

Find the build/solution manifest(s) and enumerate all projects/modules/packages.

**Stack hints**:
- **.NET**: Read `*.sln` to get all `*.csproj` paths; also `file_search **/*.csproj` to catch any not in the .sln. For each project extract `<TargetFramework>`, output type (Exe/Library/Web SDK), and `<ProjectReference>` edges. Also check `Directory.Build.props`, `Directory.Packages.props`, `global.json`, `.editorconfig`.
- **Node.js / TS**: Read root `package.json`. For monorepos, expand `workspaces`, `pnpm-workspace.yaml`, `nx.json`, `turbo.json` to find every package. For each package, extract `name`, `main`/`exports`, `dependencies`, `devDependencies`, and `tsconfig.json` references.
- **Python**: Read `pyproject.toml` (PEP 621 / Poetry / uv / Hatch sections) or `setup.cfg`/`setup.py`. For monorepos, look for `packages/`, `src/`, multiple `pyproject.toml` files. Capture dependencies and entry points (`[project.scripts]`).
- **Java / Kotlin**: Parse `pom.xml` (`<modules>`) or `settings.gradle{.kts}` (`include(...)`). For each module read its `pom.xml` / `build.gradle` for dependencies and packaging type (jar/war).
- **Go**: Read `go.mod` (module path, Go version, requires). For multi-module repos, use `go.work`. Treat each `cmd/<name>/main.go` as an executable entry point.
- **Ruby**: Read `Gemfile` and any `*.gemspec`. For Rails, note `config/application.rb` and engines.
- **PHP**: Read `composer.json` (`require`, `autoload` PSR-4 roots).
- **Rust**: Read root `Cargo.toml` `[workspace]` members; each member has its own `Cargo.toml`.

For each project/module/package, extract:
- Name, type (library, executable, web service, worker, test suite)
- Target runtime / language version
- Dependency edges (project-to-project)
- Whether it's a build artifact, a test, or a tool

Also check for repo-wide config:
- Lockfiles (pin language/runtime versions)
- Linter/formatter configs (`.editorconfig`, `.eslintrc`, `ruff.toml`, `.rubocop.yml`, etc.)
- Pre-commit / git hooks
- Container/orchestration manifests (`Dockerfile`, `docker-compose.yml`, `k8s/`, `helm/`)

**Why this matters**: The project map is the skeleton of the entire document. Every later section maps back to a project.

### Step 2: Tech Stack

Build the technology inventory from manifests and lockfiles.

Capture, where applicable:
- **Runtime / language version** (pin from lockfile or version manager file: `global.json`, `.nvmrc`, `.python-version`, `.ruby-version`, `go.mod`, `rust-toolchain.toml`)
- **Web / API framework** (ASP.NET Core, Express, Fastify, NestJS, Next.js, FastAPI, Django, Flask, Spring Boot, Rails, Laravel, Gin, Echo, Axum, etc.)
- **ORM / data access** (EF Core, Dapper, Prisma, TypeORM, Drizzle, SQLAlchemy, Django ORM, Hibernate/JPA, GORM, ActiveRecord, Eloquent, sqlx, Diesel)
- **Primary database** (PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, DynamoDB, Redis, etc.) — read connection strings, driver packages, infra config
- **Auth** (JWT, OIDC/OAuth provider, session cookies, SAML; library + identity provider)
- **Cloud / infra SDKs** (AWS SDK, Azure SDK, GCP client libs)
- **Messaging / queues** (Kafka, RabbitMQ, SQS, SNS, EventBridge, Service Bus, MediatR/MassTransit/NServiceBus, BullMQ, Celery, Sidekiq)
- **Testing** (framework + assertion lib + mocking lib + coverage tool)
- **Serialization** (System.Text.Json, Newtonsoft.Json, Jackson, Gson, Pydantic, Marshmallow, encoding/json, serde)
- **UI** (Blazor, React, Vue, Angular, Svelte, Razor, ERB, Thymeleaf, etc.)
- **HTTP client strategy** (`IHttpClientFactory`, `axios`, `fetch`, `node-fetch`, `requests`, `httpx`, `OkHttp`, `reqwest`, etc.)
- **API docs tooling** (Swashbuckle, NSwag, swagger-jsdoc, drf-spectacular, springdoc)
- **API versioning approach**

Extract actual version numbers from lockfiles or pinned manifests.

### Step 3: Project Classification & Dependency Map

Classify each project/module/package into a layer. Common layers across stacks:

| Layer | Signals |
|-------|---------|
| **Presentation / API** | HTTP routing, controllers/handlers, request DTOs, web framework entry points |
| **Application** | Use cases, commands/queries, handlers, orchestration logic, no direct infra refs |
| **Domain / Core** | Entities, value objects, interfaces, result types, domain services; no infra refs |
| **Data / Persistence** | ORM context, entity/schema definitions, migrations, repositories |
| **Infrastructure** | Implements Core interfaces, API clients, cloud SDK usage, file/email/queue adapters |
| **Tests** | Test framework references, fixtures, test base classes |
| **Workers / Jobs** | Background services, queue consumers, schedulers, Lambda/Function handlers |
| **Shared / Contracts** | DTOs/types/protobuf shared across projects, no business logic |
| **Frontend** | UI app(s), build pipeline, client-side state |

Build the dependency graph from project references / package imports. Identify:
- Dependency direction (should flow downward: API → Application → Core → Data)
- Any violations or circular references
- Legacy projects (naming, comments, thin wrappers, deprecation markers)

**Hosting model per executable**: For each runnable project, determine how it runs:
- **.NET**: Look for `Amazon.Lambda.AspNetCoreServer`, `LambdaEntryPoint`, `FunctionHandler` (Lambda); `Dockerfile` (container); `WebApplication.Run()` vs Lambda bootstrap in `Program.cs`/`Startup.cs`; Coravel (`AddScheduler`, `UseScheduler`).
- **Node.js**: `serverless.yml`, `sst.config.*`, AWS CDK `Function` constructs, `@vercel/*`, `next.config.*`; `Dockerfile`; `pm2` ecosystem files.
- **Python**: `mangum`/`aws-lambda-powertools` (Lambda); `gunicorn`/`uvicorn`/`hypercorn` config; `Dockerfile`; Celery beat (scheduler).
- **Java/Kotlin**: `spring-boot-starter` (jar), `war` packaging, `aws-lambda-java-*`, `Dockerfile`.
- **Go**: `cmd/<name>/main.go` entry points; `lambda.Start` for Lambda.

Do NOT assume all projects share the same hosting model — API projects may run on Lambda while background jobs run as standalone hosts.

### Step 4: Design Patterns

This is the most important exploration step. Scan for these patterns — they dictate how a model should write new code. Each pattern below is described in stack-neutral terms with stack hints for discovery.

**CQRS / Mediator / Use-Case dispatch**:
- **.NET**: `ICommand`, `IQuery`, `IRequest`, `ICommandHandler`, `IQueryHandler`, `IRequestHandler`, `MediatR`, custom `IMediator`.
- **TS/JS**: NestJS `@CommandHandler`/`@QueryHandler`, custom command bus classes, tRPC procedures.
- **Python**: hand-rolled command bus, `dependency-injector` providers, FastAPI dependencies acting as use cases.
- **Java/Kotlin**: Axon Framework, Spring `@Service` use-case classes, custom `CommandBus`.
- **Go**: handler functions per use case, `usecase` package convention.

For all stacks: look at how handlers are discovered/registered (assembly scanning, decorators, DI container modules, manual wiring).

**Result / Error Handling**:
- **.NET**: `Result<T>`, `ErrorOr<T>`, `OneOf`, exception-based.
- **TS**: `Result`/`Either` (neverthrow, fp-ts), discriminated unions, thrown errors.
- **Python**: `returns` library `Result`, raised exceptions, tuple `(value, error)`.
- **Java/Kotlin**: `Either` (Arrow), `Result`, checked exceptions.
- **Go**: idiomatic `(value, error)` returns; custom error types.
- **Rust**: `Result<T, E>`, `?` operator, `thiserror`/`anyhow`.

Document how handlers return success/failure and how the API layer translates that into HTTP responses.

**Validation**:
- **.NET**: `AbstractValidator` (FluentValidation), `IValidator`, custom `IBusinessValidator`, data annotations.
- **TS**: Zod, Yup, class-validator, Joi, Valibot.
- **Python**: Pydantic models, marshmallow, manual validators.
- **Java/Kotlin**: Bean Validation (`jakarta.validation`), Hibernate Validator.
- **Go**: `go-playground/validator`, manual.
- **Rails**: ActiveModel validations.

Capture how validation is wired (decorators, pipeline middleware, framework integration, manual calls).

**Pipeline / Middleware / Interceptor chains**:
- **.NET**: `IPipelineBehavior`, custom decorators, ASP.NET middleware.
- **TS**: Express/Fastify middleware, NestJS interceptors/guards/pipes, tRPC middleware.
- **Python**: FastAPI dependencies/middleware, Django middleware, DRF permissions/throttles.
- **Java/Kotlin**: Spring `HandlerInterceptor`, `Filter`, AOP aspects.
- **Go**: `http.Handler` middleware chains.

For each pipeline/decorator, read the ACTUAL implementation and capture:
- Execution order
- Concurrency model (sequential vs parallel; e.g., `Task.WhenAll`, `Promise.all`, `asyncio.gather`, goroutines)
- Error aggregation strategy (first-error-wins? collect all?)
- What it logs

These details affect how a model writes new validators/handlers; getting them wrong causes subtle runtime bugs.

**Domain Events / Outbox**:
- **.NET**: `IDomainEvent`, `INotification`, `OutboxMessage` table.
- **TS**: NestJS event emitter, custom event bus.
- **Python**: `blinker`, custom dispatchers.
- **Java/Kotlin**: Spring `ApplicationEvent`, Axon events.
- **Cross-stack**: outbox/inbox tables in DB, transactional event publishing.

**Repository Pattern**:
- Look for explicit repository interfaces vs. direct ORM context/session injection.
- **.NET**: `IRepository`, repository base class, or direct `DbContext` — and whether reads go through a `IDbContext` read-only interface (no `SaveChangesAsync`) while writes use concrete `DbContext`.
- **TS**: TypeORM repositories, Prisma client directly, custom repository classes; check for read-only wrappers.
- **Python**: SQLAlchemy sessions directly, repository classes, Django ORM managers; check for read-only session/protocol vs write session.
- **Java**: Spring Data `Repository`, custom JPA repositories; check for `@Transactional(readOnly = true)` query repositories vs write repositories.

**DI / Composition Root Registration**:
- **.NET**: `DependencyInjection.cs`, `Program.cs`/`Startup.cs`, Scrutor scanning, lifetime (singleton/scoped/transient).
- **TS**: NestJS modules, InversifyJS, tsyringe, manual factory wiring.
- **Python**: `dependency-injector`, FastAPI `Depends`, manual wiring.
- **Java/Kotlin**: Spring `@Configuration`/`@Bean`, scope annotations (`@Singleton`/`@RequestScope`).
- **Go**: wire, manual constructor injection.

For every stack, **document the lifetime/scope** of each registration category (handlers, validators, decorators, infrastructure services). Lifetime mistakes are a top source of runtime bugs.

For each pattern found, locate **one canonical example** — a real file that best demonstrates the pattern. You'll extract code from it later.

### Step 5: Data Layer

For each data store in use, capture schema management, access patterns, and conventions.

**Relational + ORM**:
- **.NET / EF Core**: Find classes inheriting `DbContext`; read it for `DbSet` count, `SaveChanges` overrides, auditing interceptors, conventions. Find `IEntityTypeConfiguration<T>` for each entity. Check migration folder. **Read 2–3 entity configs fully** for `HasData(...)` seed patterns, `HasCheckConstraint(...)` (capture naming convention), and recurring fluent API (`HasMaxLength`, `IsFixedLength`, `HasConversion`, collation, computed columns).
- **TS / Prisma**: Read `schema.prisma` — models, relations, `@@map`, `@@index`, enums, `previewFeatures`. Check `migrations/` history.
- **TS / TypeORM / Drizzle**: Entity classes with decorators; migration directory; data source configuration.
- **Python / SQLAlchemy**: `Base = declarative_base()`, mapped classes, `__tablename__`, Alembic `versions/` directory, `env.py`.
- **Python / Django**: `models.py` per app, `migrations/` per app, `Meta` classes, custom managers.
- **Java / JPA**: `@Entity` classes, `@Table`, `@Column`, Liquibase/Flyway in `db/migration/`.
- **Ruby / ActiveRecord**: `app/models/*.rb`, `db/schema.rb`, `db/migrate/*`.
- **Go**: GORM tags, sqlx queries, raw SQL with `migrate`/`goose`.

**Document for all**:
- Base entity / mixin patterns (audit fields: `CreatedAt`, `UpdatedAt`, `CreatedBy`)
- Schema / namespace partitioning
- **Read-interface vs write-concrete split**: many codebases expose a read-only interface that hides save/commit so query handlers can't accidentally mutate, while command handlers depend on the concrete context that has save/commit. Check whether the codebase follows this split and what the interface is named. Stack hints:
  - **.NET / EF Core**: `IDbContext` (or `IReadDbContext`, `IApplicationDbContextReadOnly`) — typically exposes `DbSet<T>` / `IQueryable<T>` but NO `SaveChangesAsync`. The concrete `DbContext` is used for writes.
  - **TS / Prisma**: a typed wrapper exposing only `findMany`/`findUnique`/`findFirst` (no `create`/`update`/`delete`/`$transaction`), or the full `PrismaClient` for writes.
  - **TS / TypeORM**: `EntityManager` vs read-only repository wrappers; or separate read/write `DataSource`.
  - **Python / SQLAlchemy**: a read-only session factory (autoflush off, no `commit`) vs the write session; or a `ReadOnlySession` protocol.
  - **Java / JPA**: `@Transactional(readOnly = true)` query repositories vs write repositories; or separate read/write `EntityManager` qualifiers.
  - **Go / GORM**: separate `*gorm.DB` instances (read replica vs primary) injected by role.
  - **Rule to capture and document**: never inject both the read interface and the write concrete into the same class. If a class needs to write, it depends on the write concrete and uses it for reads too. Query handlers depend on the read interface only.
- Naming conventions (snake_case columns? PascalCase entities? configured how?)
- Transaction patterns used in handlers (`using var transaction = ...`, `@Transactional`, `db.session.begin()`, `unitOfWork`)
- Cancellation/timeout conventions (e.g., `CancellationToken` rules in .NET, `AbortSignal` in JS, `context.Context` in Go)
- Enum ↔ lookup-table patterns
- Soft-delete / row-level security conventions

**Non-relational**:
- **MongoDB**: collections, indexes, validation schemas, change streams.
- **DynamoDB**: table definitions in IaC, single-table vs multi-table, GSIs, access patterns.
- **Redis**: key naming conventions, pub/sub channels, expiry policies.

### Step 6: Application Layer / Modules

List the top-level business modules / domains / vertical slices.

**Stack hints for "where modules live"**:
- **.NET**: directories under the Application project.
- **TS (NestJS)**: feature modules (`*.module.ts`).
- **TS (other)**: directories under `src/features`, `src/domains`, or `apps/<name>`.
- **Python**: Django apps, FastAPI routers, or domain packages.
- **Java/Kotlin**: packages under `com.<org>.<domain>` or Gradle subprojects.
- **Go**: top-level packages or `internal/<domain>/`.
- **Rails**: engines, namespaced controllers/models, or `app/services/<domain>`.

Build a table of all modules with domain description and complexity estimate (Low/Medium/High based on file count and sub-feature depth).

Document the **per-module folder convention** (e.g., commands/queries/handlers/DTO subdirs, MVC controller/service/model, NestJS controller/service/dto, Django views/serializers/models). Show one tree.

Document **how modules are registered / discovered** — assembly scanning, decorator-based discovery, explicit module imports, framework conventions.

### Step 7: Infrastructure & External Integrations

Map external integrations and their abstraction boundary.

For each integration capture: interface (in Core/Domain) → implementation (in Infrastructure) → HTTP client / SDK used.

**Stack hints**:
- **.NET**: `IHttpClientFactory`, `AddHttpClient`, `Refit`, `RestSharp`; `DelegatingHandler` subclasses for cross-cutting HTTP concerns (token exchange, header propagation, retry-with-reauth); resilience via Polly / `AddStandardResilienceHandler`. Document each `DelegatingHandler` and the client it's attached to.
- **TS**: `axios` interceptors, `fetch` wrapper classes, NestJS HttpModule; resilience via `cockatiel`, `axios-retry`.
- **Python**: `httpx` clients with custom transports, `requests` Session wrappers, `tenacity` for retries.
- **Java/Kotlin**: Feign clients, RestTemplate/WebClient, OkHttp interceptors; Resilience4j.
- **Go**: `http.Client` with custom `Transport`; libraries like `go-resiliency`.

Document DI lifetime / scope conventions: what's singleton vs scoped/request vs transient.

### Step 8: API Layer

This step requires thoroughness — middleware, filters, and per-project auth/CORS differences are high-value for LLM code generation and easy to miss with surface-level scanning.

**Controllers / Route Handlers**:
- **.NET**: read 3–4 representative controllers ACROSS DIFFERENT API projects; identify base controller classes and what they provide (claims helpers, shared properties). Check if all controllers use the same base or newer ones differ. Look for API versioning configuration and `CacheProfile` attributes.
- **TS (NestJS)**: `@Controller` classes, `@UseGuards`, `@UseInterceptors`, route versioning.
- **TS (Express/Fastify)**: route registration files, route handler factories.
- **Python (FastAPI)**: `APIRouter` instances, dependency injection patterns, `tags`/`response_model`.
- **Python (Django/DRF)**: `ViewSet`, `APIView`, URL conf, serializers.
- **Java (Spring)**: `@RestController`, `@RequestMapping`, base controller classes.
- **Go**: route registration with `chi`/`gin`/`echo`, handler patterns.

**Middleware / Interceptors / Filters** — read ALL of them, not a sample:
- Identify every middleware/interceptor/filter class (or function).
- For each, document: what request data it reads (JWT claims, headers, cookies), what context/scoped service it populates (e.g., `CurrentUser`, `TenantContext`, `request.state.user`), and the exact mapping (e.g., "`country` claim → `CurrentUser.Country`").
- Document delegation/impersonation patterns — custom headers parsed in middleware that override identity. Document header format and how delegate claims/permissions are modeled.

If more than 10 such components exist, focus on the 5 most referenced.

**Action filters / decorators applied to endpoints** — search exhaustively for custom attributes/decorators applied per-endpoint. For each:
- What it does (input sanitization? service-availability check? rate-limiting? logging?)
- Usage count (grep across all controllers)
- Whether it's applied globally or per-action

**Auth — check EACH API project separately**:
- Read the bootstrap file (`Program.cs`/`Startup.cs`, `main.ts`, `main.py`, `Application.java`, etc.) of EVERY API project.
- Different projects often use different auth methods (JWT Bearer, OIDC cookie, ALB/reverse-proxy headers, Lambda Authorizer, session auth).
- Identify the ACTUAL identity provider in use (Okta, Entra ID, Auth0, Cognito, custom) — not what legacy config files suggest. The configuration class wired into the bootstrap reveals the real provider.

**CORS — check EACH API project separately**:
- Note restrictive (specific origins) vs permissive (allow-any) policies per project.

**Exception handling**:
- How unhandled exceptions become HTTP responses (exception filters, error middleware, framework defaults, problem-details responses).
- Map result/error states to HTTP status codes.

### Step 9: Testing Conventions

```
Read: test project manifest(s) for framework, mocking library, assertion library, coverage tool
```

**Stack hints**:
- **.NET**: NUnit/xUnit/MSTest + Moq/NSubstitute + FluentAssertions; coverage via coverlet.
- **TS**: Jest/Vitest/Mocha + ts-mockito/jest mocks + testing-library; coverage via built-in.
- **Python**: pytest/unittest + unittest.mock/pytest-mock + hypothesis; coverage via coverage.py.
- **Java/Kotlin**: JUnit5 + Mockito/MockK + AssertJ; coverage via JaCoCo.
- **Go**: built-in `testing`, `testify`, `gomock`; coverage via `go test -cover`.
- **Ruby**: RSpec / Minitest + WebMock + VCR.

**Test base class / fixture discovery — be exhaustive**:
- Search for ALL classes/files providing shared test setup: `*TestBase`, `*Base`, `*Fixture`, pytest `conftest.py` fixtures, RSpec shared contexts, JUnit `@ExtendWith` extensions, Go test helpers in `testutil/`.
- For each, document what setup it provides (DB transaction wrapping, mock initialization, HTTP context setup, seed data), its inheritance chain, and any special attributes (`[NonParallelizable]`, `@Execution(SAME_THREAD)`, pytest `serial` markers).
- Categorize: database test base, controller/HTTP test base, service test base, integration test base.

```
Read: 2–3 representative test files for naming patterns, assertion style, arrange/act/assert structure
Check: are tests unit, integration, or both? How is the DB handled (in-memory? testcontainers? transaction rollback? truncate?)
Look for: HTTP mocking libraries (WireMock, MockHttp, nock, responses, httpx MockTransport)
```

### Step 10: Coding Conventions & Build Commands

```
Read: linter/formatter configs (.editorconfig, eslint, prettier, ruff, rubocop, gofmt, ktlint)
Read: shared build config (Directory.Build.props, root tsconfig, root pyproject)
Observe: naming patterns across read files (visibility defaults, immutability, record/dataclass usage, collection types, async conventions)
Check: README.md, Makefile, package.json scripts, justfile, taskfile.yml, CI config (.github/workflows, .gitlab-ci.yml, Jenkinsfile) for build/run/test commands
Check: launch/run config (launchSettings.json, .vscode/launch.json, docker-compose for local dev)
```

### Step 11: Business Flows & Legacy Code

```
Trace: 3–5 key features end-to-end (route handler → use case → DB/external service)
  Prioritize features that touch external systems, async processing, or complex validation
Look for: comments, docstrings, XML docs, README files that reveal business domain
Identify: any projects/modules marked as legacy, deprecated, or being phased out
Check: parallel old/new implementations of the same feature
```

---

## Phase 2: Synthesize

Now open [references/output-template.md](references/output-template.md) and write the document section by section.

### Key Principles

**Use real code, not pseudocode.** For each pattern section, extract an actual code snippet from the codebase that best demonstrates the pattern. Trim it to the essential lines — remove imports/usings, collapse irrelevant properties with `// ...` (or the language's comment syntax), but keep the structure and naming authentic. If a snippet would exceed ~30 lines, trim it. The goal is pattern recognition, not full file dumps.

**Be specific, not generic.** Don't write "the project uses CQRS." Write "the project uses an in-house Mediator (NOT MediatR), located in `ProjectName.Core.Orchestration.Mediator`" or "the project uses NestJS `@CommandHandler` with auto-discovery via `CqrsModule`." Specificity is what makes this document useful for code generation.

**Match the depth of a stack-specialized analyzer.** When analyzing a .NET solution, the output must include every .NET-specific detail a .NET-focused analyzer would capture: DbContext patterns, `IPipelineBehavior` order, DI lifetimes, `DelegatingHandler` chains, per-project auth provider, entity configuration seed/check-constraint conventions, test base inheritance trees. The stack-agnostic framing of this skill is a layer above — it must never reduce per-stack precision. Apply the same rigor to other stacks: for TS, capture decorator metadata, module hierarchies, Prisma schema details; for Python, capture dependency overrides, SQLAlchemy session scoping, Pydantic model conventions; etc.

**Include the "don't do this" rules.** Conventions about what to avoid (don't pass CancellationToken to `SaveChangesAsync`, don't await inside loops in this codebase, don't add code to legacy projects, don't cross-reference slices) are as valuable as the positive patterns.

**Tables over prose.** Use tables for tech stack, project classification, entity catalogs, integration mappings, error code mappings, and quick-reference routing.

**ASCII diagrams for architecture.** Use box-drawing characters to show the project dependency diagram. Group projects by layer with clear arrows showing dependency direction.

### Writing the Sections

Follow the template in [references/output-template.md](references/output-template.md) for exact structure. For each section:

1. Check your exploration notes for the relevant facts
2. Extract the best code snippet(s) that demonstrate the pattern — in the codebase's actual language
3. Write the section following the template's format guidance
4. Include any "rules" or "conventions" you observed as explicit callouts

### Output

Save the final document as `architecture.md` in the workspace root (or the location the user specifies).

The document title should follow the pattern:
```
# {ProjectName} — Architecture Prompt
```

The opening block should state its purpose:
```
> **Purpose**: Feed this prompt to an LLM so it completely understands how to build, extend, debug, and test the {ProjectName} codebase.
```

---

## Handling Edge Cases

**Monorepo with multiple solutions/workspaces**: Ask the user which to analyze, or do them all as separate documents.

**Polyglot repos**: Identify each service's primary stack in Phase 0 and apply the appropriate per-stack guidance per service. Produce one document with clearly delimited per-service sections, or one document per service if they're independent.

**Very large codebases (50+ projects/packages)**: Focus on the primary dependency chain (API → Application → Core → Data → Infrastructure). Group utility/tool projects into a summary table rather than individual descriptions.

**Missing patterns**: If a section from the template doesn't apply (e.g., no domain events, no legacy code, no ORM because it's raw SQL), skip it. Don't pad the document with "N/A" sections.

**Ambiguous conventions**: When you see two different patterns for the same thing (e.g., some handlers use constructor injection, others use method injection; some routes use class-based controllers, others use functional handlers), document both and note which is the current/preferred approach.

**No README or CI config**: Infer build/run/test commands from the project structure and ecosystem defaults (`dotnet build`, `npm test`, `pytest`, `go test ./...`, `./gradlew test`, etc.) and note that these are inferred, not documented.
