# API Handlers DOX

## Purpose

- Own backend HTTP API handlers and WebSocket handler entry points.
- Keep route-level behavior, authentication, CSRF, input parsing, and response shapes explicit.

## Ownership

- Files in this directory are discovered by the route registration layer in `helpers/api.py` and WebSocket registration code.
- `ws_*.py` files define WebSocket namespaces or handlers through `helpers.ws.WsHandler`.
- Plugin-provided API handlers belong inside plugin `api/` folders and follow the same base contracts.

## Local Contracts

- HTTP handlers must derive from `helpers.api.ApiHandler`.
- Implement `async def process(self, input: dict, request: Request) -> dict | Response`.
- Override `get_methods()`, `requires_auth()`, `requires_csrf()`, `requires_api_key()`, or `requires_loopback()` only when the endpoint contract requires it.
- Keep CSRF and authentication protections intact for browser-facing state-changing endpoints.
- WebSocket handlers must derive from `helpers.ws.WsHandler` and validate event data before using it.
- Do not return secrets, raw environment values, private files, or unfiltered exception details to clients.

## Work Guidance

- Use helpers for shared behavior instead of duplicating persistence, auth, file, project, plugin, or notification logic in endpoints.
- Keep request and response payloads stable; update frontend callers and tests together when payloads change.
- Prefer `Response` for files, redirects, status codes, and plain-text errors; return dictionaries for JSON success payloads.

## Verification

- Run targeted `pytest tests/test_*api*.py`, endpoint-specific tests, or WebSocket tests after changing handler behavior.
- For auth, CSRF, upload/download, tunnel, or file endpoints, run the nearest security regression tests.

## Child DOX Index

No child DOX files.
