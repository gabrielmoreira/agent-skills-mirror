#!/usr/bin/env python3
"""Download PDFs by DOI using Unpaywall with optional scihub-cli fallback."""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Serializes filename allocation + write so concurrent workers never collide on
# the same output path (unique_path's check-then-write is not atomic).
_WRITE_LOCK = threading.Lock()

UNPAYWALL_URL = "https://api.unpaywall.org/v2"
USER_AGENT = "sci-papers-downloder/1.1"
UVX_FALLBACK_CMD = [
    "uvx",
    "--from",
    "git+https://github.com/Oxidane-bot/scihub-cli.git",
    "scihub-cli",
]


@dataclass
class FallbackConfig:
    mode: str
    command: Optional[List[str]]
    email: Optional[str]
    timeout: int
    setup_error: Optional[str] = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve DOI via Unpaywall and download OA PDF if available. "
            "When enabled, use scihub-cli as fallback if Unpaywall path fails."
        )
    )
    parser.add_argument("--doi", action="append", default=[], help="DOI to process (repeatable)")
    parser.add_argument("--doi-file", help="Optional text file with one DOI per line")
    parser.add_argument("--email", help="Email for Unpaywall API. Defaults to UNPAYWALL_EMAIL env var.")
    parser.add_argument("--outdir", default="./downloads", help="Output directory for downloaded PDFs")
    parser.add_argument("--timeout", type=int, default=45, help="HTTP timeout seconds")

    parser.add_argument(
        "--scihub-fallback",
        choices=["off", "auto", "force"],
        default="auto",
        help=(
            "Fallback mode: off=Unpaywall only; auto=run fallback when Unpaywall path fails; "
            "force=skip Unpaywall and use scihub-cli only"
        ),
    )
    parser.add_argument(
        "--scihub-cmd",
        help=(
            "Optional scihub-cli command override, e.g. \"scihub-cli\" or "
            "\"uvx --from git+https://github.com/Oxidane-bot/scihub-cli.git scihub-cli\""
        ),
    )
    parser.add_argument(
        "--scihub-email",
        help=(
            "Optional email passed to scihub-cli (used by its internal Unpaywall source). "
            "Defaults to --email value."
        ),
    )
    parser.add_argument(
        "--scihub-timeout",
        type=int,
        default=180,
        help="Per-DOI timeout for scihub-cli fallback execution (seconds)",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help="Number of DOIs to download in parallel (default: 8; 1 = sequential)",
    )

    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    parser.add_argument("--out", help="Write JSON summary to file path")
    return parser.parse_args()


def load_dois(args: argparse.Namespace) -> List[str]:
    dois: List[str] = []
    seen = set()

    def push(value: str) -> None:
        doi = value.strip()
        if not doi or doi.startswith("#"):
            return
        if doi not in seen:
            seen.add(doi)
            dois.append(doi)

    for doi in args.doi:
        push(doi)

    if args.doi_file:
        for line in Path(args.doi_file).read_text(encoding="utf-8").splitlines():
            push(line)

    return dois


def quote_doi(doi: str) -> str:
    return urllib.parse.quote(doi, safe="")


def unpaywall_lookup(doi: str, email: str, timeout: int) -> Dict[str, Any]:
    url = f"{UNPAYWALL_URL}/{quote_doi(doi)}?email={urllib.parse.quote(email, safe='@._+-')}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "ignore"))


def unique_urls(urls: List[Optional[str]]) -> List[str]:
    out: List[str] = []
    seen = set()
    for url in urls:
        if not url:
            continue
        u = url.strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def build_candidate_urls(record: Dict[str, Any]) -> List[str]:
    best = record.get("best_oa_location") or {}
    urls: List[Optional[str]] = [
        best.get("url_for_pdf"),
        best.get("url"),
    ]

    for location in record.get("oa_locations") or []:
        urls.append(location.get("url_for_pdf"))
        urls.append(location.get("url"))

    return unique_urls(urls)


def maybe_extract_pdf_url_from_html(html_text: str) -> Optional[str]:
    m = re.search(
        r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']',
        html_text,
        re.I,
    )
    if m:
        return m.group(1)

    m = re.search(r'href=["\']([^"\']+\.pdf(?:\?[^"\']*)?)["\']', html_text, re.I)
    if m:
        return m.group(1)

    return None


def fetch_url_bytes(url: str, timeout: int) -> Tuple[bytes, str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf, text/html;q=0.9, */*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        content_type = resp.headers.get_content_type() if resp.headers else ""
        final_url = resp.geturl()
    return data, content_type, final_url


def is_pdf(data: bytes, content_type: str) -> bool:
    return data.startswith(b"%PDF") or "pdf" in (content_type or "").lower()


def safe_filename(value: str, default: str) -> str:
    text = value.strip() if value else ""
    if not text:
        text = default
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    text = text.strip("._")
    if not text:
        text = default
    return text[:120]


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for idx in range(2, 10000):
        candidate = parent / f"{stem}_{idx}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not allocate unique path for {path}")


def attempt_download(
    candidate_url: str, timeout: int
) -> Tuple[bool, str, Optional[bytes], Optional[str]]:
    """Fetch a candidate URL and return PDF bytes (without writing to disk).

    Returns (ok, resolved_url, data, error). Writing is deferred to the caller so
    it can be serialized under a lock for safe concurrent execution.
    """
    try:
        data, content_type, final_url = fetch_url_bytes(candidate_url, timeout)
    except Exception as exc:  # noqa: BLE001
        return False, candidate_url, None, f"request_error: {exc}"

    if is_pdf(data, content_type):
        return True, final_url, data, None

    if "html" not in (content_type or "").lower():
        return False, final_url, None, f"non_pdf_content_type: {content_type}"

    html_text = data.decode("utf-8", "ignore")
    discovered = maybe_extract_pdf_url_from_html(html_text)
    if not discovered:
        return False, final_url, None, "html_without_pdf_link"

    discovered_url = urllib.parse.urljoin(final_url, discovered)
    try:
        data2, content_type2, final_url2 = fetch_url_bytes(discovered_url, timeout)
    except Exception as exc:  # noqa: BLE001
        return False, discovered_url, None, f"followup_request_error: {exc}"

    if not is_pdf(data2, content_type2):
        return False, final_url2, None, f"followup_non_pdf_content_type: {content_type2}"

    return True, final_url2, data2, None


def reserve_and_write(outdir: Path, filename_base: str, data: bytes) -> Path:
    """Allocate a unique path and write bytes atomically across worker threads."""
    with _WRITE_LOCK:
        out_path = unique_path(outdir / f"{filename_base}.pdf")
        out_path.write_bytes(data)
    return out_path


def reserve_and_copy(outdir: Path, filename_base: str, src: Path) -> Path:
    """Allocate a unique path and copy a file atomically across worker threads."""
    with _WRITE_LOCK:
        target = unique_path(outdir / f"{filename_base}.pdf")
        shutil.copy2(src, target)
    return target


def resolve_scihub_command(command_override: Optional[str]) -> Tuple[Optional[List[str]], Optional[str]]:
    if command_override:
        cmd = shlex.split(command_override)
        if not cmd:
            return None, "empty_scihub_cmd"
        first = cmd[0]
        if os.path.sep in first:
            if not Path(first).exists():
                return None, f"scihub_cmd_not_found: {first}"
            return cmd, None
        if shutil.which(first):
            return cmd, None
        return None, f"scihub_cmd_not_found: {first}"

    if shutil.which("scihub-cli"):
        return ["scihub-cli"], None

    if shutil.which("uvx"):
        return UVX_FALLBACK_CMD.copy(), None

    return None, "scihub_cli_not_found (install with: uv tool install git+https://github.com/Oxidane-bot/scihub-cli.git)"


def is_valid_pdf_file(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(4) == b"%PDF"
    except Exception:  # noqa: BLE001
        return False


def find_best_pdf(root: Path) -> Optional[Path]:
    pdfs = [p for p in root.rglob("*.pdf") if p.is_file()]
    if not pdfs:
        return None
    pdfs.sort(key=lambda p: p.stat().st_size, reverse=True)
    return pdfs[0]


def compact_log_tail(text: str, max_lines: int = 6) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    tail = lines[-max_lines:]
    return " | ".join(tail)


def attempt_scihub_fallback(
    doi: str,
    outdir: Path,
    filename_base: str,
    fallback: FallbackConfig,
) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    if fallback.command is None:
        return False, None, None, fallback.setup_error or "scihub_fallback_not_available"

    with tempfile.TemporaryDirectory(prefix="scihub_fallback_") as td:
        tmp = Path(td)
        input_file = tmp / "input.txt"
        input_file.write_text(f"{doi}\n", encoding="utf-8")

        tmp_out = tmp / "out"
        tmp_out.mkdir(parents=True, exist_ok=True)

        cmd = list(fallback.command)
        cmd.extend(
            [
                str(input_file),
                "-o",
                str(tmp_out),
                "-t",
                str(max(15, fallback.timeout // 3)),
                "-r",
                "2",
                "-p",
                "1",
            ]
        )
        if fallback.email:
            cmd.extend(["--email", fallback.email])

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=max(60, fallback.timeout),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False, None, None, f"scihub_cli_timeout_after_{max(60, fallback.timeout)}s"
        except Exception as exc:  # noqa: BLE001
            return False, None, None, f"scihub_cli_exec_error: {exc}"

        logs = "\n".join([proc.stdout or "", proc.stderr or ""])
        best_pdf = find_best_pdf(tmp_out)
        if not best_pdf:
            err_tail = compact_log_tail(logs)
            if proc.returncode != 0:
                return (
                    False,
                    None,
                    None,
                    f"scihub_cli_no_pdf_exit_{proc.returncode}: {err_tail or 'no_detail'}",
                )
            return False, None, None, f"scihub_cli_no_pdf: {err_tail or 'no_detail'}"

        if not is_valid_pdf_file(best_pdf):
            return False, None, None, "scihub_cli_invalid_pdf_header"

        target = reserve_and_copy(outdir, filename_base, best_pdf)

        m = re.search(r"Download URL:\s*(\S+)", logs)
        resolved = m.group(1) if m else None
        return True, str(target), resolved, None


def process_doi(
    doi: str,
    email: Optional[str],
    outdir: Path,
    timeout: int,
    fallback: FallbackConfig,
    extra_urls: Optional[List[str]] = None,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "doi": doi,
        "status": "failed",
        "title": None,
        "is_oa": None,
        "resolved_url": None,
        "path": None,
        "error": None,
        "download_method": None,
        "primary_status": None,
        "primary_error": None,
        "fallback_attempted": False,
        "fallback_error": None,
    }

    filename_base = safe_filename(doi.replace("/", "_"), "paper")

    if fallback.mode == "force":
        result["fallback_attempted"] = True
        ok, path, resolved, fallback_error = attempt_scihub_fallback(doi, outdir, filename_base, fallback)
        if ok:
            result["status"] = "downloaded"
            result["path"] = path
            result["resolved_url"] = resolved
            result["download_method"] = "scihub_fallback"
            return result
        result["status"] = "failed"
        result["error"] = fallback_error
        result["fallback_error"] = fallback_error
        return result

    if not email:
        result["status"] = "failed"
        result["error"] = "missing_unpaywall_email"
        result["primary_status"] = "failed"
        result["primary_error"] = "missing_unpaywall_email"
        return result

    primary_status = "failed"
    primary_error = None

    try:
        record = unpaywall_lookup(doi, email, timeout)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "ignore")
        primary_status = "failed"
        primary_error = f"unpaywall_http_{exc.code}: {body}"
        record = None
    except Exception as exc:  # noqa: BLE001
        primary_status = "failed"
        primary_error = f"unpaywall_error: {exc}"
        record = None

    hint_urls = unique_urls(list(extra_urls or []))
    hint_set = set(hint_urls)
    unpaywall_candidates: List[str] = []
    is_oa: Optional[bool] = None

    if record is not None:
        title = record.get("title") or ""
        is_oa = bool(record.get("is_oa"))
        result["title"] = title
        result["is_oa"] = is_oa
        filename_base = safe_filename(title, default=filename_base)
        if is_oa:
            unpaywall_candidates = build_candidate_urls(record)

    # OA direct hints (e.g. from OpenAlex) are tried first, even when Unpaywall
    # reports no OA or failed entirely — the two databases disagree often enough.
    candidates = unique_urls(hint_urls + unpaywall_candidates)

    if candidates:
        for candidate in candidates:
            ok, resolved_url, data, error = attempt_download(candidate, timeout)
            result["resolved_url"] = resolved_url
            if ok and data is not None:
                out_path = reserve_and_write(outdir, filename_base, data)
                result["status"] = "downloaded"
                result["path"] = str(out_path)
                result["error"] = None
                result["download_method"] = "oa_direct" if candidate in hint_set else "unpaywall"
                result["primary_status"] = "downloaded"
                result["primary_error"] = None
                return result
            primary_error = error
        primary_status = "failed"
    elif record is not None and is_oa is False:
        primary_status = "no_oa"
    elif record is not None:
        primary_status = "no_download_url"

    result["primary_status"] = primary_status
    result["primary_error"] = primary_error

    if fallback.mode != "auto":
        result["status"] = primary_status
        result["error"] = primary_error
        return result

    if fallback.command is None:
        result["fallback_attempted"] = False
        result["status"] = primary_status
        result["error"] = primary_error
        result["fallback_error"] = fallback.setup_error
        return result

    result["fallback_attempted"] = True
    ok, path, resolved, fallback_error = attempt_scihub_fallback(doi, outdir, filename_base, fallback)
    if ok:
        result["status"] = "downloaded"
        result["path"] = path
        result["resolved_url"] = resolved or result.get("resolved_url")
        result["error"] = None
        result["download_method"] = "scihub_fallback"
        result["fallback_error"] = None
        return result

    result["status"] = "failed"
    result["error"] = primary_error or fallback_error
    result["fallback_error"] = fallback_error
    result["download_method"] = None
    return result


def process_dois_concurrent(
    jobs: List[Dict[str, Any]],
    email: Optional[str],
    outdir: Path,
    timeout: int,
    fallback: FallbackConfig,
    concurrency: int,
) -> List[Dict[str, Any]]:
    """Download a batch of DOIs in parallel, preserving input order.

    Each job is a dict with at least {"doi": str} and optional "extra_urls".
    Network IO is the bottleneck, so a thread pool gives near-linear speedup;
    disk writes are serialized inside process_doi via reserve_and_write.
    """
    workers = max(1, concurrency)
    results: List[Optional[Dict[str, Any]]] = [None] * len(jobs)

    if workers == 1:
        for idx, job in enumerate(jobs):
            results[idx] = process_doi(
                job["doi"], email, outdir, timeout, fallback, job.get("extra_urls")
            )
        return [r for r in results if r is not None]

    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_to_idx = {
            pool.submit(
                process_doi, job["doi"], email, outdir, timeout, fallback, job.get("extra_urls")
            ): idx
            for idx, job in enumerate(jobs)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as exc:  # noqa: BLE001
                results[idx] = {
                    "doi": jobs[idx]["doi"],
                    "status": "failed",
                    "error": f"worker_exception: {exc}",
                    "download_method": None,
                }

    return [r for r in results if r is not None]


def print_text_summary(summary: Dict[str, Any]) -> None:
    print(f"Unpaywall email: {summary.get('email') or 'N/A'}")
    print(f"DOI count: {summary['doi_count']}")
    print(f"SciHub fallback: {summary['scihub_fallback_mode']}")
    if summary.get("scihub_fallback_command"):
        print(f"SciHub command: {summary['scihub_fallback_command']}")
    if summary.get("scihub_fallback_setup_error"):
        print(f"SciHub setup error: {summary['scihub_fallback_setup_error']}")
    print()
    for idx, item in enumerate(summary["results"], 1):
        print(f"{idx}. DOI: {item['doi']}")
        print(f"   Status: {item['status']}")
        print(f"   Method: {item.get('download_method') or 'N/A'}")
        print(f"   Primary status: {item.get('primary_status') or 'N/A'}")
        print(f"   Title: {item.get('title') or 'N/A'}")
        print(f"   URL: {item.get('resolved_url') or 'N/A'}")
        print(f"   Path: {item.get('path') or 'N/A'}")
        if item.get("error"):
            print(f"   Error: {item['error']}")
        if item.get("fallback_error"):
            print(f"   Fallback error: {item['fallback_error']}")


def main() -> int:
    args = parse_args()

    email = args.email or os.environ.get("UNPAYWALL_EMAIL")
    if args.scihub_fallback != "force" and not email:
        print("Missing Unpaywall email. Set UNPAYWALL_EMAIL or use --email.", file=sys.stderr)
        return 2

    dois = load_dois(args)
    if not dois:
        print("No DOI provided. Use --doi or --doi-file.", file=sys.stderr)
        return 2

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    fallback_cmd: Optional[List[str]] = None
    fallback_error: Optional[str] = None
    if args.scihub_fallback in {"auto", "force"}:
        fallback_cmd, fallback_error = resolve_scihub_command(args.scihub_cmd)

    fallback_cfg = FallbackConfig(
        mode=args.scihub_fallback,
        command=fallback_cmd,
        email=args.scihub_email or email,
        timeout=max(60, args.scihub_timeout),
        setup_error=fallback_error,
    )

    jobs = [{"doi": doi} for doi in dois]
    results = process_dois_concurrent(
        jobs, email, outdir, args.timeout, fallback_cfg, args.concurrency
    )

    summary = {
        "email": email,
        "doi_count": len(dois),
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

    downloaded = sum(1 for r in results if r["status"] == "downloaded")
    return 0 if downloaded > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
