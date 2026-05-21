# Extraction Guide

## Primary: graphify

graphify is the primary extraction engine. Run it first:

```bash
pip install graphifyy
graphify . --no-viz
```

### What graphify produces for docs

| Output | Use for |
|--------|---------|
| `GRAPH_REPORT.md` god nodes | Architecture section: "what everything connects through" |
| `GRAPH_REPORT.md` communities | Module breakdown: how to organise the API reference |
| `graphify query "API routes"` | `docs/API.md` route list |
| `graphify query "data models"` | Request/response types in API docs |
| `graphify query "auth flow"` | Authentication section in README |
| `graphify query "entry point"` | Quick start and installation section |
| `rationale_for` nodes in graph | Architecture decisions and "why it was built this way" |

### Querying the graph

```bash
# Routes
graphify query "show all HTTP routes and endpoints" --graph graphify-out/graph.json

# Types
graphify query "what are the main data models, interfaces, and types?" --graph graphify-out/graph.json

# Auth
graphify query "how does authentication and authorization work?" --graph graphify-out/graph.json

# Config
graphify query "what environment variables and configuration options are available?" --graph graphify-out/graph.json

# Architecture
graphify query "what are the most connected components and how do modules relate?" --graph graphify-out/graph.json

# Entry point
graphify query "how is the application started and initialised?" --graph graphify-out/graph.json
```

### Reading graph output

Every edge in graphify output is tagged:
- `EXTRACTED` — found directly in source code. Treat as fact.
- `INFERRED` — reasonable inference with confidence score (0.0-1.0). Use in docs but qualify: "likely", "appears to", or add `[verify]`.
- `AMBIGUOUS` — flagged for review. Do not include in docs without manual verification.

---

## Fallback: Custom Extraction Scripts

Use this when graphify is unavailable. The scripts produce `.docs-extract.json` with the same structure used to write docs.

---

## TypeScript / JavaScript Projects

### Next.js (App Router)
- Routes: `app/**/route.ts` — exported HTTP method handlers (GET, POST, etc.)
- Pages: `app/**/page.tsx` — document as "page components", not endpoints
- Types: `src/types/**/*.ts`, `lib/types.ts` — shared TypeScript interfaces
- Utilities: `lib/**/*.ts`, `utils/**/*.ts` — exported helper functions
- Key files to read: `app/layout.tsx` (app metadata), `next.config.ts` (config)

### Next.js (Pages Router)
- Routes: `pages/api/**/*.ts` — default exported handler functions
- Types: same as App Router
- Key config: `next.config.js`

### Express
- Routes: calls to `app.get()`, `app.post()`, `router.get()`, etc.
- Middleware: exported functions used as middleware
- Models: any class or interface representing data shapes
- Key files: `src/app.ts` or `app.js`, `src/routes/`, `src/models/`

### Hono
- Routes: `app.get('/path', handler)`, `app.post()`, etc. Same pattern as Express.
- Zod schemas: exported `z.object(...)` definitions. Document as request/response schemas.

### Fastify
- Routes: `fastify.get('/path', opts, handler)` calls
- Schemas: inline JSON schema objects in route options

---

## Python Projects

### FastAPI
- Routes: functions decorated with `@app.get()`, `@app.post()`, `@router.get()`, etc.
- Pydantic models: classes extending `BaseModel`. Document as request/response schemas.
- Dependencies: functions used with `Depends()`. Document if they affect auth or request shape.
- Key files: `main.py`, `app/main.py`, `routers/`

### Flask
- Routes: functions decorated with `@app.route('/path', methods=['GET'])` or `@blueprint.route()`
- Models: SQLAlchemy model classes (extend `db.Model`)
- Key files: `app.py`, `__init__.py`, `routes/`, `models/`

### Django REST Framework
- Views: classes extending `APIView`, `ViewSet`, `ModelViewSet`
- Serializers: classes extending `Serializer` or `ModelSerializer`
- URLs: `urlpatterns` lists. Read `urls.py` directly.
- Key files: `views.py`, `serializers.py`, `urls.py`, `models.py`

---

## Output JSON Schema

The extraction scripts output `.docs-extract.json`:

```json
{
  "projectName": "my-api",
  "language": "typescript",
  "framework": "express",
  "entryPoints": ["src/index.ts"],
  "functions": [
    {
      "name": "createUser",
      "signature": "createUser(name: string, email: string): Promise<User>",
      "description": "Creates a new user record in the database",
      "params": [
        { "name": "name", "type": "string", "description": "" },
        { "name": "email", "type": "string", "description": "" }
      ],
      "returns": "Promise<User>",
      "file": "/src/services/user.ts",
      "isExported": true
    }
  ],
  "routes": [
    {
      "method": "POST",
      "path": "/users",
      "handler": "createUserHandler",
      "description": "",
      "file": "/src/routes/users.ts"
    }
  ],
  "types": [
    {
      "name": "User",
      "kind": "interface",
      "definition": "interface User { id: string; name: string; email: string; }",
      "description": "",
      "file": "/src/types/user.ts"
    }
  ],
  "dependencies": { "express": "^4.18.0" },
  "scripts": { "start": "node dist/index.js" }
}
```

---

## What to Prioritise When Writing Docs

From the extracted data, prioritise in this order:

1. Routes — developers integrating with your API need these most
2. Public types and interfaces — define the data contract
3. Exported utility functions — frequently called helpers
4. Classes — especially models and services
5. Internal or private functions — lowest priority, often skip

Skip:
- Test files (`*.test.ts`, `*.spec.ts`, `_test.py`)
- Generated files (`*.generated.ts`, Prisma client output)
- Config files with no user-facing exports
