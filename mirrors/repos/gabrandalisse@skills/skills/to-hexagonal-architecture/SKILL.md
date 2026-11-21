---
name: to-hexagonal-architecture
description: Analyze an existing codebase in any language or framework and produce a phased, zero-breaking-change refactoring plan to migrate it to Hexagonal Architecture (Ports and Adapters). Use when the user asks to refactor, migrate, or restructure a service, API, or monolith into hexagonal architecture, ports and adapters, or clean architecture while preserving existing contracts.
---

# To Hexagonal Architecture

Analyze an existing repository in depth and design an atomic, phased refactoring plan to migrate it to **Hexagonal Architecture (Ports and Adapters)** without breaking any external contracts or observable behavior.

Respond in the same language as the user's request. Operate strictly in **Plan Mode**: inspect the codebase first and deliver the complete plan before modifying any files.

## When to Use

- The user asks to migrate or refactor an existing project into Hexagonal Architecture or Ports and Adapters.
- The user wants to decouple business logic from web frameworks, ORMs, databases, message brokers, or external SDKs.
- The user asks for a safe, incremental architectural refactoring plan with zero breaking changes.

## Core Principles

1. **Zero Breaking Changes (Golden Rule):** Preserve every existing external contract. Routes, HTTP methods, status codes, request/response payload schemas, headers, error formats, CLI flags, or queue message shapes must remain identical.
2. **Characterization Before Refactoring:** Never move or delete production logic until automated contract/characterization tests cover existing endpoints or entry points.
3. **Strict Dependency Rule:** Source code dependencies must always point inward toward `domain`. The domain layer must have zero imports from web frameworks, database drivers, ORMs, serialization libraries, or external SDKs.
4. **Stack-Idiomatic Adaptation:** Adapt directory paths, naming conventions, typing constructs, and test runners to the project's detected language and ecosystem (e.g., TypeScript/Node, Python, Go, Java/Kotlin, C#, Rust).

## Workflow

### Step 1: Codebase Discovery

Scan the repository before proposing any folder tree or migration steps:

1. **Stack and Tooling:** Inspect dependency manifests, compiler/linter configs, and test runners to identify the language, framework, validation library, ORM/query builder, and DI approach.
2. **Entry Points and Contracts:** Inventory all driving entry points (HTTP routes, GraphQL resolvers, gRPC services, message consumers, cron jobs), their validation schemas, middlewares/interceptors, and global error handlers.
3. **External Dependencies:** Inventory all driven side effects (databases, caches, HTTP/RPC clients, queues, file storage, environment configuration, loggers).
4. **Current Execution Flow:** Trace how data currently flows from entry point to persistence/external call and back, noting where business rules are mixed with transport or persistence details.

### Step 2: Design the Target Hexagonal Layout

Map the three concentric layers to the project's idiomatic source root (for example, `src/` in TypeScript/Rust, `internal/` in Go, `src/main/<lang>/` in JVM, or the main package directory in Python):

- **`domain/` (Pure Business Core - zero framework or I/O dependencies):**
  - `entities/` and `value-objects/`: Domain models encapsulating business rules, invariants, and self-validation.
  - `ports/in/`: Driving port interfaces defining use case contracts.
  - `ports/out/`: Driven port interfaces defining repository, external service, event publisher, and `LoggerPort` contracts.
  - `errors/`: Semantic domain exceptions (for example, `ResourceNotFoundError`, `DomainValidationError`, `ConflictError`).
- **`application/` (Use Case Orchestration):**
  - `use-cases/`: Implementations of `ports/in` coordinating domain entities and `ports/out`.
  - `dtos/`: Immutable input and output data structures decoupled from transport payloads and persistence entities.
- **`infrastructure/` (Technical Details and Adapters):**
  - `adapters/in/`: Driving adapters (HTTP controllers/handlers, consumer handlers), transport validation schemas, mappers (`TransportInput -> InputDTO` and `OutputDTO -> TransportOutput`), and a global error mapper translating `domain/errors` into the exact legacy error responses.
  - `adapters/out/`: Concrete implementations of `ports/out` (database repositories, HTTP clients, brokers) with persistence/external mappers so ORM models or SDK types never leak into `domain/`.
  - `config/`: Strict loading and startup validation of environment variables and runtime settings.
  - `di/` (Composition Root): Explicit wiring of driven adapters, use cases, and driving adapters via constructor injection, avoiding hidden singletons or service locators.
- **Bootstrap Separation:** Separate application construction (`buildApp` / factory function for isolated integration testing) from server/process startup (`main` / `listen`).

### Step 3: Enforce Engineering Standards in the Plan

Ensure every phase in the plan enforces:

- **Strong Typing and Immutability:** Forbid untyped escapes (such as `any` or raw untyped maps where typed structures apply) and favor immutable DTOs and Value Objects (`readonly`, frozen dataclasses, records, value types).
- **SOLID and Constructor Injection:** Keep classes and functions small with single responsibilities; inject interfaces via constructors.
- **Observability Without Coupling:** Preserve structured logging and request correlation context while keeping `domain/` and `application/` decoupled from specific logging libraries via `LoggerPort`.
- **Pyramidal Testing:**
  - Unit tests for `domain/` (pure invariants) and `application/` (mocking `ports/out`).
  - Integration/contract tests verifying real driving adapters against the application wiring using the stack's native in-memory test client (for example, `fastify.inject`, Supertest, FastAPI `TestClient`, Spring `MockMvc`, or Go `httptest`).

## Output Format (Plan Mode)

Deliver the response structured into these exact sections:

1. **Current Architecture Diagnosis:** Concise inventory of detected stack, entry points/endpoints, external dependencies, and main coupling hotspots.
2. **Target Directory Tree:** Complete proposed folder structure using the real module and feature names found in the repository.
3. **Phased Execution Plan:** Five atomic, verifiable phases:
   - **Phase 1 - Characterization Tests and Base Scaffolding:** Create contract tests locking current behavior, create target folders, config loader, and Composition Root (`di/`).
   - **Phase 2 - Domain Extraction:** Extract entities, value objects, domain errors, and `ports/in` + `ports/out` interfaces with unit tests.
   - **Phase 3 - Application Use Cases and Driven Adapters:** Implement use cases, DTOs, `adapters/out` repositories/clients, and persistence mappers.
   - **Phase 4 - Driving Adapters and Error Translation:** Refactor controllers/handlers to delegate to use cases via mappers, wire global error translation, and connect `di/`.
   - **Phase 5 - Legacy Cleanup and Final Verification:** Remove obsolete files, run the full test suite, linter, and type checker, and verify zero contract drift.
4. **Validation Checkpoints:** Explicit command or check at the end of each phase proving nothing broke before advancing to the next phase.

## Gotchas

- **Do not edit code prematurely:** Unless the user explicitly asks to start executing Phase 1 immediately, output only the plan first so they can review module boundaries.
- **Avoid over-abstraction on trivial CRUD:** Still separate `domain`, `application`, and `infrastructure` cleanly, but keep pass-through use cases concise rather than inventing artificial domain complexity.
- **Match legacy quirks:** If an existing endpoint returns a non-standard status code or error field name, document it in Phase 1 and preserve it in the `infrastructure` error mapper so existing clients do not break.