# Error Code Registry

**Scope**: Workspace root (authoritative; may be extended hierarchically by modules)
**Purpose**: Establish consistent error codes and HTTP mappings enabling automated error handling and API documentation
**Convention**: Semantic error codes: `ERR_{DOMAIN}_{REASON}` with HTTP method mapping
**Last Updated**: 2026-06-02

---

## Contents

| Section | What's here |
|---|---|
| [Error Code Pattern](#error-code-pattern) | Naming structure for all error codes |
| [Domain Registry](#domain-registry) | Standard domains (user, product, order, payment, auth, validation, system) |
| [Reason Registry](#reason-registry) | Standard reasons (not_found, invalid, conflict, unauthorized, etc.) |
| [HTTP Method Mapping](#http-method-mapping) | Error code to HTTP status and response |
| [Error Response Format](#error-response-format) | Standard error envelope |
| [Framework Examples](#framework-examples) | Express, FastAPI, Django error classes |
| [Hierarchical Inheritance](#hierarchical-inheritance) | Module-level error extensions |
| [Best Practices](#best-practices) | When and how to use the system |

---

## Error Code Pattern

### Pattern: `ERR_{DOMAIN}_{REASON}`

**Rules:**
- Prefix: `ERR_` (searchable, prevents collisions)
- Domain: Resource type (user, product, order, payment, auth, validation, system)
- Reason: Why the error occurred (not_found, invalid, conflict, unauthorized, etc.)
- Uppercase with underscores: `ERR_USER_NOT_FOUND`, not `ERR_UserNotFound`
- Searchable: enables grep `grep ERR_PAYMENT_*` to find all payment errors

**Examples:**

| Code | HTTP | Reason | Message |
|------|------|--------|---------|
| `ERR_USER_NOT_FOUND` | 404 | User doesn't exist | "User with ID {id} not found" |
| `ERR_USER_INVALID_EMAIL` | 400 | Email format invalid | "Invalid email format: {email}" |
| `ERR_USER_ALREADY_EXISTS` | 409 | Email already registered | "User with email {email} already exists" |
| `ERR_PRODUCT_OUT_OF_STOCK` | 400 | Stock unavailable | "Product out of stock" |
| `ERR_ORDER_INVALID_TOTAL` | 400 | Total calculation error | "Order total mismatch" |
| `ERR_PAYMENT_DECLINED` | 402 | Payment processor rejected | "Payment declined by processor" |
| `ERR_AUTH_INVALID_TOKEN` | 401 | Token malformed/expired | "Invalid or expired token" |
| `ERR_AUTH_UNAUTHORIZED` | 403 | Permission denied | "Insufficient permissions" |
| `ERR_VALIDATION_SCHEMA` | 400 | Request schema mismatch | "Request validation failed: {details}" |
| `ERR_SYSTEM_INTERNAL` | 500 | Unhandled exception | "Internal server error" |

---

## Domain Registry

Standard domains for error codes:

| Domain | Purpose | Scope | Examples |
|--------|---------|-------|----------|
| `USER` | User account errors | Authentication, profiles, data | not_found, invalid_email, already_exists |
| `PRODUCT` | Product catalog errors | Inventory, pricing | not_found, out_of_stock, invalid_sku |
| `ORDER` | Order processing errors | Order creation, validation | invalid_total, empty_items, invalid_state |
| `PAYMENT` | Payment transaction errors | Charging, refunds | declined, invalid_card, insufficient_funds |
| `AUTH` | Authentication/authorization | Token, session, permission | invalid_token, unauthorized, expired_session |
| `VALIDATION` | Input validation errors | Request schema, data constraints | schema, constraint_violation, type_mismatch |
| `SYSTEM` | System/infrastructure errors | Unhandled exceptions, DB errors | internal, database, service_unavailable |

**Adding a New Domain:**
- Add to module's `.ai/error-codes.md`
- Use consistent reason names
- Document HTTP mapping

---

## Reason Registry

Standard reasons across all domains:

| Reason | HTTP | When to Use | Example |
|--------|------|------------|---------|
| `NOT_FOUND` | 404 | Resource doesn't exist | `ERR_USER_NOT_FOUND` |
| `INVALID` | 400 | Data format/value invalid | `ERR_USER_INVALID_EMAIL` |
| `ALREADY_EXISTS` | 409 | Unique constraint violated | `ERR_USER_ALREADY_EXISTS` |
| `OUT_OF_STOCK` | 400 | Inventory unavailable | `ERR_PRODUCT_OUT_OF_STOCK` |
| `INVALID_STATE` | 400 | State transition not allowed | `ERR_ORDER_INVALID_STATE` |
| `UNAUTHORIZED` | 403 | User lacks permission | `ERR_AUTH_UNAUTHORIZED` |
| `INVALID_TOKEN` | 401 | Token malformed/expired | `ERR_AUTH_INVALID_TOKEN` |
| `DECLINED` | 402 | External service rejected | `ERR_PAYMENT_DECLINED` |
| `SCHEMA` | 400 | Request validation failed | `ERR_VALIDATION_SCHEMA` |
| `INTERNAL` | 500 | Unhandled exception | `ERR_SYSTEM_INTERNAL` |

---

## HTTP Method Mapping

**Standard mappings from error code to HTTP status:**

| HTTP Status | Error Codes | Semantics |
|------------|-------------|-----------|
| **400 Bad Request** | INVALID, OUT_OF_STOCK, INVALID_STATE, SCHEMA | Client error in request data |
| **401 Unauthorized** | INVALID_TOKEN, EXPIRED_SESSION | Missing or invalid authentication |
| **403 Forbidden** | UNAUTHORIZED | Authentication valid but insufficient permission |
| **404 Not Found** | NOT_FOUND | Resource doesn't exist |
| **409 Conflict** | ALREADY_EXISTS, CONSTRAINT_VIOLATION | Request conflicts with current state |
| **402 Payment Required** | DECLINED, INSUFFICIENT_FUNDS | Payment-related rejection |
| **422 Unprocessable Entity** | VALIDATION_FAILED | Request syntax valid but semantics invalid |
| **500 Internal Server Error** | INTERNAL, DATABASE | Unhandled server error |
| **503 Service Unavailable** | SERVICE_UNAVAILABLE | Temporary service outage |

---

## Error Response Format

**Standard error envelope (all frameworks):**

```json
{
  "success": false,
  "error": {
    "code": "ERR_USER_NOT_FOUND",
    "domain": "USER",
    "reason": "NOT_FOUND",
    "message": "User with ID 123 not found",
    "details": null,
    "timestamp": "2026-06-02T10:30:00Z",
    "trace_id": "req_abc123def456"
  }
}
```

**Successful response:**

```json
{
  "success": true,
  "data": { ... },
  "meta": { "timestamp": "2026-06-02T10:30:00Z" }
}
```

**Field rules:**
- `code`: The error code (e.g., `ERR_USER_NOT_FOUND`)
- `domain`: Extracted from code (e.g., `USER`)
- `reason`: Extracted from code (e.g., `NOT_FOUND`)
- `message`: Human-readable description
- `details`: Optional extra context (validation errors, field names, etc.)
- `timestamp`: ISO 8601 UTC
- `trace_id`: Unique request ID for logging (enable correlation with logs)

---

## Framework Examples

### Express.js

```javascript
// Error class
class AppError extends Error {
  constructor(code, message, statusCode = 400, details = null) {
    super(message);
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

// Custom errors
class UserNotFoundError extends AppError {
  constructor(userId) {
    super('ERR_USER_NOT_FOUND', `User with ID ${userId} not found`, 404);
  }
}

class InvalidEmailError extends AppError {
  constructor(email) {
    super('ERR_USER_INVALID_EMAIL', `Invalid email format: ${email}`, 400, { email });
  }
}

// Route handler
router.post('/users', (req, res, next) => {
  try {
    if (!isValidEmail(req.body.email)) {
      throw new InvalidEmailError(req.body.email);
    }
    // ... create user
  } catch (err) {
    next(err);  // Pass to error middleware
  }
});

// Error middleware
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const code = err.code || 'ERR_SYSTEM_INTERNAL';

  res.status(statusCode).json({
    success: false,
    error: {
      code,
      domain: code.split('_')[1],
      reason: code.split('_').slice(2).join('_'),
      message: err.message,
      details: err.details || null,
      timestamp: new Date().toISOString(),
      trace_id: req.id
    }
  });
});
```

### FastAPI

```python
from fastapi import HTTPException
from enum import Enum

class ErrorCode(str, Enum):
    USER_NOT_FOUND = "ERR_USER_NOT_FOUND"
    USER_INVALID_EMAIL = "ERR_USER_INVALID_EMAIL"
    USER_ALREADY_EXISTS = "ERR_USER_ALREADY_EXISTS"

class AppException(HTTPException):
    def __init__(self, code: ErrorCode, message: str, details=None):
        status_code = {
            ErrorCode.USER_NOT_FOUND: 404,
            ErrorCode.USER_INVALID_EMAIL: 400,
            ErrorCode.USER_ALREADY_EXISTS: 409,
        }.get(code, 500)

        self.code = code
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)

# Routes
@app.post("/users")
async def create_user(user_data: UserSchema):
    if not is_valid_email(user_data.email):
        raise AppException(
            ErrorCode.USER_INVALID_EMAIL,
            f"Invalid email format: {user_data.email}",
            details={"email": user_data.email}
        )
    # ... create user

# Exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "domain": exc.code.split('_')[1],
                "reason": '_'.join(exc.code.split('_')[2:]),
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "trace_id": request.headers.get("x-request-id")
            }
        }
    )
```

### Django

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

class AppException(Exception):
    def __init__(self, code, message, status_code=400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

class UserNotFoundError(AppException):
    def __init__(self, user_id):
        super().__init__(
            'ERR_USER_NOT_FOUND',
            f'User with ID {user_id} not found',
            404
        )

# View
@require_http_methods(["POST"])
def create_user(request):
    try:
        data = json.loads(request.body)
        if not is_valid_email(data.get('email')):
            raise AppException(
                'ERR_USER_INVALID_EMAIL',
                f"Invalid email format: {data.get('email')}",
                400,
                details={'email': data.get('email')}
            )
        # ... create user
    except AppException as e:
        return JsonResponse({
            'success': False,
            'error': {
                'code': e.code,
                'domain': e.code.split('_')[1],
                'reason': '_'.join(e.code.split('_')[2:]),
                'message': e.message,
                'details': e.details,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'trace_id': request.META.get('HTTP_X_REQUEST_ID')
            }
        }, status=e.status_code)
```

---

## Hierarchical Inheritance

**Default behavior:** All errors inherit the master error registry above.

**Module-level override/extension:**
- Any module may create `.ai/error-codes.md` in its directory
- Module errors extend the master table without duplicating
- To create a custom error code, add it to the module's `.ai/error-codes.md`:

```markdown
# Custom Error Codes for [Module]

| Code | HTTP | Domain | Reason | Message |
|------|------|--------|--------|---------|
| `ERR_PAYMENT_GATEWAY_TIMEOUT` | 503 | PAYMENT | TIMEOUT | "Payment gateway did not respond in time" |
| `ERR_BILLING_INVOICE_LOCKED` | 409 | BILLING | LOCKED | "Invoice is locked and cannot be modified" |
```

---

## Best Practices

### Do's

✅ **Do:**
- Use error codes from the registry or extend via module rules
- Always return error code + human message together
- Include details for validation errors (which field, why)
- Log errors with `trace_id` for debugging
- Return correct HTTP status for each error code
- Document why an error can occur in comments/docs
- Test all error paths in unit tests

### Don'ts

❌ **Don't:**
- Return raw exception messages without error codes
- Use random HTTP status codes (always use standard mappings)
- Leak internal implementation details in error messages
- Return different error formats in different endpoints
- Forget to log errors with sufficient context
- Create error codes ad-hoc (use the registry)

---

## Validation Rules

The error validator checks:

1. **Code format**: Matches `ERR_{DOMAIN}_{REASON}` pattern
2. **Domain validity**: Domain is in registry or module-extended
3. **Reason validity**: Reason is in registry or module-extended
4. **HTTP mapping**: Status code matches domain/reason
5. **Consistency**: Same error code always returns same HTTP status
6. **No duplicates**: Each code defined exactly once
7. **Coverage**: All error paths throw registered codes (no ad-hoc errors)

---

## Next Steps

1. Review this convention
2. Use `error_generator.py` to create error classes
3. Run `error_discovery.py` to find all error codes
4. Run `error_validator.py` to validate consistency

---

## References

- [Error Generator](../api/error_generator.py) — generates error classes from registry
