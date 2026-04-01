# OpenClaw Enterprise — Demo

Run the real production frontend locally with mock data. No AWS account needed.

## Quick Start

```bash
# 1. Build the frontend (one-time)
cd enterprise/admin-console
npm install && npm run build

# 2. Copy dist to demo
cp -r dist ../demo/dist

# 3. Run demo server
cd ../demo
python3 server.py

# 4. Open http://localhost:8099
```

## What You Get

The exact same React frontend that runs in production — same pages, same animations, same dark theme. The only difference: API calls return mock data instead of hitting DynamoDB/S3.

## Demo Accounts

Login with any employee ID. Password can be anything (demo mode accepts all).

| Employee ID | Name | Role | What You See |
|-------------|------|------|-------------|
| emp-z3 | Zhang San | Admin | Full Admin Console (19 pages) |
| emp-lin | Lin Xiaoyu | Manager | Dashboard scoped to Product dept |
| emp-mike | Mike Johnson | Manager | Dashboard scoped to Sales dept |
| emp-w5 | Wang Wu | Employee | Portal: SDE Agent chat |
| emp-carol | Carol Zhang | Employee | Portal: Finance Agent chat |
| emp-emma | Emma Chen | Employee | Portal: CSM Agent chat |

## Scenarios to Try

1. Login as `emp-z3` (Admin) → explore all 19 admin pages
2. Login as `emp-carol` (Employee) → chat in Portal, see permission denial for shell
3. Open SOUL Editor → see three-layer identity injection (Global locked, Position editable, Personal)
4. Open Audit Center → AI Insights tab → see anomaly detection results
5. Open Usage & Cost → compare $65/mo vs ChatGPT $500/mo
6. Login as `emp-lin` (Manager) → notice data is scoped to Product department only

## How It Works

`server.py` is a ~400-line Python HTTP server that:
- Serves the production `dist/` folder (same Vite build output)
- Intercepts `/api/v1/*` requests and returns mock JSON
- Handles JWT auth (issues real tokens, accepts any password)
- SPA fallback (all non-asset routes serve `index.html`)

No dependencies beyond Python 3.10+ standard library.

## Files

```
demo/
├── README.md      # This file
├── server.py      # Mock API server (~400 lines, zero dependencies)
└── dist/          # Production frontend build (copied from admin-console)
```

## vs Production

| | Demo | Production |
|-|------|-----------|
| Frontend | Same React build | Same React build |
| Data | Mock JSON in server.py | DynamoDB + S3 |
| Agent chat | Simulated response | Real Bedrock via AgentCore |
| Auth | Any password works | ADMIN_PASSWORD env var |
| AWS | Not needed | Required |
