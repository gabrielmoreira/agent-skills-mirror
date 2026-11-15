#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v python3 >/dev/null; then
  echo "python3 is required" >&2
  exit 1
fi

# Create the virtualenv
python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate

pip install --upgrade pip
pip install -e '.[dev]'

if [ ! -f wxdata.yaml ]; then
  cat > wxdata.yaml <<'YAML'
database_url: postgresql+psycopg://wx@localhost/wxdata
skyfeed_api_key: ""
stations: []
YAML
  echo "Wrote wxdata.yaml; fill in skyfeed_api_key before running wx ingest."
fi

if command -v createdb >/dev/null && ! psql -lqt | cut -d '|' -f 1 | grep -qw wxdata; then
  createdb wxdata
fi

alembic upgrade head
echo "Ready. Try: wx ingest --day $(date -u +%F)"
