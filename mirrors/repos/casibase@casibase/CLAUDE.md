# Casibase - Claude Code Guide

## Project Overview

Casibase is an open-source enterprise-level AI knowledge base and MCP (Model Context Protocol) / A2A (Agent-to-Agent) management platform. It supports 30+ AI model providers (OpenAI, Claude, Gemini, Ollama, etc.) with admin UI, user management, and SSO via Casdoor.

## Architecture

Full-stack application:
- **Backend:** Go 1.23.6 + Beego framework (MVC), MySQL/MariaDB
- **Frontend:** React + Ant Design v5, located in `web/`
- **Auth:** Casdoor SSO integration

## Directory Structure

```
casibase/
├── main.go                 # Entry point
├── go.mod                  # Go module
├── conf/app.conf           # Beego config
├── controllers/            # HTTP handlers (60+ files)
├── object/                 # Business logic & data models (85+ files)
├── model/                  # AI model provider integrations (38+ files)
├── routers/                # Routes and middleware filters
├── embedding/              # Embedding provider implementations
├── agent/                  # MCP agent support
├── split/                  # Text splitting strategies
├── txt/                    # Document parsing (PDF, CSV, XLSX, PPTX)
├── storage/                # File storage abstractions
├── util/                   # Utilities
└── web/                    # React frontend
    ├── src/
    └── package.json
```

## Build & Run

### Backend
```bash
# Build
go build -race -ldflags "-extldflags '-static'"

# Cross-platform build (linux amd64/arm64/riscv64)
./build.sh
```

### Frontend
```bash
cd web
yarn install
yarn start       # Dev server
yarn run build   # Production build
```

### Docker
```bash
docker-compose up
```

## Testing

```bash
# Go tests (requires MySQL)
go test -v $(go list ./...) -tags skipCi

# Frontend tests
cd web && yarn test
```

## Linting

```bash
# Go - uses golangci-lint with gofumpt
golangci-lint run

# Frontend
cd web && yarn lint
```

## Key Conventions

### Backend (Go)
- Framework: Beego MVC - controllers handle HTTP, objects contain business logic
- New AI providers go in `model/` (implement the provider interface)
- Database access via Beego ORM in `object/`
- Route registration in `routers/router.go`
- i18n strings: avoid duplicate keys across frontend and backend

### Frontend (React)
- UI components use Ant Design v5
- i18n via i18next; translation files in `web/src/locales/`
- State via React Context/Hooks (no Redux)
- API calls go through `web/src/backend/` helper modules

### Commits & PRs
- Branch naming: `claude/<name>`
- Main branch: `master`
- Follows semantic versioning (`.releaserc.json`)
- PR titles should be semantic (feat/fix/chore/docs/refactor)

## CI/CD (GitHub Actions)

`.github/workflows/build.yml` runs:
1. Go unit tests (with MySQL service)
2. Frontend build (Node.js 20 + Yarn)
3. Go binary build
4. golangci-lint
5. Semantic release + Docker push to `casbin/casibase`

## Configuration

- Backend config: `conf/app.conf` (Beego format)
- Database: MySQL 8.0+ or MariaDB
- Default Docker DB: MySQL 8.0.25 via `docker-compose.yml`

## Important Files

| File | Purpose |
|------|---------|
| `main.go` | Application entry point |
| `routers/router.go` | All API route definitions |
| `object/init.go` | Application initialization |
| `conf/app.conf` | Runtime configuration |
| `web/src/App.js` | Frontend root component |
| `web/src/backend/` | API client helpers |
