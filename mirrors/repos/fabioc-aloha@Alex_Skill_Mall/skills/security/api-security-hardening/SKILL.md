---
type: skill
lifecycle: stable
inheritance: inheritable
name: api-security-hardening
description: API security hardening — rate limiting, JWT validation, CORS, input validation (4-layer defense)
tier: standard
applyTo: '**/*api*,**/*security*,**/*hardening*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# API Security Hardening

**Category**: Security
**Time Saved**: Hours of security review, prevents incidents
**Battle-tested**: Yes — AIRS Enterprise, HeadstartWebsite, GCX_Master

---

## The Problem

You're building an HTTP API. It works, but you haven't implemented security layers. One breach, one cost attack, one data leak — and you're explaining to leadership why the API was exposed.

## The Four Layers

Every production API needs these four defenses. Missing any one creates an exploitable gap.

### 1. Rate Limiting

Prevent abuse and cost attacks.

```javascript
// Express + express-rate-limit
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: 100,             // 100 requests per window per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, slow down' }
});

app.use('/api/', limiter);
```

**Rules:**

- Use sliding window, not fixed window (prevents burst at window boundaries)
- Per-user limits (100/min) AND per-IP limits (1000/min)
- For serverless: Upstash Redis (`@upstash/ratelimit`)

### 2. JWT Validation

Never trust tokens without verification.

```javascript
const jwt = require('jsonwebtoken');

function validateToken(token) {
  return jwt.verify(token, publicKey, {
    algorithms: ['RS256'],  // Explicit allowlist — NEVER omit
    issuer: 'https://your-auth-server.com',
    audience: 'your-api-identifier',
  });
}
```

**Rules:**

- Validate issuer, audience, expiration, AND signature
- Explicit algorithm allowlist (`algorithms: ['RS256']`) — prevents algorithm confusion attacks
- Never decode without verification (`jwt.decode` is NOT validation)

### 3. CORS Configuration

Block cross-origin abuse.

```javascript
const cors = require('cors');

const corsOptions = {
  origin: [
    'https://your-app.com',
    'https://staging.your-app.com'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400  // Preflight cache: 24 hours
};

app.use(cors(corsOptions));
```

**Rules:**

- Never use `origin: '*'` in production
- Explicit origin allowlist
- Include `Access-Control-Max-Age` for preflight caching
- For credentialed requests: `credentials: true` (but then NO wildcards anywhere)

### 4. Input Validation

Reject bad data at the boundary.

```javascript
const { z } = require('zod');

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150).optional(),
});

app.post('/users', (req, res) => {
  const result = CreateUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.issues });
  }
  // result.data is now typed and validated
  createUser(result.data);
});
```

**Rules:**

- Validate at the boundary — don't let bad data propagate
- Use Zod, Joi, or similar for request body, query params, AND path params
- Reject early with clear error messages (but don't leak internals)

## Checklist

| Layer | Implemented | Tested |
|-------|-------------|--------|
| Rate limiting | ☐ | ☐ |
| JWT validation with algorithm allowlist | ☐ | ☐ |
| CORS with explicit origins | ☐ | ☐ |
| Input validation on all endpoints | ☐ | ☐ |

## Anonymous Endpoint Warning

Serverless APIs with anonymous POST endpoints (image generation, AI inference) need extra protection:

- IP-based rate limiting (even without auth)
- Request size limits (`express.json({ limit: '1mb' })`)
- Async processing with queue (don't hold HTTP connection during expensive ops)
- Budget alerts at 50%, 80%, 100% of monthly allocation

---

**Source**: Promoted from AI-Memory global-knowledge.md (2026-04-27)
