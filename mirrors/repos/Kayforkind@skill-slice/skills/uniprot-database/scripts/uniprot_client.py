#!/usr/bin/env python3
"""UniProt REST helpers for https://rest.uniprot.org (stdlib only).

Functions: search_proteins, get_protein, map_ids, batch_retrieve, stream_results.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://rest.uniprot.org"
USER_AGENT = "uniprot-database-skill/1.0"
MAX_MAP_IDS = 100_000
POLL_SECONDS = 2.0
POLL_ATTEMPTS = 60


def _request(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
) -> tuple[int, dict[str, str], bytes]:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        req_headers.update(headers)
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            return response.status, dict(response.headers.items()), body
    except urllib.error.HTTPError as exc:
        err_body = exc.read()
        raise RuntimeError(
            f"UniProt HTTP {exc.code} for {url}: {err_body[:500]!r}"
        ) from exc


def search_proteins(
    query: str,
    format: str = "json",
    *,
    fields: str | None = None,
    size: int = 25,
) -> bytes:
    """Search UniProtKB. format: json, tsv, fasta, xml, txt, xlsx, rdf."""
    params: dict[str, str] = {"query": query, "format": format, "size": str(size)}
    if fields:
        params["fields"] = fields
    url = f"{BASE}/uniprotkb/search?{urllib.parse.urlencode(params)}"
    _status, _headers, body = _request(url)
    return body


def get_protein(accession: str, format: str = "fasta") -> bytes:
    """Retrieve one UniProtKB entry by accession (classic or extended)."""
    safe = urllib.parse.quote(accession, safe="")
    url = f"{BASE}/uniprotkb/{safe}.{format}"
    _status, _headers, body = _request(url)
    return body


def batch_retrieve(accessions: list[str], format: str = "fasta") -> bytes:
    """Retrieve many accessions in one call via /uniprotkb/accessions."""
    if not accessions:
        raise ValueError("accessions must be a non-empty list")
    params = {"accessions": ",".join(accessions), "format": format}
    url = f"{BASE}/uniprotkb/accessions?{urllib.parse.urlencode(params)}"
    _status, _headers, body = _request(url)
    return body


def stream_results(query: str, format: str = "fasta") -> bytes:
    """Stream every match for a query (no search pagination)."""
    params = {"query": query, "format": format}
    url = f"{BASE}/uniprotkb/stream?{urllib.parse.urlencode(params)}"
    _status, _headers, body = _request(url, timeout=300)
    return body


def map_ids(
    ids: list[str],
    from_db: str,
    to_db: str,
    *,
    poll_seconds: float = POLL_SECONDS,
) -> dict:
    """Submit an ID mapping job, poll until done, return JSON results."""
    if not ids:
        raise ValueError("ids must be a non-empty list")
    if len(ids) > MAX_MAP_IDS:
        raise ValueError(f"ID mapping accepts at most {MAX_MAP_IDS} IDs per job")
    form = urllib.parse.urlencode(
        {"from": from_db, "to": to_db, "ids": ",".join(ids)}
    ).encode("utf-8")
    _status, _headers, body = _request(
        f"{BASE}/idmapping/run",
        method="POST",
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    job = json.loads(body.decode("utf-8"))
    job_id = job.get("jobId")
    if not job_id:
        raise RuntimeError(f"ID mapping submit did not return jobId: {job!r}")

    status_url = f"{BASE}/idmapping/status/{urllib.parse.quote(job_id, safe='')}"
    for _ in range(POLL_ATTEMPTS):
        _status, _headers, status_body = _request(status_url)
        payload = json.loads(status_body.decode("utf-8"))
        job_status = payload.get("jobStatus")
        if job_status == "RUNNING":
            time.sleep(poll_seconds)
            continue
        if job_status in ("ERROR", "FAILED"):
            raise RuntimeError(f"ID mapping job {job_id} failed: {payload!r}")
        break
    else:
        raise TimeoutError(f"ID mapping job {job_id} still running after {POLL_ATTEMPTS} polls")

    results_url = f"{BASE}/idmapping/results/{urllib.parse.quote(job_id, safe='')}"
    _status, _headers, result_body = _request(results_url)
    return json.loads(result_body.decode("utf-8"))


def _print_bytes(body: bytes) -> None:
    sys.stdout.buffer.write(body)
    if not body.endswith(b"\n"):
        sys.stdout.buffer.write(b"\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UniProt REST client")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--format", default="tsv")
    p_search.add_argument("--fields", default="accession,gene_names,organism_name,length")
    p_search.add_argument("--size", type=int, default=5)

    p_get = sub.add_parser("get")
    p_get.add_argument("accession")
    p_get.add_argument("--format", default="fasta")

    p_batch = sub.add_parser("batch")
    p_batch.add_argument("accessions", help="Comma-separated accessions")
    p_batch.add_argument("--format", default="fasta")

    p_stream = sub.add_parser("stream")
    p_stream.add_argument("query")
    p_stream.add_argument("--format", default="fasta")

    p_map = sub.add_parser("map")
    p_map.add_argument("ids", help="Comma-separated IDs")
    p_map.add_argument("--from-db", default="UniProtKB_AC-ID")
    p_map.add_argument("--to-db", default="Ensembl")

    args = parser.parse_args(argv)

    if args.cmd == "search":
        _print_bytes(
            search_proteins(args.query, args.format, fields=args.fields, size=args.size)
        )
    elif args.cmd == "get":
        _print_bytes(get_protein(args.accession, args.format))
    elif args.cmd == "batch":
        _print_bytes(batch_retrieve(args.accessions.split(","), args.format))
    elif args.cmd == "stream":
        _print_bytes(stream_results(args.query, args.format))
    elif args.cmd == "map":
        result = map_ids(args.ids.split(","), args.from_db, args.to_db)
        print(json.dumps(result, indent=2))
    else:
        raise SystemExit(f"unhandled command: {args.cmd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
