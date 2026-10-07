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

**Frontend (React + shadcn/ui, built with Vite)**
```bash
cd web && yarn install
yarn start                  # dev server on port 13001, proxies /api to localhost:14000
yarn build                  # production build (vite writes build-temp, mv.js swaps it into web/build)
yarn typecheck              # tsc --noEmit
yarn lint                   # eslint
```

`web-old/` holds the previous Ant Design frontend. It is kept for reference only
while bugs are chased down against it — it is not built, served or linted, and it
does not get new work.

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

### Frontend (React + shadcn/ui on Tailwind, TypeScript, Vite)

**Routing** lives in `web/src/App.tsx`; every file in `web/src/pages` is its own lazy chunk, loaded by name. To add a new admin page:
1. Create `web/src/pages/<Name>Page.tsx` (default export).
2. Add a `<Route>` in `App.tsx` pointing at `page("<Name>Page")`.
3. Add a menu entry in `getNavGroups()` (`web/src/lib/nav.ts`), in the correct group — Basic / Connectors / Admin etc.
4. Add the nav key to `web/src/components/common/NavItemTree.tsx` so it appears in the site Navbar Items config.

**Page pattern:** list pages render `CrudListPage` (`web/src/components/crud/`) with a `ColumnDef[]`; edit pages render `SimpleEditPage` with an `EditField[]`, or compose `EditPageShell` directly when the layout is custom. Both patterns are illustrated by `MessageListPage.tsx` / `MessageEditPage.tsx`.

**Backend API layer:** `web/src/backend/<Entity>Backend.ts` — thin `fetch()` wrappers, one file per entity. Standard exports: `getGlobal<Entities>`, `get<Entity>`, `update<Entity>`, `add<Entity>`, `delete<Entity>`.

**Per-instance config:** the backend sends the Casdoor issuer, client ID and branding in the `jsonWebConfig` cookie (set with index.html and with every `/api/get-account` response) and `web/src/Conf.ts` reads it at boot, so one build serves every instance.

**i18n (frontend):** `web/src/locales/{en,zh}/data.json` namespaced by page/domain. Use `i18next.t("namespace:key")`.

### Key conventions

- Owner is always `"admin"` for system-created entities.
- Entity `Name` is a random string generated with `util.GetRandomString(n)` or a user-provided slug.
- `CreatedTime` / `UpdatedTime` use `util.GetCurrentTimeWithMilli()` (string format).
- Delete responses use `affected != 0` boolean pattern.
- All API responses go through `c.ResponseOk(data)` or `c.ResponseError(msg)`.
- The `conf/app.conf` file configures DB (`driverName`, `dataSourceName`, `dbName`) and port (`httpport = 14000`).
