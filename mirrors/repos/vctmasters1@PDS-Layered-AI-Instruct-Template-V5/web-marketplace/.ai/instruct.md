# web-marketplace: Full-Stack Marketplace

**Project**: PDS-AutomationSuite-02012026  
**Authority**: DEEP — Authoritative for all work inside `web-marketplace/`  
**Last Updated**: 2026-05-27  
**Service URL**: `pipedreamsystems.com/marketplace`

---

## Contents

| Section | What's here |
|---|-------------|
| [What This Is](#what-this-is) | Platform concept, mission, and audience |
| [Platform Concept Architecture](#platform-concept-architecture) | Listing types, creator types, navigation structure |
| [Layout and Navigation](#layout-and-navigation) | Research-backed layout rules for mobile and desktop |
| [Directory Structure](#directory-structure) | File/folder layout |
| [Role Terminology](#role-terminology) | DB role names and user-facing labels |
| [Database Ownership](#database-ownership) | Which service owns which tables |
| [Auth](#auth) | JWT setup |
| [Development](#development) | Local dev commands |
| [Deployment](#deployment) | Railway deployment details |
| [Search Sort Order](#search-sort-order) | Distance-first default sort requirement |
| [Rules](#rules) | Hard constraints for AI agents and developers |

---

## What This Is

`web-marketplace` is a **creator-discovery and connection marketplace**. The primary unit is the **Creator Profile** — a showcase of who someone is and what they offer. Buyers discover creators through browsing, search, or the local map; creators list Products, Services, and Materials. Local proximity is a first-class feature: the platform connects people with makers, specialists, authors, and suppliers in their area.

This is not a product-first catalog. The discovery path is: **find a person → explore what they do → engage** (buy, hire, source, message). Products and transactions flow through creator profiles.

---

## Directory Structure

```
web-marketplace/
├── .ai/                        ← AI instructions (authoritative)
│   └── instruct.md
├── api/                        ← Express + TypeORM backend (PostgreSQL)
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts            ← Entry — mounts all routes, serves frontend, port 3000
│       ├── database.ts         ← TypeORM DataSource — owns Marketplace-table migrations
│       ├── config/
│       │   ├── jwt.ts          ← JWT_SECRET shared with WEB-HMI and WEB-FwServer
│       │   └── stripe.ts
│       ├── entities/           ← All Marketplace DB entities (User, Product, Order, Bid, etc.)
│       ├── migrations/         ← Marketplace-table migrations only (devices/firmwares moved to their services)
│       ├── routes/             ← Auth, products, orders, bids, payments, messaging, admin...
│       ├── services/           ← Stripe, WebSocket, geocode, etc.
│       └── jobs/               ← Scheduled jobs (billing, payouts)
└── frontend/                   ← React 18 + TypeScript + Vite SPA
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.js          ← @vitejs/plugin-react, BASE_PATH env var, dev proxy
    ├── index.html              ← Minimal React shell (20 lines — mounts /src/main.tsx)
    ├── styles.css              ← Master stylesheet — @imports all css/ modules
    ├── css/                    ← Component CSS modules (_variables, _navbar, _layout, etc.)
    ├── js/                     ← Legacy vanilla JS reference — NOT loaded by build
    └── src/
        ├── vite-env.d.ts       ← /// <reference types="vite/client" />
        ├── main.tsx            ← React entry — imports styles.css + shell.css, mounts <App>
        ├── App.tsx             ← BrowserRouter + Routes (BrowseLayout / DashboardLayout)
        ├── shell.css           ← React layout classes (browse-layout, bottom-nav, dashboard-*)
        ├── api/
        │   └── client.ts       ← Typed fetch wrapper — all API calls go through here
        ├── context/
        │   └── AuthContext.tsx ← Auth state (user from localStorage + httpOnly cookie)
        ├── components/
        │   ├── layout/
        │   │   ├── BrowseLayout.tsx      ← TopNav + <Outlet> + BottomNav
        │   │   ├── DashboardLayout.tsx   ← TopNav + DashboardSidebar + <Outlet>
        │   │   ├── TopNav.tsx            ← Logo + 7-item section nav (desktop) + auth
        │   │   ├── BottomNav.tsx         ← 5-item fixed bottom bar (mobile only)
        │   │   └── DashboardSidebar.tsx  ← Role-aware sidebar nav
        │   └── auth/
        │       └── AuthModal.tsx         ← Login / register modal (single component, mode prop)
        └── pages/
            ├── Discover.tsx
            ├── Products.tsx
            ├── Services.tsx
            ├── Materials.tsx
            ├── Creators.tsx
            ├── Board.tsx
            ├── MapPage.tsx
            └── dashboard/
                ├── Dashboard.tsx
                └── AccountSettings.tsx
```

---

## Role Terminology

| Role | Label | DB | Notes |
|------|-------|-----|-------|
| Buyer | **Buyer** | `users` (role=BUYER) | Purchases products, requests services |
| Creator/Designer | **Designer** | `users` (role=DESIGNER), `sellers` | Lists products, offers design services |
| Manufacturer | **Producer** | `users` (role=PRODUCER), `manufacturers` | Manufacturing services, fulfills product orders |
| Tradesperson | **Specialist** | `users` (role=SPECIALIST) | Services only — electrician, mason, home automation, etc. |
| Writer/Creator | **Author** | `users` (role=AUTHOR) | Books (products) + writing/consulting (services) |
| Materials vendor | **Supplier** | `users` (role=SUPPLIER) | Raw materials and components (B2B-focused) |

> **Legacy note**: Tables `sellers` and `manufacturers` retain original names for migration stability. All user-facing text uses **Designer** and **Producer** for those roles. New roles (Specialist, Author, Supplier) are **architecturally defined but not yet implemented** — do not add DB migrations for them until the feature work begins.

---

## Platform Concept Architecture

### Listing Types

Every creator can hold any combination of listing types. A single profile may list books (Products), editing services (Services), and reference manuscripts (Portfolio).

| Type | Description | Transaction model |
|------|-------------|-------------------|
| **Product** | Finished physical good — book, furniture, printed part, kit | Add to cart → buy |
| **Service** | Hired work performed by the creator | Request → Quote → Accept → Deliver (full workflow) |
| **Material** | Raw material, component, or bulk supply | Add to cart → buy (bulk/unit pricing, MOQ) |
| **Portfolio** | Showcase item — past work, examples, photos | No transaction — discovery only |

**Services workflow** is a structured engagement, not a contact form:

```
Client submits Request (scope, location, budget range, timeline)
    ↓
Provider sends Proposal (price, timeline, notes)
    ↓
Client accepts → Engagement created (status: in-progress)
    ↓
Work completed → Client confirms → Review + payment released
```

This uses `service_requests`, `proposals`, and `engagements` entities. These are distinct from the existing `bids` system (which handles Producer fulfillment of Designer product orders — a separate B2B backend flow).

### Creator Profile Types

All creators share the same profile structure. Type determines default content, not capability.

| Type | Primary listings | Typical use |
|------|-----------------|-------------|
| **Designer** | Products + Services | Custom design work, sellable files, physical goods |
| **Producer/Maker** | Services + Products | Manufacturing capacity, fabrication, direct goods |
| **Author** | Products (books) + Services | Published works, workshops, editorial services |
| **Specialist** | Services only | Electrician, mason, home automation installer, etc. |
| **Supplier** | Materials | Bulk raw materials, components, stock supply |

### Navigation Structure

Seven primary sections, all accessible without an account:

| Section | Purpose |
|---------|----------|
| **Discover** | Hero landing — featured creators, trending products/services, local activity |
| **Products** | Browse and buy finished goods |
| **Services** | Browse and hire (full request/quote/engage workflow) |
| **Materials** | Source raw materials and components (B2B-focused) |
| **Creators** | Browse all creator profiles, filterable by type |
| **Board** | Community — project requests, bulletin posts, custom commissions |
| **Map** | Proximity view of creators, products, and services near you |

Newsletter and "How It Works" live in the footer. Dashboard lives in the authenticated user dropdown.

---

## Layout and Navigation

**Guiding principle**: Prefer layout patterns with published UX research backing. When patterns conflict, favor the solution with the broadest positive user outcomes across the widest audience — a meld or multi-path solution is preferred over a single opinionated layout. Avoid patterns based solely on aesthetics or convention.

### Two UI Contexts

The site operates in two structurally distinct UI contexts that require different navigation patterns. Never mix them.

| Context | Who | Desktop pattern | Mobile pattern |
|---------|-----|-----------------|----------------|
| **Browse** | Anonymous visitors + Buyers | Top navbar | Bottom tab bar |
| **Dashboard** | Logged-in Creators / Providers | Persistent left sidebar | Slide-out drawer |

### Browse Context — Navigation

**Desktop — top navbar, max 7 items:**
```
Logo | Discover | Products | Services | Materials | Creators | Board | Map | [Cart] [Sign In / User ▼]
```

**Mobile — bottom tab bar, 5 items + overflow:**
```
[Discover]  [Products]  [Services]  [Creators]  [More ▲]
```
"More" expands to: Materials, Board, Map.

Rules:
- Maximum 7 items in the desktop top nav (cognitive load ceiling — 5±2 per Miller's Law)
- Maximum 5 items in the mobile bottom bar before More overflow
- **Never use a hamburger menu as the primary browse nav on mobile**
- Location indicator (detected zip/city) lives in the top navbar — it is a first-class feature, not a buried setting

### Dashboard Context — Navigation

**Desktop** — persistent left sidebar, role-specific sections:

| Role | Sidebar sections |
|------|------------------|
| Buyer | Orders, Saved, Messages, Account |
| Designer | My Listings, Orders, Analytics, Messages, Account |
| Producer | Service Queue, Proposals, Messages, Account |
| Author | My Books, My Services, Messages, Account |
| Specialist | My Services, Requests, Messages, Account |
| Supplier | My Materials, Orders, Messages, Account |

**Mobile** — hamburger opens a slide-out drawer. Acceptable here: users expect the drawer pattern in authenticated app contexts.

### Research Basis

| Pattern | Evidence |
|---------|----------|
| Bottom tab bar beats hamburger on mobile | Nielsen Norman Group; Luke Wroblewski; Facebook/Instagram A/B studies. Hamburger reduces feature discoverability 30–66%. |
| 5±2 item limit for primary nav | Miller's Law — cognitive load research on working memory capacity |
| Top nav adequate for ≤7 desktop items | Nielsen Norman Group |
| Left sidebar optimal for dashboard nav | Nielsen Norman Group — persistent sidebar reduces navigation errors in complex authenticated states |
| Hamburger acceptable in dashboard/drawer context | Convention is established; users correctly predict slide-out behavior in app contexts |

---

## Database Ownership

> **→ `DB-Central/AI-INSTRUCT.md`** — DB-Central is the single source of truth for ALL TypeORM entities and migrations across this service, WEB-HMI/api, and WEB-FwServer/api.

All three backend services share one PostgreSQL database (`pds_marketplace`). Entities and migrations now live in `DB-Central/src/` — the 5 User-linked entities (`User`, `Designer`, `Producer`, `Product`, `Service`) are re-export shims to `@db-central`; the remaining 23 Marketplace-specific entities are local copies that map to the same DB schema.

**Authoritative docker-compose**: `DB-Central/docker-compose.yml` (see `/db-start-db`). `web-marketplace/api/docker-compose.yml` is a legacy copy.

| Service | Tables owned | Status |
|---------|--------------|--------|
| `DB-Central` | ALL tables — Marketplace, HMI, FwServer | ✅ Authoritative source |
| `web-marketplace/api` | Marketplace-specific tables (no device/firmware tables) | ✅ Migrated — `User`, `Designer`, `Producer`, `Product`, `Service` are @db-central shims; remaining entities are local copies mapped to the same schema |
| `WEB-HMI/api` | Device tables (`devices`, `device_configs`, `telemetry_logs`) | ✅ Migrated to DB-Central |
| `WEB-FwServer/api` | `firmwares` | ⬜ Migration pending |

**DB-Central `tsconfig.json` path alias** is already wired in `web-marketplace/api/tsconfig.json`:
`"@db-central/*": ["../../DB-Central/src/*"]`

> **History**: Device and firmware migrations were originally in `web-marketplace/api/src/migrations/`. They were moved to their owning services in May 2026. DB-Central scaffold created June 2026 as the consolidated entity and migration home.

---

## Auth

- JWT (`JWT_SECRET` env var). Must match across all three services.
- Marketplace-issued tokens are valid in `WEB-HMI` and `WEB-FwServer`.

---

## Development

```powershell
# Backend API (port 3000)
Set-Location "k:\PDS_AutomationSuite\web-marketplace\api"
npm install
npm run dev

# Frontend (Vite dev server, port 5174 or configured in vite.config.js)
Set-Location "k:\PDS_AutomationSuite\web-marketplace\frontend"
npm install
npm run dev
```

Vite proxies `/v1/*` → `http://localhost:3000` in dev. No gateway, no path prefix. Dev `frontend/.env` leaves `BASE_PATH` and `API_BASE` empty so all defaults resolve to `/`.

---

## Deployment

- **Railway**: one monolithic service (`web-marketplace/api`). The API builds and serves the Vite frontend from `../../frontend/dist` via `express.static`. No separate frontend service.
- **Path prefix**: `/marketplace` for frontend; `/marketplace/api` for API calls — controlled by build-time env vars `BASE_PATH=/marketplace/` and `API_BASE=/marketplace/api` set in Railway dashboard.
- **URL shape**: `pipedreamsystems.com/marketplace/` (frontend) and `pipedreamsystems.com/marketplace/api/v1/...` (API).
- **Gateway**: `WEB-Gateway/` Nginx service has two location rules: `/marketplace/api/` strips the API prefix before forwarding (Express sees `/v1/...`), and `/marketplace/` strips the frontend prefix for assets/SPA.
- **Railway build command** (in `railway.toml`): builds frontend first, then API.
- **Env vars required at build time** (Railway dashboard):
  - `BASE_PATH=/marketplace/`
  - `API_BASE=/marketplace/api`
- **Env vars required at runtime**:
  - `DATABASE_URL`, `JWT_SECRET`, `NODE_ENV=production`, `PORT`
  - `STRIPE_SECRET_KEY`, `STRIPE_PUBLIC_KEY`, `STRIPE_WEBHOOK_SECRET`
  - `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`
  - `ALLOWED_ORIGINS=https://pipedreamsystems.com`
- **Local dev**: API on `:3000`, frontend Vite dev server (separate, proxies `/v1` → `:3000`). No gateway, no path prefix. Dev `.env` leaves `BASE_PATH` and `API_BASE` empty.

### Split Seam

To split this monolith into a standalone API + standalone frontend service (no code changes once the seam is wired):

1. In `web-marketplace/api/src/index.ts`, wrap the static-serving block with `if (process.env.SERVE_FRONTEND !== 'false')`. Set `SERVE_FRONTEND=false` on Railway → pure API mode.
2. Deploy `web-marketplace/frontend/` as a new Railway static service; it builds `dist/` and serves it with `serve -s dist`.
3. Extend `apiFetch` (in `js/utils.js`) to check `__API_ORIGIN__` as a fallback before `__API_BASE__` (for cross-domain splits; same-domain gateway split needs no change here).
4. In `WEB-Gateway/nginx.conf`, point `location /marketplace/` to the new frontend service and `location /marketplace/api/` to the API service.

See `## Future: Splitting Frontend and API` in `.github/TODO/ToDo-05162026-PathRouting.md` for full cost estimate and step details.

---

## Search Sort Order

**All creator, product, and materials search results must default to distance-sorted (closest first) whenever user location is available.**

Applies to: **Creators** (designers + producers), **Products**, **Materials**. Services re-exports Creators and is covered automatically.

- Source priority: user's saved `businessLatitude`/`businessLongitude` (from auth context) → browser `navigator.geolocation` → no distance sort
- Distance is computed client-side using the Haversine formula (see `frontend/src/hooks/useUserLocation.ts`)
- Results without coordinates sort to the bottom (`Infinity` distance)
- If no user location is available, keep the API's default sort (rating DESC for designers/producers)
- The location indicator in the top navbar is the user's reference point — it must always match the coords used for sorting

**Creators/Materials**: distance sort is applied automatically (no user choice needed).  
**Products**: `'Nearest'` is the first and default option in the sort dropdown; users can override to Top Rated, Price, or Newest.  
**Field names**: designers/producers use `latitude`/`longitude`; products/materials use `designerLatitude`/`designerLongitude` from the API response.

**Implementation**: `useUserLocation` hook in `frontend/src/hooks/useUserLocation.ts` — returns `{ lat, lng, source }` or `null`. Sort in `useMemo` after filtering, not before (to preserve filter correctness).

---

## Rules

- **Never** add device provisioning, OTA, or firmware logic here. Those belong in `WEB-HMI`.
- **Only** run migrations for Marketplace tables from this service. Device table migrations live in `WEB-HMI/api/src/migrations/`; firmware table migrations live in `WEB-FwServer/api/src/migrations/`.
- **Never** use subdomain references (`marketplace.pipedreamsystems.com` is deprecated).
- For AI agents: also read `web-marketplace/api/src/.AI-Instruct.md` if it exists when working in the API.
