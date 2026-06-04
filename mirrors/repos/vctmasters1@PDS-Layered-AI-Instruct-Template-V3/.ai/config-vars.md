# Configuration Variables Registry

**Scope**: Workspace root (authoritative; may be extended hierarchically by modules)
**Purpose**: Establish typed environment variables with validation enabling deployment safety and developer onboarding
**Convention**: Semantic variable names: `{MODULE}_{RESOURCE}_{PROPERTY}` with type and validation rules
**Last Updated**: 2026-06-02

---

## Contents

| Section | What's here |
|---|---|
| [Variable Naming](#variable-naming) | Naming structure for configuration variables |
| [Type System](#type-system) | Supported types (string, number, boolean, secret) |
| [Environment Tiers](#environment-tiers) | dev, staging, production configurations |
| [Standard Variables](#standard-variables) | Variables every project must define |
| [Module Variables](#module-variables) | Domain-specific configuration variables |
| [Validation Rules](#validation-rules) | Type checking, required fields, defaults |
| [Framework Examples](#framework-examples) | Loading and validating config |
| [Hierarchical Inheritance](#hierarchical-inheritance) | Module-level config extensions |
| [Best Practices](#best-practices) | When and how to use the system |

---

## Variable Naming

### Pattern: `{MODULE}_{RESOURCE}_{PROPERTY}`

**Rules:**
- Uppercase with underscores: `DATABASE_URL`, `STRIPE_API_KEY`
- Module prefix (optional): `AUTH_`, `PAYMENT_`, `EMAIL_`
- Resource name: `DATABASE`, `STRIPE`, `SENDGRID`
- Property: `URL`, `API_KEY`, `WEBHOOK_SECRET`
- Searchable: enables grep `grep STRIPE_*` to find all Stripe config

**Examples:**

| Variable | Type | Module | Purpose |
|----------|------|--------|---------|
| `NODE_ENV` | enum | System | Execution environment (development/staging/production) |
| `DATABASE_URL` | string | Database | Connection string to primary database |
| `DATABASE_REPLICA_URL` | string | Database | Connection string to read replica |
| `REDIS_URL` | string | Cache | Redis connection string |
| `JWT_SECRET` | secret | Auth | Signing key for JWT tokens |
| `STRIPE_API_KEY` | secret | Payment | Stripe API authentication |
| `STRIPE_WEBHOOK_SECRET` | secret | Payment | Stripe webhook signing key |
| `SENDGRID_API_KEY` | secret | Email | SendGrid API key |
| `LOG_LEVEL` | enum | System | Logging verbosity (debug/info/warn/error) |
| `SENTRY_DSN` | secret | Monitoring | Error tracking endpoint |

---

## Type System

### Supported Types

| Type | Validation | Example | Usage |
|------|-----------|---------|-------|
| `string` | No validation | `"hello"` | Text values |
| `number` | Must be numeric | `42`, `3.14` | Integers, decimals |
| `boolean` | Must be true/false | `true`, `false` | Feature flags |
| `enum` | Must be one of predefined values | `development`, `staging`, `production` | Mode selection |
| `secret` | Must not be logged; validated at load time | API keys, passwords | Credentials |
| `url` | Must be valid URL | `https://example.com` | Service endpoints |
| `integer` | Must be whole number | `8080`, `100` | Ports, counts |

### Type Examples

```bash
# string
API_ENDPOINT="https://api.example.com"

# number
RATE_LIMIT_REQUESTS=1000
CACHE_TTL_SECONDS=3600

# boolean
DEBUG_MODE=false
ENABLE_METRICS=true

# enum
NODE_ENV=development  # Must be: development, staging, production
LOG_LEVEL=info        # Must be: debug, info, warn, error

# secret (never logged, use with caution)
JWT_SECRET="super-secret-key"
STRIPE_API_KEY="sk_test_123456"

# url
DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
REDIS_URL="redis://localhost:6379"

# integer
SERVER_PORT=3000
WORKER_THREADS=4
```

---

## Environment Tiers

### Development (`.env.local` - gitignored)
```bash
NODE_ENV=development
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-key-not-for-production
STRIPE_API_KEY=sk_test_123456  # Stripe test key
LOG_LEVEL=debug
```

### Staging (`.env.staging` - gitignored or in CI/CD)
```bash
NODE_ENV=staging
DATABASE_URL=postgresql://prod_user:pass@staging-db.example.com:5432/mydb_staging
REDIS_URL=redis://staging-cache.example.com:6379
JWT_SECRET=<generated-secret>  # Generate per environment
STRIPE_API_KEY=sk_test_123456
LOG_LEVEL=info
```

### Production (CI/CD / secret manager only)
```bash
NODE_ENV=production
DATABASE_URL=postgresql://prod_user:pass@prod-db.example.com:5432/mydb
REDIS_URL=redis://prod-cache.example.com:6379
JWT_SECRET=<vault-secret>  # From secret manager
STRIPE_API_KEY=sk_live_123456  # Live key
LOG_LEVEL=warn
SENTRY_DSN=https://...@sentry.io/...
```

---

## Standard Variables

Every project must define these:

| Variable | Type | Required | Default | Purpose |
|----------|------|----------|---------|---------|
| `NODE_ENV` | enum | ✅ | `development` | Execution environment |
| `DATABASE_URL` | url | ✅ | — | Primary database connection |
| `LOG_LEVEL` | enum | ✅ | `info` | Logging verbosity |
| `PORT` | integer | — | `3000` | Server listening port |
| `DEBUG_MODE` | boolean | — | `false` | Enable debug logging |

---

## Module Variables

### Authentication Module
| Variable | Type | Required | Default | Purpose |
|----------|------|----------|---------|---------|
| `JWT_SECRET` | secret | ✅ | — | JWT signing key |
| `JWT_EXPIRATION` | string | — | `24h` | Token expiration |
| `SESSION_SECRET` | secret | ✅ | — | Session signing key |

### Database Module
| Variable | Type | Required | Default | Purpose |
|----------|------|----------|---------|---------|
| `DATABASE_URL` | url | ✅ | — | Connection string |
| `DATABASE_POOL_SIZE` | integer | — | `10` | Connection pool size |
| `DATABASE_TIMEOUT_MS` | integer | — | `5000` | Query timeout |

### Payment Module
| Variable | Type | Required | Default | Purpose |
|----------|------|----------|---------|---------|
| `STRIPE_API_KEY` | secret | ✅ | — | API authentication |
| `STRIPE_WEBHOOK_SECRET` | secret | ✅ | — | Webhook verification |
| `STRIPE_API_VERSION` | string | — | `2023-10-16` | API version |

### Email Module
| Variable | Type | Required | Default | Purpose |
|----------|------|----------|---------|---------|
| `SENDGRID_API_KEY` | secret | ✅ | — | API authentication |
| `SENDGRID_FROM_EMAIL` | string | ✅ | — | Sender email address |

### Monitoring Module
| Variable | Type | Required | Default | Purpose |
|----------|------|----------|---------|---------|
| `SENTRY_DSN` | secret | — | — | Error tracking endpoint |
| `METRICS_ENABLED` | boolean | — | `true` | Enable metrics collection |

---

## Validation Rules

### Load-Time Validation

Every application must validate configuration at startup:

```javascript
// Express.js example
const requiredVars = ['DATABASE_URL', 'JWT_SECRET', 'NODE_ENV'];
const missingVars = requiredVars.filter(v => !process.env[v]);

if (missingVars.length > 0) {
  console.error(`Missing required environment variables: ${missingVars.join(', ')}`);
  process.exit(1);
}

// Type validation
if (!['development', 'staging', 'production'].includes(process.env.NODE_ENV)) {
  console.error(`Invalid NODE_ENV: ${process.env.NODE_ENV}`);
  process.exit(1);
}
```

```python
# FastAPI example
import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(...)  # Required
    JWT_SECRET: str = Field(...)
    NODE_ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="info")

    class Config:
        env_file = ".env"

try:
    settings = Settings()
except Exception as e:
    print(f"Configuration error: {e}")
    exit(1)
```

### Validation Checks

✅ **Always validate:**
- Required variables are present
- Type constraints are met (number is numeric, enum is in list)
- URLs are well-formed
- Secrets are not empty
- Sensitive variables are never logged

❌ **Never:**
- Log secrets to stdout/stderr
- Commit `.env` files to git
- Store credentials in code
- Use defaults for secrets

---

## Framework Examples

### Express.js with dotenv

```javascript
import dotenv from 'dotenv';

dotenv.config({ path: '.env' });

const config = {
  // Required
  nodeEnv: process.env.NODE_ENV || 'development',
  databaseUrl: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET,

  // Optional with defaults
  port: parseInt(process.env.PORT || '3000'),
  logLevel: process.env.LOG_LEVEL || 'info',
  debugMode: process.env.DEBUG_MODE === 'true',
};

// Validate
const errors = [];
if (!config.databaseUrl) errors.push('DATABASE_URL is required');
if (!config.jwtSecret) errors.push('JWT_SECRET is required');
if (!['development', 'staging', 'production'].includes(config.nodeEnv)) {
  errors.push(`NODE_ENV must be one of: development, staging, production`);
}

if (errors.length > 0) {
  console.error('Configuration errors:', errors);
  process.exit(1);
}

export default config;
```

### FastAPI with pydantic

```python
from pydantic import BaseSettings, validator, Field
import os

class Settings(BaseSettings):
    # Required
    database_url: str = Field(..., description="PostgreSQL connection string")
    jwt_secret: str = Field(..., description="JWT signing key")

    # Optional
    node_env: str = Field(default="development")
    log_level: str = Field(default="info")
    port: int = Field(default=8000)
    debug_mode: bool = Field(default=False)

    @validator('node_env')
    def validate_node_env(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError(f"NODE_ENV must be one of: development, staging, production")
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        if v not in ['debug', 'info', 'warn', 'error']:
            raise ValueError(f"LOG_LEVEL must be one of: debug, info, warn, error")
        return v

    class Config:
        env_file = '.env'
        case_sensitive = True

settings = Settings()
```

### Django with python-decouple

```python
from decouple import config, Csv

# Required
DATABASE_URL = config('DATABASE_URL')
JWT_SECRET = config('JWT_SECRET')

# Optional with defaults
NODE_ENV = config('NODE_ENV', default='development')
LOG_LEVEL = config('LOG_LEVEL', default='info')
DEBUG_MODE = config('DEBUG_MODE', default=False, cast=bool)
PORT = config('PORT', default=8000, cast=int)

# Validate
if NODE_ENV not in ['development', 'staging', 'production']:
    raise ValueError(f"NODE_ENV must be one of: development, staging, production")

if LOG_LEVEL not in ['debug', 'info', 'warn', 'error']:
    raise ValueError(f"LOG_LEVEL must be one of: debug, info, warn, error")
```

---

## .env File Convention

### `.env.example` (committed to git)
```bash
# THIS FILE IS COMMITTED TO GIT
# Copy to .env and fill in your values

# System
NODE_ENV=development
PORT=3000
LOG_LEVEL=info
DEBUG_MODE=false

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Authentication
JWT_SECRET=your-secret-key-here

# Monitoring
SENTRY_DSN=

# Payment (if using Stripe)
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=
```

### `.env` (gitignored)
```bash
# THIS FILE IS GITIGNORED
# Copy from .env.example and fill in your actual values

NODE_ENV=development
PORT=3000
LOG_LEVEL=debug
DEBUG_MODE=true

DATABASE_URL=postgresql://dev:dev@localhost:5432/mydb_dev

JWT_SECRET=dev-secret-12345

SENTRY_DSN=
```

### `.env.production` (CI/CD only, never committed)
```bash
# PRODUCTION CREDENTIALS - NEVER COMMIT
# This file is provided by CI/CD system from secret manager

NODE_ENV=production
PORT=8000
LOG_LEVEL=warn

DATABASE_URL=postgresql://prod:$DB_PASS@prod-db.internal:5432/mydb
JWT_SECRET=$JWT_SECRET_FROM_VAULT

STRIPE_API_KEY=$STRIPE_API_KEY_FROM_VAULT
STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET_FROM_VAULT

SENTRY_DSN=$SENTRY_DSN_FROM_VAULT
```

---

## Hierarchical Inheritance

**Default behavior:** All config variables inherit the master registry above.

**Module-level override/extension:**
- Any module may create `.ai/config-vars.md` in its directory
- Module config extends the master table without duplicating
- To create a custom variable, add it to the module's `.ai/config-vars.md`:

```markdown
# Custom Config for [Module]

| Variable | Type | Required | Default | Purpose |
|----------|------|----------|---------|---------|
| `BILLING_STRIPE_ACCOUNT_ID` | string | ✅ | — | Connected Stripe account |
| `BILLING_INVOICE_PREFIX` | string | — | `INV-` | Invoice number prefix |
```

---

## Best Practices

### Do's

✅ **Do:**
- Use the registry for all configuration
- Validate configuration at application startup
- Use `.env.example` for local development
- Use secret manager (Vault, AWS Secrets Manager) for production
- Never commit `.env` or secrets files
- Document why each variable exists
- Use type validation (pydantic, zod, joi)
- Log configuration errors clearly on startup

### Don'ts

❌ **Don't:**
- Commit `.env` files to git
- Store secrets in code comments
- Invent configuration variables ad-hoc
- Use inconsistent naming
- Log sensitive variables
- Ignore missing required configuration
- Rely on defaults for secrets
- Mix environment-specific and shared config

---

## Validation Rules

The config validator checks:

1. **Variable naming**: Follows `{MODULE}_{RESOURCE}_{PROPERTY}` pattern
2. **Type consistency**: Values match declared types
3. **Required fields**: All required variables present at startup
4. **Enum values**: Enum variables contain only allowed values
5. **No undeclared variables**: Only registered variables in use
6. **No logged secrets**: Secrets don't appear in logs
7. **URL validity**: URLs are well-formed

---

## Next Steps

1. Review this convention
2. Copy `.env.example` to `.env` and fill values
3. Use `config_generator.py` to create config validators
4. Run `config_discovery.py` to find all config usage
5. Run `config_validator.py` to validate consistency

---

## References

- [Config Generator](../config/config_generator.py) — generates config validators from registry
