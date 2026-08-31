#!/usr/bin/env python3
"""Schema-v3 / contract-v3.5 research validation for the US GARP screener.

The module performs no network access. It validates source-ledger types,
market context, broad-screen audit artifacts, latest-earnings period separation,
forward-multiple inputs, estimate breadth, cash-definition consistency, and
run completeness before deterministic scoring.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from skill_version import (
        CONTRACT_REVISION,
        RUNTIME_FINGERPRINT,
        SCHEMA_VERSION,
        SKILL_VERSION,
        runtime_metadata,
    )
except ModuleNotFoundError:  # Supports importlib-based unit loading.
    import importlib.util as _importlib_util

    _version_path = Path(__file__).with_name("skill_version.py")
    _version_spec = _importlib_util.spec_from_file_location("skill_version", _version_path)
    if _version_spec is None or _version_spec.loader is None:
        raise
    _version_module = _importlib_util.module_from_spec(_version_spec)
    _version_spec.loader.exec_module(_version_module)
    CONTRACT_REVISION = _version_module.CONTRACT_REVISION
    RUNTIME_FINGERPRINT = _version_module.RUNTIME_FINGERPRINT
    SCHEMA_VERSION = _version_module.SCHEMA_VERSION
    SKILL_VERSION = _version_module.SKILL_VERSION
    runtime_metadata = _version_module.runtime_metadata

try:
    from screening_semantics import normalize_liquidity
except ModuleNotFoundError:
    import importlib.util as _semantics_importlib_util

    _semantics_path = Path(__file__).with_name("screening_semantics.py")
    _semantics_spec = _semantics_importlib_util.spec_from_file_location(
        "screening_semantics_contract", _semantics_path
    )
    if _semantics_spec is None or _semantics_spec.loader is None:
        raise
    _semantics_module = _semantics_importlib_util.module_from_spec(_semantics_spec)
    _semantics_spec.loader.exec_module(_semantics_module)
    normalize_liquidity = _semantics_module.normalize_liquidity


ALLOWED_SOURCE_KINDS = {
    "sec_filing",
    "company_ir",
    "exchange_status",
    "official_macro",
    "official_statistics",
    "market_data",
    "consensus",
    "news",
    "third_party_transcript",
    "analyst_calculation",
    "analyst_assumption",
    "local_artifact",
}

SOURCE_KIND_TIERS: dict[str, set[int]] = {
    "sec_filing": {1},
    "official_macro": {1, 3},
    "official_statistics": {1, 3},
    "company_ir": {2},
    "exchange_status": {2, 3},
    "market_data": {3},
    "consensus": {3},
    "news": {3},
    "third_party_transcript": {3},
    "analyst_calculation": {4},
    "analyst_assumption": {4},
    "local_artifact": {4},
}

OFFICIAL_SOURCE_DOMAINS = {
    "federalreserve.gov",
    "treasury.gov",
    "bls.gov",
    "bea.gov",
    "census.gov",
    "sec.gov",
    "cftc.gov",
    "fdic.gov",
    "occ.gov",
    "irs.gov",
    "dol.gov",
}
THIRD_PARTY_TRANSCRIPT_DOMAINS = {
    "fool.com",
    "seekingalpha.com",
    "stocktitan.net",
    "marketscreener.com",
    "investing.com",
    "finance.yahoo.com",
}


def _hostname(url: str | None) -> str:
    if not url:
        return ""
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def _domain_matches(host: str, domains: set[str]) -> bool:
    return any(host == domain or host.endswith("." + domain) for domain in domains)


def _is_accession_specific_sec_url(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if not _domain_matches((parsed.hostname or "").lower().removeprefix("www."), {"sec.gov"}):
        return False
    path = parsed.path.lower()
    query = parsed.query.lower()
    return "/archives/edgar/data/" in path or "doc=/archives/edgar/data/" in query


ALLOWED_AUDIT_DECISIONS = {
    "passed",
    "passed_exception",
    "selected",
    "deferred_by_budget",
    "needs_enrichment",
    "sector_review_required",
    "near_miss_review",
    "review_required",
    "unavailable_after_enrichment",
    "screened_out",
    "excluded",
}
ALLOWED_UNIVERSE_AUDIT_DECISIONS = {
    "in_scope",
    "liquidity_review",
    "out_of_scope",
    "excluded",
    "listing_data_incomplete",
}
ALLOWED_CANDIDATE_GENERATION_MODES = {
    "full_universe_fundamentals",
    "provider_prefilter",
    "liquidity_stratified_estimates",
    "available_fundamentals",
    "user_supplied",
}
ALLOWED_REPORT_TYPES = {"quarterly", "annual"}
ALLOWED_EARNINGS_PERIOD_TYPES = {"quarter", "full_year"}
ALLOWED_FORWARD_PERIOD_KINDS = {"ntm", "fy1"}
ALLOWED_FUTURE_PERIOD_KINDS = {"fy2", "fy3", "other"}
PLACEHOLDER_RE = re.compile(
    r"replace this|placeholder|synthetic text|todo|tbd|fill in|example only|ここに|要入力",
    re.IGNORECASE,
)


class ContractError(ValueError):
    """Raised when the snapshot cannot be normalized."""


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


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
        if math.isfinite(result):
            return result
    return None


def _integer(value: Any) -> int | None:
    value = _number(value)
    if value is not None and value.is_integer():
        return int(value)
    return None


def parse_iso8601(value: Any, field: str, *, required: bool = False) -> datetime | None:
    text = _text(value)
    if text is None:
        if required:
            raise ContractError(f"{field} is required")
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ContractError(f"{field} must be ISO-8601: {text!r}") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{field} must include a timezone: {text!r}")
    return parsed


def _parse_date(value: Any, field: str) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ContractError(f"{field} must be YYYY-MM-DD: {text!r}") from exc
    return parsed.replace(tzinfo=timezone.utc)


def _pct_diff(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    base = max(abs(a), abs(b), 1e-12)
    return abs(a - b) / base * 100.0


def _is_string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _is_placeholder(value: Any) -> bool:
    text = _text(value)
    return text is None or bool(PLACEHOLDER_RE.search(text))


def _canonical_jsonl(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return b"".join(
        (
            json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        for row in rows
    )


def _safe_artifact_path(root: Path, raw_path: str) -> Path:
    candidate = (root / raw_path).resolve()
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ContractError("screening_audit.artifact_path escapes artifact_root") from exc
    return candidate


def validate_source_ledger(
    global_sources: Sequence[Any],
    candidate_sources: Sequence[Any],
    analysis_as_of: datetime,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[str], list[str]]:
    warnings: list[str] = []
    review: list[str] = []
    index: dict[str, dict[str, Any]] = {}
    normalized: list[dict[str, Any]] = []

    for position, raw in enumerate(list(global_sources) + list(candidate_sources)):
        source = _mapping(raw)
        source_id = _text(source.get("id"))
        loc = f"sources[{position}]"
        if not source_id:
            review.append(f"{loc}.id is required")
            continue
        tier = _integer(source.get("tier"))
        kind = (_text(source.get("kind")) or "").lower()
        supports = source.get("supports")
        retrieved_at = None
        published_at = None
        data_as_of = None

        if tier not in {1, 2, 3, 4}:
            review.append(f"source {source_id!r} has invalid tier")
        if kind not in ALLOWED_SOURCE_KINDS:
            review.append(f"source {source_id!r} has invalid kind {kind!r}")
        elif tier not in SOURCE_KIND_TIERS[kind]:
            review.append(f"source {source_id!r} kind {kind!r} is incompatible with tier {tier!r}")
        if not _text(source.get("title")):
            review.append(f"source {source_id!r} has no title")
        source_url = _text(source.get("url"))
        if not source_url:
            review.append(f"source {source_id!r} has no URL")
        host = _hostname(source_url)
        if kind in {"official_macro", "official_statistics"} and not _domain_matches(
            host, OFFICIAL_SOURCE_DOMAINS
        ):
            review.append(
                f"source {source_id!r} is classified as official but URL domain {host!r} is not an approved official domain"
            )
        if kind == "sec_filing":
            if not _domain_matches(host, {"sec.gov"}):
                review.append(
                    f"source {source_id!r} is classified as sec_filing but is not on sec.gov"
                )
            elif not _is_accession_specific_sec_url(source_url):
                review.append(
                    f"source {source_id!r} must use an accession-specific SEC Archives URL, not a changing company browse page"
                )
        if kind == "company_ir" and _domain_matches(host, THIRD_PARTY_TRANSCRIPT_DOMAINS):
            review.append(
                f"source {source_id!r} is a third-party page and cannot be classified as company_ir"
            )
        if kind == "third_party_transcript" and not host:
            review.append(f"source {source_id!r} transcript URL is invalid")
        if not _is_string_list(supports, nonempty=True):
            review.append(f"source {source_id!r}.supports must be a non-empty array of strings")
        try:
            retrieved_at = parse_iso8601(
                source.get("retrieved_at"), f"source {source_id}.retrieved_at", required=True
            )
        except ContractError as exc:
            review.append(str(exc))
        try:
            published_at = parse_iso8601(
                source.get("published_at"), f"source {source_id}.published_at"
            )
        except ContractError as exc:
            review.append(str(exc))
        try:
            data_as_of = parse_iso8601(source.get("data_as_of"), f"source {source_id}.data_as_of")
        except ContractError as exc:
            review.append(str(exc))
        if retrieved_at and retrieved_at > analysis_as_of:
            review.append(f"source {source_id!r} was retrieved after analysis_as_of")
        if published_at and published_at > analysis_as_of:
            review.append(f"source {source_id!r} was published after analysis_as_of")
        if data_as_of and data_as_of > analysis_as_of:
            review.append(f"source {source_id!r}.data_as_of is after analysis_as_of")

        normalized_source = deepcopy(source)
        normalized_source["id"] = source_id
        normalized_source["kind"] = kind
        normalized_source["tier"] = tier
        if source_id in index:
            if index[source_id] != normalized_source:
                review.append(f"duplicate source ID {source_id!r} has conflicting definitions")
            else:
                warnings.append(f"duplicate source ID {source_id!r} was de-duplicated")
            continue
        index[source_id] = normalized_source
        normalized.append(normalized_source)

    return index, normalized, list(dict.fromkeys(warnings)), list(dict.fromkeys(review))


def _sources_resolve(source_ids: Any, source_index: Mapping[str, Mapping[str, Any]]) -> bool:
    if not _is_string_list(source_ids, nonempty=True):
        return False
    return all(source_id in source_index for source_id in source_ids)


def _has_primary(source_ids: Any, source_index: Mapping[str, Mapping[str, Any]]) -> bool:
    if not _sources_resolve(source_ids, source_index):
        return False
    return any(_integer(source_index[source_id].get("tier")) in {1, 2} for source_id in source_ids)


def validate_market_context(
    context_raw: Any,
    source_index: Mapping[str, Mapping[str, Any]],
    analysis_as_of: datetime,
    config: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, list[str], list[str]]:
    """Validate current macro/valuation context against field-level evidence.

    Retrieval time does not make an old valuation datum current. For each
    dynamic field, use ``data_as_of`` when supplied, otherwise ``published_at``.
    Official macro fields must be supported by an official source. Statements
    about market-implied rate paths require an explicit supported inference.
    """
    context = _mapping(context_raw)
    warnings: list[str] = []
    review: list[str] = []
    summary = _text(context.get("summary"))
    if _is_placeholder(summary) or (summary and len(summary) < 40):
        review.append(
            "market_context.summary is missing, too short, or still contains placeholder text"
        )

    as_of = None
    try:
        as_of = parse_iso8601(context.get("as_of"), "market_context.as_of", required=True)
    except ContractError as exc:
        review.append(str(exc))
    if as_of:
        if as_of > analysis_as_of:
            review.append("market_context.as_of is after analysis_as_of")
        max_age = _number(config.get("max_market_context_age_days")) or 14.0
        age_days = (analysis_as_of - as_of).total_seconds() / 86_400
        if age_days > max_age:
            review.append(
                f"market context is stale ({age_days:.1f} days old; maximum {max_age:.0f})"
            )

    required_numeric = (
        "policy_rate_pct",
        "treasury_10y_yield_pct",
        "inflation_yoy_pct",
        "market_forward_pe",
    )
    for key in required_numeric:
        if _number(context.get(key)) is None:
            review.append(f"market_context.{key} is required")
    if _number(context.get("real_gdp_growth_pct")) is None:
        warnings.append("market_context.real_gdp_growth_pct is not verified")
    if not _text(context.get("small_mid_cap_valuation_context")):
        review.append("market_context.small_mid_cap_valuation_context is required")
    if not isinstance(context.get("sector_cycle_notes"), list):
        review.append("market_context.sector_cycle_notes must be an array")

    source_ids = context.get("source_ids")
    if not _sources_resolve(source_ids, source_index) or len(source_ids) < 2:
        review.append("market_context.source_ids must resolve to at least two sources")
        source_ids = []

    def supporting_sources(path: str) -> list[Mapping[str, Any]]:
        rows: list[Mapping[str, Any]] = []
        for source_id in source_ids if isinstance(source_ids, list) else []:
            source = source_index.get(source_id)
            if not source:
                continue
            supports = source.get("supports")
            if isinstance(supports, list) and any(
                isinstance(value, str) and (value == path or value.startswith(path + "."))
                for value in supports
            ):
                rows.append(source)
        return rows

    def effective_date(source: Mapping[str, Any]) -> datetime | None:
        for key in ("data_as_of", "published_at"):
            try:
                value = parse_iso8601(source.get(key), f"source {source.get('id')}.{key}")
            except ContractError:
                value = None
            if value is not None:
                return value
        return None

    field_rules = {
        "policy_rate_pct": {
            "path": "market_context.policy_rate_pct",
            "max_age": _number(config.get("max_policy_rate_source_age_days")) or 60.0,
            "official": True,
        },
        "treasury_10y_yield_pct": {
            "path": "market_context.treasury_10y_yield_pct",
            "max_age": _number(config.get("max_market_rate_source_age_days")) or 7.0,
            "official": True,
        },
        "inflation_yoy_pct": {
            "path": "market_context.inflation_yoy_pct",
            "max_age": _number(config.get("max_inflation_source_age_days")) or 45.0,
            "official": True,
        },
        "real_gdp_growth_pct": {
            "path": "market_context.real_gdp_growth_pct",
            "max_age": _number(config.get("max_gdp_source_age_days")) or 120.0,
            "official": True,
        },
        "market_forward_pe": {
            "path": "market_context.market_forward_pe",
            "max_age": _number(config.get("max_market_valuation_source_age_days"))
            or _number(config.get("max_market_context_age_days"))
            or 14.0,
            "official": False,
        },
        "small_mid_cap_valuation_context": {
            "path": "market_context.small_mid_cap_valuation_context",
            "max_age": _number(config.get("max_small_mid_context_source_age_days"))
            or _number(config.get("max_market_context_age_days"))
            or 14.0,
            "official": False,
        },
    }
    official_kinds = {"official_macro", "official_statistics"}
    for field, rule in field_rules.items():
        if field == "real_gdp_growth_pct" and _number(context.get(field)) is None:
            continue
        if field == "small_mid_cap_valuation_context" and not _text(context.get(field)):
            continue
        rows = supporting_sources(str(rule["path"]))
        if not rows:
            review.append(f"{rule['path']} has no field-level supporting source")
            continue
        if rule["official"] and not any(
            (_text(row.get("kind")) or "").lower() in official_kinds for row in rows
        ):
            review.append(
                f"{rule['path']} must be supported by an official macro/statistics source"
            )
        fresh = False
        ages: list[float] = []
        for row in rows:
            stamp = effective_date(row)
            if stamp is None:
                continue
            age_days = (analysis_as_of - stamp).total_seconds() / 86_400
            ages.append(age_days)
            if age_days <= float(rule["max_age"]):
                fresh = True
        if not fresh:
            oldest_note = (
                f"; observed ages={','.join(f'{age:.1f}' for age in ages)}" if ages else ""
            )
            review.append(
                f"{rule['path']} lacks a source within {float(rule['max_age']):.0f} days{oldest_note}"
            )

    # Market-implied policy-path language must be traceable, not silently inferred.
    summary_lower = (summary or "").lower()
    expectation_terms = (
        "markets price",
        "market prices",
        "priced in",
        "rate hike",
        "rate cut",
        "市場は",
        "織り込",
        "利上げ",
        "利下げ",
    )
    if any(term in summary_lower for term in expectation_terms):
        expectation_sources = supporting_sources("market_context.market_rate_expectations")
        inference_rows = _list(context.get("inferences"))
        inference_supported = any(
            (_text(_mapping(row).get("classification")) or "").lower() == "analyst_inference"
            and _sources_resolve(_mapping(row).get("source_ids"), source_index)
            for row in inference_rows
        )
        if not expectation_sources and not inference_supported:
            review.append(
                "market_context.summary contains a market-rate expectation without a supporting source or analyst_inference record"
            )

    normalized = deepcopy(context)
    normalized["valid"] = not review
    return normalized, not review, list(dict.fromkeys(warnings)), list(dict.fromkeys(review))


def _load_jsonl_artifact(
    section: Mapping[str, Any],
    artifact_root: Path | None,
    *,
    label: str,
) -> tuple[list[dict[str, Any]], str | None, list[str]]:
    review: list[str] = []
    rows_raw = section.get("embedded_rows")
    if isinstance(rows_raw, list):
        rows = [_mapping(row) for row in rows_raw]
        return rows, hashlib.sha256(_canonical_jsonl(rows)).hexdigest(), review

    artifact_path = _text(section.get("artifact_path"))
    if not artifact_path:
        return [], None, [f"{label}.artifact_path or embedded_rows is required"]
    if artifact_root is None:
        return [], None, [f"artifact_root is required to verify {label}.artifact_path"]
    try:
        path = _safe_artifact_path(artifact_root, artifact_path)
    except ContractError as exc:
        return [], None, [str(exc)]
    if not path.is_file():
        return [], None, [f"{label} artifact does not exist: {path}"]
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            review.append(f"{label} line {line_number} is not valid JSON")
            continue
        if not isinstance(value, Mapping):
            review.append(f"{label} line {line_number} is not an object")
            continue
        rows.append(dict(value))
    return rows, digest, review


def validate_screening_audit(
    audit_raw: Any,
    funnel_raw: Any,
    source_index: Mapping[str, Mapping[str, Any]],
    analysis_as_of: datetime,
    artifact_root: Path | None,
    config: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, list[str], list[str]]:
    """Validate the v3.5 staged listing/candidate-pool audit.

    Completion is resolution-based, never attempt-count based. A no-candidates
    conclusion is valid only when the bounded candidate pool is explicitly
    exhausted, every row has a final broad-screen disposition, and no
    enrichment queue remains.
    """
    audit = _mapping(audit_raw)
    funnel = _mapping(funnel_raw)
    warnings: list[str] = []
    review: list[str] = []

    if _integer(audit.get("audit_schema_version")) != 3:
        normalized = deepcopy(audit)
        normalized["valid"] = False
        return (
            normalized,
            False,
            warnings,
            [
                f"screening_audit.audit_schema_version must equal 3 for contract revision {CONTRACT_REVISION}"
            ],
        )
    if (_text(audit.get("contract_revision")) or "") != CONTRACT_REVISION:
        review.append(f"screening_audit.contract_revision must equal {CONTRACT_REVISION!r}")
    runtime = _mapping(audit.get("runtime"))
    expected_runtime = runtime_metadata()
    for key in (
        "skill_name",
        "skill_version",
        "schema_version",
        "contract_revision",
        "runtime_fingerprint",
    ):
        if runtime.get(key) != expected_runtime.get(key):
            review.append(
                f"screening_audit.runtime.{key} does not match the installed v{SKILL_VERSION} runtime"
            )

    try:
        parse_iso8601(audit.get("generated_at"), "screening_audit.generated_at", required=True)
    except ContractError as exc:
        review.append(str(exc))
    try:
        audit_as_of = parse_iso8601(
            audit.get("analysis_as_of"), "screening_audit.analysis_as_of", required=True
        )
        if audit_as_of and abs((audit_as_of - analysis_as_of).total_seconds()) > 1:
            review.append("screening_audit.analysis_as_of does not match top-level analysis_as_of")
    except ContractError as exc:
        review.append(str(exc))

    mode = (_text(audit.get("candidate_generation_mode")) or "").lower()
    if mode not in ALLOWED_CANDIDATE_GENERATION_MODES:
        review.append(f"screening_audit.candidate_generation_mode is invalid: {mode!r}")
    if not _mapping(audit.get("filters")):
        review.append("screening_audit.filters is required")
    if not _sources_resolve(audit.get("source_ids"), source_index):
        review.append("screening_audit.source_ids do not resolve")

    scope = _mapping(audit.get("scope"))
    requested_min = _number(scope.get("requested_min_market_cap"))
    requested_max = _number(scope.get("requested_max_market_cap"))
    retrieval_min = _number(scope.get("retrieval_min_market_cap"))
    retrieval_max = _number(scope.get("retrieval_max_market_cap"))
    bounds_valid = None not in {requested_min, requested_max, retrieval_min, retrieval_max}
    retrieval_covers_requested = False
    reduced = False
    if not bounds_valid:
        review.append("screening_audit.scope requires requested and retrieval market-cap bounds")
    else:
        assert requested_min is not None and requested_max is not None
        assert retrieval_min is not None and retrieval_max is not None
        if requested_min >= requested_max or retrieval_min >= retrieval_max:
            review.append("screening_audit.scope market-cap bounds are invalid")
        retrieval_covers_requested = (
            retrieval_min <= requested_min and retrieval_max >= requested_max
        )
        reduced = not retrieval_covers_requested
        if reduced and scope.get("scope_override_authorized") is not True:
            review.append("reduced execution scope was not explicitly authorized by the user")
        if reduced and (
            not _text(scope.get("scope_reduction_reason"))
            or not _text(scope.get("user_scope_evidence"))
        ):
            review.append(
                "authorized reduced scope requires scope_reduction_reason and user_scope_evidence"
            )
    if scope.get("retrieval_scope_explicit") is not True:
        review.append("screening_audit.scope.retrieval_scope_explicit must be true")

    user_scope = _mapping(scope.get("user_requested_scope"))
    executed_scope = _mapping(scope.get("executed_scope"))
    if (
        _number(user_scope.get("min_market_cap")) != requested_min
        or _number(user_scope.get("max_market_cap")) != requested_max
    ):
        review.append("screening_audit.scope.user_requested_scope does not match requested bounds")
    if (
        _number(executed_scope.get("min_market_cap")) != retrieval_min
        or _number(executed_scope.get("max_market_cap")) != retrieval_max
    ):
        review.append("screening_audit.scope.executed_scope does not match retrieval bounds")

    enumeration = _mapping(scope.get("enumeration"))
    pages_fetched = _integer(enumeration.get("pages_fetched"))
    band_rows = _list(enumeration.get("band_audit"))
    band_ranges: list[tuple[float, float]] = []
    bands_well_formed = bool(band_rows)
    for position, raw_band in enumerate(band_rows):
        band = _mapping(raw_band)
        band_min = _number(band.get("min_market_cap"))
        band_max = _number(band.get("max_market_cap"))
        band_count = _integer(band.get("rows_fetched"))
        if (
            band_min is None
            or band_max is None
            or band_min >= band_max
            or band_count is None
            or band_count < 0
            or band.get("provider_exhausted") is not True
        ):
            bands_well_formed = False
            review.append(
                f"screening_audit.scope.enumeration.band_audit[{position}] is malformed or not exhausted"
            )
            continue
        band_ranges.append((band_min, band_max))
    band_ranges.sort()
    bands_cover_retrieval = False
    if (
        bands_well_formed
        and band_ranges
        and retrieval_min is not None
        and retrieval_max is not None
    ):
        cursor = retrieval_min
        bands_cover_retrieval = True
        for band_min, band_max in band_ranges:
            if band_max < retrieval_min or band_min > retrieval_max:
                continue
            clipped_min = max(band_min, retrieval_min)
            clipped_max = min(band_max, retrieval_max)
            if clipped_min > cursor:
                bands_cover_retrieval = False
                break
            cursor = max(cursor, clipped_max)
        bands_cover_retrieval = bands_cover_retrieval and cursor >= retrieval_max
    bands_verified = bands_well_formed and bands_cover_retrieval
    pagination_verified = enumeration.get("pagination_exhausted") is True or bands_verified
    provider_total = _integer(enumeration.get("provider_reported_total"))
    rows_fetched = _integer(enumeration.get("rows_fetched"))
    provider_total_consistent = not (
        rows_fetched is not None and provider_total is not None and rows_fetched < provider_total
    )
    full_enumeration_verified = bool(pagination_verified and provider_total_consistent)
    executed_scope_complete = bool(
        scope.get("retrieval_scope_explicit") is True and full_enumeration_verified
    )
    user_requested_scope_complete = bool(retrieval_covers_requested and executed_scope_complete)

    if enumeration.get("verified") is not full_enumeration_verified:
        review.append(
            "screening_audit.scope.enumeration.verified does not match pagination/band evidence"
        )
    if (
        enumeration.get("bands_well_formed") is not None
        and enumeration.get("bands_well_formed") is not bands_well_formed
    ):
        review.append(
            "screening_audit.scope.enumeration.bands_well_formed does not match band evidence"
        )
    declared_cover = enumeration.get("bands_cover_executed_range")
    if declared_cover is None:
        declared_cover = enumeration.get("bands_cover_requested_range")
    if declared_cover is not None and declared_cover is not bands_cover_retrieval:
        review.append(
            "screening_audit.scope.enumeration band-coverage flag does not match evidence"
        )
    if (
        enumeration.get("bands_verified") is not None
        and enumeration.get("bands_verified") is not bands_verified
    ):
        review.append(
            "screening_audit.scope.enumeration.bands_verified does not match band evidence"
        )
    if pages_fetched is not None and pages_fetched <= 0:
        review.append("screening_audit.scope.enumeration.pages_fetched must be positive")
    if not provider_total_consistent:
        review.append("universe rows_fetched is below provider_reported_total")
    if scope.get("executed_scope_complete") is not executed_scope_complete:
        review.append(
            "screening_audit.scope.executed_scope_complete does not match enumeration evidence"
        )
    if scope.get("user_requested_scope_complete") is not user_requested_scope_complete:
        review.append("screening_audit.scope.user_requested_scope_complete does not match evidence")
    if scope.get("scope_complete") is not user_requested_scope_complete:
        review.append(
            "screening_audit.scope.scope_complete must represent full user-requested enumeration"
        )

    universe_section = _mapping(audit.get("universe"))
    candidate_section = _mapping(audit.get("candidate_pool"))
    enrichment = _mapping(audit.get("enrichment"))
    if not _sources_resolve(universe_section.get("source_ids"), source_index):
        review.append("screening_audit.universe.source_ids do not resolve")
    if (_integer(candidate_section.get("row_count")) or 0) > 0 and not _sources_resolve(
        candidate_section.get("source_ids"), source_index
    ):
        review.append("screening_audit.candidate_pool.source_ids do not resolve")

    universe_rows, universe_digest, universe_review = _load_jsonl_artifact(
        universe_section, artifact_root, label="screening_audit.universe"
    )
    candidate_rows, candidate_digest, candidate_review = _load_jsonl_artifact(
        candidate_section, artifact_root, label="screening_audit.candidate_pool"
    )
    review.extend(universe_review)
    review.extend(candidate_review)
    if (
        universe_digest
        and (_text(universe_section.get("artifact_sha256")) or "").lower() != universe_digest
    ):
        review.append("screening_audit.universe.artifact_sha256 does not match")
    if (
        candidate_digest
        and (_text(candidate_section.get("artifact_sha256")) or "").lower() != candidate_digest
    ):
        review.append("screening_audit.candidate_pool.artifact_sha256 does not match")

    universe_symbols: set[str] = set()
    universe_counts: dict[str, int] = {}
    listing_complete = 0
    for position, row in enumerate(universe_rows):
        symbol = (_text(row.get("symbol")) or "").upper()
        status = (_text(_mapping(row.get("listing_decision")).get("status")) or "").lower()
        if not symbol:
            review.append(f"universe audit row {position} has no symbol")
            continue
        if symbol in universe_symbols:
            review.append(f"universe audit contains duplicate symbol {symbol}")
        universe_symbols.add(symbol)
        if status not in ALLOWED_UNIVERSE_AUDIT_DECISIONS:
            review.append(f"universe audit row {symbol} has invalid status {status!r}")
            continue
        universe_counts[status] = universe_counts.get(status, 0) + 1
        listing_complete += int(row.get("listing_data_complete") is True)

    in_scope_universe_symbols = {
        (_text(row.get("symbol")) or "").upper()
        for row in universe_rows
        if (_text(_mapping(row.get("listing_decision")).get("status")) or "").lower()
        in {"in_scope", "liquidity_review"}
    }
    in_scope_universe_symbols.discard("")

    candidate_symbols: set[str] = set()
    candidate_counts: dict[str, int] = {}
    selected_symbols: list[str] = []
    discovery_evaluable = 0
    fundamental_complete = 0
    enrichment_attempted = 0
    enrichment_resolved = 0
    actual_queue_symbols: list[str] = []
    for position, row in enumerate(candidate_rows):
        symbol = (_text(row.get("symbol")) or "").upper()
        decision = _mapping(row.get("decision"))
        status = (_text(decision.get("status")) or "").lower()
        if not symbol:
            review.append(f"candidate-pool row {position} has no symbol")
            continue
        if symbol in candidate_symbols:
            review.append(f"candidate-pool audit contains duplicate symbol {symbol}")
        candidate_symbols.add(symbol)
        if symbol not in universe_symbols:
            review.append(f"candidate-pool symbol {symbol} is not present in the listing universe")
        if status not in ALLOWED_AUDIT_DECISIONS:
            review.append(f"candidate-pool row {symbol} has invalid decision status {status!r}")
            continue
        candidate_counts[status] = candidate_counts.get(status, 0) + 1
        discovery_evaluable += int(row.get("discovery_evaluable") is True)
        fundamental_complete += int(row.get("fundamental_complete") is True)
        enrichment_attempted += int(row.get("enrichment_attempted") is True)
        resolved = (
            row.get("enrichment_resolved") is True or decision.get("resolution") == "resolved"
        )
        enrichment_resolved += int(resolved)
        if not resolved:
            actual_queue_symbols.append(symbol)
        if status == "unavailable_after_enrichment":
            if decision.get("enrichment_exhausted") is not True:
                review.append(f"unavailable candidate {symbol} lacks enrichment_exhausted=true")
            if not _text(decision.get("enrichment_exhaustion_reason")):
                review.append(
                    f"unavailable candidate {symbol} lacks an enrichment exhaustion reason"
                )
            source_ids = decision.get("enrichment_source_ids")
            if not _sources_resolve(source_ids, source_index):
                review.append(
                    f"unavailable candidate {symbol} lacks resolving enrichment source IDs"
                )
        if status == "selected":
            selected_symbols.append(symbol)
            if row.get("discovery_evaluable") is not True:
                review.append(f"selected candidate {symbol} is not discovery-evaluable")
            if _number(row.get("broad_score")) is None:
                review.append(f"selected candidate {symbol} lacks a real broad score")

    if _integer(universe_section.get("row_count")) != len(universe_rows):
        review.append("screening_audit.universe.row_count does not match artifact")
    if _integer(candidate_section.get("row_count")) != len(candidate_rows):
        review.append("screening_audit.candidate_pool.row_count does not match artifact")

    calculated_listing_pct = listing_complete / len(universe_rows) * 100.0 if universe_rows else 0.0
    declared_listing_pct = _number(universe_section.get("listing_data_complete_pct"))
    if declared_listing_pct is None or abs(declared_listing_pct - calculated_listing_pct) > 0.05:
        review.append("screening_audit.universe.listing_data_complete_pct does not match artifact")
    minimum_listing_pct = _number(config.get("minimum_listing_data_coverage_pct")) or 95.0
    if calculated_listing_pct < minimum_listing_pct:
        review.append(
            f"listing-data coverage is {calculated_listing_pct:.1f}%, below the configured {minimum_listing_pct:.1f}%"
        )

    declared_selected = sorted(str(value).upper() for value in _list(audit.get("selected_symbols")))
    if declared_selected != sorted(selected_symbols):
        review.append(
            "screening_audit.selected_symbols does not match selected candidate-pool rows"
        )
    deep_plan = _mapping(audit.get("deep_dive_plan"))
    if sorted(str(value).upper() for value in _list(deep_plan.get("selected_symbols"))) != sorted(
        selected_symbols
    ):
        review.append(
            "screening_audit.deep_dive_plan.selected_symbols does not match selected rows"
        )
    if _integer(deep_plan.get("selected_count")) != len(selected_symbols):
        review.append("screening_audit.deep_dive_plan.selected_count does not match selected rows")
    for key in (
        "all_selected_must_be_resolved",
        "budget_locked",
        "budget_change_requires_rescreen",
    ):
        if deep_plan.get(key) is not True:
            review.append(f"screening_audit.deep_dive_plan.{key} must be true")
    if deep_plan.get("user_confirmation_required") is not False:
        review.append("screening_audit.deep_dive_plan.user_confirmation_required must be false")
    if deep_plan.get("user_continue_instruction_allowed") is not False:
        review.append(
            "screening_audit.deep_dive_plan.user_continue_instruction_allowed must be false"
        )
    if deep_plan.get("selected_set_is_committed") is not True:
        review.append("screening_audit.deep_dive_plan.selected_set_is_committed must be true")
    max_deep_dives = _integer(deep_plan.get("max_deep_dive_candidates"))
    if max_deep_dives != _integer(_mapping(audit.get("filters")).get("max_deep_dive_candidates")):
        review.append("screening_audit.deep_dive_plan.max_deep_dive_candidates must match filters")
    commitment_payload = _mapping(deep_plan.get("commitment_payload"))
    expected_payload = {
        "analysis_as_of": _text(audit.get("analysis_as_of")),
        "max_deep_dive_candidates": max_deep_dives,
        "selected_symbols": sorted(selected_symbols),
    }
    if commitment_payload != expected_payload:
        review.append(
            "screening_audit.deep_dive_plan.commitment_payload does not match selected set"
        )
    expected_commitment_sha = hashlib.sha256(
        json.dumps(expected_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if (_text(deep_plan.get("selected_set_sha256")) or "").lower() != expected_commitment_sha:
        review.append(
            "screening_audit.deep_dive_plan.selected_set_sha256 does not match commitment payload"
        )
    declared_not_in_universe = sorted(
        str(value).upper() for value in _list(candidate_section.get("symbols_not_in_universe"))
    )
    actual_not_in_universe = sorted(candidate_symbols - universe_symbols)
    if declared_not_in_universe != actual_not_in_universe:
        review.append(
            "screening_audit.candidate_pool.symbols_not_in_universe does not match artifacts"
        )

    actual_missing_in_scope = sorted(in_scope_universe_symbols - candidate_symbols)
    actual_listing_coverage_complete = not actual_missing_in_scope
    if _integer(candidate_section.get("in_scope_covered_count")) != len(
        in_scope_universe_symbols & candidate_symbols
    ):
        review.append(
            "screening_audit.candidate_pool.in_scope_covered_count does not match artifacts"
        )
    if _integer(candidate_section.get("in_scope_missing_count")) != len(actual_missing_in_scope):
        review.append(
            "screening_audit.candidate_pool.in_scope_missing_count does not match artifacts"
        )
    declared_missing_in_scope = sorted(
        str(value).upper() for value in _list(candidate_section.get("in_scope_missing_symbols"))
    )
    if declared_missing_in_scope != actual_missing_in_scope:
        review.append(
            "screening_audit.candidate_pool.in_scope_missing_symbols does not match artifacts"
        )
    if candidate_section.get("listing_coverage_complete") is not actual_listing_coverage_complete:
        review.append(
            "screening_audit.candidate_pool.listing_coverage_complete does not match artifacts"
        )

    coverage_scope = (_text(candidate_section.get("coverage_scope")) or "").lower()
    generation_audit = _mapping(candidate_section.get("generation_audit"))
    generation_valid = generation_audit.get("valid") is True
    bounded_sampling_ready = False

    if mode == "liquidity_stratified_estimates":
        expected_generation_runtime = runtime_metadata()
        generation_runtime = _mapping(generation_audit.get("runtime"))
        for key in (
            "skill_name",
            "skill_version",
            "schema_version",
            "contract_revision",
            "runtime_fingerprint",
        ):
            if generation_runtime.get(key) != expected_generation_runtime.get(key):
                generation_valid = False
                review.append(
                    f"candidate-pool generation runtime {key} does not match installed skill"
                )
        if (
            _text(generation_audit.get("selection_method")) or ""
        ).lower() != "sector_market_cap_stratified_validated_liquidity":
            generation_valid = False
            review.append(
                "liquidity-stratified candidate pool must use validated average-liquidity selection"
            )
        liquidity_validation = _mapping(generation_audit.get("liquidity_validation"))
        if liquidity_validation.get("basis_validated") is not True:
            generation_valid = False
            review.append("candidate-pool generation lacks validated average-liquidity evidence")
        minimum_window = _integer(liquidity_validation.get("minimum_window_days"))
        if minimum_window is None or minimum_window < 20:
            generation_valid = False
            review.append(
                "candidate-pool generation average-liquidity window must be at least 20 days"
            )

        generation_scope = _mapping(generation_audit.get("scope"))
        if (
            generation_scope.get("scope_valid") is not True
            or generation_scope.get("scope_reduced") is True
        ):
            generation_valid = False
            review.append(
                "candidate-pool generation may not narrow the user-requested market-cap scope"
            )
        if _number(generation_scope.get("user_requested_min_market_cap")) != requested_min:
            generation_valid = False
            review.append("candidate-pool generation requested lower bound does not match")
        if _number(generation_scope.get("user_requested_max_market_cap")) != requested_max:
            generation_valid = False
            review.append("candidate-pool generation requested upper bound does not match")

        coverage_plan = _mapping(generation_audit.get("coverage_plan"))
        if coverage_plan.get("coverage_plan_valid") is not True:
            generation_valid = False
            review.append("candidate-pool generation coverage_plan_valid must be true")
        if coverage_plan.get("user_requested_range_spanned") is not True:
            generation_valid = False
            review.append("candidate-pool generation does not span the user-requested range")
        if coverage_plan.get("market_cap_buckets_cover_user_requested_range") is not True:
            generation_valid = False
            review.append("candidate-pool generation buckets do not cover the user-requested range")
        if coverage_plan.get("single_band_only") is True:
            generation_valid = False
            review.append("single-band candidate pool cannot represent the requested range")

        invalid_liquidity_symbols: list[str] = []
        for candidate in candidate_rows:
            # screen_universe serializes normalized discovery metrics under
            # candidate["metrics"].  Raw discovery input rows may still carry
            # the fields at top level, so accept either representation without
            # accepting single-session volume.
            liquidity_payload = dict(candidate)
            liquidity_payload.update(_mapping(candidate.get("metrics")))
            evidence = normalize_liquidity(liquidity_payload, minimum_period_days=20)
            if evidence.get("valid_for_screen") is not True:
                invalid_liquidity_symbols.append(
                    (_text(candidate.get("symbol")) or "UNKNOWN").upper()
                )
        if invalid_liquidity_symbols:
            generation_valid = False
            review.append(
                "candidate-pool rows lack valid average-liquidity evidence: "
                + ", ".join(sorted(invalid_liquidity_symbols))
            )

    if mode == "full_universe_fundamentals":
        actual_pool_scope_verified = (
            actual_listing_coverage_complete and user_requested_scope_complete
        )
        expected_scope = "full_listing_universe"
    else:
        actual_pool_scope_verified = generation_valid
        expected_scope = {
            "liquidity_stratified_estimates": "stratified_discovery_pool",
            "provider_prefilter": "provider_prefilter",
            "available_fundamentals": "bounded_available_fundamentals",
            "user_supplied": "user_supplied",
        }.get(mode, "bounded_candidate_pool")
        declared_generation_symbols = sorted(
            str(value).upper() for value in _list(generation_audit.get("actual_selected_symbols"))
        )
        if declared_generation_symbols != sorted(candidate_symbols):
            review.append("candidate-pool generation audit symbols do not match candidate artifact")
        if _integer(generation_audit.get("actual_input_row_count")) != len(universe_rows):
            review.append(
                "candidate-pool generation audit input count does not match listing frame"
            )
        bounded_sampling_ready = bool(
            actual_pool_scope_verified and retrieval_covers_requested and not reduced
        )

    actual_screening_scope_ready = bool(
        user_requested_scope_complete
        or bounded_sampling_ready
        or (reduced and scope.get("scope_override_authorized") is True and executed_scope_complete)
    )
    if scope.get("bounded_sampling_ready") is not bounded_sampling_ready:
        review.append(
            "screening_audit.scope.bounded_sampling_ready does not match generation evidence"
        )
    if scope.get("screening_scope_ready") is not actual_screening_scope_ready:
        review.append("screening_audit.scope.screening_scope_ready does not match evidence")
    if not actual_screening_scope_ready:
        review.append(
            "screening scope is not ready: use full requested enumeration or an audited stratified pool spanning the requested range"
        )

    if coverage_scope != expected_scope:
        review.append(f"screening_audit.candidate_pool.coverage_scope must be {expected_scope!r}")
    if candidate_section.get("coverage_complete") is not actual_pool_scope_verified:
        review.append(
            "screening_audit.candidate_pool.coverage_complete does not match verified pool scope"
        )

    enrichment_status = (_text(enrichment.get("status")) or "").lower()
    if enrichment_status not in {"pending", "complete", "not_required"}:
        review.append("screening_audit.enrichment.status is invalid")
    exhausted = enrichment.get("candidate_pool_exhausted") is True
    declared_exhausted = enrichment.get("candidate_pool_exhaustion_declared") is True
    all_rows_resolved = enrichment_resolved == len(candidate_rows) and not actual_queue_symbols
    pool_ready = (
        enrichment_status in {"complete", "not_required"}
        and exhausted
        and declared_exhausted
        and all_rows_resolved
        and actual_pool_scope_verified
        and actual_screening_scope_ready
    )
    if enrichment.get("candidate_pool_covers_in_scope") is not actual_listing_coverage_complete:
        review.append(
            "screening_audit.enrichment.candidate_pool_covers_in_scope does not match listing artifacts"
        )
    if enrichment.get("candidate_pool_scope_verified") is not actual_pool_scope_verified:
        review.append(
            "screening_audit.enrichment.candidate_pool_scope_verified does not match generation evidence"
        )
    if exhausted and not actual_pool_scope_verified:
        review.append(
            "candidate_pool_exhausted cannot be true before the candidate-pool generation scope is verified"
        )
    if enrichment_status in {"complete", "not_required"} and not pool_ready:
        review.append(
            "candidate-pool enrichment is marked complete before the pool is exhausted and every row is resolved"
        )

    declared_queue = sorted(str(value).upper() for value in _list(enrichment.get("queue_symbols")))
    if declared_queue != sorted(actual_queue_symbols):
        review.append(
            "screening_audit.enrichment.queue_symbols does not match unresolved candidate rows"
        )
    if _integer(enrichment.get("queue_count")) != len(actual_queue_symbols):
        review.append(
            "screening_audit.enrichment.queue_count does not match unresolved candidate rows"
        )
    if _integer(enrichment.get("attempted_count")) != enrichment_attempted:
        review.append("screening_audit.enrichment.attempted_count does not match candidate rows")
    if _integer(enrichment.get("resolved_count")) != enrichment_resolved:
        review.append("screening_audit.enrichment.resolved_count does not match candidate rows")
    if _integer(enrichment.get("unresolved_count")) != len(actual_queue_symbols):
        review.append("screening_audit.enrichment.unresolved_count does not match candidate rows")
    if enrichment.get("all_rows_resolved") is not all_rows_resolved:
        review.append("screening_audit.enrichment.all_rows_resolved does not match candidate rows")
    calculated_resolution_pct = (
        enrichment_resolved / len(candidate_rows) * 100.0 if candidate_rows else 0.0
    )
    declared_resolution_pct = _number(enrichment.get("resolution_pct"))
    if (
        declared_resolution_pct is None
        or abs(declared_resolution_pct - calculated_resolution_pct) > 0.05
    ):
        review.append("screening_audit.enrichment.resolution_pct does not match candidate rows")

    if selected_symbols and pool_ready:
        expected_pool_status = "sufficient"
    elif selected_symbols:
        expected_pool_status = "sufficient_pending_enrichment"
    elif pool_ready and discovery_evaluable > 0:
        expected_pool_status = (
            "no_qualifying_candidates"
            if expected_scope == "full_listing_universe"
            else "no_qualifying_candidates_in_bounded_pool"
        )
    else:
        expected_pool_status = "insufficient_data"
    pool_status = (_text(audit.get("candidate_pool_status")) or "").lower()
    if pool_status != expected_pool_status:
        review.append(
            f"screening_audit.candidate_pool_status must be {expected_pool_status!r} for the audited pool"
        )
    expected_outcome = {
        "sufficient": "selected",
        "sufficient_pending_enrichment": "selected_pending_enrichment",
        "no_qualifying_candidates": "no_candidates",
        "no_qualifying_candidates_in_bounded_pool": "no_candidates_in_bounded_pool",
        "insufficient_data": "insufficient_data",
    }[expected_pool_status]
    outcome = (_text(audit.get("selection_outcome")) or "").lower()
    if outcome != expected_outcome:
        review.append(
            f"screening_audit.selection_outcome must be {expected_outcome!r} for the audited pool"
        )
    if expected_pool_status in {"insufficient_data", "sufficient_pending_enrichment"}:
        warnings.append(
            "candidate pool remains unresolved; continue enrichment/exhaustion verification before publishing a final ranking or no-candidates conclusion"
        )
    if pool_status in {"no_qualifying_candidates", "no_qualifying_candidates_in_bounded_pool"}:
        if (
            not exhausted
            or not declared_exhausted
            or actual_queue_symbols
            or not all_rows_resolved
            or not actual_pool_scope_verified
        ):
            review.append(
                "no-candidates conclusion requires an explicitly exhausted, fully resolved, scope-verified candidate pool"
            )
        if pool_status == "no_qualifying_candidates" and not actual_listing_coverage_complete:
            review.append(
                "market-wide no_qualifying_candidates requires coverage of every in-scope listing"
            )

    universe_count = _integer(funnel.get("universe_count"))
    candidate_pool_count = _integer(funnel.get("candidate_pool_count"))
    if candidate_pool_count is None:
        candidate_pool_count = _integer(funnel.get("broad_screen_count"))
    selected_count = _integer(funnel.get("deep_dive_selected_count"))
    if selected_count is None:
        selected_count = _integer(funnel.get("deep_dive_count"))
    if universe_count != len(universe_rows):
        review.append("screening_funnel.universe_count does not equal universe artifact rows")
    if candidate_pool_count != len(candidate_rows):
        review.append(
            "screening_funnel.candidate_pool_count does not equal candidate artifact rows"
        )
    if selected_count != len(selected_symbols):
        review.append(
            "screening_funnel.deep_dive_selected_count does not equal selected-symbol count"
        )
    if len(universe_rows) < len(candidate_rows) or len(candidate_rows) < len(selected_symbols):
        review.append("screening funnel layer counts are inconsistent")

    fundamental_pct = fundamental_complete / len(candidate_rows) * 100.0 if candidate_rows else 0.0
    discovery_pct = discovery_evaluable / len(candidate_rows) * 100.0 if candidate_rows else 0.0
    if mode != "full_universe_fundamentals":
        warnings.append(
            "tiered candidate-generation mode used; financial coverage applies only to the bounded candidate pool"
        )
    if candidate_rows and fundamental_pct < 50.0:
        warnings.append(
            f"candidate-pool full-fundamental coverage is {fundamental_pct:.1f}%; selected names still require complete primary-source underwriting"
        )

    normalized = deepcopy(audit)
    normalized.update(
        {
            "actual_universe_sha256": universe_digest,
            "actual_candidate_pool_sha256": candidate_digest,
            "actual_candidate_rows": deepcopy(candidate_rows),
            "actual_universe_row_count": len(universe_rows),
            "actual_candidate_pool_row_count": len(candidate_rows),
            "actual_universe_decision_counts": universe_counts,
            "actual_candidate_decision_counts": candidate_counts,
            "actual_selected_symbols": sorted(selected_symbols),
            "actual_listing_data_complete_pct": round(calculated_listing_pct, 4),
            "actual_candidate_pool_discovery_evaluable_pct": round(discovery_pct, 4),
            "actual_candidate_pool_fundamental_complete_pct": round(fundamental_pct, 4),
            "actual_enrichment_attempted_count": enrichment_attempted,
            "actual_enrichment_resolved_count": enrichment_resolved,
            "actual_enrichment_unresolved_count": len(actual_queue_symbols),
            "actual_enrichment_resolution_pct": round(calculated_resolution_pct, 4),
            "actual_enrichment_queue_symbols": sorted(actual_queue_symbols),
            "actual_candidate_pool_exhausted": exhausted,
            "actual_candidate_pool_coverage_complete": actual_pool_scope_verified,
            "actual_listing_coverage_complete": actual_listing_coverage_complete,
            "actual_candidate_pool_coverage_scope": expected_scope,
            "actual_candidate_pool_missing_in_scope_symbols": actual_missing_in_scope,
            "actual_executed_scope_complete": executed_scope_complete,
            "actual_user_requested_scope_complete": user_requested_scope_complete,
            "actual_bounded_sampling_ready": bounded_sampling_ready,
            "actual_screening_scope_ready": actual_screening_scope_ready,
            "screening_completion_ready": pool_ready,
            "valid": not review,
        }
    )
    return normalized, not review, list(dict.fromkeys(warnings)), list(dict.fromkeys(review))


def _derive_growth_state(metrics: Mapping[str, Any]) -> str:
    values = [
        _number(metrics.get("revenue_yoy_pct")),
        _number(metrics.get("gaap_operating_income_yoy_pct")),
        _number(metrics.get("gaap_eps_yoy_pct")),
        _number(metrics.get("adjusted_eps_yoy_pct")),
    ]
    values = [value for value in values if value is not None]
    if len(values) < 2:
        return "insufficient_data"
    if sum(value < 0 for value in values) >= 2:
        return "decelerating_or_contracting"
    if sum(value >= 10 for value in values) >= 2:
        return "accelerating_or_strong"
    return "stable_or_mixed"


def _validate_earnings_record(
    record_raw: Any,
    expected_type: str,
    source_index: Mapping[str, Mapping[str, Any]],
    analysis_as_of: datetime,
    location: str,
) -> tuple[dict[str, Any], datetime | None, list[str], list[str]]:
    record = _mapping(record_raw)
    warnings: list[str] = []
    review: list[str] = []
    period_type = (_text(record.get("period_type")) or "").lower()
    period = _text(record.get("period"))
    if period_type != expected_type:
        review.append(f"{location}.period_type must equal {expected_type!r}")
    if not period:
        review.append(f"{location}.period is required")
    elif "/" in period:
        review.append(f"{location}.period must not combine quarter and full-year labels")
    elif expected_type == "quarter" and not re.search(r"\bQ[1-4]\b", period, re.IGNORECASE):
        review.append(f"{location}.period must identify a fiscal quarter")
    elif expected_type == "full_year" and re.search(r"\bQ[1-4]\b", period, re.IGNORECASE):
        review.append(f"{location}.period must contain only the full-year period")
    try:
        _parse_date(record.get("period_end"), f"{location}.period_end")
    except ContractError as exc:
        review.append(str(exc))
    published = None
    try:
        published = parse_iso8601(
            record.get("published_at"), f"{location}.published_at", required=True
        )
    except ContractError as exc:
        review.append(str(exc))
    if published and published > analysis_as_of:
        review.append(f"{location}.published_at is after analysis_as_of")
    if not _has_primary(record.get("source_ids"), source_index):
        review.append(f"{location}.source_ids must resolve to SEC or company IR evidence")
    metrics = _mapping(record.get("metrics"))
    if _number(metrics.get("revenue")) is None:
        review.append(f"{location}.metrics.revenue is required")
    if (
        _number(metrics.get("gaap_eps")) is None
        and _number(metrics.get("gaap_operating_income")) is None
    ):
        review.append(f"{location} requires GAAP EPS or GAAP operating income")
    if not isinstance(record.get("guidance"), list):
        review.append(f"{location}.guidance must be an array")
    if not isinstance(record.get("key_kpis"), list):
        review.append(f"{location}.key_kpis must be an array")
    if not isinstance(record.get("one_time_items"), list):
        review.append(f"{location}.one_time_items must be an array")

    normalized = deepcopy(record)
    if expected_type == "quarter":
        derived = _derive_growth_state(metrics)
        supplied = (_text(record.get("growth_state")) or "").lower()
        normalized["derived_growth_state"] = derived
        if supplied and derived != "insufficient_data" and supplied != derived:
            review.append(f"{location}.growth_state conflicts with quarter metrics ({derived})")
        elif not supplied:
            normalized["growth_state"] = derived
    return normalized, published, list(dict.fromkeys(warnings)), list(dict.fromkeys(review))


def validate_latest_earnings(
    latest_raw: Any,
    source_index: Mapping[str, Mapping[str, Any]],
    analysis_as_of: datetime,
) -> tuple[dict[str, Any], dict[str, Any], datetime | None, bool, list[str], list[str]]:
    latest = _mapping(latest_raw)
    report_type = (_text(latest.get("latest_report_type")) or "").lower()
    warnings: list[str] = []
    review: list[str] = []
    if report_type not in ALLOWED_REPORT_TYPES:
        review.append("latest_earnings.latest_report_type must be quarterly or annual")

    quarter: dict[str, Any] = {}
    full_year: dict[str, Any] = {}
    published_dates: list[datetime] = []
    if latest.get("quarter") is not None:
        quarter, published, row_warnings, row_review = _validate_earnings_record(
            latest.get("quarter"),
            "quarter",
            source_index,
            analysis_as_of,
            "latest_earnings.quarter",
        )
        warnings.extend(row_warnings)
        review.extend(row_review)
        if published:
            published_dates.append(published)
    if latest.get("full_year") is not None:
        full_year, published, row_warnings, row_review = _validate_earnings_record(
            latest.get("full_year"),
            "full_year",
            source_index,
            analysis_as_of,
            "latest_earnings.full_year",
        )
        warnings.extend(row_warnings)
        review.extend(row_review)
        if published:
            published_dates.append(published)

    if report_type == "quarterly" and not quarter:
        review.append("quarterly latest report requires latest_earnings.quarter")
    if report_type == "annual" and not full_year:
        review.append("annual latest report requires latest_earnings.full_year")
    if not quarter and not full_year:
        review.append("latest_earnings contains no report record")

    primary = quarter if quarter else full_year
    latest_published = max(published_dates) if published_dates else None
    normalized = {
        "latest_report_type": report_type,
        "quarter": quarter or None,
        "full_year": full_year or None,
        "valid": not review,
    }
    return (
        normalized,
        primary,
        latest_published,
        not review,
        list(dict.fromkeys(warnings)),
        list(dict.fromkeys(review)),
    )


def validate_forward_periods(
    candidate: Mapping[str, Any], config: Mapping[str, Any]
) -> tuple[dict[str, bool], list[str], list[str]]:
    valuation = _mapping(candidate.get("valuation_case"))
    periods = _mapping(valuation.get("periods"))
    warnings: list[str] = []
    review: list[str] = []
    rankable: dict[str, bool] = {}
    min_count = _integer(config.get("minimum_analyst_count_for_ranked_horizon")) or 3

    current = _mapping(periods.get("current"))
    current_kind = (_text(current.get("period_kind")) or "").lower()
    if current_kind not in ALLOWED_FORWARD_PERIOD_KINDS:
        review.append("valuation current period must be NTM or FY1; TTM is supplemental only")
    if _number(current.get("metric")) is None or _number(current.get("metric")) <= 0:
        review.append("valuation current forward metric must be positive")
    if not _text(current.get("period_end")):
        review.append("valuation current period_end is required")
    current_count = _integer(current.get("analyst_count"))
    source_type = (_text(current.get("source_type")) or "").lower()
    if source_type in {"market_consensus", "analyst_estimate"} and (current_count or 0) < min_count:
        review.append(
            f"current forward metric requires at least {min_count} analysts or an independent model"
        )

    ranges = {"year_2": (1.5, 2.5), "year_3": (2.5, 3.5)}
    for key, (low, high) in ranges.items():
        row = _mapping(periods.get(key))
        metric = _number(row.get("metric"))
        if metric is None:
            rankable[key] = False
            continue
        kind = (_text(row.get("period_kind")) or "").lower()
        years = _number(row.get("years"))
        if kind not in ALLOWED_FUTURE_PERIOD_KINDS:
            review.append(f"valuation {key} period_kind is invalid")
        if years is None or not (low <= years <= high):
            review.append(f"valuation {key}.years must be between {low} and {high}")
        if not _text(row.get("period_end")):
            review.append(f"valuation {key}.period_end is required")
        count = _integer(row.get("analyst_count"))
        row_source_type = (_text(row.get("source_type")) or "").lower()
        independent = row.get("independent_model") is True
        if (
            row_source_type in {"market_consensus", "analyst_estimate"}
            and not independent
            and (count or 0) < min_count
        ):
            warnings.append(
                f"{key} estimate has only {count or 0} analysts and cannot be the sole ranked horizon"
            )
            rankable[key] = False
        else:
            rankable[key] = True
    if not any(rankable.values()):
        review.append("no adequately supported two- or three-year forecast horizon")
    return rankable, list(dict.fromkeys(warnings)), list(dict.fromkeys(review))


def normalize_cash_classification(
    candidate: dict[str, Any],
    latest: Mapping[str, Any],
) -> tuple[list[str], list[str]]:
    """Normalize ordinary balance-sheet cash into ``corporate_cash``.

    Payment processors and other custodial-cash businesses must provide an
    explicit separation and are never auto-normalized.
    """
    warnings: list[str] = []
    review: list[str] = []
    financials = _mapping(candidate.get("financials"))
    cash = _mapping(financials.get("cash_classification"))
    profile_type = (
        _text(_mapping(candidate.get("sector_profile")).get("type")) or "general"
    ).lower()
    custodial_profiles = {"payments", "broker", "custodian", "exchange"}

    if _number(cash.get("corporate_cash")) is None:
        explicit_cash = _number(cash.get("cash_and_equivalents"))
        primary = (
            _mapping(latest.get("quarter")) or _mapping(latest.get("full_year")) or _mapping(latest)
        )
        metrics = _mapping(primary.get("metrics"))
        reported_cash = _number(metrics.get("cash_and_equivalents"))
        if profile_type in custodial_profiles:
            review.append(
                "custodial/payments business requires explicit corporate_cash separate from customer funds"
            )
        else:
            derived = explicit_cash if explicit_cash is not None else reported_cash
            if derived is not None:
                cash["corporate_cash"] = derived
                cash["classification_method"] = "derived_from_reported_cash_and_equivalents"
                cash["corporate_cash_derived"] = True
                warnings.append("corporate_cash was normalized from reported cash and equivalents")
            else:
                review.append("corporate_cash or reported cash_and_equivalents is required")

    if _number(cash.get("marketable_securities")) is None:
        primary = (
            _mapping(latest.get("quarter")) or _mapping(latest.get("full_year")) or _mapping(latest)
        )
        reported = _number(_mapping(primary.get("metrics")).get("marketable_securities"))
        if reported is not None:
            cash["marketable_securities"] = reported
            cash["marketable_securities_derived"] = True

    financials["cash_classification"] = cash
    candidate["financials"] = financials
    return warnings, review


def validate_cash_consistency(
    candidate: Mapping[str, Any], latest: Mapping[str, Any], config: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, list[str], list[str]]:
    financials = _mapping(candidate.get("financials"))
    cash = _mapping(financials.get("cash_classification"))
    primary = _mapping(latest.get("quarter")) or _mapping(latest.get("full_year"))
    metrics = _mapping(primary.get("metrics"))
    warnings: list[str] = []
    review: list[str] = []
    tolerance = _number(config.get("cash_consistency_tolerance_pct")) or 3.0
    reconciliation_note = _text(cash.get("reconciliation_note"))
    checks: dict[str, Any] = {}

    pairs = {
        "cash_and_equivalents": (
            _number(metrics.get("cash_and_equivalents")),
            _number(cash.get("corporate_cash")),
        ),
        "marketable_securities": (
            _number(metrics.get("marketable_securities")),
            _number(cash.get("marketable_securities")),
        ),
        "total_debt": (_number(metrics.get("total_debt")), _number(financials.get("total_debt"))),
    }
    for key, (reported, normalized) in pairs.items():
        diff = _pct_diff(reported, normalized)
        checks[key] = {
            "earnings_value": reported,
            "normalized_value": normalized,
            "difference_pct": diff,
        }
        if diff is not None and diff > tolerance:
            message = (
                f"{key} differs by {diff:.1f}% between latest earnings and normalized financials"
            )
            if reconciliation_note:
                warnings.append(message + f"; reconciliation: {reconciliation_note}")
            else:
                review.append(message + " without a reconciliation note")

    return (
        {"checks": checks, "reconciliation_note": reconciliation_note},
        not review,
        list(dict.fromkeys(warnings)),
        list(dict.fromkeys(review)),
    )


def validate_and_normalize_snapshot(
    payload_raw: Mapping[str, Any],
    *,
    artifact_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = deepcopy(dict(payload_raw))
    if _integer(payload.get("schema_version")) != SCHEMA_VERSION:
        raise ContractError(f"schema_version must equal {SCHEMA_VERSION}")
    payload_runtime = _mapping(payload.get("runtime"))
    expected_runtime = runtime_metadata()
    runtime_mismatches = [
        key
        for key in (
            "skill_name",
            "skill_version",
            "schema_version",
            "contract_revision",
            "runtime_fingerprint",
        )
        if payload_runtime.get(key) != expected_runtime.get(key)
    ]
    if runtime_mismatches:
        raise ContractError(
            "snapshot runtime does not match the installed skill; stale or cached package detected: "
            + ", ".join(runtime_mismatches)
        )
    analysis_as_of = parse_iso8601(payload.get("analysis_as_of"), "analysis_as_of", required=True)
    assert analysis_as_of is not None
    config = _mapping(payload.get("config"))

    global_index, normalized_global_sources, source_warnings, source_review = (
        validate_source_ledger(_list(payload.get("global_sources")), [], analysis_as_of)
    )
    market_context, market_valid, market_warnings, market_review = validate_market_context(
        payload.get("market_context"), global_index, analysis_as_of, config
    )
    screening_audit, audit_valid, audit_warnings, audit_review = validate_screening_audit(
        payload.get("screening_audit"),
        payload.get("screening_funnel"),
        global_index,
        analysis_as_of,
        artifact_root,
        config,
    )

    global_review = source_review + market_review + audit_review
    global_warnings = source_warnings + market_warnings + audit_warnings
    selected_symbols = set(screening_audit.get("actual_selected_symbols") or [])

    normalized_candidates: list[dict[str, Any]] = []
    candidate_symbols: set[str] = set()
    for raw_candidate in _list(payload.get("candidates")):
        candidate = deepcopy(_mapping(raw_candidate))
        identity = _mapping(candidate.get("identity"))
        symbol = (_text(identity.get("symbol")) or "UNKNOWN").upper()
        transition_aliases = {"recent_spin_off", "transformative_acquisition", "large_divestiture"}
        legacy_special_case = (_text(identity.get("special_case")) or "none").lower()
        transition_review: list[str] = []
        transition_warnings: list[str] = []
        if legacy_special_case in transition_aliases:
            identity["special_case"] = "none"
            candidate["identity"] = identity
            transition = _mapping(candidate.get("corporate_transition"))
            transition.setdefault("type", legacy_special_case)
            transition.setdefault("source_ids", [])
            candidate["corporate_transition"] = transition
            transition_warnings.append(
                f"legacy identity.special_case={legacy_special_case!r} was normalized to corporate_transition.type"
            )
        transition = _mapping(candidate.get("corporate_transition"))
        transition_type = (_text(transition.get("type")) or "none").lower()
        if transition_type != "none":
            source_ids = transition.get("source_ids")
            pro_forma = transition.get("pro_forma_normalization")
            if not _sources_resolve(
                source_ids,
                global_index
                | {
                    str(_mapping(src).get("id")): _mapping(src)
                    for src in _list(candidate.get("sources"))
                    if _text(_mapping(src).get("id"))
                },
            ):
                transition_review.append("corporate transition lacks resolving source evidence")
            if transition_type in {
                "recent_spin_off",
                "transformative_acquisition",
            } and not isinstance(pro_forma, Mapping):
                transition_review.append(
                    "recent spin-off/acquisition requires a sourced pro-forma normalization"
                )
        candidate_symbols.add(symbol)
        source_index, normalized_sources, candidate_source_warnings, candidate_source_review = (
            validate_source_ledger(
                normalized_global_sources, _list(candidate.get("sources")), analysis_as_of
            )
        )
        latest, primary, latest_published, latest_valid, latest_warnings, latest_review = (
            validate_latest_earnings(candidate.get("latest_earnings"), source_index, analysis_as_of)
            if (_text(_mapping(candidate.get("screening_decision")).get("status")) or "passed")
            != "screened_out"
            else ({}, {}, None, True, [], [])
        )
        rankable_horizons, forward_warnings, forward_review = (
            validate_forward_periods(candidate, config) if primary else ({}, [], [])
        )
        cash_normalization_warnings, cash_normalization_review = (
            normalize_cash_classification(candidate, latest) if primary else ([], [])
        )
        cash_consistency, cash_valid, cash_warnings, cash_review = (
            validate_cash_consistency(candidate, latest, config) if primary else ({}, True, [], [])
        )

        review_reasons = list(
            dict.fromkeys(
                global_review
                + candidate_source_review
                + latest_review
                + forward_review
                + cash_normalization_review
                + cash_review
                + transition_review
            )
        )
        warnings = list(
            dict.fromkeys(
                global_warnings
                + candidate_source_warnings
                + latest_warnings
                + forward_warnings
                + cash_normalization_warnings
                + cash_warnings
                + transition_warnings
            )
        )
        quality_caps: list[dict[str, Any]] = []
        if not market_valid:
            quality_caps.append({"cap": 70, "reason": "market context is incomplete or invalid"})
        if not audit_valid:
            quality_caps.append(
                {"cap": 65, "reason": "broad-screen audit is incomplete or unverified"}
            )
        if candidate_source_review or source_review:
            quality_caps.append(
                {"cap": 60, "reason": "source ledger schema or classification is invalid"}
            )
        if not latest_valid and primary:
            quality_caps.append(
                {"cap": 55, "reason": "latest earnings periods are incomplete or mixed"}
            )
        if forward_review and primary:
            quality_caps.append({"cap": 60, "reason": "forward valuation basis is incomplete"})
        if not cash_valid and primary:
            quality_caps.append({"cap": 70, "reason": "cash/debt definitions are inconsistent"})
        if transition_review:
            quality_caps.append(
                {"cap": 65, "reason": "corporate transition/pro-forma evidence is incomplete"}
            )

        candidate["sources"] = normalized_sources
        candidate["latest_earnings_records"] = latest
        candidate["latest_earnings"] = primary
        periods = _mapping(_mapping(candidate.get("valuation_case")).get("periods"))
        for key, rankable in rankable_horizons.items():
            row = _mapping(periods.get(key))
            row["rankable"] = rankable
            periods[key] = row
        if periods:
            candidate.setdefault("valuation_case", {})["periods"] = periods
        candidate["_contract"] = {
            "review_reasons": review_reasons,
            "warnings": warnings,
            "quality_caps": quality_caps,
            "source_schema_valid": not candidate_source_review and not source_review,
            "latest_earnings_valid": latest_valid,
            "latest_published_at": latest_published.isoformat() if latest_published else None,
            "forward_basis_valid": not forward_review,
            "rankable_horizons": rankable_horizons,
            "cash_consistency_valid": cash_valid,
            "cash_consistency": cash_consistency,
            "global_contract_valid": not global_review,
        }
        normalized_candidates.append(candidate)

    run_metadata = _mapping(payload.get("run_metadata"))
    declared_status = (_text(run_metadata.get("status")) or "partial").lower()
    unprocessed = {
        str(value).upper() for value in _list(run_metadata.get("unprocessed_candidates"))
    }
    missing_selected = sorted(selected_symbols - candidate_symbols)
    unexpected_unprocessed = sorted(unprocessed - selected_symbols)
    selection_outcome = (_text(screening_audit.get("selection_outcome")) or "").lower()
    candidate_pool_status = (_text(screening_audit.get("candidate_pool_status")) or "").lower()
    no_qualified = candidate_pool_status in {
        "no_qualifying_candidates",
        "no_qualifying_candidates_in_bounded_pool",
    }
    completion_ready = (
        screening_audit.get("valid") is True
        and screening_audit.get("screening_completion_ready") is True
        and candidate_pool_status
        in {"sufficient", "no_qualifying_candidates", "no_qualifying_candidates_in_bounded_pool"}
    )
    if missing_selected:
        global_review.append(
            "selected broad-screen symbols are missing candidate records: "
            + ", ".join(missing_selected)
        )
    if unexpected_unprocessed:
        global_review.append(
            "unprocessed_candidates contains symbols that were not selected: "
            + ", ".join(unexpected_unprocessed)
        )
    if declared_status == "complete" and unprocessed:
        global_review.append("run is marked complete but unprocessed_candidates is not empty")
    if declared_status == "complete" and missing_selected:
        global_review.append(
            "run is marked complete but not all selected symbols were underwritten"
        )
    if declared_status == "complete" and not completion_ready:
        global_review.append(
            "run is marked complete before the staged screening contract is completion-ready"
        )
    if declared_status == "complete" and candidate_pool_status in {
        "insufficient_data",
        "sufficient_pending_enrichment",
    }:
        global_review.append("run is marked complete while the candidate pool is unresolved")
    if declared_status == "complete" and not selected_symbols and not no_qualified:
        global_review.append(
            "complete run with no selected symbols requires a scope-qualified no-candidates status"
        )

    payload["global_sources"] = normalized_global_sources
    payload["market_context"] = market_context
    payload["screening_audit"] = screening_audit
    payload["candidates"] = normalized_candidates
    contract = {
        "runtime": runtime_metadata(),
        "valid": not global_review,
        "market_context_valid": market_valid,
        "screening_audit_valid": audit_valid,
        "source_schema_valid": not source_review,
        "selected_symbols": sorted(selected_symbols),
        "missing_selected_symbols": missing_selected,
        "selection_outcome": selection_outcome,
        "candidate_pool_status": candidate_pool_status,
        "screening_completion_ready": completion_ready,
        "no_qualified_candidates": no_qualified,
        "review_reasons": list(dict.fromkeys(global_review)),
        "warnings": list(dict.fromkeys(global_warnings)),
    }
    payload["_contract"] = contract
    return payload, contract
