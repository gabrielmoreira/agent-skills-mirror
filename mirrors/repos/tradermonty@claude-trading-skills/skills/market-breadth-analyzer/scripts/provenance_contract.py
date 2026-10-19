"""Standalone common schema 1.0 and opt-in market handoff policy.

Vendored identically in the three market-regime skills. Keep schema validation
compatible with scripts/validate_provenance.py; strict policy is separate.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo

SCHEMA_VERSION = "1.0"

REQUIRED_FIELDS = (
    "schema_version",
    "provider",
    "endpoint",
    "retrieved_at",
    "as_of",
    "timezone",
    "adjusted",
    "point_in_time",
    "survivorship_free",
    "corporate_actions_handled",
)

# Provenance fields are intentionally global so the contract is versioned in one
# place; each skill references them when emitting a block.
STRING_FIELDS = ("provider", "endpoint", "timezone", "schema_version")
BOOL_FIELDS = (
    "adjusted",
    "point_in_time",
    "survivorship_free",
    "corporate_actions_handled",
)


def _is_iso_datetime(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def validate_provenance(block: Any, schema_version: str = SCHEMA_VERSION) -> list[str]:
    """Return a list of validation errors; an empty list means the block is valid.

    Unknown fields are intentionally permitted so the contract can be extended.
    Each error identifies the offending field and the requirement it violates.
    """
    if not isinstance(block, dict):
        return ["data_provenance must be a mapping"]

    errors: list[str] = []

    declared_version = block.get("schema_version")
    if declared_version is not None and declared_version != schema_version:
        errors.append(
            f"schema_version {declared_version!r} does not match contract {schema_version!r}"
        )

    for field in REQUIRED_FIELDS:
        if field not in block:
            errors.append(f"missing required field: {field}")

    for field in STRING_FIELDS:
        if field in block and (not isinstance(block[field], str) or not block[field].strip()):
            errors.append(f"{field} must be a non-empty string")

    for field in BOOL_FIELDS:
        if field in block and not _is_bool(block[field]):
            errors.append(f"{field} must be a boolean (state honestly, e.g. False)")

    if "retrieved_at" in block and not _is_iso_datetime(block["retrieved_at"]):
        errors.append("retrieved_at must be an ISO-8601 UTC timestamp with timezone")

    if "as_of" in block and not (_is_iso_date(block["as_of"]) or _is_iso_datetime(block["as_of"])):
        errors.append("as_of must be an ISO-8601 date (YYYY-MM-DD)")

    if "timezone" in block and isinstance(block["timezone"], str) and block["timezone"].strip():
        try:
            ZoneInfo(block["timezone"])
        except (KeyError, ValueError):
            errors.append(f"timezone {block['timezone']!r} is not a valid IANA timezone")

    return errors


def build_provenance(
    *,
    provider: str,
    endpoint: str,
    retrieved_at: str,
    as_of: str,
    run_id: str,
    timezone_name: str = "America/New_York",
) -> dict:
    block = {
        "schema_version": SCHEMA_VERSION,
        "provider": provider,
        "endpoint": endpoint,
        "retrieved_at": retrieved_at,
        "as_of": as_of,
        "timezone": timezone_name,
        "adjusted": False,
        "point_in_time": False,
        "survivorship_free": False,
        "corporate_actions_handled": False,
        "run_id": run_id,
        "scope": "primary timeseries only; auxiliary source dates unverified",
    }
    errors = validate_provenance(block)
    if errors:
        raise ValueError("invalid primary provenance: " + "; ".join(errors))
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be non-empty")
    return block


def _aware(value: str, label: str) -> datetime:
    if not _is_iso_datetime(value):
        raise ValueError(label + " must be a timezone-aware ISO timestamp")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_handoff(block: Any, *, run_id: str, evaluation: str, max_age_days: int) -> dict:
    errors = validate_provenance(block)
    if errors:
        raise ValueError("invalid data_provenance: " + "; ".join(errors))
    if not isinstance(run_id, str) or not run_id.strip() or block.get("run_id") != run_id:
        raise ValueError("data_provenance run_id does not match expected run")
    if isinstance(max_age_days, bool) or not isinstance(max_age_days, int) or max_age_days < 0:
        raise ValueError("max_age_days must be a nonnegative integer")
    now = _aware(evaluation, "evaluation")
    retrieved = _aware(block["retrieved_at"], "retrieved_at")
    if retrieved.utcoffset() != timedelta(0):
        raise ValueError("retrieved_at must be UTC")
    if retrieved > now:
        raise ValueError("retrieved_at cannot be after evaluation")
    value = block["as_of"]
    if _is_iso_date(value):
        business_date = date.fromisoformat(value)
        reporting_zone = ZoneInfo(block["timezone"])
        if business_date > retrieved.astimezone(reporting_zone).date():
            raise ValueError("as_of cannot be after retrieval business date")
        age = (now.astimezone(reporting_zone).date() - business_date).days
        if age > max_age_days:
            raise ValueError("primary data is stale")
    else:
        as_of = _aware(value, "as_of")
        if as_of > retrieved:
            raise ValueError("as_of cannot be after retrieval")
        if (now - as_of).total_seconds() > max_age_days * 86400:
            raise ValueError("primary data is stale")
    return dict(block)


def validate_market_inputs(
    breadth: Any, uptrend: Any, *, run_id: str, evaluation: str, max_age_days: int
) -> dict:
    accepted = {}
    for name, payload in (("breadth", breadth), ("uptrend", uptrend)):
        if not isinstance(payload, dict):
            raise ValueError(name + " input is required in strict mode")
        try:
            accepted[name] = validate_handoff(
                payload.get("data_provenance"),
                run_id=run_id,
                evaluation=evaluation,
                max_age_days=max_age_days,
            )
        except ValueError as exc:
            raise ValueError(name + ": " + str(exc)) from exc
    return {
        "run_id": run_id,
        "evaluation_at": evaluation,
        "max_age_days": max_age_days,
        "accepted_inputs": accepted,
        "boundaries": [
            "quality flags are conservative, not independently verified",
            "auxiliary source dates are not verified",
            "optional top-risk and other inputs are outside this gate",
            "run_id is a caller consistency marker, not authentication or PIT proof",
        ],
    }


def safe_source_url(value: str) -> str:
    """Keep source identity without credentials, query secrets or fragments."""
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    if ":" in host:
        host = "[" + host + "]"
    if parsed.port:
        host += ":" + str(parsed.port)
    return urlunsplit((parsed.scheme, host, parsed.path, "", ""))
