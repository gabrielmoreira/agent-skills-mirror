#!/usr/bin/env python3
"""Build an audited, bounded discovery pool for the US GARP screener.

Contract v3.5 retains and extends fail-closed controls that operate *before* any symbol is
prioritized:

1. Liquidity must be based on a genuine average (normally 20+ sessions), not
   ``price × today's volume``.
2. The user's requested market-cap scope is preserved separately from the
   executed/retrieved scope. A narrower execution range is never silently
   rewritten as the original request.

The script does not fetch market data. It validates and stratifies rows supplied
by the calling agent or provider connector, then writes a reproducible pool and
an audit record.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from skill_version import runtime_metadata
except ModuleNotFoundError:  # Supports importlib-based unit loading.
    import importlib.util as _importlib_util

    _version_path = Path(__file__).with_name("skill_version.py")
    _version_spec = _importlib_util.spec_from_file_location("skill_version", _version_path)
    if _version_spec is None or _version_spec.loader is None:
        raise
    _version_module = _importlib_util.module_from_spec(_version_spec)
    _version_spec.loader.exec_module(_version_module)
    runtime_metadata = _version_module.runtime_metadata

try:
    from screening_semantics import normalize_liquidity
except ModuleNotFoundError:
    import importlib.util as _semantics_importlib_util

    _semantics_path = Path(__file__).with_name("screening_semantics.py")
    _semantics_spec = _semantics_importlib_util.spec_from_file_location(
        "screening_semantics", _semantics_path
    )
    if _semantics_spec is None or _semantics_spec.loader is None:
        raise
    _semantics_module = _semantics_importlib_util.module_from_spec(_semantics_spec)
    _semantics_spec.loader.exec_module(_semantics_module)
    normalize_liquidity = _semantics_module.normalize_liquidity

ALLOWED_EXCHANGES = {"NYSE", "NASDAQ", "NYSE AMERICAN", "NYSEAMERICAN", "AMEX"}
DEFAULT_BUCKETS = [500_000_000, 2_000_000_000, 5_000_000_000, 10_000_000_000, 20_000_000_000]
MIN_AVERAGE_WINDOW_DAYS = 20
VALID_LIQUIDITY_METHODS = {
    "mean_dollar_volume",
    "mean_20d_dollar_volume",
    "provider_average_dollar_volume",
    "average_volume_x_price",
    "provider_avg_volume_x_price",
    "mean_20d_volume_x_price",
}


class DiscoveryError(ValueError):
    pass


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        return result if math.isfinite(result) else None
    if isinstance(value, str):
        try:
            result = float(value.replace(",", "").strip())
        except ValueError:
            return None
        return result if math.isfinite(result) else None
    return None


def _integer(value: Any) -> int | None:
    number = _number(value)
    return int(number) if number is not None and number.is_integer() else None


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    return None


def _load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix in {".jsonl", ".ndjson"}:
        rows: list[dict[str, Any]] = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, Mapping):
                raise DiscoveryError(f"line {line_no} is not an object")
            rows.append(dict(value))
        return rows
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return [_mapping(row) for row in value]
    if isinstance(value, Mapping) and isinstance(value.get("rows"), list):
        return [_mapping(row) for row in value["rows"]]
    raise DiscoveryError("input must be a JSON array, {rows:[...]}, JSONL, or CSV")


def _metric(row: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _number(row.get(key))
        if value is not None:
            return value
    return None


def _liquidity_evidence(row: Mapping[str, Any], price: float | None) -> dict[str, Any]:
    """Delegate to the shared fail-closed liquidity normalizer."""
    normalized = normalize_liquidity(row, minimum_period_days=MIN_AVERAGE_WINDOW_DAYS)
    return {
        "value": normalized.get("value"),
        "valid": normalized.get("valid_for_screen") is True,
        "method": normalized.get("method"),
        "window_days": normalized.get("period_days"),
        "source_ids": normalized.get("source_ids", []),
        "average_volume": normalized.get("average_volume"),
        "reasons": sorted(set(normalized.get("reasons") or [])),
    }


def _normalized_listing(row: Mapping[str, Any]) -> dict[str, Any]:
    price = _metric(row, "price", "last")
    liquidity = _liquidity_evidence(row, price)
    return {
        "symbol": (_text(row.get("symbol")) or _text(row.get("ticker")) or "UNKNOWN").upper(),
        "company_name": _text(row.get("company_name"))
        or _text(row.get("companyName"))
        or _text(row.get("name")),
        "exchange": (
            _text(row.get("exchange")) or _text(row.get("exchangeShortName")) or ""
        ).upper(),
        "sector": (_text(row.get("sector")) or "Unknown").strip(),
        "industry": _text(row.get("industry")),
        "price": price,
        "market_cap": _metric(row, "market_cap", "marketCap"),
        "average_daily_dollar_volume": liquidity["value"],
        "liquidity_method": liquidity["method"],
        "liquidity_window_days": liquidity["window_days"],
        "liquidity_source_ids": liquidity["source_ids"],
        "average_volume": liquidity["average_volume"],
        "liquidity_basis_valid": liquidity["valid"],
        "liquidity_review_reasons": liquidity["reasons"],
        "is_actively_trading": _bool(row.get("is_actively_trading"))
        if "is_actively_trading" in row
        else _bool(row.get("isActivelyTrading")),
        "is_common_stock": _bool(row.get("is_common_stock"))
        if "is_common_stock" in row
        else _bool(row.get("common_stock")),
        "source_row": dict(row),
    }


def _bucket_label(market_cap: float, buckets: Sequence[float]) -> str:
    for low, high in zip(buckets, buckets[1:]):
        if low <= market_cap < high:
            return f"{int(low)}-{int(high)}"
    if market_cap == buckets[-1]:
        return f"{int(buckets[-2])}-{int(buckets[-1])}"
    return "out-of-range"


def build_pool(
    rows: Sequence[Mapping[str, Any]],
    *,
    min_market_cap: float,
    max_market_cap: float,
    min_price: float,
    hard_min_adv: float,
    max_pool: int,
    per_cell: int,
    buckets: Sequence[float] | None = None,
    user_requested_min_market_cap: float | None = None,
    user_requested_max_market_cap: float | None = None,
    scope_reduction_authorized: bool = False,
    scope_reduction_reason: str | None = None,
    user_scope_evidence: str | None = None,
    default_liquidity_source_ids: Sequence[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if max_pool <= 0 or per_cell <= 0:
        raise DiscoveryError("max_pool and per_cell must be positive")
    if min_market_cap >= max_market_cap:
        raise DiscoveryError("executed market-cap range must be increasing")

    requested_min = float(
        user_requested_min_market_cap
        if user_requested_min_market_cap is not None
        else min_market_cap
    )
    requested_max = float(
        user_requested_max_market_cap
        if user_requested_max_market_cap is not None
        else max_market_cap
    )
    if requested_min >= requested_max:
        raise DiscoveryError("user-requested market-cap range must be increasing")
    scope_reduced = min_market_cap > requested_min or max_market_cap < requested_max
    scope_reason = _text(scope_reduction_reason)
    # Automatic resource-bounded execution is valid only as a disclosed bounded result.
    # Explicit user authorization is recorded separately; it is not required to
    # produce a scoped diagnostic/ranking.
    # Resource pressure may bound the discovery *row count*, but it may not
    # rewrite the user's requested market-cap range. A narrower executed range
    # is invalid; an explicitly narrower user request must be passed as the
    # user-requested bounds themselves.
    scope_valid = not scope_reduced

    bucket_edges = list(buckets or DEFAULT_BUCKETS)
    if bucket_edges[0] != min_market_cap or bucket_edges[-1] != max_market_cap:
        bucket_edges = (
            [min_market_cap]
            + [edge for edge in bucket_edges if min_market_cap < edge < max_market_cap]
            + [max_market_cap]
        )
    if any(a >= b for a, b in zip(bucket_edges, bucket_edges[1:])):
        raise DiscoveryError("market-cap buckets must be strictly increasing")

    normalized: list[dict[str, Any]] = []
    exclusions: dict[str, int] = defaultdict(int)
    liquidity_reason_counts: dict[str, int] = defaultdict(int)
    for raw in rows:
        source_row = dict(raw)
        if not source_row.get("liquidity_source_ids") and default_liquidity_source_ids:
            source_row["liquidity_source_ids"] = list(default_liquidity_source_ids)
        row = _normalized_listing(source_row)
        exchange = row["exchange"]
        price = row["price"]
        market_cap = row["market_cap"]
        adv = row["average_daily_dollar_volume"]
        active = row["is_actively_trading"]
        common = row["is_common_stock"]
        reason: str | None = None
        if exchange not in ALLOWED_EXCHANGES:
            reason = "exchange_out_of_scope"
        elif active is False:
            reason = "inactive_symbol"
        elif common is False:
            reason = "not_common_stock"
        elif price is None or price < min_price:
            reason = "price_below_minimum"
        elif market_cap is None or not (min_market_cap <= market_cap <= max_market_cap):
            reason = "market_cap_out_of_range"
        elif row["liquidity_basis_valid"] is not True:
            reason = "validated_average_liquidity_unavailable"
            for item in row["liquidity_review_reasons"]:
                liquidity_reason_counts[str(item)] += 1
        elif adv is None or adv < hard_min_adv:
            reason = "liquidity_below_hard_floor"
        if reason:
            exclusions[reason] += 1
            continue
        row["market_cap_bucket"] = _bucket_label(float(market_cap), bucket_edges)
        normalized.append(row)

    cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        sector = str(row["sector"]).strip().upper() or "UNKNOWN"
        cells[(sector, str(row["market_cap_bucket"]))].append(row)
    for values in cells.values():
        values.sort(
            key=lambda row: (
                -(row["average_daily_dollar_volume"] or 0),
                -(row["market_cap"] or 0),
                row["symbol"],
            )
        )

    selected: list[dict[str, Any]] = []
    selected_symbols: set[str] = set()
    cell_keys = sorted(cells)
    for depth in range(per_cell):
        layer = [cells[cell][depth] for cell in cell_keys if len(cells[cell]) > depth]
        layer.sort(
            key=lambda row: (
                -(row["average_daily_dollar_volume"] or 0),
                -(row["market_cap"] or 0),
                row["symbol"],
            )
        )
        for row in layer:
            if len(selected) >= max_pool:
                break
            if row["symbol"] in selected_symbols:
                continue
            selected.append(row)
            selected_symbols.add(row["symbol"])
        if len(selected) >= max_pool:
            break

    if len(selected) < max_pool:
        remaining = sorted(
            (row for row in normalized if row["symbol"] not in selected_symbols),
            key=lambda row: (
                -(row["average_daily_dollar_volume"] or 0),
                -(row["market_cap"] or 0),
                row["symbol"],
            ),
        )
        for row in remaining:
            if len(selected) >= max_pool:
                break
            selected.append(row)
            selected_symbols.add(row["symbol"])

    output_rows: list[dict[str, Any]] = []
    for rank, row in enumerate(selected, start=1):
        output_rows.append(
            {
                "symbol": row["symbol"],
                "company_name": row["company_name"],
                "exchange": row["exchange"],
                "sector": row["sector"],
                "industry": row["industry"],
                "price": row["price"],
                "market_cap": row["market_cap"],
                "average_daily_dollar_volume": row["average_daily_dollar_volume"],
                "average_volume": row["average_volume"],
                "liquidity_method": row["liquidity_method"],
                "liquidity_window_days": row["liquidity_window_days"],
                "liquidity_source_ids": row["liquidity_source_ids"],
                "liquidity_basis_valid": True,
                "market_cap_bucket": row["market_cap_bucket"],
                "discovery_rank": rank,
                "discovery_reason": "sector_market_cap_stratified_validated_liquidity",
            }
        )

    sector_counts: dict[str, int] = defaultdict(int)
    bucket_counts: dict[str, int] = defaultdict(int)
    for row in output_rows:
        sector_counts[str(row["sector"])] += 1
        bucket_counts[str(row["market_cap_bucket"])] += 1

    windows = [
        int(row["liquidity_window_days"])
        for row in selected
        if row.get("liquidity_window_days") is not None
    ]
    input_exchanges = sorted({str(row["exchange"]) for row in normalized if row.get("exchange")})
    requested_range_spanned = bool(
        min_market_cap <= requested_min
        and max_market_cap >= requested_max
        and bucket_edges[0] <= requested_min
        and bucket_edges[-1] >= requested_max
    )
    coverage_plan = {
        "method": "sector_market_cap_stratified_validated_liquidity",
        "user_requested_range_spanned": requested_range_spanned,
        "market_cap_buckets_cover_user_requested_range": requested_range_spanned,
        "input_exchange_coverage": input_exchanges,
        "required_exchange_families": ["NYSE", "NASDAQ", "NYSE AMERICAN"],
        "single_band_only": bool(scope_reduced),
        "coverage_plan_valid": bool(scope_valid and requested_range_spanned),
        "bounded_pool_disclosed": True,
    }
    audit = {
        "schema_version": 3,
        "runtime": runtime_metadata(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "valid": bool(
            scope_valid and all(row.get("liquidity_basis_valid") is True for row in selected)
        ),
        "input_row_count": len(rows),
        "in_scope_row_count": len(normalized),
        "selected_count": len(output_rows),
        "selection_method": "sector_market_cap_stratified_validated_liquidity",
        "max_pool": max_pool,
        "per_sector_bucket_limit": per_cell,
        "market_cap_buckets": bucket_edges,
        "selected_symbols": [row["symbol"] for row in output_rows],
        "selected_by_sector": dict(sorted(sector_counts.items())),
        "selected_by_market_cap_bucket": dict(sorted(bucket_counts.items())),
        "exclusion_counts": dict(sorted(exclusions.items())),
        "liquidity_validation": {
            "basis_validated": all(row.get("liquidity_basis_valid") is True for row in selected),
            "minimum_window_days": min(windows) if windows else None,
            "required_minimum_window_days": MIN_AVERAGE_WINDOW_DAYS,
            "selected_with_validated_liquidity": len(selected),
            "unverified_reason_counts": dict(sorted(liquidity_reason_counts.items())),
        },
        "coverage_plan": coverage_plan,
        "scope": {
            "user_requested_min_market_cap": requested_min,
            "user_requested_max_market_cap": requested_max,
            "executed_min_market_cap": float(min_market_cap),
            "executed_max_market_cap": float(max_market_cap),
            "scope_reduced": scope_reduced,
            "scope_reduction_authorized": scope_reduction_authorized,
            "scope_reduction_mode": "invalid_internal_narrowing" if scope_reduced else "none",
            "scope_reduction_disclosed": (not scope_reduced) or bool(scope_reason),
            "scope_reduction_reason": scope_reason,
            "user_scope_evidence": _text(user_scope_evidence),
            "user_requested_scope_complete": requested_range_spanned,
            "scope_valid": scope_valid,
        },
    }
    return output_rows, audit


def _canonical_line(row: Mapping[str, Any]) -> str:
    return json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a bounded stratified discovery pool using validated average liquidity."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-id", action="append", required=True)
    parser.add_argument(
        "--min-market-cap", type=float, default=500_000_000, help="Executed pool lower bound."
    )
    parser.add_argument(
        "--max-market-cap", type=float, default=20_000_000_000, help="Executed pool upper bound."
    )
    parser.add_argument("--user-requested-min-market-cap", type=float, default=500_000_000)
    parser.add_argument("--user-requested-max-market-cap", type=float, default=20_000_000_000)
    parser.add_argument(
        "--user-scope-override-authorized",
        action="store_true",
        help="Required only when the user explicitly requested non-default bounds.",
    )
    parser.add_argument("--user-scope-evidence")
    parser.add_argument("--scope-reduction-reason")
    parser.add_argument(
        "--allow-reduced-scope",
        action="store_true",
        help="Deprecated and non-authoritative; internal narrowing remains invalid.",
    )
    parser.add_argument("--min-price", type=float, default=5.0)
    parser.add_argument("--hard-min-adv", type=float, default=1_000_000)
    parser.add_argument("--max-pool", type=int, default=120)
    parser.add_argument("--per-cell", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    if "--version" in raw_argv:
        print(json.dumps(runtime_metadata(), sort_keys=True))
        return 0
    args = parse_args(raw_argv)
    try:
        rows = _load_rows(args.input)
        default_requested = (500_000_000.0, 20_000_000_000.0)
        requested = (
            float(args.user_requested_min_market_cap),
            float(args.user_requested_max_market_cap),
        )
        if requested != default_requested and (
            not args.user_scope_override_authorized or not _text(args.user_scope_evidence)
        ):
            raise DiscoveryError(
                "non-default user-requested bounds require --user-scope-override-authorized "
                "and --user-scope-evidence"
            )
        pool, audit = build_pool(
            rows,
            min_market_cap=args.min_market_cap,
            max_market_cap=args.max_market_cap,
            min_price=args.min_price,
            hard_min_adv=args.hard_min_adv,
            max_pool=args.max_pool,
            per_cell=args.per_cell,
            user_requested_min_market_cap=args.user_requested_min_market_cap,
            user_requested_max_market_cap=args.user_requested_max_market_cap,
            scope_reduction_authorized=args.user_scope_override_authorized,
            scope_reduction_reason=args.scope_reduction_reason,
            user_scope_evidence=args.user_scope_evidence,
            default_liquidity_source_ids=args.source_id,
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        pool_path = args.output_dir / "discovery-pool.jsonl"
        pool_path.write_text("".join(_canonical_line(row) for row in pool), encoding="utf-8")
        audit["source_ids"] = list(args.source_id)
        audit["artifact_path"] = pool_path.name
        audit["artifact_sha256"] = hashlib.sha256(pool_path.read_bytes()).hexdigest()
        audit_path = args.output_dir / "discovery-audit.json"
        audit_path.write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, json.JSONDecodeError, DiscoveryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"wrote: {pool_path}")
    print(f"wrote: {audit_path}")
    if audit.get("valid") is not True or not pool:
        print(
            "INCOMPLETE: discovery pool has unverified liquidity, unauthorized reduced scope, or no eligible rows",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
