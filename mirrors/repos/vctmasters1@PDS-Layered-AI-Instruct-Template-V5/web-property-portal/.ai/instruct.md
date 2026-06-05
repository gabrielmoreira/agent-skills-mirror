# PDS Property Portal Module

**Authority**: DEEP — Authoritative for all work inside `web-property-portal/`
**Last Updated**: 2026-05-27

---

## Contents

| Section | What's here |
|---------|-------------|
| [Project Overview](#project-overview) | Purpose and scope of property portal |
| [Tech Stack](#tech-stack) | Frontend, backend, database, payments |
| [Multi-Tenancy Model](#multi-tenancy-model) | account_id scoped architecture |
| [Accounting Model](#accounting-model) | Accrual vs Cash Basis accounting |
| [Project Structure](#project-structure) | Directory layout and file organization |
| [Key Modules](#key-modules) | Priority-ordered feature modules |
| [Development Rules](#development-rules) | Mandatory development practices |
| [Naming Conventions](#naming-conventions) | PDS naming standards |

---

## Project Overview

This module handles property portal functionality for the PDS system — a full-featured, professional property management system for 17 units (scalable to multi-user).

**Core Philosophy**:
- Tenant Portal is highest priority.
- Built as a premium product even if primarily for personal use.
- Follow PDS-Layered-AI-Instruct-Template-V3 strictly (depth priority, safety, naming, etc.).
- Everything scoped by `account_id`.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19 + TypeScript + Vite + Tailwind + shadcn/ui + React Router v6 + TanStack Query + React Hook Form + Zod |
| **Backend** | Express + TypeORM (extend existing PDS patterns) |
| **Database** | PostgreSQL `db-central` on Railway |
| **Payments** | Stripe (existing integration) |
| **Storage** | AWS S3 with signed URLs for documents |
| **Emails** | Existing PDS email system + templates |

---

## Multi-Tenancy Model

All data and functionality is strictly scoped by `account_id`.

**Requirements**:
- Every database query includes `WHERE account_id = ?` or equivalent
- All API endpoints validate `account_id` from authentication context
- Row Level Security (RLS) enabled on PostgreSQL where possible
- No data leakage between accounts — enforced at multiple layers

---

## Accounting Model

The system supports **accrual accounting** as the backend standard, with UI toggles for user preference:

| Basis | Description |
|-------|-------------|
| **Accrual** (backend default) | Record revenue when earned, expenses when incurred |
| **Cash Basis** (UI toggle) | Record when cash actually changes hands |

**Implementation Rules**:
- All financial records stored in accrual format
- UI converts to requested basis for display only
- Journal entries follow double-entry bookkeeping

---

## Project Structure

```
web-property-portal/
├── .ai/
│   └── instruct.md              ← This file - module authority guidelines
├── src/
│   ├── core/                    # Core business logic (entities, services)
│   │   ├── account.ts           # Account management (multi-tenancy root)
│   │   ├── tenant/              # Tenant-related logic
│   │   ├── unit/                # Unit management
│   │   ├── lease/               # Lease contracts
│   │   └── accounting/          # GL, rent roll, financial reports
│   ├── api/                     # Express routes and controllers
│   │   ├── v1/
│   │   │   ├── account.ts       # Account-scoped routes
│   │   │   ├── tenant.ts        # Tenant management API
│   │   │   ├── unit.ts          # Unit operations
│   │   │   └── accounting.ts    # Financial reporting API
│   ├── models/                  # TypeScript interfaces and DTOs
│   │   ├── account.ts           # Account entity (multi-tenancy root)
│   │   ├── tenant.ts            # Tenant profile
│   │   ├── unit.ts              # Property unit
│   │   └── accounting.ts        # Ledger entries, transactions
│   └── ui/                      # Shared UI components (if any)
├── tests/
│   ├── core/                    # Unit tests for business logic
│   ├── api/                     # Integration tests for API endpoints
│   └── fixtures/                # Test data factories
└── README.md                    # User-facing documentation
```

---

## Key Modules

### Priority 1: Tenant Portal (Self-Service)
| Feature | Status |
|---------|--------|
| Tenant registration | |
| Lease viewing | |
| Rent payment (Stripe) | |
| Maintenance requests | |
| Document downloads | |

### Priority 2: Owner Dashboard
| Feature | Status |
|---------|--------|
| Units overview | |
| Tenant management | |
| Lease tracking | |
| Financial summary | |

### Priority 3: Maintenance Requests
| Feature | Status |
|---------|--------|
| Request submission (tenant) | |
| Auto-forward to vendors | |
| Status tracking | |
| History log | |

### Priority 4: Rent Collection & Transactions
| Feature | Status |
|---------|--------|
| Scheduled rent payments | |
| Payment history | |
| Late fee handling | |
| Receipt generation | |

### Priority 5: Accounting
| Feature | Status |
|---------|--------|
| General Ledger | |
| Rent Roll reports | |
| Financial statements (Income/Expense, Balance Sheet) | |
| Cash/Accrual toggle | |

### Priority 6: Documents & Form Letters
| Feature | Status |
|---------|--------|
| Document upload (AWS S3) | |
| Signed URL generation | |
| Template-based form letters | |
| Archive management | |

### Priority 7: Automated Reminders
| Feature | Status |
|---------|--------|
| Lease expiration notice | |
| Rent due reminder | |
| Maintenance follow-up | |

---

## Development Rules

1. **Always create `.ai/instruct.md`** in each feature subdirectory
2. **Feature-sliced design**: Group by feature, not layer
3. **All API calls include `account_id` validation**
4. **Prioritize mobile-friendly responsive design**
5. **Use Zod for input validation** on all API endpoints
6. **Database migrations** go in `db-central/src/migrations/`
7. **Entity definitions** go in `db-central/src/entities/`

### Naming Conventions

| Scope | Pattern | Example |
|-------|---------|---------|
| Directory names | kebab-case | `tenant-management/` |
| TypeScript files | PascalCase | `TenantProfile.ts` |
| React components | PascalCase | `TenantDashboard.tsx` |
| API routes | kebab-case | `/api/v1/tenants` |
| Database columns | snake_case | `first_name`, `account_id` |

---

## API Endpoints

All endpoints are scoped to `account_id` from authentication context.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/properties | List properties (scoped by account) |
| GET | /api/v1/properties/{id} | Get property details |
| POST | /api/v1/properties | Create new property |
| PUT | /api/v1/properties/{id} | Update property |
| DELETE | /api/v1/properties/{id} | Delete property |
| GET | /api/v1/tenants | List tenants for account |
| GET | /api/v1/leases | List active leases |
| GET | /api/v1/accounting/ledger | Get general ledger |

> **Note**: Full API specification in `src/api/v1/` subdirectories.

---

## Dependencies

- See `package.json` for npm dependencies
- Database entities: `db-central/src/entities/`
- Migrations: `db-central/src/migrations/`

---

## Testing Strategy

| Test Type | Coverage Target |
|-----------|-----------------|
| Unit tests (core) | 80%+ coverage |
| API integration | All endpoints covered |
| End-to-end | Critical user flows |

---

## Deployment

- Deployed on Railway alongside other PDS services
- Environment variables managed via Railway secrets
- Database: `db-central` PostgreSQL instance---  
 
## API Endpoints 
