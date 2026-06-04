# API Endpoint Naming Conventions

**Scope**: Workspace root (authoritative; may be extended hierarchically by modules)
**Purpose**: Establish naming conventions for API endpoints enabling automated discovery, documentation, and testing
**Convention**: Semantic names with searchable pattern: `{resource}_{action}[_{detail}]`
**Last Updated**: 2026-06-02

---

## Contents

| Section | What's here |
|---|---|
| [Naming Pattern](#naming-pattern) | Core convention and structure |
| [Action Registry](#action-registry) | Standard action names (list, create, update, delete, etc.) |
| [Resource Categories](#resource-categories) | How to name resource types |
| [HTTP Method Mapping](#http-method-mapping) | REST to action name mapping |
| [Metadata Discovery](#metadata-discovery) | What the discovery tool captures |
| [Hierarchical Inheritance](#hierarchical-inheritance) | How modules extend conventions |
| [Best Practices](#best-practices) | When and how to use the system |

---

## Naming Pattern

### Structure

```
{resource}_{action}[_{detail}]
```

**Components:**
- `{resource}`: Singular noun (not plural) — `user`, `product`, `order`, `invoice`
- `{action}`: Verb or standard action — `list`, `create`, `update`, `delete`, `detail`, `search`, `batch`
- `[_{detail}]`: Optional clarifier — `bulk`, `archived`, `for_review`

### Examples

| Pattern | Endpoint | HTTP Method | Path |
|---------|----------|-------------|------|
| `user_list` | List users | `GET` | `/api/v1/users` |
| `user_create` | Create user | `POST` | `/api/v1/users` |
| `user_detail` | Get user by ID | `GET` | `/api/v1/users/{id}` |
| `user_update` | Update user | `PUT` | `/api/v1/users/{id}` |
| `user_delete` | Delete user | `DELETE` | `/api/v1/users/{id}` |
| `user_batch_create` | Bulk create users | `POST` | `/api/v1/users/batch` |
| `product_search` | Search products | `GET` | `/api/v1/products/search` |
| `order_list_archived` | List archived orders | `GET` | `/api/v1/orders?archived=true` |
| `invoice_export_pdf` | Export invoice as PDF | `GET` | `/api/v1/invoices/{id}/export.pdf` |
| `webhook_user_created` | User created webhook | `POST` | `/webhooks/user.created` |

### Searchability (Key Feature)

The naming pattern enables powerful searches:

```bash
# Find all user endpoints
grep -r "user_" src/

# Find all list endpoints
grep -r "*_list" src/

# Find all batch operations
grep -r "*_batch" src/

# Find all delete operations
grep -r "*_delete" src/
```

---

## Action Registry

Standard action names mapped to REST semantics and common HTTP methods.

| Action | HTTP Method | REST Semantics | Example | Notes |
|--------|------------|---|---------|-------|
| `list` | `GET` | Read collection | `user_list` | Paginated or full list |
| `create` | `POST` | Create resource | `user_create` | Singular item creation |
| `detail` | `GET` | Read single resource | `user_detail` | Fetch by ID or unique identifier |
| `update` | `PUT` / `PATCH` | Update resource | `user_update` | Modify existing resource |
| `delete` | `DELETE` | Remove resource | `user_delete` | Soft or hard delete |
| `search` | `GET` | Query/filter collection | `product_search` | Complex search; may use POST |
| `export` | `GET` | Generate/download file | `invoice_export_pdf` | Returns file (CSV, PDF, etc.) |
| `import` | `POST` | Bulk upload data | `user_import_csv` | File upload; creates multiple |
| `batch` | `POST` | Bulk create/modify | `order_batch_create` | Multiple items in one request |
| `validate` | `POST` / `GET` | Syntax/business logic check | `email_validate` | Pre-submission validation |
| `webhook` | `POST` | Event notification | `webhook_user_created` | Async event delivery |
| `auth` | `POST` | Authentication action | `user_auth_login` | Login, logout, refresh token |
| `subscribe` | `POST` / `PUT` | Add to collection | `user_subscribe_mailing_list` | Add/join subscription |
| `unsubscribe` | `DELETE` / `POST` | Remove from collection | `user_unsubscribe_mailing_list` | Remove/leave subscription |

---

## Resource Categories

### Naming Resources

**Use singular nouns, never plural:**

| ❌ Don't | ✅ Do | Reason |
|---------|------|--------|
| `users_list` | `user_list` | Convention + searchable |
| `products_create` | `product_create` | Consistent pattern |
| `orders_detail` | `order_detail` | Singular maps to REST semantics |

### Hierarchical Resources

For nested resources, use dot or underscore:

| Pattern | HTTP Method | Path | Notes |
|---------|------------|------|-------|
| `user_post_list` | `GET` | `/api/v1/users/{user_id}/posts` | Parent-child relationship |
| `user_post_create` | `POST` | `/api/v1/users/{user_id}/posts` | Create child under parent |
| `user_post_detail` | `GET` | `/api/v1/users/{user_id}/posts/{post_id}` | Fetch specific child |

**Option**: Use dots for nesting if preferred:

| Pattern | HTTP Method | Path |
|---------|------------|------|
| `user.post_list` | `GET` | `/api/v1/users/{user_id}/posts` |
| `user.post_create` | `POST` | `/api/v1/users/{user_id}/posts` |

---

## HTTP Method Mapping

### REST Convention Defaults

| HTTP Method | Expected Action | Example |
|-------------|-----------------|---------|
| `GET` | `list`, `detail`, `search`, `export`, `validate` | `user_list`, `product_detail` |
| `POST` | `create`, `batch`, `import`, `auth`, `webhook` | `user_create`, `order_batch_create` |
| `PUT` | `update` (full replacement) | `user_update` |
| `PATCH` | `update` (partial) | `user_update` (or `user_patch`) |
| `DELETE` | `delete`, `unsubscribe` | `user_delete` |

### Exceptions

When naming doesn't match REST convention, clarify:

| Pattern | HTTP Method | Notes |
|---------|------------|-------|
| `product_search` | `POST` | POST for complex search body |
| `user_export_csv` | `GET` | GET for simple download |
| `data_sync` | `POST` | Bidirectional data sync |
| `config_update` | `PATCH` | Partial config update |

---

## Metadata Discovery

The discovery tool extracts and catalogs this metadata for each endpoint:

```json
{
  "endpoint_name": "user_create",
  "resource": "user",
  "action": "create",
  "http_method": "POST",
  "path": "/api/v1/users",
  "file": "controllers/user.js",
  "line": 42,
  "params": {
    "required": ["name", "email"],
    "optional": ["phone", "address"]
  },
  "response": {
    "success": 201,
    "error": [400, 409, 500]
  },
  "auth": "bearer_token",
  "rate_limit": "100/hour",
  "tags": ["public", "v1"]
}
```

**Discoverable metadata** (extracted by the tool):
- ✅ Endpoint name / resource / action
- ✅ HTTP method
- ✅ Route path
- ✅ File location and line number
- ⚠️ Parameters (documented via JSDoc, decorators, or Swagger)
- ⚠️ Response codes (documented)
- ⚠️ Authentication requirements
- ⚠️ Rate limits (documented)
- ⚠️ Tags/categories

---

## Hierarchical Inheritance

**Default behavior:** All endpoints inherit the master naming convention above.

**Module-level override/extension:**
- Any module may create `.ai/api-conventions.md` in its directory
- Module conventions extend the master table without duplicating
- To create a custom action, add it to the module's `.ai/api-conventions.md`:

```markdown
# Custom Actions for [Module]

| Action | HTTP | Semantics | Example |
|--------|------|-----------|---------|
| `analyze` | `POST` | Run analysis | `document_analyze` |
| `generate` | `POST` | Generate output | `report_generate` |
```

---

## Best Practices

### Naming Guidelines

✅ **Do:**
- Use singular resource names: `user_list`, not `users_list`
- Use lowercase with underscores: `product_batch_import`, not `productBatchImport`
- Be descriptive: `invoice_send_reminder`, not `invoice_action`
- Match HTTP semantics: `GET` for `detail` and `list`, `POST` for `create`

❌ **Don't:**
- Use generic verbs: `user_get` (use `user_detail` instead)
- Mix conventions: `user_list` + `products_list` (inconsistent)
- Abbreviate unnecessarily: `usr_lst` (unclear)
- Duplicate the method: `get_user_detail` (the `GET` method is the method)

### Endpoint Organization

Group related endpoints:
```
user_list
user_create
user_detail
user_update
user_delete
user_search
user_export_csv

product_list
product_create
product_detail
...
```

### Versioning

Include version in path, not endpoint name:

```
✅ user_list    → GET /api/v1/users
✅ user_list    → GET /api/v2/users  (same endpoint name, different API version)

❌ user_list_v1  (avoid in endpoint name)
❌ user_list_v2  (version should be in path)
```

### Deprecated Endpoints

Mark clearly:

```
user_list_deprecated    → GET /api/v1/users (old endpoint, will be removed)
user_list               → GET /api/v2/users (new endpoint)
```

Or use tags:
```
endpoint_name: user_list
tags: [deprecated, v1]
replacement: (See v2 documentation)
```

---

## Examples by Framework

### Express.js / Node.js

```javascript
// Router definition
app.get('/api/v1/users', getUserList);           // user_list
app.post('/api/v1/users', createUser);           // user_create
app.get('/api/v1/users/:id', getUserDetail);     // user_detail
app.put('/api/v1/users/:id', updateUser);        // user_update
app.delete('/api/v1/users/:id', deleteUser);     // user_delete

// Discovery: The tool finds and catalogs these automatically
```

### FastAPI / Python

```python
@app.get("/api/v1/users")           # user_list
def list_users(): pass

@app.post("/api/v1/users")          # user_create
def create_user(): pass

@app.get("/api/v1/users/{user_id}") # user_detail
def get_user(user_id: int): pass
```

### Django REST Framework

```python
# ViewSet automatically generates endpoints
class UserViewSet(viewsets.ModelViewSet):
    # user_list (GET /users/)
    # user_create (POST /users/)
    # user_detail (GET /users/:id/)
    # user_update (PUT /users/:id/)
    # user_delete (DELETE /users/:id/)
```

---

## Validation Rules

The validator checks:

1. **Naming consistency**: `{resource}_{action}[_{detail}]` format
2. **HTTP method correctness**: Matches expected method for action
3. **No duplicates**: Each endpoint name is unique
4. **Searchability**: Pattern enables `grep -r "pattern_*"`
5. **Documentation**: Required metadata is present (JSDoc, comments, decorators)

---

## Next Steps

1. Review this convention
2. Choose your framework/language
3. Use `endpoint_generator.py` to create endpoints
4. Run `endpoint_discovery.py` to find all endpoints
5. Run `endpoint_validator.py` to validate consistency

---

## References

- [API Endpoint Generator](../api/endpoint_generator.py) — generates endpoint code from spec
- [Endpoint Discovery Tool](../api/endpoint_discovery.py) — scans codebase for all endpoints
- [Endpoint Generator Guide](../api/endpoint-generator-guide.md) — prose walkthrough
- [`api/README.md`](../api/README.md) — module overview
