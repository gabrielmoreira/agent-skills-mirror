#!/usr/bin/env python3
"""Search OpenAlex (no API key) and return paper entries with DOI/title/OA metadata.

OpenAlex is a free, open scholarly index (~250M works) that needs no API key.
Providing a contact email joins the faster "polite pool". This is a drop-in
no-key replacement for the Scopus search half of the pipeline; output entries are
shape-compatible with search_scopus.extract_entries (title/doi/year/source/cited_by)
plus an oa_url hint that downstream downloaders can try directly.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

OPENALEX_WORKS_URL = "https://api.openalex.org/works"
SELECT_FIELDS = (
    "id,doi,title,publication_year,cited_by_count,open_access,best_oa_location,primary_location"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search OpenAlex by keywords, title, or raw filter (no API key required)."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keywords", help="Full-text search terms")
    mode.add_argument("--title", help="Title search")
    mode.add_argument("--query", help="Raw OpenAlex filter expression, e.g. 'title.search:x,is_oa:true'")

    parser.add_argument("--email", help="Contact email for OpenAlex polite pool. Defaults to UNPAYWALL_EMAIL/OPENALEX_EMAIL env")
    parser.add_argument("--count", type=int, default=20, help="Max entries to fetch (default: 20)")
    parser.add_argument("--per-page", type=int, default=25, help="Page size per API call (max 200)")
    parser.add_argument("--from-year", type=int, help="Lower publication year bound (inclusive)")
    parser.add_argument("--oa-only", action="store_true", help="Restrict to open-access works")
    parser.add_argument(
        "--sort",
        default="cited_by_count:desc",
        help="OpenAlex sort, e.g. cited_by_count:desc or publication_date:desc",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--out", help="Optional output file path (used with --json)")
    return parser.parse_args()


def resolve_email(explicit: Optional[str]) -> Optional[str]:
    return explicit or os.environ.get("OPENALEX_EMAIL") or os.environ.get("UNPAYWALL_EMAIL")


def build_filters(args: argparse.Namespace) -> List[str]:
    filters: List[str] = []
    if args.query:
        filters.append(args.query)
    elif args.title:
        filters.append(f"title.search:{args.title}")
    if args.from_year and args.from_year > 0:
        filters.append(f"from_publication_date:{args.from_year}-01-01")
    if args.oa_only:
        filters.append("is_oa:true")
    return filters


def openalex_request(
    search: Optional[str],
    filters: List[str],
    sort: str,
    per_page: int,
    page: int,
    email: Optional[str],
) -> Dict[str, Any]:
    params: Dict[str, str] = {
        "select": SELECT_FIELDS,
        "per-page": str(max(1, min(200, per_page))),
        "page": str(max(1, page)),
        "sort": sort,
    }
    if search:
        params["search"] = search
    if filters:
        params["filter"] = ",".join(filters)
    if email:
        params["mailto"] = email

    url = f"{OPENALEX_WORKS_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "Accept": "application/json",
        "User-Agent": f"sci-papers-downloder/2.0 (mailto:{email})" if email else "sci-papers-downloder/2.0",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"OpenAlex API error HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc}") from exc


def normalize_doi(doi_url: Optional[str]) -> str:
    if not doi_url:
        return "N/A"
    doi = doi_url.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi or "N/A"


def best_oa_url(work: Dict[str, Any]) -> Optional[str]:
    best = work.get("best_oa_location") or {}
    url = best.get("pdf_url") or best.get("landing_page_url")
    if url:
        return url
    return (work.get("open_access") or {}).get("oa_url")


def source_name(work: Dict[str, Any]) -> str:
    primary = work.get("primary_location") or {}
    src = primary.get("source") or {}
    return src.get("display_name") or ""


def extract_entries(raw: Dict[str, Any]) -> Dict[str, Any]:
    total = int((raw.get("meta") or {}).get("count") or 0)
    entries: List[Dict[str, Any]] = []
    for work in raw.get("results") or []:
        entries.append(
            {
                "title": work.get("title") or "",
                "doi": normalize_doi(work.get("doi")),
                "year": str(work.get("publication_year") or "N/A"),
                "source": source_name(work),
                "cited_by": int(work.get("cited_by_count") or 0),
                "is_oa": bool((work.get("open_access") or {}).get("is_oa")),
                "oa_url": best_oa_url(work),
            }
        )
    return {"total": total, "entries": entries}


def search_paged(
    search: Optional[str],
    filters: List[str],
    sort: str,
    per_page: int,
    count: int,
    email: Optional[str],
) -> Dict[str, Any]:
    """Collect up to `count` entries, paging as needed."""
    collected: List[Dict[str, Any]] = []
    total = 0
    page = 1
    while len(collected) < count:
        want = min(per_page, count - len(collected))
        raw = openalex_request(search, filters, sort, want, page, email)
        parsed = extract_entries(raw)
        total = parsed["total"]
        batch = parsed["entries"]
        if not batch:
            break
        collected.extend(batch)
        if len(collected) >= total:
            break
        page += 1
    return {"total": total, "entries": collected[:count]}


def print_text(payload: Dict[str, Any]) -> None:
    print(f"Total hits: {payload['total']}")
    print()
    for idx, e in enumerate(payload["entries"], 1):
        print(f"{idx}. {e['title']}")
        print(f"   DOI: {e['doi']}")
        print(f"   Year: {e['year']} | Cited by: {e['cited_by']} | OA: {e['is_oa']}")
        print(f"   Source: {e['source']}")
        print(f"   OA URL: {e['oa_url'] or 'N/A'}")


def main() -> int:
    args = parse_args()
    email = resolve_email(args.email)
    search = args.keywords if args.keywords else None
    filters = build_filters(args)

    try:
        payload = search_paged(
            search=search,
            filters=filters,
            sort=args.sort,
            per_page=args.per_page,
            count=args.count,
            email=email,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = {
        "search": search,
        "filters": filters,
        "sort": args.sort,
        "total": payload["total"],
        "count": len(payload["entries"]),
        "entries": payload["entries"],
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
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
