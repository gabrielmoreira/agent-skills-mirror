# Backend Helpers DOX

## Purpose

- Own shared Python framework utilities used by agents, APIs, tools, plugins, WebSockets, persistence, and runtime services.
- Keep cross-cutting behavior stable and tested.

## Ownership

- Helper modules provide reusable services; feature-specific route handlers belong in `api/`, tool behavior in `tools/`, and plugin-local logic inside plugin directories.
- Security, auth, settings, file access, plugin discovery, extension dispatch, notifications, state snapshots, scheduler, tunnel, and WebSocket primitives live here.

## Local Contracts

- Preserve public helper APIs used by core code and plugins unless all callers, docs, and tests are updated.
- Use structured parsers and serializers for YAML, JSON, paths, and URLs instead of ad hoc string handling.
- Keep path handling constrained to intended roots for user files, uploads, downloads, projects, and workdirs.
- Project metadata defaults must remain backwards-compatible; missing `include_agents_md` is treated as enabled and project instruction file content is injected with an explicit source path.
- Do not hardcode secrets, provider keys, local absolute paths, or environment-specific values.
- Use `RepairableException` for errors an agent may be able to fix.

## Work Guidance

- Prefer cohesive helper modules over adding unrelated utilities to large files.
- Keep imports acyclic where possible; defer imports inside functions only when needed to avoid startup cycles.
- For changes touching auth, CSRF, files, plugins, tunnels, WebSockets, or model calls, read the caller and tests before editing.

## Verification

- Run targeted tests for changed helper modules.
- Run security regression tests for auth, CSRF, filesystem, WebSocket, tunnel, upload, or image-serving changes.

## Child DOX Index

No child DOX files.
