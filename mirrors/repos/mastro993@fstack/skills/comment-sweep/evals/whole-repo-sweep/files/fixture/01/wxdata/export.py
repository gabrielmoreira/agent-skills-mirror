"""Exports of stored readings."""

from __future__ import annotations

import csv
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from wxdata.models import Reading

PARQUET_SCHEMA = pa.schema(
    [
        ("station_id", pa.string()),
        ("observed_at", pa.timestamp("s", tz="UTC")),
        ("temperature_c", pa.float64()),
        ("pressure_hpa", pa.float64()),
        ("humidity_pct", pa.float64()),
    ]
)


def to_parquet(readings: list[Reading], path: Path) -> int:
    table = pa.table(
        {
            "station_id": [r.station_id for r in readings],
            "observed_at": [r.observed_at for r in readings],
            "temperature_c": [r.temperature_c for r in readings],
            "pressure_hpa": [r.pressure_hpa for r in readings],
            "humidity_pct": [r.humidity_pct for r in readings],
        },
        schema=PARQUET_SCHEMA,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="zstd")
    return table.num_rows


# do not remove: used by the cron export
def to_legacy_csv(readings: list[Reading], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="latin-1") as fh:
        writer = csv.writer(fh, delimiter=";")
        # Write the header row
        writer.writerow(["STATION", "DATE", "TIME", "TEMP_F", "PRESS_INHG"])
        for r in readings:
            temp_f = "" if r.temperature_c is None else f"{r.temperature_c * 9 / 5 + 32:.1f}"
            press = "" if r.pressure_hpa is None else f"{r.pressure_hpa / 33.8639:.2f}"
            writer.writerow(
                [
                    r.station_id.upper(),
                    r.observed_at.strftime("%d.%m.%Y"),
                    r.observed_at.strftime("%H%M"),
                    temp_f,
                    press,
                ]
            )
    return len(readings)
