# Port Registry - web-firmware-server

## Frontend

| Service | Port | Notes |
|---------|------|-------|
| None (API-only service) | — | No frontend application |

## Backend API (Express + TypeScript)

| Service | Port | Notes |
|---------|------|-------|
| Express OTA Server | **3002** | Configured in .env.example for firmware storage and OTA delivery |

## Database / Other

| Service | Port/Value | Notes |
|---------|------------|-------|
| PostgreSQL (shared) | 5432 | Shared with web-hmi and web-marketplace via DATABASE_URL |