#!/usr/bin/env python3
"""Look up multilingual Wikidata item labels for a small batch of terms."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import time
import zlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_ENDPOINT = "https://www.wikidata.org/w/api.php"
USER_AGENT = (
    "AcademicTranslationSkills/4.0.0 "
    "(https://github.com/Koloyaaa/academic-translation-skills/issues)"
)
MAX_TERMS = 10
MAX_RESULTS = 5
MAX_RESPONSE_BYTES = 2_000_000
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}


class LookupError(Exception):
    """An expected API or network failure safe to report to the calling Skill."""


def _retry_delay(headers, attempt: int) -> float:
    value = headers.get("Retry-After", "") if headers else ""
    try:
        return min(10.0, max(0.5, float(value)))
    except (TypeError, ValueError):
        if value:
            try:
                retry_at = parsedate_to_datetime(value)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                return min(10.0, max(0.5, (retry_at - datetime.now(timezone.utc)).total_seconds()))
            except (TypeError, ValueError, OverflowError):
                pass
    return min(4.0, 0.5 * (attempt + 1))


def _request_json(params: dict[str, str], timeout: float) -> dict:
    url = f"{API_ENDPOINT}?{urlencode(params)}"
    for attempt in range(3):
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = response.read(MAX_RESPONSE_BYTES + 1)
                content_encoding = response.headers.get("Content-Encoding", "").lower()
            try:
                if content_encoding == "gzip":
                    payload = gzip.decompress(payload)
                elif content_encoding == "deflate":
                    payload = zlib.decompress(payload)
            except (OSError, zlib.error) as error:
                raise LookupError("Wikidata returned invalid compressed data.") from error
            if len(payload) > MAX_RESPONSE_BYTES:
                raise LookupError("Wikidata returned an unexpectedly large response.")
            result = json.loads(payload.decode("utf-8"))
            if not isinstance(result, dict):
                raise LookupError("Wikidata returned an invalid JSON response.")
            if "error" in result:
                error = result.get("error") or {}
                raise LookupError(f"Wikidata API error: {error.get('code', 'unknown')}.")
            return result
        except HTTPError as error:
            if error.code in TRANSIENT_HTTP_CODES and attempt < 2:
                time.sleep(_retry_delay(error.headers, attempt))
                continue
            raise LookupError(f"Wikidata returned HTTP {error.code}.") from error
        except (URLError, TimeoutError, OSError) as error:
            if attempt < 2:
                time.sleep(_retry_delay({}, attempt))
                continue
            reason = getattr(error, "reason", None)
            detail = type(reason).__name__ if reason is not None else type(error).__name__
            raise LookupError(f"Could not reach Wikidata ({detail}).") from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise LookupError("Wikidata returned invalid JSON.") from error
    raise LookupError("Wikidata lookup failed after retries.")


def _target_languages(language: str) -> list[str]:
    normalized = language.strip().lower().replace("_", "-")
    if normalized.startswith("zh"):
        return list(dict.fromkeys([normalized, "zh-cn", "zh-hans", "zh", "zh-sg"]))
    return [normalized]


def _search_term(term: str, source_language: str, limit: int, timeout: float) -> dict:
    try:
        payload = _request_json(
            {
                "action": "wbsearchentities",
                "format": "json",
                "formatversion": "2",
                "search": term,
                "language": source_language,
                "uselang": source_language,
                "type": "item",
                "limit": str(limit),
                "maxlag": "5",
            },
            timeout,
        )
    except LookupError as error:
        return {"term": term, "status": "UNAVAILABLE", "message": str(error), "candidates": []}

    candidates = []
    for item in payload.get("search", []):
        if not isinstance(item, dict) or not item.get("id"):
            continue
        match = item.get("match") if isinstance(item.get("match"), dict) else {}
        candidates.append(
            {
                "id": item["id"],
                "source_label": item.get("label", ""),
                "source_description": item.get("description", ""),
                "matched_text": match.get("text", ""),
                "match_type": match.get("type", ""),
                "url": f"https://www.wikidata.org/wiki/{item['id']}",
            }
        )
    return {
        "term": term,
        "status": "OK" if candidates else "NOT_FOUND",
        "candidates": candidates,
    }


def _attach_target_labels(results: list[dict], target_language: str, timeout: float) -> None:
    ids = list(
        dict.fromkeys(
            candidate["id"]
            for result in results
            for candidate in result.get("candidates", [])
        )
    )
    if not ids:
        return

    try:
        payload = _request_json(
            {
                "action": "wbgetentities",
                "format": "json",
                "formatversion": "2",
                "ids": "|".join(ids),
                "props": "labels|descriptions|aliases",
                "languages": "|".join(_target_languages(target_language)),
                "maxlag": "5",
            },
            timeout,
        )
    except LookupError as error:
        for result in results:
            if result.get("candidates"):
                result["target_labels_status"] = "UNAVAILABLE"
                result["target_labels_message"] = str(error)
        return

    entities = payload.get("entities", [])
    if isinstance(entities, dict):
        entity_map = entities
    else:
        entity_map = {entity.get("id"): entity for entity in entities if isinstance(entity, dict)}

    languages = _target_languages(target_language)
    for result in results:
        for candidate in result.get("candidates", []):
            entity = entity_map.get(candidate["id"], {})
            labels = entity.get("labels", {}) if isinstance(entity, dict) else {}
            descriptions = entity.get("descriptions", {}) if isinstance(entity, dict) else {}
            aliases = entity.get("aliases", {}) if isinstance(entity, dict) else {}
            for language in languages:
                label = labels.get(language, {}).get("value")
                if label:
                    candidate["target_label"] = label
                    candidate["target_label_language"] = language
                    candidate["target_description"] = descriptions.get(language, {}).get("value", "")
                    candidate["target_aliases"] = [
                        alias.get("value", "") for alias in aliases.get(language, []) if alias.get("value")
                    ][:5]
                    break
            if "target_label" not in candidate:
                candidate["target_label"] = None
                candidate["target_label_language"] = None
                candidate["target_description"] = ""
                candidate["target_aliases"] = []


def lookup(terms: list[str], source_language: str, target_language: str, limit: int, timeout: float) -> dict:
    unique_terms = []
    seen = set()
    for term in terms:
        normalized = term.strip()
        key = normalized.casefold()
        if normalized and key not in seen:
            unique_terms.append(normalized)
            seen.add(key)

    results = []
    rate_limited = False
    for index, term in enumerate(unique_terms):
        if index:
            time.sleep(0.4)
        result = _search_term(term, source_language, limit, timeout)
        results.append(result)
        if result.get("status") == "UNAVAILABLE" and "HTTP 429" in result.get("message", ""):
            rate_limited = True
            for remaining_term in unique_terms[index + 1 :]:
                results.append(
                    {
                        "term": remaining_term,
                        "status": "UNAVAILABLE",
                        "message": "Wikidata rate-limited the lookup; this term was not sent.",
                        "candidates": [],
                    }
                )
            break
    if not rate_limited:
        _attach_target_labels(results, target_language, timeout)

    return {
        "source": "Wikidata",
        "api": API_ENDPOINT,
        "data_license": "CC0 1.0",
        "source_language": source_language,
        "target_language": target_language,
        "results": results,
        "usage_note": (
            "Candidates are community-maintained knowledge-base entries, not authoritative subject dictionaries. "
            "Choose only a contextually suitable match; use contextual translation if results are ambiguous, "
            "lack a target-language label, or are unavailable."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Look up a few source-language terms in Wikidata and return target-language labels."
    )
    parser.add_argument("terms", nargs="+", help="one or more individual terms or short phrases")
    parser.add_argument("--source-language", required=True, help="Wikidata language code, such as en or fr")
    parser.add_argument("--target-language", default="zh-cn", help="target label language (default: zh-cn)")
    parser.add_argument("--limit", type=int, default=5, help="candidate limit per term (1-5)")
    parser.add_argument("--timeout", type=float, default=10.0, help="request timeout in seconds")
    args = parser.parse_args()

    distinct_terms = {term.strip().casefold() for term in args.terms if term.strip()}
    if not distinct_terms:
        parser.error("Provide at least one non-empty term or short phrase.")
    if len(distinct_terms) > MAX_TERMS:
        parser.error(f"Use at most {MAX_TERMS} distinct terms per call.")
    language_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9-]{1,15}$")
    if not language_pattern.fullmatch(args.source_language) or not language_pattern.fullmatch(args.target_language):
        parser.error("Language values must be Wikidata language codes, such as en, fr, or zh-cn.")
    if not 1 <= args.limit <= MAX_RESULTS:
        parser.error(f"--limit must be between 1 and {MAX_RESULTS}.")
    if not 0.5 <= args.timeout <= 60:
        parser.error("--timeout must be between 0.5 and 60 seconds.")

    result = lookup(args.terms, args.source_language, args.target_language, args.limit, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
