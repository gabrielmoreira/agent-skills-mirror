# Frontend Module Architecture Guide

> **Parent**: Refer to `marketplace/.ai/instruct.md` for marketplace-level instructions and `copilot-instructions.md` for the depth-priority hierarchical methodology.

## Overview
The PDS Marketplace frontend uses a **modular architecture** with 16 focused JS modules and a fully modular CSS structure, bundled via **Vite**.

### Build System
- **Bundler:** Vite (dev server on port 5173, proxies `/v1` and `/socket.io` to Express backend on port 3000)
- **Entry point:** `main.js` â€” imports all JS modules and CSS in dependency order
- **HTML:** `index.html` loads `main.js` as a `<script type="module">`
- **Production:** `vite build` outputs to `dist/`; Express serves the built files in production

### CSS Architecture
All styles are organized into **21 single-responsibility CSS modules** in the `css/` directory, imported via `styles.css` (the master stylesheet). See `css/.ai/instruct.md` for the full file inventory, import order rules, responsive breakpoint conventions, and editing guidelines.

Key principles:
- One file per component/feature (cards, modals, cart, map, etc.)
- Entity-specific card files: `_cards-product.css`, `_cards-designer.css`, `_cards-producer.css`
- Responsive overrides isolated in `_tablet.css` (â‰¤768px) and `_phone.css` (â‰¤480px), loaded last
- All colors via CSS custom properties in `_variables.css`; no preprocessor needed (Vite handles `@import`)

## JS Module Breakdown (16 modules)

All modules are loaded via ES `import` statements in `main.js`. Each module attaches its exports to `window` for compatibility with `onclick` handlers in HTML.

### Core Modules (loaded first, order matters)

#### 1. **js/auth.js** â€” Authentication
- `AuthService` singleton â†’ `window.authService`
- Login, signup, logout, user profile management
- Cookie-only auth (httpOnly `pds_token` cookie set by server; no token stored in localStorage)
- Role-based UI visibility (buyer/designer/producer/admin)

#### 2. **js/theme.js** â€” Theme Toggle
- `initializeTheme()`, `toggleTheme()`, `watchSystemTheme()`
- Dark/light mode via CSS class on `<html>` + localStorage persistence
- System theme detection via `prefers-color-scheme`

#### 3. **js/data.js** â€” Data Arrays & API Fetch
- `designers`, `producers`, `products`, `customProjects`, `buyerLocation`
- `fetchDesignersFromAPI()`, `fetchProducersFromAPI()`, `fetchAllMarketplaceData()`
- Standalone, no dependencies
- Empty arrays populated from `/v1/search/designers` and `/v1/search/producers` at startup
- Backward-compatible aliases (`mockDesigners = designers`, etc.) maintained for legacy references
- Newsletter posts kept as static editorial content

#### 4. **js/utils.js** â€” Shared Helpers
- `calculateDistance()` â€” Haversine formula (miles)
- `formatPrice()`, `generateStars()`, `parseLocation()`
- `escapeHtml()` â€” XSS protection for rendered content
- `debounce()` â€” Input throttling
- Pure functions, no dependencies

#### 5. **js/websocket.js** â€” WebSocket Client
- Socket.IO client â†’ `window.wsClient`
- Real-time notification delivery
- Connection management and reconnection

### Feature Modules (loaded after core)

#### 6. **js/search.js** â€” Search & Discovery (Phase 4)
- Product, designer, and producer search
- Saved searches CRUD
- Favorites/wishlist management
- Recommendations display
- ~450 lines, 20+ functions

#### 7. **js/render.js** â€” DOM Rendering
- `renderProducts()`, `renderDesigners()`, `renderProducers()`
- Product/designer/producer card HTML generation
- Result rendering for search
- Largest module (~15 KB) due to HTML template strings

#### 8. **js/ui.js** â€” UI Interactions
- `setupMap()` â€” Leaflet map initialization
- `updateLocation()`, `contactBusiness()`
- `showTab()`, `showSection()` â€” Navigation
- Modal management helpers

#### 9. **js/cart.js** â€” Shopping Cart (Phase 1)
- Cart state in localStorage
- Add/remove/update quantities
- Checkout flow with address selection
- Order placement via `/v1/orders`

#### 10. **js/products.js** â€” Designer Product Management (Phase 2a)
- Product CRUD forms
- Publish/unpublish toggle
- Producer routing configuration
- "My Products" dashboard tab

#### 11. **js/producer-queue.js** â€” Producer Queue (Phase 2b)
- Available orders browsing
- Bid submission with quotes and lead times
- Bid tracking and withdrawal
- Producer statistics dashboard
- ~380 lines

#### 12. **js/messaging.js** â€” Messaging (Phase 6)
- User-to-user conversations
- Message threading
- Conversation search
- Unread indicators

#### 13. **js/notifications.js** â€” Notifications (Phase 6)
- System notification display (17+ event types)
- Notification preferences management
- Unread badge counts
- Mark-as-read functionality

#### 14. **js/admin.js** â€” Admin Dashboard (Phase 7)
- User management (verify, suspend)
- Order monitoring
- Dispute resolution
- Site settings editor
- ~612 lines, 19 functions

#### 15. **js/bulletin-board.js** â€” Bulletin Board
- Bulletin card posting UI ($1 Stripe fee)
- Card browsing and display
- Integration with invoiceService

### Coordinator

#### 16. **app.js** â€” Main Coordinator
- Page initialization on DOMContentLoaded
- Event listener wiring for all features
- Tab navigation coordination
- Dashboard tab management (`showDashboardTab()`)
- Fee structure modal
- Newsletter rendering

## Import Order (Critical!)

The `main.js` file imports all modules in strict dependency order:

```javascript
// CSS â€” Vite resolves @import chains automatically
import "./styles.css";

// Core modules (order matters)
import "./js/auth.js";        // AuthService singleton
import "./js/theme.js";       // Theme toggle
import "./js/data.js";        // Data arrays + API fetch functions (no deps)
import "./js/utils.js";       // Shared helpers (no deps)
import "./js/websocket.js";   // WS client

// Feature modules
import "./js/search.js";
import "./js/render.js";
import "./js/ui.js";
import "./js/cart.js";
import "./js/products.js";
import "./js/producer-queue.js";
import "./js/messaging.js";
import "./js/notifications.js";
import "./js/admin.js";
import "./js/bulletin-board.js";

// Main coordinator (must be last)
import "./app.js";
```

**DO NOT CHANGE THIS ORDER** â€” core modules must load before feature modules that depend on them.

## External Libraries (loaded in index.html)

| Library | Purpose | Load Method |
|---|---|---|
| Leaflet 1.9.4 | Map rendering | `<script>` + `<link>` in `<head>` |
| Stripe.js v3 | Payment UI | `<script>` in `<head>` |
| Socket.IO | Real-time events | `<script>` from Express server (`/socket.io/socket.io.js`) |

## Architecture Benefits

- **Separation of Concerns**: Each module has a single responsibility
- **Vite Bundling**: Fast dev server with HMR, optimized production builds
- **Testability**: Modules can be unit tested independently
- **Maintainability**: Changes to one module don't affect others
- **Scalability**: Easy to add new modules

## Adding New Features

1. **Create** the JS module in `js/` with functions attached to `window`
2. **Add** the `import` to `main.js` in the appropriate group
3. **Document** the module in this file
4. **Add CSS** to the appropriate `css/_*.css` file (or create a new one)
5. **Test** the module and its dependents

## Legacy Code

The original monolithic `app.js` has been backed up at `.old/app.js.bak`. The original monolithic `styles.css` (~2868 lines) was decomposed into 21 CSS modules on February 16, 2026. The previous `<script>` tag loading pattern was migrated to Vite module imports.

## Performance Notes

- **Lazy Loading**: Map is only initialized when the map tab is clicked
- **Debouncing**: Search inputs are debounced to prevent excessive calculations
- **DOM Updates**: Only necessary DOM nodes are updated
- **Theme Flash Prevention**: Inline `<script>` in `<head>` applies dark mode class before body renders

## Troubleshooting

**Issue**: Functions not found in console
- **Solution**: Ensure the module attaches to `window` and is imported in `main.js`

**Issue**: ReferenceError: products is undefined (or legacy mockProducts)
- **Solution**: `data.js` must be imported before any module that uses it in `main.js`. Data arrays start empty and are populated asynchronously via API calls during initialization.

**Issue**: Map not appearing
- **Solution**: Verify Leaflet library loads via `<script>` tag in `<head>` and map div exists

**Issue**: Vite dev server not proxying API calls
- **Solution**: Check `vite.config.js` proxy settings â€” `/v1` should proxy to `http://localhost:3000`

## Production Status

As of February 2026, the frontend is in **production mode**:
- All mock/hardcoded data has been removed â€” data is fetched from the API at startup
- Empty state messages display when API returns no data
- `data.js` arrays (`products`, `designers`, `producers`) are populated via `fetchAllMarketplaceData()`
- `app.js` dashboard functions (`loadPurchaseHistory`, `loadInProcessOrders`, `loadMyBids`) are fully API-backed
- `products.js` producer list is fetched from `/v1/search/producers`
- Map initialization is non-blocking (warns instead of errors if no data)

---
_Last updated: February 18, 2026_

