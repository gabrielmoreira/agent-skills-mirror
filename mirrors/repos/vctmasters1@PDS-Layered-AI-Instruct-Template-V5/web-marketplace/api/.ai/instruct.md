# .AI-Instruct.md (marketplace/api)

> **Parent**: `marketplace/.AI-Instruct.md` for marketplace-level instructions and `copilot-instructions.md` for the depth-priority hierarchical methodology.

## Directory Overview

This directory contains the **Express.js + TypeORM API backend** for the PipeDream Marketplace. It is the primary server — it serves both the REST API (`/v1/...`) and the static frontend files.

> **URL Context:** In production this service is accessed at `pipedreamsystems.com/marketplace`. A reverse proxy strips or passes the `/marketplace` prefix before hitting this Express app. All internal API routes remain `/v1/...` — the proxy handles the path translation. Do **not** hardcode `marketplace.pipedreamsystems.com` anywhere in this service.
>
> **Device routes removed:** Device provisioning, config, and firmware routes have moved to the `devices-hmi/` service. Firmware binary storage and OTA delivery are handled by `devices-fw/`. Do **not** re-add device routes, device entities, or device handlers to this service. The marketplace database migrations still own the device table schema (Device, DeviceConfig, Firmware tables).

## Tech Stack

| Layer | Technology |
|---|---|
| Language | TypeScript (strict) |
| Framework | Express.js |
| ORM | TypeORM |
| Database | PostgreSQL (all environments, Docker for local dev) |
| Auth | JWT (Bearer tokens, 7-day expiry) |
| Payments | Stripe SDK (skeleton ready) |
| Real-time | Socket.IO (WebSocket) |
| Deployment | Railway.app (auto-deploy from `master`) |

## Source Structure

```
src/
├── index.ts                # Express app setup, middleware stack, route mounting, server start
├── database.ts             # TypeORM DataSource config (PostgreSQL)
├── entities/               # 25 TypeORM entity classes (database models — device entities moved to devices/ service)
│   ├── index.ts            # Barrel export for all entities
│   ├── user.ts             # User + UserRole enum (BUYER, DESIGNER, PRODUCER, ADMIN)
│   ├── designer.ts         # Designer profile (legacy table: "sellers")
│   ├── producer.ts         # Producer profile (legacy table: "manufacturers")
│   ├── product.ts          # Product listings
│   ├── order.ts            # Purchase orders
│   ├── order-item.ts       # Order line items (price snapshots)
│   ├── bid.ts              # Producer bids on orders
│   ├── payment-milestone.ts # 3-stage escrow (40/30/30)
│   ├── dispute.ts          # Order disputes
│   ├── message.ts          # User-to-user messages
│   ├── notification.ts     # System notifications (17+ event types)
│   ├── notification-preference.ts
│   ├── search.ts           # Saved searches (SearchSavedSearch)
│   ├── favorite.ts         # Wishlist items
│   ├── review.ts           # Two-tier rating system
│   ├── invoice.ts          # GAAP-compliant invoices
│   ├── payout.ts           # Payout tracking (Stripe Connect)
│   ├── service.ts          # Service listings
│   ├── site-settings.ts    # Platform configuration (fees, commissions)
│   ├── audit-log.ts        # Audit trail entries
│   ├── bulletin-card.ts    # Bulletin board cards ($1 posting fee)
│   ├── portfolio-image.ts  # Designer/producer portfolio images
│   ├── report.ts           # User abuse reports
│   ├── message-fee.ts      # Messaging fee records
│   ├── messaging-fee-waiver.ts
│   ├── password-reset-token.ts
│   └── email-verification-token.ts
│   # NOTE: device.ts, device-config.ts, firmware.ts → moved to devices-hmi/api/src/entities/
│   #       firmware binaries and OTA delivery → devices-fw/
├── routes/                 # Express route handlers (17 modules — devices route moved to devices/ service)
│   ├── auth.ts             # /v1/auth — Register, login, profile, password reset
│   ├── products.ts         # /v1/products — Designer product CRUD
│   ├── orders.ts           # /v1/orders — Purchase flow, order management
│   ├── bids.ts             # /v1/bids — Bid acceptance, milestones, disputes
│   ├── producer-queue.ts   # /v1/producer-queue — Producer order queue, bid submission
│   ├── messaging.ts        # /v1/messaging — User-to-user messages
│   ├── notifications.ts    # /v1/notifications — System notifications
│   ├── search.ts           # /v1/search — Product/designer/producer search, favorites
│   ├── admin.ts            # /v1/admin — User mgmt, disputes, settings, analytics
│   ├── payments.ts         # /v1/payments — Stripe integration, webhooks
│   ├── uploads.ts          # /v1/uploads — Image uploads with compression
│   ├── reviews.ts          # /v1/reviews — Two-tier rating system
│   ├── invoices.ts         # /v1/invoices — Invoice retrieval, summary totals
│   ├── payouts.ts          # /v1/payouts — Payout tracking, Stripe Connect status
│   ├── portfolio.ts        # /v1/portfolio — Portfolio image gallery (50 max/user)
│   ├── reports.ts          # /v1/reports — User abuse reporting
│   └── bulletin-board.ts   # /v1/bulletin-board — Bulletin posting ($1 fee)
├── middleware/
│   ├── security.ts         # Helmet headers, rate limiters, HTTPS redirect, content-type validation
│   ├── accessControl.ts    # Testing-phase access whitelist
│   └── validation.ts       # Joi schema validation middleware
├── services/
│   ├── websocket.ts        # Socket.IO initialization and event handlers
│   ├── notificationService.ts # Notification creation helpers
│   ├── auditService.ts     # Audit log writing
│   ├── emailService.ts     # Email delivery (verification, notifications)
│   ├── geocode.ts          # Address geocoding (ZIP to lat/lng, with caching)
│   ├── geolocation.ts      # Haversine distance calculations
│   ├── invoiceService.ts   # Invoice generation & numbering (GAAP-compliant)
│   └── payoutService.ts    # Payout calculation & Stripe Connect distribution
├── jobs/
│   ├── messaging-fee-billing.ts # Scheduled messaging fee billing (00:05 UTC)
│   └── payout-processing.ts    # Scheduled payout processing (01:00 UTC)
├── config/
│   ├── jwt.ts              # JWT secret & token expiry config
│   └── stripe.ts           # Stripe API client initialization
├── migrations/             # TypeORM migrations (10 versioned migrations)
└── scripts/
    └── seed-admin.ts       # Bootstrap admin user
```

## API Routes Summary

| Module | Endpoints | Base Path | Auth |
|---|---|---|---|
| Auth | 5+ | `/v1/auth` | Rate-limited |
| Products | 6 | `/v1/products` | JWT (designer) |
| Orders | 8+ | `/v1/orders` | JWT + rate-limited |
| Bids | 7 | `/v1/bids` | JWT |
| Producer Queue | 5 | `/v1/producer-queue` | JWT (producer) |
| Messaging | 7 | `/v1/messaging` | JWT |
| Notifications | 7 | `/v1/notifications` | JWT |
| Search | 11 | `/v1/search` | JWT |
| Admin | 13 | `/v1/admin` | JWT (isStaff) |
| Payments | 3+ | `/v1/payments` | JWT + Stripe |
| Uploads | 2 | `/v1/uploads` | JWT |
| Reviews | 4+ | `/v1/reviews` | JWT |
| Invoices | 3 | `/v1/invoices` | JWT |
| Payouts | 3+ | `/v1/payouts` | JWT |
| Portfolio | 4 | `/v1/portfolio` | JWT |
| Reports | 2+ | `/v1/reports` | JWT |
| Bulletin Board | 3+ | `/v1/bulletin-board` | JWT + Stripe |

> **Devices routes** (`/v1/devices`) have moved to the `devices/` service.

## Role Terminology in Code

Per the root `.AI-Instruct.md`, use **Designer** and **Producer** in all new code, comments, and docs.

Legacy references that must NOT be renamed (migration stability):
- Entity class `Designer` maps to table `sellers`
- Entity class `Producer` maps to table `manufacturers`
- `UserRole` enum values are `DESIGNER` and `PRODUCER` (already updated)

## Middleware Stack (order matters)

Applied in `index.ts` in this order:
1. `httpsRedirect` — Redirect HTTP→HTTPS in production
2. `securityHeaders` — Helmet security headers
3. `securityLogger` — Log suspicious patterns
4. `validateContentType` — Enforce `application/json`
5. `cors()` — Configured per environment (env var `ALLOWED_ORIGINS` or hardcoded defaults)
6. Stripe raw body handler (before `express.json()`)
7. `express.json()` + `urlencoded` + `cookieParser`
8. `apiLimiter` — Global rate limit
9. `testingAccessWhitelist` — Dev/testing access control (disabled in production: `TESTING_MODE=false`)
10. Static file serving (frontend + uploads)

## Middleware Files

| File | Purpose |
|---|---|
| `security.ts` | Helmet headers, rate limiters (`apiLimiter`, `authLimiter`), HTTPS redirect, content-type validation, security logger |
| `accessControl.ts` | Testing-phase IP/route whitelist |
| `validation.ts` | Joi schema validation middleware (`validate()` wrapper) |

## Database Conventions

- **Dev**: PostgreSQL via Docker (`docker compose up -d`) with `synchronize: true` — schema auto-syncs from entities
- **Prod**: PostgreSQL (Railway) with `synchronize: true` (temporary) + `runMigrations()` — migrations handle schema changes. `synchronize: true` will be disabled once schema is fully stabilized.
- **Entities**: Always register new entities in both the `entities/index.ts` barrel export and the `database.ts` entity arrays
- **Relationships**: Use `onDelete: "RESTRICT"` for financial entities, `onDelete: "CASCADE"` only for non-critical child records
- **UUIDs**: All primary keys are UUID v4

## Instructions

1. Before modifying any entity, check the GAAP compliance notes in `.dev-docs/audit-todo.md` regarding cascade deletions.
2. New routes must be registered in `index.ts` with appropriate rate limiters.
3. All state-changing endpoints require JWT auth via `verifyToken` middleware.
4. Admin endpoints require `requireAdmin()` middleware.
5. Test locally with PostgreSQL (Docker) before deploying to Railway.
6. Place implementation summaries in `marketplace/.dev-docs/` or root `.dev-docs/`.

## Documentation

- `DATABASE_SCHEMA.md` — Entity relationship documentation
- `IMPLEMENTATION_STATUS.md` — Feature completion status
- `NEXT_STEPS.md` — Pending work items
- `TEST_RESULTS.md` — Test execution records

## Production Hardening (February–March 2026)

- API rate limit increased to 300 req/15min per IP (SPA-friendly)
- 404 handler for undefined `/v1/*` routes
- Global error handler — suppresses stack traces in production
- SPA catch-all serves `index.html` for non-API routes
- Placeholder `/v1/marketplace/` routes removed (search routes cover this)
- `TESTING_MODE` middleware kept in stack but disabled in production (`TESTING_MODE=false`)
- Bootstrap-admin endpoint self-guards (refuses if admin already exists)
- Health check verifies database connectivity (`SELECT 1`)
- Graceful shutdown on SIGTERM/SIGINT (closes HTTP server + database connection)
- `unhandledRejection` handler prevents silent crashes
- CORS origins configurable via `ALLOWED_ORIGINS` environment variable
- SSL certificate verification configurable via `DB_SSL_REJECT_UNAUTHORIZED` env var
- Webhook idempotency tracking prevents duplicate Stripe event processing
- Bid acceptance uses pessimistic write lock to prevent race conditions
- Listing fee flow: save product as inactive → charge Stripe → activate on success
- Search pagination capped at 100 results per request
- Review helpful votes deduplicated per user
- Auto-bid creation uses batch insert instead of N+1 individual saves
- Tax rate and shipping cost configurable via `TAX_RATE` and `FLAT_SHIPPING` env vars
- Admin auth checks include `isStaff` flag alongside role check
- Route path conflicts resolved (static routes before parameterized routes)
- Debug `console.log` statements removed from production frontend code

---
_Last updated: 2026-05-29_

> **Consolidation fix applied 2026-05-29**: `tsconfig.json` `@db-central/*` path corrected from `../../DB-Central/src/*` → `../../db-central/src/*` (lowercase). References path also lowercased.

