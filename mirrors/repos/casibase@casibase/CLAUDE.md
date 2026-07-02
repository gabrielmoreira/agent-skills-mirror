# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Backend (Go)**
```bash
go build                    # build backend binary
go run main.go              # run backend (port 14000)
go test ./...               # run all tests
go test ./object/... -run TestFoo  # run a single test
```

**Frontend (React)**
```bash
cd web && yarn install
yarn start                  # dev server on port 13001
yarn build                  # production build (output goes to web/build, then copied to static/)
yarn lint:js                # lint JS
```

**Full production build** uses `build.sh` which cross-compiles for linux/amd64, linux/arm64, linux/riscv64.

Backend serves the frontend as embedded static files (`embed.go`); during development the frontend proxy is configured to hit `localhost:14000`.

## Architecture

### Backend (Go / Beego)

**Module:** `github.com/the-open-agent/openagent`

The backend is a standard [Beego](https://beego.vip/) MVC app. Every entity follows the same three-layer pattern:

1. **`object/<entity>.go`** — struct definition (xorm tags for DB), and all DB access functions: `GetGlobal<Entities>`, `Get<Entity>Count`, `GetPagination<Entities>`, `Get<Entity>`, `Add<Entity>`, `Update<Entity>`, `Delete<Entity>`. The primary key is always `(Owner string, Name string)`. Use `util.GetId(owner, name)` / `util.GetOwnerAndNameFromIdWithError(id)` for composite key serialization.

2. **`controllers/<entity>.go`** — Beego controller methods wired to routes. Standard set: `GetGlobal<Entities>`, `Get<Entities>`, `Get<Entity>`, `Add<Entity>`, `Update<Entity>`, `Delete<Entity>`. Use `c.IsAdmin()` / `c.IsGlobalAdmin()` / `c.RequireSignedIn()` for auth. Paginated list APIs accept `p`, `pageSize`, `field`, `value`, `sortField`, `sortOrder` query params and use `pagination.SetPaginator`.

3. **`routers/router.go`** — `beego.Router` calls grouped by entity (all routes for the same entity's CRUD kept together). No alphabetical ordering within a group. New entity routes should be inserted next to their entity's existing routes (not appended to the end of the file).

**DB schema** is auto-migrated via `object/adapter.go` → `createTable()` using `engine.Sync2(new(EntityStruct))`. Add new entities there.

**i18n (backend):** `i18n/locales/{en,zh}/data.json` — keys are namespaced by category (e.g. `"comment:..."`, `"general:..."`). Use `c.T("namespace:key")` in controllers.

### Frontend (React)

**Routing** is all in `web/src/ManagementPage.js` — both the left sidebar menu and `<Route>` declarations live there. To add a new admin page:
1. Add a `<Route>` in `renderRouter()`.
2. Add a menu entry in the `getMenuItems()` function (within the correct group — Basic / Connectors / Admin etc.).
3. Add the nav key to `NavItemTree.js` (`web/src/component/nav-item-tree/NavItemTree.js`) so it appears in the site Navbar Items config.

**Page pattern:** List pages extend `BaseListPage` (class component). They implement `fetch()` which calls a backend function and calls `this.setState({data, pagination})`. Edit pages are plain class components with `UNSAFE_componentWillMount` for initial data load. Both patterns are illustrated by `MessageListPage.js` / `MessageEditPage.js`.

**Backend API layer:** `web/src/backend/<Entity>Backend.js` — thin `fetch()` wrappers, one file per entity. Standard exports: `getGlobal<Entities>`, `get<Entity>`, `update<Entity>`, `add<Entity>`, `delete<Entity>`.

**i18n (frontend):** `web/src/locales/{en,zh}/data.json` namespaced by page/domain. Use `i18next.t("namespace:key")`.

### Key conventions

- Owner is always `"admin"` for system-created entities.
- Entity `Name` is a random string generated with `util.GetRandomString(n)` or a user-provided slug.
- `CreatedTime` / `UpdatedTime` use `util.GetCurrentTimeWithMilli()` (string format).
- Delete responses use `affected != 0` boolean pattern.
- All API responses go through `c.ResponseOk(data)` or `c.ResponseError(msg)`.
- The `conf/app.conf` file configures DB (`driverName`, `dataSourceName`, `dbName`) and port (`httpport = 14000`).
