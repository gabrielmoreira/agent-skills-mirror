"""Nightly CSV export for the finance warehouse, run from deploy/crontab."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path

from wxdata.config import load_settings
from wxdata.db import init_engine, session_scope
from wxdata.export import to_legacy_csv
from wxdata.models import readings_between


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="Directory for the CSV files.")
    args = parser.parse_args(argv)

    settings = load_settings()
    init_engine(settings.database_url)
    end = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=1)
    with session_scope() as session:
        readings = readings_between(session, start, end)
        written = to_legacy_csv(readings, args.out / f"readings_{start:%Y%m%d}.csv")
    print(f"exported {written} readings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
