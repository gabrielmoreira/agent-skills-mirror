#!/usr/bin/env python3
"""Normalize annual consensus rows into contract-3.5 discovery metrics.

A current forward P/E is computed only from a dated FY1 estimate.  The helper
never substitutes FY2/FY3 merely because FY1 is missing.  It records estimate
breadth, range dispersion, period continuity, growth horizons, and source IDs so
the deterministic broad screen can reject FRMI-like outer-year artefacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

# Provider publish/acceptance stamps without an explicit offset are US/Eastern
# wall time (the SEC acceptance clock), not UTC.
PROVIDER_PUBLISH_TZ = ZoneInfo("America/New_York")

try:
    from skill_version import SKILL_VERSION, runtime_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib.util as _importlib_util

    _path = Path(__file__).with_name("skill_version.py")
    _spec = _importlib_util.spec_from_file_location("skill_version", _path)
    if _spec is None or _spec.loader is None:
        raise
    _module = _importlib_util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    runtime_metadata = _module.runtime_metadata
    SKILL_VERSION = _module.SKILL_VERSION


class NormalizeError(ValueError):
    """Raised for malformed estimate inputs."""


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


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


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


def _parse_date(value: Any, label: str) -> datetime:
    text = _text(value)
    if not text:
        raise NormalizeError(f"{label} is required")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise NormalizeError(f"{label} is not ISO-8601: {text!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    text = path.read_text(encoding="utf-8")
    if suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    value = json.loads(text)
    if isinstance(value, list):
        return [dict(row) for row in value if isinstance(row, Mapping)]
    if isinstance(value, Mapping) and isinstance(value.get("rows"), list):
        return [dict(row) for row in value["rows"] if isinstance(row, Mapping)]
    raise NormalizeError(f"unsupported row container in {path}")


def _symbol(row: Mapping[str, Any]) -> str:
    return (_text(row.get("symbol")) or _text(row.get("ticker")) or "UNKNOWN").upper()


def _period_end(row: Mapping[str, Any]) -> datetime | None:
    for key in ("date", "period_end", "fiscal_period_end", "fiscalDateEnding"):
        text = _text(row.get(key))
        if not text:
            continue
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    return None


def _pick(row: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _number(row.get(key))
        if value is not None:
            return value
    return None


def _period_record(row: Mapping[str, Any]) -> dict[str, Any] | None:
    end = _period_end(row)
    if end is None:
        return None
    fiscal_year = _text(row.get("fiscalYear")) or _text(row.get("fiscal_year")) or str(end.year)
    fiscal_year = fiscal_year.upper().removeprefix("FY")
    is_actual = (
        _bool(row.get("isActual")) or _bool(row.get("is_actual")) or _bool(row.get("actual"))
    )
    return {
        "fiscal_year": fiscal_year,
        "period": f"FY{fiscal_year}",
        "period_end": end.isoformat(),
        "eps_avg": _pick(row, "epsAvg", "eps_avg", "eps", "estimated_eps"),
        "eps_low": _pick(row, "epsLow", "eps_low"),
        "eps_high": _pick(row, "epsHigh", "eps_high"),
        "revenue_avg": _pick(row, "revenueAvg", "revenue_avg", "revenue", "estimated_revenue"),
        "eps_analyst_count": _integer(row.get("numAnalystsEps"))
        or _integer(row.get("num_analysts_eps")),
        "revenue_analyst_count": _integer(row.get("numAnalystsRevenue"))
        or _integer(row.get("num_analysts_revenue")),
        "is_actual": bool(is_actual),
        "published_at": _text(row.get("publishedDate"))
        or _text(row.get("published_at"))
        or _text(row.get("updatedAt"))
        or None,
    }


def _latest_actual_period(
    periods: Sequence[Mapping[str, Any]], analysis_as_of: datetime
) -> Mapping[str, Any] | None:
    """Return the most recent provider-marked actual annual EPS row, else None.

    Verified reported figures normally arrive through
    ``apply_verified_actual_eps`` (annual income statement with an accepted
    date at or before ``analysis_as_of``); this helper only honours explicit
    provider actual markers and never treats a prior-year estimate as actual.
    """

    # Fail closed: only rows the provider explicitly marks as actuals count,
    # and only when (a) their period has already ended AND (b) the row carries
    # a publication timestamp at or before analysis_as_of. Without a provable
    # publication time, a CURRENT provider snapshot replayed against a
    # HISTORICAL analysis_as_of would leak an actual that was not yet public
    # on that date (e.g. FY ended 2025-12-31, as-of 2026-01-05, filed
    # 2026-02-27). An unmarked prior-year row is consensus, never an actual.
    def _published_before(record: Mapping[str, Any]) -> bool:
        raw = _text(record.get("published_at"))
        if not raw:
            return False
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00").replace(" ", "T"))
        except ValueError:
            # NormalizeError is a ValueError subclass; any unparsable stamp
            # fails closed (treated as not yet published).
            return False
        if parsed.tzinfo is None:
            if len(raw.strip()) <= 10:
                # A date-only publish stamp cannot prove intraday precedence:
                # count it only once the whole publication day (ET) has passed.
                parsed = parsed.replace(hour=23, minute=59, second=59)
            parsed = parsed.replace(tzinfo=PROVIDER_PUBLISH_TZ)
        published = parsed.astimezone(timezone.utc)
        return published <= analysis_as_of

    marked_actual = [
        record
        for record in periods
        if record.get("is_actual")
        and _parse_date(record["period_end"], "period_end") <= analysis_as_of
        and _published_before(record)
    ]
    if marked_actual:
        return max(marked_actual, key=lambda record: str(record["period_end"]))
    return None


def _growth_pattern(
    latest_actual_eps: float | None,
    fy1_eps: float | None,
    fy3_eps: float | None,
    early_growth_pct: float | None,
    late_growth_pct: float | None,
) -> str:
    if latest_actual_eps is None or latest_actual_eps <= 0:
        return "unknown"
    if fy1_eps is not None and fy3_eps is not None:
        if fy1_eps < latest_actual_eps and fy3_eps > latest_actual_eps:
            return "trough_recovery"
        if fy3_eps < latest_actual_eps:
            return "declining"
    if early_growth_pct is not None and late_growth_pct is not None:
        if late_growth_pct > early_growth_pct + 1e-9:
            return "accelerating"
    return "steady"


def _dispersion_pct(avg: float | None, low: float | None, high: float | None) -> float | None:
    if avg is None or low is None or high is None or avg == 0:
        return None
    return abs(high - low) / abs(avg) * 100.0


def _cagr(start: float | None, end: float | None, years: float) -> float | None:
    if start is None or end is None or start <= 0 or end <= 0 or years <= 0:
        return None
    return ((end / start) ** (1.0 / years) - 1.0) * 100.0


def normalize_symbol(
    symbol: str,
    estimate_rows: Sequence[Mapping[str, Any]],
    listing: Mapping[str, Any],
    *,
    analysis_as_of: datetime,
    estimate_as_of: datetime,
    source_ids: Sequence[str],
    minimum_analysts: int,
    max_dispersion_pct: float,
    max_fy1_horizon_days: int,
    forward_pe_tolerance_pct: float,
) -> dict[str, Any]:
    price = _pick(listing, "price", "last")
    periods = [record for row in estimate_rows if (record := _period_record(row)) is not None]
    periods.sort(key=lambda record: str(record["period_end"]))
    future = [
        record
        for record in periods
        if _parse_date(record["period_end"], "period_end") > analysis_as_of
    ]

    reasons: list[str] = []
    operating_stage = (_text(listing.get("operating_stage")) or "").lower().replace(" ", "_")
    if _bool(listing.get("is_pre_operating")) is True or operating_stage in {
        "pre_operating",
        "pre-revenue",
        "pre_revenue",
        "development_stage",
    }:
        reasons.append("pre_operating_company")

    fy1 = future[0] if future else None
    fy1_horizon_days: int | None = None
    if fy1 is None:
        reasons.append("fy1_estimate_unavailable")
    else:
        fy1_horizon_days = (_parse_date(fy1["period_end"], "fy1.period_end") - analysis_as_of).days
        if fy1_horizon_days <= 0 or fy1_horizon_days > max_fy1_horizon_days:
            reasons.append("invalid_fy1_horizon")
        eps = _number(fy1.get("eps_avg"))
        low = _number(fy1.get("eps_low"))
        high = _number(fy1.get("eps_high"))
        if eps is None or eps <= 0:
            reasons.append("non_positive_fy1_eps")
        if low is not None and high is not None and low <= 0 <= high:
            reasons.append("fy1_eps_range_crosses_zero")
        dispersion = _dispersion_pct(eps, low, high)
        if dispersion is not None and dispersion > max_dispersion_pct:
            reasons.append("fy1_estimate_dispersion_excessive")
        analysts = _integer(fy1.get("eps_analyst_count"))
        if analysts is None or analysts < minimum_analysts:
            reasons.append("estimate_breadth_below_discovery_minimum")

    series_contiguous = True
    for left, right in zip(future, future[1:]):
        delta_days = (
            _parse_date(right["period_end"], "period_end")
            - _parse_date(left["period_end"], "period_end")
        ).days
        if not 300 <= delta_days <= 430:
            series_contiguous = False
            break
    if len(future) >= 2 and not series_contiguous:
        reasons.append("annual_estimate_series_not_contiguous")

    forward_eps = _number(fy1.get("eps_avg")) if fy1 else None
    forward_pe = (
        price / forward_eps
        if price is not None and price > 0 and forward_eps is not None and forward_eps > 0
        else None
    )
    if price is None or price <= 0:
        reasons.append("price_unavailable_or_non_positive")
    supplied_pe = _pick(listing, "forward_pe", "fy1_pe", "ntm_pe")
    if supplied_pe is not None and forward_pe is not None:
        mismatch = abs(supplied_pe - forward_pe) / max(abs(forward_pe), 1e-9) * 100.0
        if mismatch > forward_pe_tolerance_pct:
            reasons.append("forward_pe_reconciliation_failed")

    growth_end = future[2] if len(future) >= 3 else (future[1] if len(future) >= 2 else None)
    growth_years = 0.0
    if fy1 and growth_end:
        growth_years = (
            _parse_date(growth_end["period_end"], "growth_end.period_end")
            - _parse_date(fy1["period_end"], "fy1.period_end")
        ).days / 365.25
    eps_growth = _cagr(
        forward_eps, _number(growth_end.get("eps_avg")) if growth_end else None, growth_years
    )
    revenue_growth = _cagr(
        _number(fy1.get("revenue_avg")) if fy1 else None,
        _number(growth_end.get("revenue_avg")) if growth_end else None,
        growth_years,
    )

    # Growth-basis diagnostics (v3.6.1): compare the forward estimate path to
    # the latest actual annual EPS so a trough-recovery FY1->FY3 CAGR (a
    # current-year decline masked by an eventual rebound, e.g. YELP FY26E
    # below FY25 actual) is visible rather than silently blended away.
    latest_actual_period = _latest_actual_period(periods, analysis_as_of)
    latest_actual_eps = (
        _number(latest_actual_period.get("eps_avg")) if latest_actual_period else None
    )
    latest_actual_period_end = (
        latest_actual_period.get("period_end") if latest_actual_period else None
    )
    # Same-basis reference: the provider's most recent prior-year row. It is
    # CONSENSUS on the provider's (usually adjusted) basis -- never reported as
    # an actual -- but it is the only figure on the same basis as FY1/FY3, so
    # it is the correct comparator for "is the current year a decline".
    fy0_candidates = [
        record
        for record in periods
        if _parse_date(record["period_end"], "period_end") <= analysis_as_of
    ]
    fy0 = (
        max(fy0_candidates, key=lambda record: str(record["period_end"]))
        if fy0_candidates
        else None
    )
    fy0_consensus_eps = _number(fy0.get("eps_avg")) if fy0 else None
    fy0_period_end = fy0.get("period_end") if fy0 else None
    fy1_raw_eps = _number(fy1.get("eps_avg")) if fy1 else None
    growth_end_raw_eps = _number(growth_end.get("eps_avg")) if growth_end else None
    has_positive_actual = latest_actual_eps is not None and latest_actual_eps > 0
    has_positive_fy0 = fy0_consensus_eps is not None and fy0_consensus_eps > 0

    fy1_eps_below_latest_actual = (
        fy1_raw_eps < latest_actual_eps if has_positive_actual and fy1_raw_eps is not None else None
    )
    fy1_eps_below_fy0_consensus = (
        fy1_raw_eps < fy0_consensus_eps if has_positive_fy0 and fy1_raw_eps is not None else None
    )
    current_year_growth_pct = (
        (fy1_raw_eps / fy0_consensus_eps - 1.0) * 100.0
        if has_positive_fy0 and fy1_raw_eps is not None
        else None
    )
    actual_to_growth_end_years = 0.0
    if latest_actual_period is not None and growth_end is not None:
        actual_to_growth_end_years = (
            _parse_date(growth_end["period_end"], "growth_end.period_end")
            - _parse_date(latest_actual_period["period_end"], "latest_actual.period_end")
        ).days / 365.25
    eps_growth_actual_to_fy3 = (
        _cagr(latest_actual_eps, growth_end_raw_eps, actual_to_growth_end_years)
        if has_positive_actual
        else None
    )

    fy2 = future[1] if len(future) >= 2 else None
    early_growth_pct = None
    late_growth_pct = None
    if fy1 and fy2:
        early_years = (
            _parse_date(fy2["period_end"], "fy2.period_end")
            - _parse_date(fy1["period_end"], "fy1.period_end")
        ).days / 365.25
        early_growth_pct = _cagr(fy1_raw_eps, _number(fy2.get("eps_avg")), early_years)
    if len(future) >= 3:
        fy3 = future[2]
        late_years = (
            _parse_date(fy3["period_end"], "fy3.period_end")
            - _parse_date(fy2["period_end"], "fy2.period_end")
        ).days / 365.25
        late_growth_pct = _cagr(
            _number(fy2.get("eps_avg")), _number(fy3.get("eps_avg")), late_years
        )

    growth_pattern = _growth_pattern(
        fy0_consensus_eps,
        fy1_raw_eps,
        growth_end_raw_eps,
        early_growth_pct,
        late_growth_pct,
    )
    growth_pattern_basis = "consensus_same_basis" if has_positive_fy0 else "unknown"

    status = "valid" if not reasons else "unavailable"
    canonical_forward_eps = forward_eps if status == "valid" else None
    canonical_forward_pe = forward_pe if status == "valid" else None
    canonical_fy1 = fy1 if status == "valid" else None

    result = dict(listing)
    result.update(
        {
            "symbol": symbol,
            "normalized_estimates_version": SKILL_VERSION,
            "enrichment_attempted": True,
            # The enrichment step is resolved whether it produced a usable FY1
            # metric or exhausted the available evidence with explicit reasons.
            "enrichment_resolved": True,
            "forward_metric_basis": "fy1" if canonical_fy1 else None,
            "forward_pe_period": "FY1" if canonical_fy1 else None,
            "forward_metric_period": "FY1" if canonical_fy1 else None,
            "forward_fiscal_year": canonical_fy1.get("fiscal_year") if canonical_fy1 else None,
            "forward_period_end": canonical_fy1.get("period_end") if canonical_fy1 else None,
            "forward_metric_period_end": canonical_fy1.get("period_end") if canonical_fy1 else None,
            "forward_estimate_as_of": estimate_as_of.isoformat(),
            "forward_estimate_source_ids": list(source_ids),
            "forward_metric_source_ids": list(source_ids),
            "forward_metric_origin": "computed_from_price_and_fy1_eps" if canonical_fy1 else None,
            "fy1_horizon_days": fy1_horizon_days,
            "forward_eps": canonical_forward_eps,
            "fy1_eps": canonical_forward_eps,
            "forward_eps_low": _number(canonical_fy1.get("eps_low")) if canonical_fy1 else None,
            "forward_eps_high": _number(canonical_fy1.get("eps_high")) if canonical_fy1 else None,
            "forward_estimate_dispersion_pct": _dispersion_pct(
                canonical_forward_eps,
                _number(canonical_fy1.get("eps_low")) if canonical_fy1 else None,
                _number(canonical_fy1.get("eps_high")) if canonical_fy1 else None,
            ),
            "forward_pe": round(canonical_forward_pe, 6)
            if canonical_forward_pe is not None
            else None,
            "fy1_pe": round(canonical_forward_pe, 6) if canonical_forward_pe is not None else None,
            "analyst_count": _integer(canonical_fy1.get("eps_analyst_count"))
            if canonical_fy1
            else None,
            "forward_eps_analyst_count": _integer(canonical_fy1.get("eps_analyst_count"))
            if canonical_fy1
            else None,
            "fy1_analyst_count": _integer(canonical_fy1.get("eps_analyst_count"))
            if canonical_fy1
            else None,
            "eps_growth_pct": round(eps_growth, 6)
            if eps_growth is not None and status == "valid"
            else None,
            # v3.6.1 alias: identical semantics to eps_growth_pct (FY1->FY3
            # CAGR), kept under an explicit name alongside eps_growth_actual_to_fy3_pct.
            "eps_growth_fy1_to_fy3_pct": round(eps_growth, 6)
            if eps_growth is not None and status == "valid"
            else None,
            "latest_actual_eps": round(latest_actual_eps, 6)
            if latest_actual_eps is not None
            else None,
            "latest_actual_period_end": latest_actual_period_end,
            "latest_actual_verified": latest_actual_period is not None,
            "latest_actual_basis": "provider_marked_actual"
            if latest_actual_period is not None
            else None,
            "latest_actual_source_ids": list(source_ids)
            if latest_actual_period is not None
            else [],
            "fy1_eps_below_latest_actual": fy1_eps_below_latest_actual,
            "fy0_consensus_eps": round(fy0_consensus_eps, 6)
            if fy0_consensus_eps is not None
            else None,
            "fy0_period_end": fy0_period_end,
            "fy1_eps_below_fy0_consensus": fy1_eps_below_fy0_consensus,
            "current_year_growth_pct": round(current_year_growth_pct, 6)
            if current_year_growth_pct is not None
            else None,
            "growth_pattern_basis": growth_pattern_basis,
            "estimate_basis_likely_adjusted": None,
            "eps_growth_actual_to_fy3_pct": round(eps_growth_actual_to_fy3, 6)
            if eps_growth_actual_to_fy3 is not None
            else None,
            "growth_pattern": growth_pattern,
            "growth_basis_source_ids": list(source_ids),
            "revenue_growth_pct": round(revenue_growth, 6)
            if revenue_growth is not None and status == "valid"
            else None,
            "growth_horizon_start_period": "FY1" if canonical_fy1 else None,
            "growth_horizon_start_period_end": canonical_fy1.get("period_end")
            if canonical_fy1
            else None,
            "growth_horizon_end_period": growth_end.get("period")
            if growth_end and status == "valid"
            else None,
            "growth_horizon_end_period_end": growth_end.get("period_end")
            if growth_end and status == "valid"
            else None,
            "growth_horizon_years": round(growth_years, 6)
            if growth_years > 0 and status == "valid"
            else None,
            "growth_estimate_source_ids": list(source_ids),
            "estimate_series_contiguous": series_contiguous,
            "estimate_periods": future[:4],
            "estimate_normalization_status": status,
            "estimate_normalization_reasons": sorted(set(reasons)),
            # Preserve the raw candidate for diagnostics without allowing it to
            # masquerade as the current FY1/NTM valuation in downstream screens.
            "raw_forward_candidate": {
                "fiscal_year": fy1.get("fiscal_year") if fy1 else None,
                "period_end": fy1.get("period_end") if fy1 else None,
                "eps": forward_eps,
                "eps_low": _number(fy1.get("eps_low")) if fy1 else None,
                "eps_high": _number(fy1.get("eps_high")) if fy1 else None,
                "computed_pe": round(forward_pe, 6) if forward_pe is not None else None,
                "analyst_count": _integer(fy1.get("eps_analyst_count")) if fy1 else None,
            },
        }
    )
    if reasons:
        result.update(
            {
                "enrichment_exhausted": True,
                "enrichment_exhaustion_reason": "; ".join(sorted(set(reasons))),
                "enrichment_source_ids": list(source_ids),
            }
        )
    else:
        result.update(
            {
                "enrichment_exhausted": False,
                "enrichment_exhaustion_reason": None,
                "enrichment_source_ids": list(source_ids),
            }
        )
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize raw annual estimates into current FY1/NTM discovery rows."
    )
    parser.add_argument("--estimates", type=Path, required=True)
    parser.add_argument("--listing-input", type=Path, required=True)
    parser.add_argument("--analysis-as-of", required=True)
    parser.add_argument("--estimate-as-of", required=True, help="Estimate retrieval/data timestamp")
    parser.add_argument("--source-id", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-analysts", type=int, default=2)
    parser.add_argument("--max-dispersion-pct", type=float, default=100.0)
    parser.add_argument("--max-fy1-horizon-days", type=int, default=430)
    parser.add_argument("--forward-pe-tolerance-pct", type=float, default=3.0)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    if "--version" in raw_argv:
        print(json.dumps(runtime_metadata(), sort_keys=True))
        return 0
    args = parse_args(raw_argv)
    try:
        analysis_as_of = _parse_date(args.analysis_as_of, "analysis_as_of")
        estimate_as_of = _parse_date(args.estimate_as_of, "estimate_as_of")
        estimate_rows = _load_rows(args.estimates)
        listing_rows = _load_rows(args.listing_input)
        listing_index = {_symbol(row): row for row in listing_rows}
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in estimate_rows:
            grouped[_symbol(row)].append(dict(row))
        symbols = sorted(set(listing_index) | set(grouped))
        output_rows = [
            normalize_symbol(
                symbol,
                grouped.get(symbol, []),
                listing_index.get(symbol, {"symbol": symbol}),
                analysis_as_of=analysis_as_of,
                estimate_as_of=estimate_as_of,
                source_ids=args.source_id,
                minimum_analysts=args.minimum_analysts,
                max_dispersion_pct=args.max_dispersion_pct,
                max_fy1_horizon_days=args.max_fy1_horizon_days,
                forward_pe_tolerance_pct=args.forward_pe_tolerance_pct,
            )
            for symbol in symbols
        ]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "".join(
                json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                for row in output_rows
            ),
            encoding="utf-8",
        )
    except (OSError, ValueError, json.JSONDecodeError, NormalizeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def apply_verified_actual_eps(
    row: Mapping[str, Any],
    *,
    actual_eps: float | None,
    period_end: str | None,
    analysis_as_of: datetime,
    source_ids: Sequence[str],
) -> dict[str, Any]:
    """Re-derive the growth-basis fields from a VERIFIED reported annual EPS.

    ``actual_eps``/``period_end`` must come from a filing whose accepted date is
    at or before ``analysis_as_of`` (the caller checks that). When the actual is
    missing, non-positive, or dated after ``analysis_as_of``, every
    actual-derived field is reset to None and ``growth_pattern`` to
    ``"unknown"`` so nothing downstream can mistake consensus for a reported
    figure.
    """
    out = dict(row)
    # growth_pattern / current_year_growth_pct stay on the consensus same-basis
    # comparison made at normalization; a GAAP actual must never be compared
    # against an (usually adjusted) consensus to relabel them.
    reset = {
        "latest_actual_eps": None,
        "latest_actual_period_end": None,
        "latest_actual_source_ids": [],
        "latest_actual_verified": False,
        "latest_actual_basis": None,
        "fy1_eps_below_latest_actual": None,
        "current_year_growth_pct_vs_gaap_actual": None,
        "eps_growth_actual_to_fy3_pct": None,
        "estimate_basis_likely_adjusted": None,
    }
    if actual_eps is None or actual_eps <= 0 or not period_end:
        out.update(reset)
        return out
    end = _parse_date(period_end, "actual.period_end")
    if end > analysis_as_of:
        out.update(reset)
        return out

    fy1_eps = _number(out.get("fy1_eps"))
    periods = [dict(p) for p in (out.get("estimate_periods") or []) if isinstance(p, Mapping)]
    growth_end_period = _text(out.get("growth_horizon_end_period"))
    growth_end = next((p for p in periods if _text(p.get("period")) == growth_end_period), None)
    growth_end_eps = _number(growth_end.get("eps_avg")) if growth_end else None
    growth_end_end = _text(growth_end.get("period_end")) if growth_end else None

    fy1_below = fy1_eps < actual_eps if fy1_eps is not None else None
    current_year_growth = (fy1_eps / actual_eps - 1.0) * 100.0 if fy1_eps is not None else None
    fy0_consensus = _number(out.get("fy0_consensus_eps"))
    # Consensus is usually adjusted (ex-SBC, ex-amortization); when the
    # provider's own prior-year row differs from the GAAP actual by more than
    # 15%, the bases differ and GAAP-vs-consensus comparisons are unreliable.
    basis_flag = (
        abs(fy0_consensus - actual_eps) / actual_eps > 0.15 if fy0_consensus is not None else None
    )
    actual_to_fy3 = None
    if growth_end_eps is not None and growth_end_end:
        years = (_parse_date(growth_end_end, "growth_end.period_end") - end).days / 365.25
        actual_to_fy3 = _cagr(actual_eps, growth_end_eps, years)

    out.update(
        {
            "latest_actual_eps": round(actual_eps, 6),
            "latest_actual_period_end": period_end,
            "latest_actual_source_ids": list(source_ids),
            "latest_actual_verified": True,
            "latest_actual_basis": "gaap_diluted",
            "fy1_eps_below_latest_actual": fy1_below,
            "current_year_growth_pct_vs_gaap_actual": round(current_year_growth, 6)
            if current_year_growth is not None
            else None,
            "eps_growth_actual_to_fy3_pct": round(actual_to_fy3, 6)
            if actual_to_fy3 is not None
            else None,
            "estimate_basis_likely_adjusted": basis_flag,
        }
    )
    return out
