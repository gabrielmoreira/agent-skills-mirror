# Port Registry - web-hmi

## Frontend (Vite)

| Service | Port | Notes |
|---------|------|-------|
| Main App (React) | **5173** | Vite dev server port. Run: `npm run dev` in this directory |

## Backend API (Express + TypeScript)

| Service | Port | Notes |
|---------|------|-------|
| Express API | **3001** | Configured in .env.example, used for device management API with OTA support |

## Database / Other

| Service | Port/Value | Notes |
|---------|------------|-------|
| PostgreSQL (shared) | 5432 | Shared with web-marketplace via DATABASE_URL |

> **Note on Vite port sharing**: Each module runs its own Vite dev server in a separate terminal/process. The frontend port is only active when `npm run dev` is executed in that specific module's directory.
