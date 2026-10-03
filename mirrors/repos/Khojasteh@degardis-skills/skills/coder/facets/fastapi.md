---
title: FastAPI
category: Framework and library
x-claim-provenance:
- claim: FastAPI runs synchronous path operations and dependencies in an external thread pool, while directly called utility functions receive no such automatic offloading.
  source: https://fastapi.tiangolo.com/async/
- claim: FastAPI validates and serializes returned data through the response model or return type, and response_model takes priority over the return annotation.
  source: https://fastapi.tiangolo.com/tutorial/response-model/
- claim: The exit code of dependencies with yield ran after the response before FastAPI 0.106.0, before the response from 0.106.0 so background tasks lost access to yielded resources, and after the response again from 0.118.0; 0.121.0 added Depends(scope="function") to close a dependency before the response; from 0.110.0 an exception caught in an except block and not re-raised is no longer forwarded to exception handlers.
  source: https://fastapi.tiangolo.com/advanced/advanced-dependencies/
- claim: app.dependency_overrides is a dict that maps an original dependency to the override FastAPI calls instead.
  source: https://fastapi.tiangolo.com/advanced/testing-dependencies/
- claim: Pydantic V2 renames BaseModel.dict() and json() to model_dump() and model_dump_json() and deprecates @validator in favor of @field_validator.
  source: https://pydantic.dev/docs/validation/latest/get-started/migration/
---

FastAPI's behavior is split between the framework, its validation library, and the ASGI server that runs it. Pydantic's major version changes model and validator syntax — version 2 renames `dict()` and `json()` to `model_dump()` and `model_dump_json()` and replaces `@validator` with `@field_validator` — so model code follows the version the project resolves rather than whichever form looks familiar.

Route and dependency scope, request and response models, validation and error shape, authentication and authorization, background-task ownership, and lifespan resources are behavioral contracts. The generated OpenAPI schema is public behavior too: client-visible status codes, headers, bodies, aliases, nullability, and field inclusion change it, and generated clients depend on it.

A response model or return type does more than document: FastAPI validates and serializes returned data through it, and `response_model` takes priority over the return annotation, so the declared output model, as the resolved version serializes it, decides which fields leave the application, and returning an internal or ORM object without a narrower output model is how fields such as password hashes reach clients.

Synchronous path operations and dependencies run in a thread pool, but a blocking call made directly inside an `async` function runs on the event loop and stalls every request that loop serves. Which of the two a slow path is doing decides both the defect and the remedy.

Cleanup in dependencies with `yield` is version-sensitive. From 0.106.0 their exit code ran before the response was sent, so background tasks lost access to resources such as a database session the dependency yielded; 0.118.0 moved the default back to after the response so streaming responses can use those resources; and 0.121.0 added `Depends(scope="function")` to close a dependency before the response. Since 0.110.0, an exception caught in a dependency's `except` block and not re-raised no longer reaches exception handlers. Code that shares resources between a request, its dependencies, and its background tasks therefore behaves according to the resolved FastAPI version.

Behavior is also wired indirectly through:

- router inclusion and prefixes
- middleware order and exception handlers
- dependency overrides, security dependencies, and response models
- aliases and the generated OpenAPI schema
- settings, ORM sessions, and ASGI host configuration

Other characteristic failures are request-scoped resources escaping their scope, validation performed only in a client model, and unbounded input.

A direct function call is evidence only when routing, dependencies, validation, serialization, and the ASGI lifecycle play no part; otherwise the evidence boundary is the configured application, where `app.dependency_overrides` replaces a dependency without changing routes. Evidence covers dependency scopes and cleanup, validation failures, allowed and denied security paths, the OpenAPI shape, response filtering, synchronous and asynchronous failure timing, cancellation, streaming, lifespan, and background work. Concurrency behavior depends on the configured server and event-loop setup, and a change must preserve schema compatibility and database transaction ownership unless altering them is part of its requested outcome. A performance result holds only for the deployed server, worker, reload, event-loop, validation, and serializer configuration it reproduces, and validation, serialization, dependency resolution, and database I/O are measurable at the real application boundary.
