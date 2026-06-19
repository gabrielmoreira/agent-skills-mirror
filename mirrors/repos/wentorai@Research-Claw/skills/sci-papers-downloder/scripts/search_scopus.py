#!/usr/bin/env python3
"""Search Scopus and return paper entries with DOI/title metadata."""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

SCOPUS_SEARCH_URL = "https://api.elsevier.com/content/search/scopus"

# Plaintext default Elsevier key for self-use. Rotated periodically; override via
# --api-key or ELSEVIER_API_KEY env when a different key is needed.
DEFAULT_ELSEVIER_API_KEY = "1a86a22a0f4dac7995ff6185cba431c2"


def resolve_api_key(explicit: Optional[str]) -> str:
    return explicit or os.environ.get("ELSEVIER_API_KEY") or DEFAULT_ELSEVIER_API_KEY


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search Scopus by keywords, DOI, title, or raw query."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keywords", help="Topic keywords for TITLE-ABS-KEY query")
    mode.add_argument("--doi", help="Exact DOI lookup")
    mode.add_argument("--title", help="Exact title lookup")
    mode.add_argument("--query", help="Raw Scopus query string")

    parser.add_argument("--api-key", help="Elsevier API key. Defaults to ELSEVIER_API_KEY env, then a built-in self-use key")
    parser.add_argument("--count", type=int, default=20, help="Max entries to fetch (default: 20)")
    parser.add_argument(
        "--sort",
        default="-citedby-count",
        help="Scopus sort expression, e.g. -citedby-count or -coverDate",
    )
    parser.add_argument("--start", type=int, default=0, help="Result offset (default: 0)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--out", help="Optional output file path (used with --json)")

    return parser.parse_args()


def build_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query
    if args.doi:
        return f"DOI({quote_term(args.doi)})"
    if args.title:
        return f"TITLE(\"{escape_quotes(args.title)}\")"
    # keywords mode
    return f"TITLE-ABS-KEY(\"{escape_quotes(args.keywords)}\")"


def quote_term(term: str) -> str:
    # Scopus query grammar supports quoted literals; quote when spaces exist.
    if any(ch.isspace() for ch in term):
        return f'"{escape_quotes(term)}"'
    return term


def escape_quotes(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def scopus_request(api_key: str, query: str, count: int, start: int, sort: str) -> Dict[str, Any]:
    params = urllib.parse.urlencode(
        {
            "query": query,
            "count": count,
            "start": start,
            "sort": sort,
        }
    )
    url = f"{SCOPUS_SEARCH_URL}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "X-ELS-APIKey": api_key,
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Scopus API error HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc}") from exc


def extract_entries(raw: Dict[str, Any]) -> Dict[str, Any]:
    results = raw.get("search-results", {})
    total = int(results.get("opensearch:totalResults", "0") or "0")
    entries_raw = results.get("entry") or []

    entries: List[Dict[str, Any]] = []
    for item in entries_raw:
        entry = {
            "title": item.get("dc:title") or "",
            "doi": item.get("prism:doi") or "N/A",
            "year": (item.get("prism:coverDate") or "")[:4] or "N/A",
            "source": item.get("prism:publicationName") or "",
            "cited_by": safe_int(item.get("citedby-count")),
            "authors": item.get("dc:creator") or "",
            "eid": item.get("eid") or "",
        }
        entries.append(entry)

    return {
        "total": total,
        "entries": entries,
    }


def safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def print_text(query: str, payload: Dict[str, Any]) -> None:
    print(f"Query: {query}")
    print(f"Total hits: {payload['total']}")
    print()
    for idx, e in enumerate(payload["entries"], 1):
        print(f"{idx}. {e['title']}")
        print(f"   DOI: {e['doi']}")
        print(f"   Year: {e['year']}")
        print(f"   Source: {e['source']}")
        print(f"   Cited by: {e['cited_by']}")


def main() -> int:
    args = parse_args()

    api_key = resolve_api_key(args.api_key)

    query = build_query(args)

    try:
        raw = scopus_request(api_key=api_key, query=query, count=args.count, start=args.start, sort=args.sort)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parsed = extract_entries(raw)
    output = {
        "query": query,
        "total": parsed["total"],
        "count": len(parsed["entries"]),
        "entries": parsed["entries"],
    }

    if args.json:
        text = json.dumps(output, ensure_ascii=False, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(text)
            print(args.out)
        else:
            print(text)
    else:
        print_text(query, parsed)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
