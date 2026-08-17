"""Sidecar for the literature-review skill.

Public helpers (referenced from SKILL.md):
    verify_dois, crossref_lookup, search_openalex, expand_citations,
    extract_dois, style_pass

Top level is definition-only — imports, constants, functions — so the sidecar
AST gate accepts it. Network access happens only inside function bodies, and
only against CrossRef, OpenAlex, and doi.org.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

DOI_PATTERN = r"10\.\d{4,9}/[^\s\"'`\]\}—–&|]+"
_UA_BASE = "WispScience-literature-review/1.0"


# ------------------------------------------------------------ HTTP plumbing

def _contact_email():
    """Polite-pool contact for CrossRef/OpenAlex, or None.

    Wisp never injects credentials or profile data into Python; the only way
    to identify these requests is an explicit WISP_LITERATURE_CONTACT_EMAIL
    in the environment the kernel was started with.
    """
    import os
    return os.environ.get("WISP_LITERATURE_CONTACT_EMAIL", "").strip() or None


def _user_agent():
    c = _contact_email()
    ua = _UA_BASE + (f" (mailto:{c})" if c else "")
    return ua.encode("ascii", "ignore").decode("ascii")


def _openalex_key_param():
    """`&api_key=…` for api.openalex.org, or "" when unset. Honors only an
    OPENALEX_API_KEY already present in the environment, and must never be
    appended to any other service's URL."""
    import os
    key = os.environ.get("OPENALEX_API_KEY")
    return f"&api_key={urllib.parse.quote(key, safe='')}" if key else ""


def _mailto_param():
    c = _contact_email()
    return f"&mailto={urllib.parse.quote(c)}" if c else ""


def _get_json(url, timeout=15):
    """GET → decoded JSON; one 2-second retry on HTTP 429; None otherwise."""
    for attempt in (0, 1):
        req = urllib.request.Request(url, headers={"User-Agent": _user_agent()})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(2)
                continue
            return None
        except Exception:
            return None
    return None


def _head_status(url, timeout=10):
    """Origin server's own HEAD status, redirects NOT followed.

    doi.org answers 302 for a registered DOI and 404 for an unregistered
    one; following the redirect would report the publisher's status instead
    of the registry's. One 2-second retry on 429; None only when no status
    could be obtained at all (connection failure, timeout)."""
    class _StopRedirects(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(_StopRedirects)
    for attempt in (0, 1):
        req = urllib.request.Request(url, headers={"User-Agent": _user_agent()},
                                     method="HEAD")
        try:
            with opener.open(req, timeout=timeout) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(2)
                continue
            return e.code
        except Exception:
            return None
    return None


# ------------------------------------------------------------- DOI handling

def _encode_doi(doi):
    """Percent-encode a DOI path segment-by-segment, unquoting first so an
    already-encoded `%28` doesn't get double-encoded (callers pass either
    form)."""
    return "/".join(
        urllib.parse.quote(urllib.parse.unquote(seg), safe="")
        for seg in doi.split("/")
    )


def _has_dot_segment(doi):
    """True when any suffix path segment is empty, `.`, or `..`.

    No registration agency issues such DOIs, but a dot-segment-normalizing
    server or CDN can make a fabricated identifier appear to resolve.
    The whole string is unquoted *before* splitting so `%2E%2E` and an
    encoded slash smuggling `..` (`a%2F..%2Fb`) both surface."""
    segments = urllib.parse.unquote(doi).split("/")
    return any(seg in ("", ".", "..") for seg in segments[1:])


def _year_of(message):
    """Publication year from a CrossRef `message`, or None."""
    parts = (message.get("published") or {}).get("date-parts") or [[None]]
    return (parts[0] or [None])[0]


def _crossref_record(doi_encoded):
    """CrossRef work record → normalized dict, or None on miss/failure."""
    j = _get_json(f"https://api.crossref.org/works/{doi_encoded}")
    if not j or "message" not in j:
        return None
    m = j["message"]
    title = (m.get("title") or [""])[0]
    update_types = [u.get("type", "") for u in (m.get("update-to") or [])]
    retracted = (
        any("retract" in t.lower() for t in update_types)
        or str(m.get("subtype") or "").lower() == "retraction"
        or title.upper().startswith("RETRACTED")
    )
    return {
        "ok": True,
        "title": title,
        "year": _year_of(m),
        "journal": (m.get("container-title") or [""])[0],
        "retracted": retracted,
        "registry": "crossref",
    }


def verify_dois(dois):
    """Check that each DOI resolves to a real registered work.

    CrossRef is tried first (rich metadata, retraction flags); DOIs
    registered elsewhere (DataCite, mEDRA, arXiv) fall back to a doi.org
    HEAD. Result per DOI:

      ok=True   resolves (CrossRef hit, or doi.org 2xx/3xx)
      ok=False  does not resolve (doi.org 404 — fabricated or typo)
      ok=None   could not be verified (network/5xx) — NOT proof of fabrication

    `retracted` is boolean only on a CrossRef hit; None for non-CrossRef
    registries and unverified lookups.
    """
    results = {}
    for doi in dois:
        doi = doi.strip()
        if _has_dot_segment(doi):
            results[doi] = {"ok": False, "error": "dot-segment in DOI"}
            continue
        encoded = _encode_doi(doi)
        record = _crossref_record(encoded)
        time.sleep(0.06)
        if record:
            results[doi] = record
            continue
        # doi.org is authoritative across all registration agencies, so on a
        # CrossRef miss its verdict decides ok.
        status = _head_status(f"https://doi.org/{encoded}")
        if status is not None and 200 <= status < 400:
            results[doi] = {"ok": True, "registry": "non-crossref", "retracted": None}
        elif status == 404:
            results[doi] = {"ok": False}
        else:
            results[doi] = {"ok": None, "error": "unverified (network)", "retracted": None}
    return results


def crossref_lookup(ref_string):
    """Resolve a free-text citation (author/title/year) to its DOI.

    Returns the best CrossRef match as {doi, title, year, score}, or None.
    This is the alternative to pattern-completing a DOI from memory."""
    q = urllib.parse.quote(ref_string)
    j = _get_json(f"https://api.crossref.org/works?query.bibliographic={q}&rows=1")
    items = (j or {}).get("message", {}).get("items", [])
    if not items:
        return None
    m = items[0]
    return {
        "doi": m.get("DOI"),
        "title": (m.get("title") or [""])[0],
        "year": _year_of(m),
        "score": m.get("score"),
    }


# ----------------------------------------------------------------- OpenAlex

def _openalex_row(work):
    return {
        "doi": (work.get("doi") or "").replace("https://doi.org/", ""),
        "title": work.get("title"),
        "year": work.get("publication_year"),
        "cited_by": work.get("cited_by_count"),
    }


def search_openalex(query, n=10, filters=""):
    """Keyword search over OpenAlex (~250M works), most-cited first.

    Returns up to n rows of {doi, title, year, cited_by, venue, oa_url}.
    `filters` is a raw OpenAlex filter expression, e.g.
    'from_publication_date:2022-01-01'."""
    q = urllib.parse.quote(query)
    flt = f"&filter={filters}" if filters else ""
    j = _get_json(
        f"https://api.openalex.org/works?search={q}&per-page={min(n, 25)}"
        f"&sort=cited_by_count:desc{flt}{_mailto_param()}{_openalex_key_param()}"
    )
    rows = []
    for w in (j or {}).get("results", [])[:n]:
        row = _openalex_row(w)
        source = ((w.get("primary_location") or {}).get("source") or {})
        row["venue"] = source.get("display_name")
        row["oa_url"] = (w.get("open_access") or {}).get("oa_url")
        rows.append(row)
    return rows


def expand_citations(doi, n_backward=50, n_forward=15):
    """One hop in each direction on the citation graph, via OpenAlex.

    `references` — the paper's own bibliography (backward; OpenAlex filter
    `cited_by:<id>`), most-cited first. `cited_by` — papers citing this one
    (forward; filter `cites:<id>`). Rows are {doi, title, year, cited_by}.
    Costs three OpenAlex requests; both lists come back empty when OpenAlex
    doesn't know the DOI or rate-limits the list endpoint."""
    extra = _mailto_param() + _openalex_key_param()
    resolved = _get_json(
        f"https://api.openalex.org/works/doi:{_encode_doi(doi)}?select=id{extra}"
    )
    work_id = ((resolved or {}).get("id") or "").rsplit("/", 1)[-1]
    if not work_id:
        return {"references": [], "cited_by": []}

    def listing(filter_expr, limit):
        j = _get_json(
            f"https://api.openalex.org/works?filter={filter_expr}"
            f"&select=doi,title,publication_year,cited_by_count"
            f"&sort=cited_by_count:desc&per-page={min(limit, 100)}{extra}"
        )
        return [_openalex_row(w) for w in (j or {}).get("results", [])]

    return {
        "references": listing(f"cited_by:{work_id}", n_backward),
        "cited_by": listing(f"cites:{work_id}", n_forward),
    }


# ----------------------------------------------------------- text utilities

_HTML_ENTITIES = (("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&"),
                  ("&nbsp;", " "), ("&#x2F;", "/"), ("&#47;", "/"))


def _decode_entities(s):
    for entity, char in _HTML_ENTITIES:
        s = s.replace(entity, char)
    return s


def extract_dois(text):
    """Every DOI-shaped string in `text`, cleaned for verify_dois.

    Handles HTML-escaped text, `</tag>` truncation, trailing markdown
    punctuation, sentence-final periods, and unbalanced closing parens
    (SICI-style DOIs keep their balanced ones)."""
    out = set()
    for match in re.findall(DOI_PATTERN, _decode_entities(text)):
        d = match.split("</")[0]
        if d.count("<") != d.count(">"):
            d = d.split("<")[0]
        d = re.sub(r"(?:\*\*|__|[_\]\*>`,;:])+$", "", d)
        d = d.removesuffix(".")
        while d.endswith(")") and d.count("(") < d.count(")"):
            d = d[:-1]
        if len(d) > 8:
            out.add(d)
    return sorted(out)


# ----------------------------------------------------------------- lint

def _lint_emdash(draft, words):
    n = draft.count("—")
    per_kw = 1000 * n / words
    if n > 6 and per_kw > 8:
        return f"{n} em-dashes ({per_kw:.0f}/1kw); swap most for comma/colon/period, at most one per paragraph"


def _lint_honest(draft, words):
    m = re.search(
        r"\b(the\s+|an?\s+)?honest(ly)?\s+(answer|summary|read|reading|look|"
        r"perspective|assessment|appraisal|take|view)\b", draft, re.I)
    if m:
        return f"{m.group(0)!r}: drop the framing and write the sentence it was guarding"


def _lint_procnote(draft, words):
    if re.search(r"(DOIs?\s+(were\s+)?verif|verified against (CrossRef|PubMed)|"
                 r"no retraction|current as of)", draft, re.I):
        return "process-narration line present; delete it"


def _lint_parendoi(draft, words):
    if re.search(r"\]\(https://doi\.org/[^)\s]*\([^)\s]*\)", draft):
        return "DOI href contains literal ( ); encode as %28 %29 so the link survives simple renderers"


def _lint_longhead(draft, words):
    h2 = [ln for ln in draft.split("\n") if ln.startswith("## ")]
    long = [ln for ln in h2 if len(ln.split()) > 8]
    if len(long) >= 2:
        return f"{len(long)} headings read as sentences; shorten to <=6-word noun phrases"


def _lint_flatstruct(draft, words):
    lines = draft.split("\n")
    h2 = [ln for ln in lines if ln.startswith("## ")]
    if len(h2) >= 7 and not any(ln.startswith("### ") for ln in lines):
        return f"{len(h2)} top-level sections, no subsections; group related ## under a parent and demote to ###"


_LINT_RULES = (
    ("EMDASH", _lint_emdash),
    ("HONEST", _lint_honest),
    ("PROCNOTE", _lint_procnote),
    ("PARENDOI", _lint_parendoi),
    ("LONGHEAD", _lint_longhead),
    ("FLATSTRUCT", _lint_flatstruct),
)


def style_pass(draft, model=None):
    """Deterministic prose lint → {ok, issues:[{code, note}]}.

    Codes: EMDASH, HONEST, PROCNOTE, PARENDOI, LONGHEAD, FLATSTRUCT.

    Deliberately no LLM involvement: drafts routinely embed third-party text
    retrieved from the web, and a free-text "fix hint" the agent is told to
    apply would be an indirect prompt-injection channel. `model` is accepted
    for call-site compatibility and ignored."""
    del model
    words = len(draft.split()) or 1
    issues = [
        {"code": code, "note": note}
        for code, rule in _LINT_RULES
        if (note := rule(draft, words))
    ]
    return {"ok": not issues, "issues": issues}
