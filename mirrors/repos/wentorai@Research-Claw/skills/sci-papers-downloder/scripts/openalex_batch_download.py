#!/usr/bin/env python3
"""No-key end-to-end: search OpenAlex by topic and download papers concurrently.

This is the key-free counterpart to topic_batch_download.py. It swaps Scopus
(which needs an Elsevier key + institutional entitlement) for OpenAlex (free,
no key) and downloads with a thread pool instead of a sequential loop. OA PDF
hints from OpenAlex are tried directly, with Unpaywall (and optional scihub-cli)
as fallbacks. Quantity/freshness intent mapping is shared with topic_batch_download.
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from download_open_access import (  # noqa: E402
    FallbackConfig,
    process_dois_concurrent,
    resolve_scihub_command,
)
from search_openalex import resolve_email, search_paged  # noqa: E402
from topic_batch_download import decide_plan  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search OpenAlex (no API key) and download papers concurrently with "
            "quantity-aware defaults (few/batch/max) and latest/recent handling."
        )
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keywords", help="Full-text search terms")
    mode.add_argument("--title", help="Title search")
    mode.add_argument("--query", help="Raw OpenAlex filter expression")

    parser.add_argument("--email", help="Contact email (OpenAlex polite pool + Unpaywall). Defaults to UNPAYWALL_EMAIL/OPENALEX_EMAIL env")

    parser.add_argument("--quantity-mode", choices=["few", "batch", "max"], default="batch",
                        help="few=~5; batch=~20; max=as many as possible under caps")
    parser.add_argument("--target", type=int, help="Explicit target download count; overrides quantity-mode")
    parser.add_argument("--max-search-results", type=int, help="Max entries to scan; overrides mode default")
    parser.add_argument("--max-attempts", type=int, help="Max DOI download attempts; overrides mode default")
    parser.add_argument("--max-success", type=int, help="Hard cap on successful downloads")

    parser.add_argument("--latest", action="store_true", help="Prefer latest papers (recent-year filter + date sort)")
    parser.add_argument("--years-back", type=int, default=3, help="With --latest, keep papers from last N years (default 3)")
    parser.add_argument("--from-year", type=int, help="Explicit lower year bound (inclusive), e.g. 2023")

    parser.add_argument("--oa-only", dest="oa_only", action="store_true", default=True,
                        help="Restrict search to open-access works (default: on)")
    parser.add_argument("--no-oa-only", dest="oa_only", action="store_false",
                        help="Include non-OA works (download relies on Unpaywall/scihub)")

    parser.add_argument("--per-page", type=int, default=50, help="OpenAlex page size per API call")
    parser.add_argument("--sort", help="OpenAlex sort. Default publication_date:desc for latest, else cited_by_count:desc")
    parser.add_argument("--timeout", type=int, default=45, help="HTTP timeout seconds")
    parser.add_argument("--concurrency", type=int, default=8, help="Parallel download workers (default 8)")
    parser.add_argument("--outdir", default="./downloads", help="Output directory")

    parser.add_argument("--scihub-fallback", choices=["off", "auto", "force"], default="auto",
                        help="Fallback for non-OA/failed downloads (default auto; off disables, force skips Unpaywall)")
    parser.add_argument("--scihub-cmd", help="Optional override command for scihub-cli")
    parser.add_argument("--scihub-timeout", type=int, default=180, help="Fallback timeout seconds")

    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument("--out", help="Write JSON summary to file path")
    return parser.parse_args()


def resolve_from_year(args: argparse.Namespace) -> Optional[int]:
    if args.from_year and args.from_year > 0:
        return args.from_year
    if args.latest:
        years_back = max(1, args.years_back)
        return date.today().year - years_back + 1
    return None


def build_search_terms(args: argparse.Namespace) -> Dict[str, Any]:
    search = args.keywords if args.keywords else None
    filters: List[str] = []
    if args.query:
        filters.append(args.query)
    elif args.title:
        filters.append(f"title.search:{args.title}")

    from_year = resolve_from_year(args)
    if from_year is not None:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if args.oa_only:
        filters.append("is_oa:true")

    latest_mode = bool(args.latest or from_year is not None)
    sort = args.sort or ("publication_date:desc" if latest_mode else "cited_by_count:desc")
    return {"search": search, "filters": filters, "sort": sort,
            "latest_mode": latest_mode, "from_year": from_year}


def build_jobs(entries: List[Dict[str, Any]], attempt_cap: int) -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    seen = set()
    missing = 0
    for e in entries:
        doi = (e.get("doi") or "").strip()
        oa_url = e.get("oa_url")
        has_doi = bool(doi and doi.upper() != "N/A")
        if not has_doi and not oa_url:
            missing += 1
            continue
        key = doi if has_doi else oa_url
        if key in seen:
            continue
        seen.add(key)
        jobs.append({
            "doi": doi if has_doi else "N/A",
            "extra_urls": [oa_url] if oa_url else [],
            "_meta": {"title": e.get("title"), "year": e.get("year"),
                      "source": e.get("source"), "cited_by": e.get("cited_by")},
        })
        if len(jobs) >= attempt_cap:
            break
    return jobs, missing


def print_text_summary(summary: Dict[str, Any]) -> None:
    print(f"Search: {summary['search']}")
    print(f"Filters: {summary['filters']}")
    print(f"Sort: {summary['sort']} | Latest: {summary['latest_mode']} | From year: {summary['from_year']}")
    print(f"Quantity mode: {summary['quantity_mode']} | Target: {summary['target_downloads']}")
    print(f"OpenAlex total hits: {summary['total_hits']} | Scanned: {summary['scanned']}")
    print(f"Candidates: {summary['candidate_count']} | Skipped (no doi/oa): {summary['missing_count']}")
    print(f"Downloaded: {summary['downloaded_count']} / Attempted: {summary['attempted_count']} (concurrency={summary['concurrency']})")
    print()
    for idx, item in enumerate(summary["results"], 1):
        print(f"{idx}. {item.get('title') or item['doi']}")
        print(f"   DOI: {item['doi']} | Status: {item['status']} | Method: {item.get('download_method') or 'N/A'}")
        print(f"   Path: {item.get('path') or 'N/A'}")
        if item.get("error"):
            print(f"   Error: {str(item['error'])[:120]}")


def main() -> int:
    args = parse_args()
    email = resolve_email(args.email)
    if not email:
        print("Missing email. Set UNPAYWALL_EMAIL/OPENALEX_EMAIL or use --email.", file=sys.stderr)
        return 2

    plan = decide_plan(args)
    terms = build_search_terms(args)

    try:
        found = search_paged(
            search=terms["search"], filters=terms["filters"], sort=terms["sort"],
            per_page=args.per_page, count=plan.search_cap, email=email,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"OpenAlex search failed: {exc}", file=sys.stderr)
        return 1

    jobs, missing = build_jobs(found["entries"], plan.attempt_cap)

    fallback_cmd: Optional[List[str]] = None
    fallback_error: Optional[str] = None
    if args.scihub_fallback in {"auto", "force"}:
        fallback_cmd, fallback_error = resolve_scihub_command(args.scihub_cmd)
    fallback_cfg = FallbackConfig(
        mode=args.scihub_fallback, command=fallback_cmd, email=email,
        timeout=max(60, args.scihub_timeout), setup_error=fallback_error,
    )

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Download in waves so we can stop once the success target is reached, while
    # staying concurrent within each wave. A single big pool would over-download
    # (e.g. "few"=5 would still fetch every candidate before stopping).
    target = plan.success_cap if plan.success_cap is not None else plan.target_downloads
    workers = max(1, args.concurrency)
    wave_size = workers if target is None else max(workers, min(target, plan.attempt_cap))

    results: List[Dict[str, Any]] = []
    raw_results: List[Dict[str, Any]] = []
    downloaded = 0
    i = 0
    while i < len(jobs) and (target is None or downloaded < target):
        chunk = jobs[i:i + wave_size]
        i += len(chunk)
        chunk_results = process_dois_concurrent(
            chunk, email, outdir, args.timeout, fallback_cfg, workers
        )
        for job, res in zip(chunk, chunk_results):
            meta = job.get("_meta") or {}
            for k in ("title", "year", "source", "cited_by"):
                if not res.get(k):
                    res[k] = meta.get(k)
            results.append(res)
            raw_results.append(res)
            if res.get("status") == "downloaded":
                downloaded += 1

    summary = {
        "search": terms["search"],
        "filters": terms["filters"],
        "sort": terms["sort"],
        "latest_mode": terms["latest_mode"],
        "from_year": terms["from_year"],
        "quantity_mode": plan.mode,
        "target_downloads": plan.target_downloads,
        "concurrency": max(1, args.concurrency),
        "total_hits": found["total"],
        "scanned": len(found["entries"]),
        "candidate_count": len(jobs),
        "missing_count": missing,
        "attempted_count": len(results),
        "downloaded_count": downloaded,
        "scihub_fallback_mode": args.scihub_fallback,
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
