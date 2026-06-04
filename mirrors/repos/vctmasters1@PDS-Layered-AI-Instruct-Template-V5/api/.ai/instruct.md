# API Module — AI Instructions

**Scope**: Authoritative for all files in the `api/` module and subdirectories
**Last Updated**: 2026-06-02

> When working in `api/` or its subdirectories, this file is more authoritative than the workspace root `.ai/instruct.md`.
> See `.github/copilot-instructions.md` for the depth-priority hierarchy.

---

## Contents

| Section | What's here |
|---|-------------|
| [Module Overview](#module-overview) | Purpose and scope of the API module |
| [Code Generation Rules](#code-generation-rules) | Mandatory procedures for endpoint creation |
| [Endpoint Naming Convention](#endpoint-naming-convention) | Semantic naming pattern for discoverability |
| [Integration with Central Generator](#integration-with-central-generator) | How to use `api/endpoint_generator.py` |
| [Discovery & Validation](#discovery--validation) | Automated endpoint analysis pipeline |
| [Common Patterns](#common-patterns) | Example implementations across frameworks |

---

## Module Overview

This module contains all API endpoint definitions, route handlers, and API-related logic.

**Purpose**: Build consistent, discoverable, testable API endpoints following semantic naming conventions.

**Key principle**: Every endpoint follows `{resource}_{action}[_{detail}]` pattern that enables:
- Automated discovery of all endpoints in the codebase
- HTTP method inference and validation
- Grep-based endpoint search (find all user endpoints, all list endpoints, etc.)
- Generated API documentation indexed by resource and action
- Consistent REST path generation

---

## Code Generation Rules

### When Creating Any API Endpoint

**Use the governed tool**: `.ai/agents/tools/generate-api-endpoint.json`

**Order of operations** (mandatory):

1. **Determine resource and action** — identify the resource (user, product, invoice, etc.) and the action (list, create, detail, update, delete, search, export, import, batch, validate, webhook, auth, subscribe, unsubscribe). Consult `.ai/api-conventions.md` for standard actions.

2. **Generate endpoint name** — use the central generator to enforce naming rules:
   ```bash
   python api/endpoint_generator.py --resource user --action create --verbose
   # Output: user_create (POST /api/v1/users)
   ```

3. **Verify HTTP method** — confirm the action maps to correct HTTP verb(s):
   ```bash
   python api/endpoint_generator.py --list-actions
   # Shows create→POST, list→GET, delete→DELETE, etc.
   ```

4. **Check for conflicts** — ensure the endpoint name is unique:
   ```bash
   python api/endpoint_generator.py --check-exists user_create
   ```

5. **Write the endpoint** — implement the route handler using the generated endpoint name

6. **Scan to validate** — after endpoint is written, update the discovery registry:
   ```bash
   python api/endpoint_discovery.py --scan-root ./api --framework auto --output api-endpoints.json
   ```

7. **Verify discovery** — confirm the endpoint was found with correct resource/action extraction:
   ```bash
   python api/endpoint_discovery.py --scan-root ./api --framework auto --validate user_create
   ```

---

## Endpoint Naming Convention

### Pattern: `{resource}_{action}[_{detail}]`

**Examples:**
- List all users → `user_list` (GET)
- Create a user → `user_create` (POST)
- Get user by ID → `user_detail` (GET)
- Update a user → `user_update` (PUT)
- Delete a user → `user_delete` (DELETE)
- Search products → `product_search` (GET)
- Export invoices as PDF → `invoice_export_pdf` (GET)
- Batch create orders → `order_batch` (POST)
- Validate email → `email_validate` (POST)

### Standard Actions & HTTP Methods

→ **[Master Registry](../../.ai/api-conventions.md)** — complete list of 14 standard actions

Quick reference:
| Action | HTTP Method | Purpose | Example |
|--------|-----------|---------|---------|
| `list` | GET | Read collection | `user_list` → GET /api/v1/users |
| `create` | POST | Create resource | `user_create` → POST /api/v1/users |
| `detail` | GET | Read single resource | `user_detail` → GET /api/v1/users/{id} |
| `update` | PUT/PATCH | Update resource | `user_update` → PUT /api/v1/users/{id} |
| `delete` | DELETE | Remove resource | `user_delete` → DELETE /api/v1/users/{id} |
| `search` | GET/POST | Query/filter | `product_search` → GET /api/v1/products/search |
| `export` | GET | Generate file | `invoice_export_pdf` → GET /api/v1/invoices/{id}/export.pdf |
| `import` | POST | Bulk upload | `user_import` → POST /api/v1/users/import |
| `batch` | POST | Bulk operation | `order_batch` → POST /api/v1/orders/batch |
| `validate` | POST/GET | Validation check | `email_validate` → POST /api/v1/email/validate |
| `webhook` | POST | Event notification | `order_webhook` → POST /api/v1/orders/webhook |
| `auth` | POST | Authentication | `user_auth` → POST /api/v1/users/auth |
| `subscribe` | POST/PUT | Add to collection | `notification_subscribe` → POST /api/v1/notifications/subscribe |
| `unsubscribe` | DELETE/POST | Remove from collection | `notification_unsubscribe` → DELETE /api/v1/notifications/unsubscribe |

---

## Integration with Central Generator

### The Generator CLI

```bash
# Generate endpoint name with path
python api/endpoint_generator.py --resource <RESOURCE> --action <ACTION> [--detail <DETAIL>] --verbose

# List all standard actions
python api/endpoint_generator.py --list-actions

# Validate an endpoint name
python api/endpoint_generator.py --validate <ENDPOINT_NAME>

# Check if endpoint already exists
python api/endpoint_generator.py --check-exists <ENDPOINT_NAME>

# Set API version
python api/endpoint_generator.py --resource user --action create --api-version v2
```

### Why Use the Central Generator?

- **Prevents mistakes** — enforces naming rules and HTTP method consistency at creation time
- **Searchable naming** — enables grep-based discovery of all endpoints by resource or action
- **Auto-path generation** — generates REST paths automatically from resource/action pairs
- **Conflict detection** — catches duplicate endpoint definitions before they cause issues
- **Documentation** — generated names map directly to REST conventions

---

## Discovery & Validation

### Discovery Phase

Scan the API module to find all endpoints across frameworks:

```bash
python api/endpoint_discovery.py --scan-root ./api --framework auto --output api-endpoints.json
```

**Supported frameworks**:
- `auto` — auto-detect (Express, FastAPI, Django patterns)
- `express` — Express.js (app.get, router.post, etc.)
- `fastapi` — FastAPI (@app.get decorators)
- `django` — Django (path, re_path functions)
- `generic` — fallback pattern for other frameworks

**Output**: JSON file with endpoint paths, HTTP methods, detected resource/action, line numbers, and context

### Validation Phase

Analyze discovered endpoints for compliance:

```bash
# Validate specific endpoint
python api/endpoint_discovery.py --scan-root ./api --validate user_create

# Generate compliance report
python api/endpoint_discovery.py --scan-root ./api --framework auto --output api-endpoints.json
```

**Validation checks**:
- ✅ Endpoint name follows `{resource}_{action}[_{detail}]` pattern
- ✅ HTTP method matches standard action mapping
- ✅ Resource/action pair is recognized in registry
- ✅ No duplicate endpoint definitions
- ✅ Path template is REST-compliant

---

## Common Patterns

### Express.js

```javascript
const express = require('express');
const router = express.Router();

// user_list: GET /api/v1/users
router.get('/users', (req, res) => {
  // List all users
});

// user_create: POST /api/v1/users
router.post('/users', (req, res) => {
  // Create a new user
});

// user_detail: GET /api/v1/users/:id
router.get('/users/:id', (req, res) => {
  // Get user by ID
});

// user_update: PUT /api/v1/users/:id
router.put('/users/:id', (req, res) => {
  // Update user
});

// user_delete: DELETE /api/v1/users/:id
router.delete('/users/:id', (req, res) => {
  // Delete user
});

// product_search: GET /api/v1/products/search
router.get('/products/search', (req, res) => {
  // Search products
});

// invoice_export_pdf: GET /api/v1/invoices/:id/export.pdf
router.get('/invoices/:id/export.pdf', (req, res) => {
  // Export invoice as PDF
});

module.exports = router;
```

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from typing import List

app = FastAPI()

# user_list: GET /api/v1/users
@app.get("/api/v1/users")
async def user_list():
    """List all users"""
    return []

# user_create: POST /api/v1/users
@app.post("/api/v1/users")
async def user_create(user_data: dict):
    """Create a new user"""
    return {"id": 1, **user_data}

# user_detail: GET /api/v1/users/{id}
@app.get("/api/v1/users/{id}")
async def user_detail(id: int):
    """Get user by ID"""
    return {"id": id, "name": "User"}

# user_update: PUT /api/v1/users/{id}
@app.put("/api/v1/users/{id}")
async def user_update(id: int, user_data: dict):
    """Update user"""
    return {"id": id, **user_data}

# user_delete: DELETE /api/v1/users/{id}
@app.delete("/api/v1/users/{id}")
async def user_delete(id: int):
    """Delete user"""
    return {"deleted": True}

# product_search: GET /api/v1/products/search
@app.get("/api/v1/products/search")
async def product_search(q: str):
    """Search products"""
    return []

# invoice_export_pdf: GET /api/v1/invoices/{id}/export.pdf
@app.get("/api/v1/invoices/{id}/export.pdf")
async def invoice_export_pdf(id: int):
    """Export invoice as PDF"""
    return {"file": "invoice.pdf"}
```

### Django

```python
from django.urls import path
from . import views

urlpatterns = [
    # user_list: GET /api/v1/users/
    path('api/v1/users/', views.user_list, name='user_list'),

    # user_create: POST /api/v1/users/
    path('api/v1/users/', views.user_create, name='user_create'),

    # user_detail: GET /api/v1/users/<int:id>/
    path('api/v1/users/<int:id>/', views.user_detail, name='user_detail'),

    # user_update: PUT /api/v1/users/<int:id>/
    path('api/v1/users/<int:id>/', views.user_update, name='user_update'),

    # user_delete: DELETE /api/v1/users/<int:id>/
    path('api/v1/users/<int:id>/', views.user_delete, name='user_delete'),

    # product_search: GET /api/v1/products/search/
    path('api/v1/products/search/', views.product_search, name='product_search'),
]

# views.py
def user_list(request):
    """List all users"""
    return JsonResponse([])

def user_create(request):
    """Create a new user"""
    return JsonResponse({"id": 1})

def user_detail(request, id):
    """Get user by ID"""
    return JsonResponse({"id": id, "name": "User"})

def user_update(request, id):
    """Update user"""
    return JsonResponse({"id": id})

def user_delete(request, id):
    """Delete user"""
    return JsonResponse({"deleted": True})

def product_search(request):
    """Search products"""
    return JsonResponse([])
```

---

## Hierarchical Overrides

This module uses the workspace-level endpoint naming conventions from `.ai/api-conventions.md`.

**Module-level extension** (if needed):
- Create `api/.ai/api-conventions.md` to add or override conventions specific to the API module
- Example: Add `billing_invoice_settle` action, custom webhook patterns
- Module-level conventions take precedence over workspace level in this module only

---

## Related Documentation

- [API Endpoint Naming Conventions](../../.ai/api-conventions.md) — complete action registry
- [API Endpoint Generator Guide](../../api/endpoint-generator-guide.md) — detailed tool usage
- [API System Documentation](../../README.md) — system overview and integration
- [Governed Tool: generate-api-endpoint](../../.ai/agents/tools/generate-api-endpoint.json) — checklist and order of operations
