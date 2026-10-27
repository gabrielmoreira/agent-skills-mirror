#!/usr/bin/env python3
"""
Uptrend Analyzer - CSV Data Fetcher

Downloads and parses Monty's Uptrend Ratio Dashboard CSV data from GitHub.
No API key required - uses publicly available CSV files.

Data Sources:
- Timeseries: uptrend_ratio_timeseries.csv (all + 11 sectors, 2023/08~present)
- Sector Summary: sector_summary.csv (latest snapshot)
"""

import csv
import io
import math
import sys
from typing import Optional

import requests

TIMESERIES_URL = (
    "https://raw.githubusercontent.com/tradermonty/uptrend-dashboard/"
    "main/data/uptrend_ratio_timeseries.csv"
)
SECTOR_SUMMARY_URL = (
    "https://raw.githubusercontent.com/tradermonty/uptrend-dashboard/main/data/sector_summary.csv"
)

TIMESERIES_COLUMNS = ("worksheet", "date", "count", "total", "ratio", "ma_10", "slope", "trend")
SECTOR_SUMMARY_COLUMNS = ("Sector", "Ratio", "10MA", "Trend", "Slope", "Status")

WORKSHEET_TO_DISPLAY = {
    "sec_basicmaterials": "Basic Materials",
    "sec_communicationservices": "Communication Services",
    "sec_consumercyclical": "Consumer Cyclical",
    "sec_consumerdefensive": "Consumer Defensive",
    "sec_energy": "Energy",
    "sec_financial": "Financial",
    "sec_healthcare": "Healthcare",
    "sec_industrials": "Industrials",
    "sec_realestate": "Real Estate",
    "sec_technology": "Technology",
    "sec_utilities": "Utilities",
}

# Monty's official dashboard thresholds (same as in sector_participation_calculator)
OVERBOUGHT_THRESHOLD = 0.37
OVERSOLD_THRESHOLD = 0.097


def build_summary_from_timeseries(sector_timeseries: dict[str, dict]) -> list[dict]:
    """Build sector_summary-compatible list from timeseries latest rows.

    Used as fallback when sector_summary.csv is unavailable.

    Args:
        sector_timeseries: Dict mapping worksheet name -> latest timeseries row
            e.g. {"sec_technology": {"ratio": 0.288, "ma_10": 0.266, ...}}

    Returns:
        List of dicts matching sector_summary format:
            [{"Sector": "Technology", "Ratio": 0.288, "10MA": 0.266, ...}]
    """
    rows = []
    for ws_name, row in sector_timeseries.items():
        display_name = WORKSHEET_TO_DISPLAY.get(ws_name, ws_name)
        ratio = row.get("ratio")
        status = (
            "Overbought"
            if ratio is not None and ratio > OVERBOUGHT_THRESHOLD
            else "Oversold"
            if ratio is not None and ratio < OVERSOLD_THRESHOLD
            else "Normal"
        )
        rows.append(
            {
                "Sector": display_name,
                "Ratio": ratio,
                "10MA": row.get("ma_10"),
                "Trend": (row.get("trend") or "").capitalize(),
                "Slope": row.get("slope"),
                "Status": status,
                "Count": row.get("count"),
                "Total": row.get("total"),
            }
        )
    return rows


class UptrendDataFetcher:
    """Client for Monty's Uptrend Ratio Dashboard CSV data"""

    def __init__(self):
        self.session = requests.Session()
        self._timeseries_cache: Optional[list[dict]] = None
        self._sector_summary_cache: Optional[list[dict]] = None

    def fetch_timeseries(self) -> list[dict]:
        """Download and parse the timeseries CSV.

        Returns:
            List of dicts with keys: worksheet, date, count, total, ratio,
            ma_10, slope, trend. Numeric fields cast to float/int.
        """
        if self._timeseries_cache is not None:
            return self._timeseries_cache

        try:
            response = self.session.get(TIMESERIES_URL, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Failed to fetch timeseries CSV: {e}", file=sys.stderr)
            return []

        csv_body = _read_csv(response.text, "uptrend_ratio_timeseries.csv")
        if csv_body is None:
            self._timeseries_cache = []
            return []
        fieldnames, raw_rows = csv_body
        missing = _missing_columns(fieldnames, TIMESERIES_COLUMNS)
        if missing:
            _report_drift("uptrend_ratio_timeseries.csv", f"missing columns [{','.join(missing)}]")
            self._timeseries_cache = []
            return []

        rows = []
        for row in raw_rows:
            parsed = _parse_timeseries_row(row)
            if parsed:
                rows.append(parsed)

        if not any(_is_usable_ratio(r["ratio"]) for r in rows if r["worksheet"] == "all"):
            _report_drift("uptrend_ratio_timeseries.csv", "no usable 'all' ratio values")
            self._timeseries_cache = []
            return []

        self._timeseries_cache = rows
        return rows

    def fetch_sector_summary(self) -> list[dict]:
        """Download and parse the sector summary CSV.

        Returns:
            List of dicts with keys: Sector, Ratio, 10MA, Trend, Slope, Status.
            Numeric fields cast to float.
        """
        if self._sector_summary_cache is not None:
            return self._sector_summary_cache

        try:
            response = self.session.get(SECTOR_SUMMARY_URL, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Failed to fetch sector summary CSV: {e}", file=sys.stderr)
            return []

        csv_body = _read_csv(response.text, "sector_summary.csv")
        if csv_body is None:
            self._sector_summary_cache = []
            return []
        fieldnames, raw_rows = csv_body
        missing = _missing_columns(fieldnames, SECTOR_SUMMARY_COLUMNS)
        if missing:
            _report_drift("sector_summary.csv", f"missing columns [{','.join(missing)}]")
            self._sector_summary_cache = []
            return []

        rows = []
        for row in raw_rows:
            parsed = _parse_sector_summary_row(row)
            if parsed:
                rows.append(parsed)

        self._sector_summary_cache = rows
        return rows

    def get_all_timeseries(self) -> list[dict]:
        """Get timeseries filtered to worksheet=='all', sorted by date ascending."""
        data = self.fetch_timeseries()
        filtered = [r for r in data if r["worksheet"] == "all"]
        filtered.sort(key=lambda r: r["date"])
        return filtered

    def get_sector_timeseries(self, sector: str) -> list[dict]:
        """Get timeseries for a specific sector worksheet, sorted by date ascending."""
        data = self.fetch_timeseries()
        filtered = [r for r in data if r["worksheet"] == sector]
        filtered.sort(key=lambda r: r["date"])
        return filtered

    def get_latest_all(self) -> Optional[dict]:
        """Get the most recent 'all' row."""
        ts = self.get_all_timeseries()
        return ts[-1] if ts else None

    def get_all_sector_latest(self) -> dict[str, dict]:
        """Get latest row for each sector (excluding 'all').

        Returns:
            Dict mapping sector name -> latest timeseries row
        """
        data = self.fetch_timeseries()
        sectors: dict[str, dict] = {}
        for row in data:
            ws = row["worksheet"]
            if ws == "all":
                continue
            if ws not in sectors or row["date"] > sectors[ws]["date"]:
                sectors[ws] = row
        return sectors


def _parse_timeseries_row(row: dict) -> Optional[dict]:
    """Parse a timeseries CSV row, casting numeric fields."""
    try:
        return {
            "worksheet": _text(row, "worksheet"),
            "date": _text(row, "date"),
            "count": _safe_int(row.get("count")),
            "total": _safe_int(row.get("total")),
            "ratio": _safe_float(row.get("ratio")),
            "ma_10": _safe_float(row.get("ma_10")),
            "slope": _safe_float(row.get("slope")),
            "trend": _text(row, "trend"),
        }
    except (ValueError, TypeError):
        return None


def _parse_sector_summary_row(row: dict) -> Optional[dict]:
    """Parse a sector summary CSV row, casting numeric fields."""
    try:
        return {
            "Sector": _text(row, "Sector"),
            "Ratio": _safe_float(row.get("Ratio")),
            "10MA": _safe_float(row.get("10MA")),
            "Trend": _text(row, "Trend"),
            "Slope": _safe_float(row.get("Slope")),
            "Status": _text(row, "Status"),
        }
    except (ValueError, TypeError):
        return None


def _open_reader(text: str) -> csv.DictReader:
    """Build a DictReader with a BOM-free text and whitespace-stripped header names.

    DictReader row keys come from ``fieldnames``, so stripping them once here keeps
    the header check and the row lookups consistent.
    """
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    if reader.fieldnames is not None:
        reader.fieldnames = [(name or "").strip() for name in reader.fieldnames]
    return reader


def _read_csv(text: str, filename: str) -> Optional[tuple[list[str], list[dict]]]:
    """Parse a whole CSV body; report an unparsable body (NUL, oversized field) once."""
    try:
        reader = _open_reader(text)
        return list(reader.fieldnames or []), list(reader)
    except csv.Error as exc:
        _report_drift(filename, f"unparsable CSV ({exc})")
        return None


def _missing_columns(fieldnames, required) -> list[str]:
    """Return sorted required columns absent from a header normalized by _open_reader."""
    return sorted(set(required) - set(fieldnames or []))


def _text(row: dict, key: str) -> str:
    """Stripped cell text; a missing key or a short row (restval None) gives ''."""
    return (row.get(key) or "").strip()


def _report_drift(filename: str, detail: str) -> None:
    print(f"ERROR: {filename} schema drift: {detail}", file=sys.stderr)


def _is_usable_ratio(value) -> bool:
    """True when a parsed ratio is a finite number (None and NaN are unusable)."""
    return value is not None and math.isfinite(value)


def _safe_float(value) -> Optional[float]:
    """Convert to float, return None if empty or invalid."""
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value) -> Optional[int]:
    """Convert to int, return None if empty or invalid."""
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None
