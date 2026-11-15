# wxdata

Pulls weather station readings from the SkyFeed API, cleans them, stores them in Postgres, and
builds the daily station report.

## Setup

```
scripts/bootstrap.sh
cp wxdata.example.yaml wxdata.yaml   # then fill in database_url and skyfeed_api_key
make migrate
```

## Everyday commands

| Command | What it does |
|---|---|
| `wx ingest --day 2024-07-01` | Fetch and store one day of readings |
| `wx report --day 2024-07-01 --out build/report.html` | Render the daily report |
| `wx export --start 2024-07-01 --end 2024-08-01 --out july.parquet` | Export readings to Parquet |
| `make test lint typecheck` | Checks run in CI |

## Layout

- `wxdata/` — the service
- `vendor/retrying_lite/` — vendored copy of retrying-lite 0.3.1; don't edit, re-vendor instead
- `wxdata/proto/` — generated from `proto/readings.proto` with `make proto`
- `migrations/` — Alembic migrations
- `infra/` — Terraform for the reports bucket and the database
