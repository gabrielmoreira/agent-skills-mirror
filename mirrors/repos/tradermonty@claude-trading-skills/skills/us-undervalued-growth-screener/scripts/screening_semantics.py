#!/usr/bin/env python3
"""Shared fail-closed semantics for broad-screen liquidity and estimates.

The discovery layer must not confuse one-session share volume with average daily
*dollar* volume.  Likewise, a distant outer-year estimate must never be labelled
as the current NTM/FY1 metric merely because it makes a P/E look low.  All
helpers in this module return normalized evidence plus explicit reason codes;
callers may explain those reasons, but may not override them.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

VALID_ADDV_METHODS = {
    "provider_average_dollar_volume",
    "price_x_provider_average_volume",
    "price_x_20d_average_volume",
    "price_x_30d_average_volume",
    "price_x_60d_average_volume",
    "price_x_90d_average_volume",
}
INVALID_SINGLE_SESSION_METHODS = {
    "price_x_single_session_volume",
    "single_session_dollar_volume",
    "single_session_volume",
    "price_x_volume",
}
VALID_CURRENT_FORWARD_PERIODS = {"NTM", "FY1"}
VALID_FORWARD_ORIGINS = {
    "computed_from_price_and_fy1_eps",
    "computed_from_price_and_ntm_eps",
    "provider_fy1_pe_with_eps_reconciliation",
    "provider_ntm_pe_with_eps_reconciliation",
}


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
        value = value.strip()
        return value or None
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


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _parse_datetime(value: Any) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def normalize_liquidity(
    row: Mapping[str, Any],
    *,
    minimum_period_days: int = 20,
) -> dict[str, Any]:
    """Return auditable average-daily-dollar-volume evidence.

    A raw ``volume`` value is deliberately ignored.  To be valid, liquidity
    must carry an allowed averaging method, a window of at least
    ``minimum_period_days``, and at least one source ID.  Provider camelCase
    aliases are accepted only for the *average* volume field.
    """
    price = _number(row.get("price"))
    if price is None:
        price = _number(row.get("last"))

    explicit_addv = _number(row.get("average_daily_dollar_volume"))
    if explicit_addv is None:
        explicit_addv = _number(row.get("avg_dollar_volume"))

    average_volume = _number(row.get("average_volume"))
    if average_volume is None:
        average_volume = _number(row.get("avg_volume"))
    if average_volume is None:
        average_volume = _number(row.get("avgVolume"))
    if average_volume is None:
        average_volume = _number(row.get("averageVolume"))

    method = (
        _text(row.get("average_daily_dollar_volume_method"))
        or _text(row.get("liquidity_method"))
        or ""
    ).lower()
    period_days = (
        _integer(row.get("average_volume_period_days"))
        or _integer(row.get("liquidity_window_days"))
        or _integer(row.get("average_daily_dollar_volume_period_days"))
    )
    source_ids = _list_of_strings(row.get("liquidity_source_ids"))
    if not source_ids:
        source_ids = _list_of_strings(row.get("average_daily_dollar_volume_source_ids"))

    reasons: list[str] = []
    value: float | None = None

    if method in INVALID_SINGLE_SESSION_METHODS:
        reasons.append("single_session_volume_not_valid_for_addv")
    elif method not in VALID_ADDV_METHODS:
        reasons.append("average_liquidity_method_missing_or_invalid")
    elif period_days is None or period_days < minimum_period_days:
        reasons.append("average_liquidity_window_below_minimum")
    elif method == "provider_average_dollar_volume":
        if explicit_addv is None or explicit_addv <= 0:
            reasons.append("average_daily_dollar_volume_unavailable_or_non_positive")
        else:
            value = explicit_addv
    else:
        if price is None or price <= 0 or average_volume is None or average_volume <= 0:
            reasons.append("price_or_average_volume_unavailable_or_non_positive")
        else:
            value = price * average_volume
            if explicit_addv is not None:
                tolerance = max(abs(value), 1.0) * 0.05
                if abs(explicit_addv - value) > tolerance:
                    reasons.append("average_daily_dollar_volume_reconciliation_failed")

    if not source_ids:
        reasons.append("liquidity_source_ids_required")

    valid = value is not None and value > 0 and not reasons
    return {
        "value": value if valid else None,
        "valid_for_screen": valid,
        "method": method or None,
        "period_days": period_days,
        "source_ids": source_ids,
        "reasons": sorted(set(reasons)),
        "price": price,
        "average_volume": average_volume,
        "raw_single_session_volume_present": _number(row.get("volume")) is not None,
    }


def normalize_forward_valuation(
    row: Mapping[str, Any],
    *,
    price: float | None,
    analysis_as_of: str | None,
    max_age_days: int = 45,
    reconciliation_tolerance_pct: float = 5.0,
    maximum_dispersion_pct: float = 100.0,
    maximum_fy1_horizon_days: int = 430,
) -> dict[str, Any]:
    """Validate that the current multiple is genuinely NTM or FY1.

    ``forward_pe`` alone is never sufficient.  The row must identify the
    current period (NTM/FY1), its period end, the estimate date, source IDs, a
    positive matching EPS, and the origin of the multiple.  Distant FY2/FY3
    estimates, pre-operating companies, zero-crossing ranges, and discontinuous
    annual series fail closed.
    """
    reasons: list[str] = []

    normalization_status = (_text(row.get("estimate_normalization_status")) or "").lower()
    normalization_reasons = _list_of_strings(row.get("estimate_normalization_reasons"))
    if normalization_status and normalization_status != "valid":
        reasons.append("estimate_normalization_not_valid")
        reasons.extend(normalization_reasons)
    elif normalization_status == "valid" and normalization_reasons:
        reasons.append("estimate_normalization_status_inconsistent")
        reasons.extend(normalization_reasons)

    if _number(row.get("ntm_pe")) is not None:
        pe = _number(row.get("ntm_pe"))
        period = "NTM"
        eps = _number(row.get("ntm_eps")) or _number(row.get("forward_eps"))
        inferred_origin = "provider_ntm_pe_with_eps_reconciliation"
    elif _number(row.get("fy1_pe")) is not None:
        pe = _number(row.get("fy1_pe"))
        period = "FY1"
        eps = _number(row.get("fy1_eps")) or _number(row.get("forward_eps"))
        inferred_origin = "provider_fy1_pe_with_eps_reconciliation"
    else:
        pe = _number(row.get("forward_pe"))
        period = (
            _text(row.get("forward_pe_period")) or _text(row.get("forward_metric_period")) or ""
        ).upper() or None
        eps = _number(row.get("forward_eps"))
        if period == "NTM" and eps is None:
            eps = _number(row.get("ntm_eps"))
        if period == "FY1" and eps is None:
            eps = _number(row.get("fy1_eps"))
        inferred_origin = None

    origin = (
        _text(row.get("forward_metric_origin"))
        or _text(row.get("forward_pe_origin"))
        or inferred_origin
    )
    fiscal_year = _text(row.get("forward_fiscal_year")) or _text(row.get("fy1_fiscal_year"))
    period_end_text = (
        _text(row.get("forward_period_end"))
        or _text(row.get("forward_metric_period_end"))
        or _text(row.get("fy1_period_end"))
    )
    period_end = _parse_datetime(period_end_text)
    estimate_as_of_text = _text(row.get("forward_estimate_as_of")) or _text(
        row.get("estimate_as_of")
    )
    estimate_as_of = _parse_datetime(estimate_as_of_text)
    analysis_dt = _parse_datetime(analysis_as_of)
    source_ids = _list_of_strings(row.get("forward_estimate_source_ids"))
    if not source_ids:
        source_ids = _list_of_strings(row.get("forward_metric_source_ids"))
    if not source_ids:
        source_ids = _list_of_strings(row.get("enrichment_source_ids"))

    low = _number(row.get("forward_eps_low"))
    high = _number(row.get("forward_eps_high"))
    dispersion_pct: float | None = None
    horizon_days: float | None = None

    if pe is None or pe <= 0:
        reasons.append("forward_pe_unavailable_or_non_positive")
    if period not in VALID_CURRENT_FORWARD_PERIODS:
        reasons.append("forward_pe_period_must_be_ntm_or_fy1")
    if eps is None or eps <= 0:
        reasons.append("current_forward_eps_unavailable_or_non_positive")
    if origin not in VALID_FORWARD_ORIGINS:
        reasons.append("forward_metric_origin_missing_or_invalid")
    if period == "FY1" and not fiscal_year:
        reasons.append("fy1_fiscal_year_required")
    if period_end is None:
        reasons.append("current_forward_period_end_required")
    elif analysis_dt is not None:
        horizon_days = (period_end - analysis_dt).total_seconds() / 86400.0
        if horizon_days <= 0:
            reasons.append("current_forward_period_must_end_after_analysis")
        elif horizon_days > maximum_fy1_horizon_days:
            reasons.append("current_forward_period_is_not_fy1_or_ntm")

    operating_stage = (_text(row.get("operating_stage")) or "").lower().replace(" ", "_")
    if _bool(row.get("is_pre_operating")) is True or operating_stage in {
        "pre_operating",
        "pre-revenue",
        "pre_revenue",
        "development_stage",
    }:
        reasons.append("pre_operating_company_not_pe_evaluable")
    if row.get("estimate_series_contiguous") is False:
        reasons.append("annual_estimate_series_not_contiguous")

    if estimate_as_of is None:
        reasons.append("forward_estimate_as_of_required")
    elif analysis_dt is not None:
        age_days = (analysis_dt - estimate_as_of).total_seconds() / 86400.0
        if age_days < -1e-6:
            reasons.append("forward_estimate_after_analysis_as_of")
        elif age_days > max_age_days:
            reasons.append("forward_estimate_stale")
    if not source_ids:
        reasons.append("forward_estimate_source_ids_required")

    implied: float | None = None
    if (
        price is not None
        and price > 0
        and pe is not None
        and pe > 0
        and eps is not None
        and eps > 0
    ):
        implied = price / eps
        diff_pct = abs(implied - pe) / max(abs(pe), 1e-9) * 100.0
        if diff_pct > reconciliation_tolerance_pct:
            reasons.append("forward_pe_does_not_reconcile_to_price_and_eps")
    else:
        reasons.append("price_eps_multiple_reconciliation_unavailable")

    if low is not None and high is not None:
        if low > high:
            reasons.append("forward_eps_range_invalid")
        elif low <= 0 <= high:
            reasons.append("forward_eps_range_crosses_zero")
        elif eps is not None and eps != 0:
            dispersion_pct = abs(high - low) / abs(eps) * 100.0
            if dispersion_pct > maximum_dispersion_pct:
                reasons.append("forward_eps_dispersion_excessive")

    valid = not reasons
    analyst_count = (
        _integer(row.get("forward_eps_analyst_count"))
        or _integer(row.get("fy1_analyst_count"))
        or _integer(row.get("analyst_count"))
    )
    return {
        "valid": valid,
        "forward_pe": pe if valid else None,
        "forward_eps": eps if valid else None,
        "period": period,
        "fiscal_year": fiscal_year,
        "period_end": period_end_text,
        "horizon_days": horizon_days,
        "estimate_as_of": estimate_as_of_text,
        "source_ids": source_ids,
        "origin": origin,
        "analyst_count": analyst_count,
        "eps_low": low,
        "eps_high": high,
        "dispersion_pct": dispersion_pct,
        "implied_forward_pe": implied,
        "reasons": sorted(set(reasons)),
    }
