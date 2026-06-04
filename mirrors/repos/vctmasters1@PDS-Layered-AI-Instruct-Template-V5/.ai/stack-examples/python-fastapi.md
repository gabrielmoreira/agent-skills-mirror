# Stack Example — Python + FastAPI

> Reference snippet. Copy into a real module's `.ai/instruct.md` and tune.

## Contents

| Section | What's here |
|---|-------------|
| [Code Organization](#code-organization) | Layering and DI rules |
| [Python conventions](#python-conventions) | Versions, naming, typing |
| [Async](#async) | I/O and background work rules |
| [Pydantic](#pydantic) | Request/response model discipline |
| [Testing](#testing) | pytest setup |

## Code Organization

- **Layering** (top → bottom, each layer only depends on the one below):
  - `routers/` — FastAPI `APIRouter`s; thin HTTP adapters.
  - `services/` — business logic; framework-agnostic.
  - `repositories/` — DB access only; returns ORM entities or domain objects.
  - `models/` — SQLAlchemy ORM models (one per table).
  - `schemas/` — Pydantic request/response models.
- **No business logic in routers.** A router endpoint: validate via Pydantic → call service → return response model. That's it.
- **Dependency injection** through FastAPI `Depends()` for repositories and services — never instantiate them at module import time.

## Python conventions

- Python 3.12+; `mypy --strict` clean; `ruff` + `ruff format` for lint/format.
- File names `snake_case.py`. Class names `PascalCase`. Function and variable names `snake_case`.
- No `from module import *`. No implicit re-exports.
- Type-annotate every public function signature. Internal helpers may rely on inference if obvious.

## Async

- All I/O is `async`. Use `asyncpg`/`SQLAlchemy 2.x async`, `httpx.AsyncClient`, etc.
- Never call `time.sleep` in an async path — use `asyncio.sleep`.
- Background work goes through an explicit task runner (Arq, Celery, RQ) — not `BackgroundTasks` for anything that must survive a redeploy.

## Pydantic

- Pydantic v2. Request models and response models are **separate classes** (never reuse a single model for both).
- Use `model_config = ConfigDict(from_attributes=True)` on response models that wrap ORM entities.
- Don't expose ORM models directly to the wire — always go through a response schema.

## Testing

- `pytest` + `pytest-asyncio` + `httpx.AsyncClient`.
- Database tests run against a real Postgres (testcontainers), not SQLite — they catch dialect bugs.
- Fixtures live in `tests/conftest.py`; no per-file fixture duplication.
