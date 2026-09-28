# API, Dependencies, Database and Tooling Conventions

These standards cover FastAPI dependencies (validation, authorization, resource access), REST
design, response serialization, OpenAPI docs, database naming and SQL, migrations, API testing
and linting for the unified FastAPI + RAG + Agentic AI backend.

In generated projects, this file lives at `docs/standards/API_CONVENTIONS.md`. It works together
with `docs/standards/ASYNC_EXECUTION.md` and `docs/standards/PYDANTIC_STANDARDS.md`.

**Status labels:**

- 🟢 **Convention.** A proposed standard. Follow it by default.
- 🟡 **Needs approval.** An open team decision. Present the options and don't pick one silently.
- ⚪ **Illustrative.** Example code showing a pattern. It is not an implemented module, and it doesn't mandate a library or provider.

**Origin tags:**

- **[FBP]** Adopted from the FastAPI best-practices guidance.
- **[NEW]** Added or tightened for this template (typed dependencies, RAG/agent access scopes, ECS, SQS, safety).

---

## 0. Quick rules for code generation

| # | Rule | Origin | Status |
|---|---|---|---|
| 1 | Checks that need I/O (exists, is owned, is active, is unique) go in **dependencies**, never in Pydantic validators. | FBP | 🟢 |
| 2 | Dependencies return **typed objects** (`PostInternal`, `Principal`), not `dict`/`Mapping`. | NEW | 🟢 |
| 3 | Declare reusable dependencies once as `Annotated` aliases (`ValidPost = Annotated[PostInternal, Depends(valid_post_id)]`). | NEW | 🟢 |
| 4 | Build larger checks by **chaining** small dependencies. Rely on per-request caching; don't re-query. | FBP | 🟢 |
| 5 | Prefer `async def` dependencies, but only if everything they call is non-blocking (ASYNC_EXECUTION §2). | FBP | 🟢 |
| 6 | Authorization lives in dependencies and in `execution/`. RAG retrieval and agent tools receive an explicit **access scope**; the LLM never decides access. | NEW | 🟢 |
| 7 | Secrets (JWT keys, API keys) come from settings as `SecretStr`, never literals in code. | NEW | 🟢 |
| 8 | RESTful paths with **consistent path-parameter names** across modules so dependencies chain. | FBP | 🟢 |
| 9 | Declare the response shape once (`response_model` **or** return annotation). Know that FastAPI re-validates the output. | FBP | 🟢 |
| 10 | `BackgroundTasks` only for tiny best-effort side effects. Anything you would page someone about goes to SQS (Path B). | FBP + NEW | 🟢 |
| 11 | Validator messages reach clients as 422s. Keep them safe and stable. Never raise `HTTPException` in a validator. | FBP | 🟢 |
| 12 | OpenAPI docs are **off by default** and enabled per environment through settings. | FBP | 🟢 |
| 13 | Every route declares `status_code`, `summary`, `response_model` and its error `responses`. | FBP | 🟢 |
| 14 | Explicit DB constraint naming convention, `lower_snake` singular table names, `_at` / `_date` suffixes. | FBP | 🟢 (DB choice 🟡) |
| 15 | SQL-first: joins, filtering, aggregation and JSON building happen in the database. Pydantic validates the result. | FBP | 🟢 |
| 16 | Migrations are static, reversible, descriptively named and **never run from the app's lifespan**. | FBP + NEW | 🟡 (tooling) |
| 17 | Async test client (`httpx.AsyncClient` + `ASGITransport`) from day 0. | FBP | 🟢 |
| 18 | Swap collaborators in tests with `app.dependency_overrides`, never monkeypatching internals. | FBP | 🟢 |
| 19 | `ruff check --fix` and `ruff format` are the only lint/format tools. | FBP | 🟢 (config 🟡) |

### Where the code goes

| Code | Location |
|---|---|
| Resource-validation dependencies (`valid_<entity>_id`) | `<domain>/dependencies.py` |
| `current_principal`, `Principal`, `require_<permission>`, scope dependencies | `auth/dependencies.py` (JWT/JWKS validation in `auth/tokens.py`, policies in `auth/permissions.py`, API_SECURITY.md §2–§4) |
| Accessors for lifespan-created clients (`get_llm_client`, `get_vector_store`) | The owning module's `dependencies.py` (`llm/`, `providers/…` consumers via `rag/`, `agents/`) |
| Cross-domain dependencies (pagination params, request ID) | `common/dependencies.py` |
| Domain exceptions (`PostNotFound`) | `<domain>/exceptions.py`, subclassing the base in `src/exceptions.py` |
| Exception → `ErrorResponse` handlers | Registered once in `main.py`, defined in `src/exceptions.py` |
| DB metadata, naming convention, engine and session factory | `src/database.py` |
| SQL queries | `<domain>/service.py` (or a `<domain>/repository.py` if the team adopts one 🟡) |
| Migrations 🟡 | `alembic/` + `alembic.ini` at the project root, only after approval |
| Async test client and override fixtures | `tests/conftest.py` |
| Lint/format script | `scripts/lint.sh` 🟡 |

---

## 1. Dependencies as request validation

Pydantic validates **shape**. It can't know whether a post exists, whether the caller owns it, or
whether an email is taken. Those checks need I/O, so they go in dependencies **[FBP]**. Without
them, every endpoint repeats the same lookup, the same 404 and the same tests.

```python
# ⚪ Illustrative content for src/posts/dependencies.py
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.posts import service
from src.posts.exceptions import PostNotFound
from src.posts.schemas import PostInternal


async def valid_post_id(post_id: UUID) -> PostInternal:
    post = await service.get_by_id(post_id)
    if post is None:
        raise PostNotFound()
    return post


ValidPost = Annotated[PostInternal, Depends(valid_post_id)]
```

```python
# ⚪ Illustrative content for src/posts/router.py
from fastapi import APIRouter

from src.posts import service
from src.posts.dependencies import OwnedPost, ValidPost
from src.posts.schemas import PostInternal, PostResponse, PostUpdate

router = APIRouter()


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post: ValidPost) -> PostInternal:
    return post


@router.patch("/posts/{post_id}", response_model=PostResponse)
async def update_post(data: PostUpdate, post: OwnedPost) -> PostInternal:
    return await service.update(post.id, data)
```

### Rules 🟢

- **Name** resource dependencies `valid_<entity>_id` and permission dependencies `require_<permission>` / `valid_owned_<entity>`.
- **Return typed objects.** A dependency returns the internal Pydantic model (PYDANTIC_STANDARDS §3) or a small dataclass, never a raw `dict`, `Mapping` or ORM row that leaks into the router. **[NEW]** (the upstream guide returns dicts).
- **Raise domain exceptions**, not `HTTPException`. `PostNotFound` carries its status and stable `code`, and one handler in `main.py` renders it as `ErrorResponse`. The `code` catalogue is 🟡 (PYDANTIC_STANDARDS §12).
- **One job per dependency.** Existence, ownership and state checks are separate functions chained together (§2), so each is tested once.
- **No business workflows in dependencies.** They validate and resolve. Creating, updating and orchestrating stay in `service.py`.
- **Parse, don't re-validate.** Path/query/body parsing is FastAPI's job. The dependency receives already-typed parameters (`post_id: UUID`).

---

## 2. Chaining, caching and authorization

Dependencies can depend on other dependencies. FastAPI **caches each dependency's result for the
duration of one request**, so a dependency used by three others still runs once **[FBP]**.

```python
# ⚪ Illustrative content for src/auth/dependencies.py
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth import tokens as auth_tokens
from src.auth.config import AuthSettings, get_auth_settings
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import Principal

bearer = HTTPBearer(auto_error=False)   # the scheme itself is 🟡 (OAuth2, Cognito, API keys…)


async def current_principal(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> Principal:
    if creds is None:
        raise InvalidCredentials()
    return await auth_tokens.decode_access_token(creds.credentials, settings)   # raises InvalidCredentials (API_SECURITY.md §2.4)


CurrentPrincipal = Annotated[Principal, Depends(current_principal)]
```

```python
# ⚪ Illustrative content for src/posts/dependencies.py (continued)
async def valid_owned_post(post: ValidPost, principal: CurrentPrincipal) -> PostInternal:
    if post.creator_id != principal.user_id:
        raise UserNotOwner()
    return post


async def valid_active_creator(principal: CurrentPrincipal) -> UserInternal:
    user = await users_service.get_by_id(principal.user_id)
    if user is None or not user.is_active:
        raise UserIsBanned()
    if not user.is_creator:
        raise UserNotCreator()
    return user


OwnedPost = Annotated[PostInternal, Depends(valid_owned_post)]
ActiveCreator = Annotated[UserInternal, Depends(valid_active_creator)]

# A route using OwnedPost and ActiveCreator decodes the token exactly once.
```

### Caching rules 🟢

- The cache is **per request** and keyed by the dependency callable (and its security scopes). Nothing is shared between requests. Long-lived state belongs in the lifespan (ASYNC_EXECUTION §10), not in dependencies.
- Use `Depends(fn, use_cache=False)` only when you deliberately want a fresh value within one request. Say why in a comment.
- Because the same callable is cached, **don't wrap dependencies in lambdas or factories inside routes**. Each wrapper is a new callable and defeats the cache. Factories (`require_permission("posts:write")`) must be created once at module level.

### Authorization rules 🟢 [NEW]

- **Authentication** (who) is `current_principal`. **Authorization** (may they) is a chained dependency or a check in `execution/`. Both are enforced server-side on every request.
- Signing keys, audiences and issuers come from `AuthSettings` (`SecretStr`, `AUTH_` prefix). Never write a secret literal such as `"JWT_SECRET"` in code, examples or tests.
- Always pin the accepted algorithms and validate expiry, audience and issuer when decoding tokens. The identity provider, token format and library are 🟡. The full validation rules, JWKS handling, scopes and access-control layers are in `API_SECURITY.md` §2–§4.
- **RAG.** `rag/dependencies.py` resolves the principal into an `AccessScope` (tenants, collections, document ACLs). Retrieval receives the scope as a parameter and applies it as a **vector-store / database filter before ranking**. Never retrieve first and ask the LLM to ignore forbidden passages.
- **Agents.** `agents/dependencies.py` resolves the principal and its permitted tools into an execution context passed to `execution/`. Tool authorization is checked there before every call (PYDANTIC_STANDARDS §8: validation isn't authorization).
- **Guardrails.** Content-safety checks run after authorization, never instead of it (GUARDRAILS.md §1). `GuardrailBlocked` is a domain exception rendered as `ErrorResponse` like any other.
- **Background jobs.** The request's dependency cache ends with the request. A job message carries the principal's **ID**, never a token or resolved permissions, and the worker re-resolves and re-checks permissions when it runs, because they may have changed.

---

## 3. Async dependencies and resource dependencies

- **[FBP] Prefer `async def` dependencies.** A `def` dependency runs in the AnyIO thread pool, just like a `def` route, and takes one of the 40 default tokens (ASYNC_EXECUTION §2). For small non-I/O logic that thread hop is pure overhead.
- **[NEW] But never block inside an `async def` dependency.** If the dependency must call a sync SDK, either make it `def` deliberately (and budget the thread tokens) or offload the call with a limiter (ASYNC_EXECUTION §3). Using `async` around blocking code freezes the event loop for every request.
- **Resource dependencies use `yield`** (DB sessions, per-request transactions). Code after `yield` is cleanup and must not raise new errors that hide the original one.

```python
# ⚪ Illustrative content for src/database.py (async SQLAlchemy is 🟡 until the DB stack is approved)
async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:   # session_factory created in the lifespan
        yield session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
```

- **Don't hand request-scoped resources to background work.** A session from a `yield` dependency may be closed before a `BackgroundTasks` task or a queued job runs. Pass IDs; the task opens its own session.
- **Long-lived clients** (HTTP, LLM, vector store, queue) are created once in `main.py`'s lifespan and exposed through small accessor dependencies (`get_llm_client`). Tests override the accessor (§9).

---

## 4. REST design and path naming

- **[FBP] Follow REST.** Resources are nouns, HTTP methods are verbs: `GET /courses/{course_id}`, `GET /courses/{course_id}/chapters/{chapter_id}/lessons`, `GET /chapters/{chapter_id}`.
- **[FBP] Use the same path-parameter name for the same entity everywhere** so dependencies chain. If `/creators/{creator_id}` is really a profile that is also a creator, name the parameter `profile_id` and chain `valid_creator_id` on top of `valid_profile_id`:

```python
# ⚪ Illustrative.
# src/profiles/dependencies.py
async def valid_profile_id(profile_id: UUID) -> ProfileInternal: ...

# src/creators/dependencies.py
async def valid_creator_id(profile: ValidProfile) -> ProfileInternal:
    if not profile.is_creator:
        raise ProfileNotCreator()
    return profile

# src/creators/router.py
@router.get("/creators/{profile_id}", response_model=ProfileResponse)
async def get_creator(profile: ValidCreator) -> ProfileInternal:
    return profile
```

- **[NEW] Versioning and mounting.** All paths live under `/api/v1`, set once in `api/v1/router.py` together with each router's `prefix` and `tags`. Routers don't hard-code the version.
- **[NEW] Long-running operations** return `202 Accepted` with a job resource (`POST /ingestion-jobs` → `{"job_id": …}`, then `GET /ingestion-jobs/{job_id}`), not a request that blocks until the work finishes (ASYNC_EXECUTION §6).
- **[NEW] RAG and agent endpoints are resources too:** `POST /conversations/{conversation_id}/messages`, `POST /agent-runs`, `GET /agent-runs/{run_id}`. Streaming responses use SSE on a clearly named endpoint 🟡.
- Plural nouns, `kebab-case` path segments and `snake_case` path/query parameter names 🟢. JSON field casing is 🟡 (PYDANTIC_STANDARDS §12).

---

## 5. Response serialization

**[FBP] FastAPI validates your output again.** When a route returns a Pydantic object and a
`response_model` (or return annotation) is declared, FastAPI converts the object to plain data,
**validates it against `response_model`**, and only then serializes it to JSON. A model returned
from a route is therefore constructed twice, and its validators run twice.

### Rules 🟢

- Declare the response shape **once**: either `response_model=` or the return annotation. When they differ on purpose (return `PostInternal`, publish `PostResponse`), use `response_model=`; FastAPI's validation then **filters out** internal fields, which is a security feature.
- Keep validators pure, deterministic and cheap. They run on the way out, too (PYDANTIC_STANDARDS §1).
- Don't convert manually (`model.model_dump()` then return the dict). It adds a step and doesn't skip the re-validation.
- Returning a `Response` directly (`Response(model.model_dump_json(), media_type="application/json")`) **skips** validation and filtering. Do it only on a profiled hot path, with the exact public model, and keep `response_model` for the docs. Say why in a comment. **[NEW]**
- Large list responses: paginate (`Page[T]`) rather than optimizing serialization.

---

## 6. Sync SDKs from async code

**[FBP]** If a library has no async version, don't call it directly inside `async def`. Run it in
the thread pool with `run_in_threadpool` or `anyio.to_thread.run_sync`. The full rules (limiters,
timeouts on the client, cancellation, thread safety) are in ASYNC_EXECUTION §3–§4 and take
precedence over the short upstream example.

---

## 7. `BackgroundTasks` vs the queue

**[FBP]** `BackgroundTasks` runs **after the response is sent, in the same worker process**. If the
process dies, the task is gone: no retry, no visibility, no scheduling. On ECS, tasks are stopped
routinely by deployments and scale-in.

| Use `BackgroundTasks` when… | Use SQS → ECS worker / Lambda (Path B) when… |
|---|---|
| The task is tiny (well under a second) | It takes seconds to hours |
| Losing it is acceptable | You need retries, a DLQ or an audit trail |
| It's in-process and light (emit a metric, write a log line) | It's CPU-heavy, calls an LLM, or needs its own worker pool |
| No scheduling or rate limiting is needed | You need scheduling, rate limiting or backpressure |

**Rule of thumb [FBP]:** if you would page someone when the task is lost, it doesn't belong in
`BackgroundTasks`.

**[NEW] Adaptations for this template:**

- The upstream guide suggests Celery, Arq or RQ for durable work. Here the durable path is **SQS**, and Celery vs native SQS workers is still 🟡 (ASYNC_EXECUTION §9). Arq and RQ need Redis, which isn't approved. Don't add any of them.
- Emails, webhooks and notifications that users expect to receive are **not** best-effort. Enqueue them through `execution/job_scheduler.py`.
- Never run ingestion, embedding, LLM calls, evaluation or agent steps in `BackgroundTasks`.

---

## 8. Validator errors become 422 responses

**[FBP]** A `ValueError` raised in a validator of a request-body model becomes a `ValidationError`,
and FastAPI returns it to the client as a 422 with your message.

### Rules 🟢

- Messages must be **safe for clients** and name the rule ("must contain an upper-case letter"), never internals: table names, regexes with secrets, stack details, other users' data.
- Use `PydanticCustomError("password_too_weak", "...")` when clients or tests need a **stable error type** instead of the generic `value_error`. **[NEW]**
- Never raise `HTTPException` (or domain exceptions) inside validators. Validators stay framework-free so the same schema works in workers and tests.
- **[NEW] LLM-output and tool-argument models are never request bodies.** Their validation errors are internal. They go to the bounded-retry loop and are sanitized before being fed back to the model (PYDANTIC_STANDARDS §9), and they are never returned verbatim to users.
- Whether the default `{"detail": [...]}` 422 body is re-shaped into `ErrorResponse` is 🟡 (PYDANTIC_STANDARDS §12).

---

## 9. OpenAPI docs

### Hide docs by default [FBP] 🟢

Unless the API is public, docs are disabled and turned on only in an explicit list of
environments. Read the environment from settings (PYDANTIC_STANDARDS §4), not from a separate
`.env` parser.

```python
# ⚪ Illustrative content for src/main.py
from fastapi import FastAPI
from src.config import get_app_settings

settings = get_app_settings()          # read once while building the app, not at import time elsewhere

app_kwargs: dict = {"title": settings.app_name, "lifespan": lifespan}
if settings.environment not in settings.show_docs_environments:   # e.g. {"local", "staging"} 🟡
    app_kwargs["openapi_url"] = None   # also disables /docs and /redoc

app = FastAPI(**app_kwargs)
```

The exact environment names and whether staging docs sit behind auth are 🟡.

### Document every route [FBP] 🟢

- Set `response_model`, `status_code`, `summary` and `description`. Tags come from `api/v1/router.py`.
- List the non-default outcomes in `responses=`, using `ErrorResponse` for errors, so clients see every shape they can receive.

```python
# ⚪ Illustrative.
@router.post(
    "/ingestion-jobs",
    response_model=IngestionJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue documents for ingestion",
    description="Validates the request, stores inputs and enqueues an ingestion job.",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Knowledge base not found"},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Job already exists"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Queue unavailable, retry later"},
    },
)
async def create_ingestion_job(data: IngestionJobCreate, kb: ValidKnowledgeBase) -> IngestionJobResponse: ...
```

- Stable `operationId`s for generated clients (`generate_unique_id_function`) are 🟡.
- Field `description`s on API schemas appear in the docs. Keep them accurate. For LLM-output schemas they are also prompt text (PYDANTIC_STANDARDS §6).

---

## 10. Database conventions 🟡 (engine, ORM and driver need approval)

This template doesn't choose a database. The rules below apply **once a relational database is
approved**. The examples assume PostgreSQL and SQLAlchemy 2.0's async API, which is the upstream
recommendation for new projects. Vector storage stays behind `providers/vector_store/` whatever
the relational choice.

### Constraint naming convention [FBP] 🟢

Set explicit names for indexes and constraints instead of relying on generated ones. Migrations
become deterministic and constraint errors become readable.

```python
# ⚪ Illustrative content for src/database.py
from sqlalchemy import MetaData

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
```

Every ORM model shares this one `metadata` (one declarative base in `src/database.py`).

### Table and column naming [FBP] 🟢

- `lower_snake_case`, **singular** table names: `post`, `post_like`, `user_playlist`.
- Group related tables with a module prefix: `payment_account`, `payment_bill`, `rag_document`, `rag_chunk`, `agent_run`, `agent_step`.
- Be consistent: `profile_id` everywhere, but a more specific name where only a subset is valid (`creator_id` when only creators qualify, `course_id` in `chapter`).
- `_at` suffix for timestamps, `_date` for dates. **[NEW]** `_at` columns are `timestamp with time zone`, and map to `UtcDatetime` in schemas (PYDANTIC_STANDARDS §2). Never store naive timestamps.

### SQL-first, Pydantic second [FBP] 🟢

- The database does joins, filtering, sorting, pagination and aggregation faster than CPython. Do it in SQL.
- For nested responses, build the JSON in the database (`json_build_object`, `json_agg`) and validate the result with the response model. Don't load rows and assemble nested dicts in Python loops.
- Never fetch everything and filter in Python. Push `WHERE`, `LIMIT` and access-scope filters (§2) into the query.

```python
# ⚪ Illustrative content for src/posts/service.py (SQLAlchemy 2.0 async)
from sqlalchemy import desc, func, select
from sqlalchemy.sql.functions import coalesce

async def get_creator_posts(
    session: AsyncSession, creator_id: UUID, *, limit: int = 20, offset: int = 0
) -> list[PostInternal]:
    creator = func.json_build_object(
        "id", Profile.id,
        "first_name", Profile.first_name,
        "last_name", Profile.last_name,
        "username", Profile.username,
    ).label("creator")
    stmt = (
        select(Post.id, Post.slug, Post.title, creator)
        .join(Profile, Post.owner_id == Profile.id)
        .where(Post.owner_id == creator_id)
        .order_by(desc(coalesce(Post.updated_at, Post.published_at, Post.created_at)))
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).mappings().all()
    return [PostInternal.model_validate(row) for row in rows]
```

### Access and sessions [NEW] 🟢

- One engine and session factory per process, created in the lifespan. Pool size × Uvicorn workers × ECS tasks must fit the database's connection limit 🟡 (sizes need approval).
- Sessions come from the `get_db_session` dependency in routes and from an explicit `async with session_factory()` in workers and Lambda handlers.
- A sync driver inside `async def` code blocks the event loop. If a sync driver is ever used, follow ASYNC_EXECUTION §2–§3.
- Raw SQL uses bound parameters only. Never format user or LLM text into SQL.

---

## 11. Migrations 🟡 (Alembic adoption needs approval)

Nothing in this skill creates migrations. When the team approves Alembic, these rules apply:

- **[FBP] Static and reversible.** Every migration has a working `downgrade()`. If a migration depends on dynamic data, only the **data** may be dynamic, never the **structure**.
- **[FBP] Descriptive names.** Every revision has a slug that explains the change (`alembic revision -m "post_content_idx"`).
- **[FBP] Human-readable file names**, `date_slug.py`:

  ```ini
  # alembic.ini
  file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
  ```

- **[NEW] Review autogenerated migrations.** Autogenerate misses or misreads renames, server defaults, enum changes and some type changes. Treat its output as a draft.
- **[NEW] Never run migrations from the FastAPI lifespan.** Several ECS tasks start at once and would race. Run them as a separate one-off step (a one-off ECS task or a deploy step) before the new version takes traffic. The mechanism is 🟡.
- **[NEW] Expand, then contract.** During a rolling deploy, old and new code run together. Add columns and tables first, deploy, backfill, and remove old columns in a later release.
- Long backfills of RAG or agent data are **jobs** (Path B), not migrations.

---

## 12. Testing the API

### Async client from day 0 [FBP] 🟢

Starting with a sync `TestClient` and switching later tends to end in event-loop errors in
integration tests. Use `httpx.AsyncClient` with `ASGITransport` from the start. Don't use
`async_asgi_testclient`; it is unmaintained.

```python
# ⚪ Illustrative content for tests/conftest.py
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_create_post(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/posts", json={"title": "t", "slug": "t"})
    assert resp.status_code == 201
```

**[NEW] Things the upstream example leaves out:**

- **`ASGITransport` doesn't run the lifespan.** Clients and limiters created there won't exist. Either override their accessor dependencies with fakes (preferred for unit-level API tests) or wrap the app in a lifespan manager such as `asgi-lifespan` 🟡 (new dependency).
- **Pick one async test plugin** 🟡: `pytest-asyncio` (with `asyncio_mode = "auto"`, or `@pytest.mark.asyncio` plus `pytest_asyncio.fixture` in strict mode) or AnyIO's pytest plugin (`@pytest.mark.anyio`). Don't mix them.
- Integration tests that need a database use a real test database and roll back per test 🟡 (container vs shared instance needs approval). They live in `tests/integration/`.

### Override dependencies, don't monkeypatch [FBP] 🟢

`app.dependency_overrides` swaps any dependency for a fake: auth, settings, LLM client, vector
store, queue publisher.

```python
# ⚪ Illustrative content for tests/conftest.py (continued)
from src.auth.dependencies import current_principal
from src.auth.schemas import Principal
from src.llm.dependencies import get_llm_client

FAKE_PRINCIPAL = Principal(user_id=UUID("00000000-0000-0000-0000-000000000001"), permissions=frozenset())


@pytest.fixture
def as_user():
    app.dependency_overrides[current_principal] = lambda: FAKE_PRINCIPAL
    yield FAKE_PRINCIPAL
    app.dependency_overrides.pop(current_principal, None)


@pytest.fixture
def fake_llm(fake_llm_client):
    app.dependency_overrides[get_llm_client] = lambda: fake_llm_client
    yield fake_llm_client
    app.dependency_overrides.pop(get_llm_client, None)
```

### Rules 🟢

- Override the **exact callable** used in `Depends(...)`. Overriding a different function with the same name does nothing.
- Remove only the overrides you added (`pop`), so fixtures compose. Use `clear()` only in a single session-level teardown.
- Overrides are opt-in fixtures. Make auth `autouse` only in a test package where every test is authenticated, and test the unauthenticated path explicitly (401, 403, forbidden access scope).
- Test each validation dependency once (exists / missing / not owned), then trust it in route tests.
- No test calls a live LLM, vector store, queue or AWS service, and no test needs real credentials (PYDANTIC_STANDARDS §11).

---

## 13. Linting and formatting

**[FBP]** Ruff replaces black, isort, autoflake and most flake8 plugins, and it is fast enough to
run on every save. Formatting is not a code-review topic.

```sh
#!/bin/sh -e
# ⚪ Illustrative content for scripts/lint.sh
set -x

ruff check --fix src tests
ruff format src tests
```

- 🟢 Ruff is the only linter and formatter. Don't add black, isort or flake8 alongside it.
- 🟢 Generated code must pass `ruff check` and `ruff format --check` once ruff is configured.
- 🟡 The rule selection, line length and target Python version in `[tool.ruff]`. Nothing is added to `pyproject.toml` until approved, and ruff isn't installed by this skill.
- 🟡 Pre-commit hooks vs a plain script (the upstream team found the script sufficient).
- 🟡 A type checker (mypy or pyright) and its strictness.
- CI enforcement comes in a later phase.

---

## 14. Decisions still requiring team approval 🟡

1. **Auth.** Identity provider, token format and library, bearer scheme, permission model and the `Principal` fields.
2. **Access scopes.** How RAG `AccessScope` is modelled (tenant, collection, document ACL) and enforced in each vector store.
3. **Error catalogue.** Domain exception codes and the 422 shape (shared with PYDANTIC_STANDARDS §12).
4. **Docs exposure.** Environment names for docs, and whether non-local docs require auth.
5. **Operation IDs** for generated clients.
6. **Database.** Engine, ORM (SQLAlchemy 2.0 async proposed), driver, pool sizes, and whether a repository layer is used.
7. **Migrations.** Alembic adoption, and the mechanism that runs migrations on ECS.
8. **Testing stack.** `pytest-asyncio` vs AnyIO plugin, lifespan handling in tests, and the integration-test database.
9. **Linting.** Ruff rules and line length, pre-commit vs script, and a type checker.
10. **Streaming endpoints.** SSE conventions for RAG answers and agent runs.
