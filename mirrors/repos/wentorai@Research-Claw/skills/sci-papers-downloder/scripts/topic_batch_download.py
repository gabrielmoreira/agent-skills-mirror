#!/usr/bin/env python3
"""Search Scopus by topic and download papers with quantity/freshness strategy."""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from download_open_access import (  # noqa: E402
    FallbackConfig,
    process_doi,
    resolve_scihub_command,
)
from search_scopus import extract_entries, resolve_api_key, scopus_request  # noqa: E402


@dataclass
class QuantityPlan:
    mode: str
    target_downloads: Optional[int]
    search_cap: int
    attempt_cap: int
    success_cap: Optional[int]


@dataclass
class QueryPlan:
    query: str
    sort: str
    latest_mode: bool
    from_year: Optional[int]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search Scopus and download papers with quantity-aware defaults. "
            "Supports intents like few/batch/max and latest/recent papers."
        )
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keywords", help="Topic keywords for TITLE-ABS-KEY query")
    mode.add_argument("--title", help="Exact title lookup")
    mode.add_argument("--query", help="Raw Scopus query string")

    parser.add_argument("--api-key", help="Elsevier API key. Defaults to ELSEVIER_API_KEY env, then a built-in self-use key")
    parser.add_argument("--email", help="Unpaywall email. Defaults to UNPAYWALL_EMAIL env")

    parser.add_argument(
        "--quantity-mode",
        choices=["few", "batch", "max"],
        default="batch",
        help="few=~5 papers; batch=~20 papers; max=as many as possible under caps",
    )
    parser.add_argument(
        "--target",
        type=int,
        help="Explicit target download count; overrides quantity-mode target",
    )
    parser.add_argument(
        "--max-search-results",
        type=int,
        help="Max Scopus entries to scan; overrides mode default",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        help="Max DOI download attempts; overrides mode default",
    )
    parser.add_argument(
        "--max-success",
        type=int,
        help="Hard cap on successful downloads (useful in max mode)",
    )

    parser.add_argument(
        "--latest",
        action="store_true",
        help="Prefer latest papers: add year filter and default sort by cover date",
    )
    parser.add_argument(
        "--years-back",
        type=int,
        default=3,
        help="When --latest is set, keep papers from last N years (default: 3)",
    )
    parser.add_argument(
        "--from-year",
        type=int,
        help="Explicit lower year bound (inclusive), e.g. 2023",
    )

    parser.add_argument("--page-size", type=int, default=25, help="Scopus page size per API call")
    parser.add_argument(
        "--sort",
        help=(
            "Scopus sort expression. Default is -coverDate for latest mode, "
            "otherwise -citedby-count"
        ),
    )
    parser.add_argument("--timeout", type=int, default=45, help="HTTP timeout seconds")
    parser.add_argument("--outdir", default="./downloads", help="Output directory")

    parser.add_argument(
        "--scihub-fallback",
        choices=["off", "auto", "force"],
        default="auto",
        help="Fallback mode for failed/non-OA DOI downloads",
    )
    parser.add_argument("--scihub-cmd", help="Optional override command for scihub-cli")
    parser.add_argument("--scihub-timeout", type=int, default=180, help="Fallback timeout seconds")

    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument("--out", help="Write JSON summary to file path")
    return parser.parse_args()


def build_base_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query
    if args.title:
        safe_title = args.title.replace("\\", "\\\\").replace('"', '\\"')
        return f'TITLE("{safe_title}")'
    safe_kw = (args.keywords or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'TITLE-ABS-KEY("{safe_kw}")'


def resolve_from_year(args: argparse.Namespace) -> Optional[int]:
    if args.from_year and args.from_year > 0:
        return args.from_year
    if args.latest:
        years_back = max(1, args.years_back)
        current_year = date.today().year
        return current_year - years_back + 1
    return None


def build_query_plan(args: argparse.Namespace) -> QueryPlan:
    base_query = build_base_query(args)
    from_year = resolve_from_year(args)

    query = base_query
    latest_mode = bool(args.latest or from_year is not None)
    if from_year is not None:
        # Scopus commonly uses PUBYEAR comparisons. This form is inclusive for from_year.
        query = f"({base_query}) AND PUBYEAR > {from_year - 1}"

    sort = args.sort or ("-coverDate" if latest_mode else "-citedby-count")
    return QueryPlan(query=query, sort=sort, latest_mode=latest_mode, from_year=from_year)


def decide_plan(args: argparse.Namespace) -> QuantityPlan:
    if args.quantity_mode == "few":
        target_downloads = 5
        search_cap = 30
        attempt_cap = 20
        success_cap = 5
    elif args.quantity_mode == "batch":
        target_downloads = 20
        search_cap = 120
        attempt_cap = 80
        success_cap = 20
    else:
        target_downloads = None
        search_cap = 300
        attempt_cap = 300
        success_cap = 100

    if args.target and args.target > 0:
        target_downloads = args.target
        search_cap = min(max(30, args.target * 4), 600)
        attempt_cap = min(max(20, args.target * 3), 500)
        success_cap = args.target

    if args.max_search_results and args.max_search_results > 0:
        search_cap = args.max_search_results
    if args.max_attempts and args.max_attempts > 0:
        attempt_cap = args.max_attempts
    if args.max_success and args.max_success > 0:
        success_cap = args.max_success

    return QuantityPlan(
        mode=args.quantity_mode,
        target_downloads=target_downloads,
        search_cap=max(1, search_cap),
        attempt_cap=max(1, attempt_cap),
        success_cap=success_cap,
    )


def collect_candidate_entries(
    api_key: str,
    query: str,
    page_size: int,
    sort: str,
    plan: QuantityPlan,
) -> Dict[str, Any]:
    start = 0
    total_hits: Optional[int] = None
    candidates: List[Dict[str, Any]] = []
    seen_dois = set()
    missing_doi = 0

    while start < plan.search_cap and len(candidates) < plan.attempt_cap:
        count = min(max(1, page_size), plan.search_cap - start)
        raw = scopus_request(api_key=api_key, query=query, count=count, start=start, sort=sort)
        parsed = extract_entries(raw)

        if total_hits is None:
            total_hits = parsed["total"]

        entries = parsed["entries"]
        if not entries:
            break

        for entry in entries:
            doi = (entry.get("doi") or "").strip()
            if not doi or doi.upper() == "N/A":
                missing_doi += 1
                continue
            if doi in seen_dois:
                continue
            seen_dois.add(doi)
            candidates.append(entry)
            if len(candidates) >= plan.attempt_cap:
                break

        start += len(entries)
        if total_hits is not None and start >= total_hits:
            break

    return {
        "total_hits": total_hits or 0,
        "scanned": start,
        "missing_doi": missing_doi,
        "candidates": candidates,
    }


def print_text_summary(summary: Dict[str, Any]) -> None:
    print(f"Query: {summary['query']}")
    print(f"Sort: {summary['sort']}")
    print(f"Latest mode: {summary['latest_mode']}")
    print(f"From year: {summary['from_year'] if summary['from_year'] is not None else 'N/A'}")
    print(f"Quantity mode: {summary['quantity_mode']}")
    print(
        "Target downloads: "
        f"{summary['target_downloads'] if summary['target_downloads'] is not None else 'unbounded'}"
    )
    print(f"Search cap: {summary['search_cap']} | Attempt cap: {summary['attempt_cap']}")
    print(f"Scopus total hits: {summary['scopus_total_hits']}")
    print(f"Scopus scanned entries: {summary['scopus_scanned_entries']}")
    print(
        f"Candidates with DOI: {summary['candidate_count']} | "
        f"Missing DOI in scanned: {summary['missing_doi_count']}"
    )
    print(f"Downloaded: {summary['downloaded_count']} / Attempted: {summary['attempted_count']}")
    print()

    for idx, item in enumerate(summary["results"], 1):
        print(f"{idx}. DOI: {item['doi']}")
        print(f"   Status: {item['status']}")
        print(f"   Method: {item.get('download_method') or 'N/A'}")
        print(f"   Title: {item.get('title') or 'N/A'}")
        print(f"   Source: {item.get('source') or 'N/A'}")
        print(f"   Year: {item.get('year') or 'N/A'}")
        print(f"   Cited by: {item.get('cited_by')}")
        print(f"   URL: {item.get('resolved_url') or 'N/A'}")
        print(f"   Path: {item.get('path') or 'N/A'}")
        if item.get("error"):
            print(f"   Error: {item['error']}")


def main() -> int:
    args = parse_args()

    api_key = resolve_api_key(args.api_key)

    email = args.email or os.environ.get("UNPAYWALL_EMAIL")
    if args.scihub_fallback != "force" and not email:
        print("Missing email. Set UNPAYWALL_EMAIL or use --email.", file=sys.stderr)
        return 2

    plan = decide_plan(args)
    query_plan = build_query_plan(args)

    try:
        collected = collect_candidate_entries(
            api_key=api_key,
            query=query_plan.query,
            page_size=args.page_size,
            sort=query_plan.sort,
            plan=plan,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Scopus search failed: {exc}", file=sys.stderr)
        return 1

    fallback_cmd: Optional[List[str]] = None
    fallback_error: Optional[str] = None
    if args.scihub_fallback in {"auto", "force"}:
        fallback_cmd, fallback_error = resolve_scihub_command(args.scihub_cmd)

    fallback_cfg = FallbackConfig(
        mode=args.scihub_fallback,
        command=fallback_cmd,
        email=email,
        timeout=max(60, args.scihub_timeout),
        setup_error=fallback_error,
    )

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []
    downloaded = 0
    attempted = 0

    for entry in collected["candidates"]:
        doi = entry["doi"]
        result = process_doi(
            doi=doi,
            email=email,
            outdir=outdir,
            timeout=args.timeout,
            fallback=fallback_cfg,
        )
        result["source"] = entry.get("source")
        result["year"] = entry.get("year")
        result["cited_by"] = entry.get("cited_by")
        if not result.get("title"):
            result["title"] = entry.get("title")

        results.append(result)
        attempted += 1
        if result.get("status") == "downloaded":
            downloaded += 1

        if plan.success_cap is not None and downloaded >= plan.success_cap:
            break
        if plan.target_downloads is not None and downloaded >= plan.target_downloads:
            break

    summary = {
        "query": query_plan.query,
        "sort": query_plan.sort,
        "latest_mode": query_plan.latest_mode,
        "from_year": query_plan.from_year,
        "quantity_mode": plan.mode,
        "target_downloads": plan.target_downloads,
        "search_cap": plan.search_cap,
        "attempt_cap": plan.attempt_cap,
        "scopus_total_hits": collected["total_hits"],
        "scopus_scanned_entries": collected["scanned"],
        "candidate_count": len(collected["candidates"]),
        "missing_doi_count": collected["missing_doi"],
        "attempted_count": attempted,
        "downloaded_count": downloaded,
        "scihub_fallback_mode": args.scihub_fallback,
        "scihub_fallback_command": " ".join(fallback_cmd) if fallback_cmd else None,
        "scihub_fallback_setup_error": fallback_error,
        "results": results,
    }

    if args.json:
        output = json.dumps(summary, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
            print(args.out)
        else:
            print(output)
    else:
        print_text_summary(summary)

    return 0 if downloaded > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
