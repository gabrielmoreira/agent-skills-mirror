"""Sidecar for the pdf-explore skill.

Loaded once per session via the "Python Kernel Sidecar" exec line that
`use_skill` appends; definitions then persist in the project's Python kernel.
Top level is definition-only and every non-stdlib import sits inside a
function body, so loading never fails on a missing package. Names carry a
``pdf_`` prefix because the sidecar shares the kernel's ``__main__``.

Public surface:
    pdf_pages(path, ...)  page-level parse → [{page, text, n_chars, image_path?}]
    pdf_outline(path)     embedded-bookmark TOC with an offset sanity check
    pdf_resolve(path)     ~-expansion and a clear error for artifact-id input

The reference host's LLM fan-out helpers (pdf_scan / pdf_extract / pdf_map
and the LLM outline fallback) need an in-kernel model bridge Wisp does not
provide; they are absent by design rather than left to fail at call time.
"""

import hashlib
import os
import re

PDF_PAGE_CACHE = {}
"""In-memory parse cache, keyed (abs_path, mtime_ns, mode, dpi).

Lets repeated reads of one file skip re-parsing and re-rendering; lives until
the kernel restarts."""

PDF_AUTO_IMAGE_CHARS_THRESHOLD = 80
"""mode='auto' switches to rendering when the mean page carries fewer
extractable characters than this — the signature of a scanned or
image-only PDF."""

PDF_INSTALL_HINT = (
    "Install pypdfium2 (and pillow for mode='image') into the project's "
    "python environment — e.g. `pixi add pypdfium2 pillow` from the "
    "project directory, or pip in the active venv — then re-run."
)

_ARTIFACT_ID_SHAPE = re.compile(r"[0-9a-fA-F-]{32,36}")


def pdf_resolve(path_or_id):
    """Expand ``~`` and hand back a filesystem path.

    Wisp has no in-kernel artifact resolver, so a UUID-shaped string that is
    not an existing file raises immediately with an explanation instead of
    being treated as a path that merely doesn't exist yet.
    """
    if not isinstance(path_or_id, str) or not path_or_id:
        raise TypeError("pdf_resolve: path_or_id must be a non-empty str")
    expanded = os.path.expanduser(path_or_id)
    if os.path.exists(expanded):
        return expanded
    if _ARTIFACT_ID_SHAPE.fullmatch(path_or_id.strip()):
        raise FileNotFoundError(
            f"pdf_resolve: {path_or_id!r} looks like an artifact id; "
            f"artifact resolution is not available here — pass a file path."
        )
    return expanded


# --------------------------------------------------------------- internals

def _page_indices(total, want):
    """0-based page indices to visit, honoring an optional 1-based filter."""
    if want is None:
        return range(total)
    return sorted(i - 1 for i in want if 1 <= i <= total)


def _render_dir(abspath, mtime, dpi):
    """Per-document render directory under ``./.cache/pdf-explore/``.

    Keyed on a path hash + mtime + dpi so an in-place edit or a different
    resolution never silently reuses stale PNGs. Living under ``.cache/``
    keeps the renders out of accidental context scans — pages are meant to
    be viewed one at a time via ``view_image`` on their ``image_path``.
    """
    tag = hashlib.sha1(abspath.encode()).hexdigest()[:8]
    d = os.path.join(os.getcwd(), ".cache", "pdf-explore",
                     f"{tag}-{mtime}", f"dpi{int(dpi)}")
    os.makedirs(d, exist_ok=True)
    return d


def _password_error(path, unlock_hint):
    return ValueError(
        f"pdf_pages: {path!r} is password-protected. Decrypt it first "
        f"(e.g. `qpdf --decrypt --password=... in out` or {unlock_hint})."
    )


def _row(page_number, text, image_path):
    return {"page": page_number, "text": text,
            "n_chars": len(text), "image_path": image_path}


def _pick_backends(render):
    """Return (pdfium_module_or_None, fitz_module_or_None) in priority order.

    pypdfium2 leads (permissive license). Its ``to_pil()`` lazily imports
    PIL, so when rendering is requested and pillow is missing we demote it —
    otherwise the render path dies with a bare ModuleNotFoundError instead
    of reaching fitz (whose ``pix.save()`` writes PNG natively) or the
    install hint. Text-only pdfium has no pillow dependency.
    """
    try:
        import pypdfium2 as pdfium
    except ImportError:
        pdfium = None
    if pdfium is not None and render:
        try:
            import PIL.Image  # noqa: F401
        except ImportError:
            pdfium = None
    fitz = None
    if pdfium is None:
        try:
            import fitz  # pymupdf — user-installed fallback (AGPL-3.0)
        except ImportError:
            pass
    return pdfium, fitz


def _parse_pdfium(pdfium, abspath, path, want, need_text, render, img_dir, dpi, cache):
    try:
        doc = pdfium.PdfDocument(abspath)
    except Exception as e:
        if "password" in str(e).lower():
            raise _password_error(
                path, "pypdfium2.PdfDocument(path, password=pw)") from e
        raise
    rows = []
    try:
        for i in _page_indices(len(doc), want):
            page = doc[i]
            text = ""
            if need_text:
                tp = page.get_textpage()
                # pdfium emits \r\n; normalize so n_chars and the auto-mode
                # threshold behave identically across backends.
                text = tp.get_text_bounded().replace("\r\n", "\n")
                tp.close()
            image_path = None
            if render:
                image_path = os.path.join(img_dir, f"p{i + 1:03d}.png")
                if not (cache and os.path.exists(image_path)):
                    bitmap = page.render(scale=float(dpi) / 72.0)  # PDF native is 72dpi
                    bitmap.to_pil().save(image_path)
            rows.append(_row(i + 1, text, image_path))
    finally:
        doc.close()
    return rows


def _parse_fitz(fitz, abspath, path, want, need_text, render, img_dir, dpi, cache):
    doc = fitz.open(abspath)
    rows = []
    try:
        if doc.needs_pass:
            raise _password_error(path, "`fitz.open(path).authenticate(pw)`")
        for i in _page_indices(doc.page_count, want):
            page = doc.load_page(i)
            text = page.get_text("text") if need_text else ""
            image_path = None
            if render:
                image_path = os.path.join(img_dir, f"p{i + 1:03d}.png")
                if not (cache and os.path.exists(image_path)):
                    zoom = float(dpi) / 72.0  # PDF native is 72dpi
                    page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(image_path)
            rows.append(_row(i + 1, text, image_path))
    finally:
        doc.close()
    return rows


def _parse_pypdf(abspath, want):
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ImportError(
            "pdf_pages requires pypdfium2 or pypdf. " + PDF_INSTALL_HINT
        ) from e
    reader = PdfReader(abspath)
    return [
        _row(i + 1, reader.pages[i].extract_text() or "", None)
        for i in _page_indices(len(reader.pages), want)
    ]


def pdf_pages(path, mode="auto", pages=None, dpi=100, cache=True):
    """Parse a PDF into per-page records, cached on (path, mtime, mode, dpi).

    Returns ``[{"page": int (1-based), "text": str, "n_chars": int,
    "image_path": str|None}, ...]``.

    mode:
        "auto"   (default) extract text; when the mean page falls below
                 :data:`PDF_AUTO_IMAGE_CHARS_THRESHOLD` characters — a
                 scanned or image-only file — re-parse in image mode. Costs
                 nothing extra on normal text-layer PDFs.
        "text"   extraction only: cheap, blind to figures and scans.
        "image"  render each page to PNG at ``dpi`` (default 100 ≈ 1200×1600
                 for letter) under ``./.cache/pdf-explore/…``.
        "both"   text and renders together.

    pages: optional 1-based list/range restriction, e.g. ``[3, 4, 5]`` or
    ``range(1, 11)``. Only a full read populates the in-memory cache; subset
    reads are then served from it, but a *cold* subset read re-parses (page
    PNGs are still reused from disk).

    Backends: pypdfium2 first, the user's pymupdf second, pypdf third
    (text-only). ImportError with an install hint when none is present.
    """
    path = pdf_resolve(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"pdf_pages: {path!r} not found")
    if mode not in ("text", "image", "both", "auto"):
        raise ValueError(
            f"pdf_pages: mode must be 'text'|'image'|'both'|'auto', got {mode!r}"
        )
    # auto-mode calls back into pdf_pages twice with the same `pages`;
    # materialize one-shot iterables so the second pass doesn't receive an
    # exhausted generator and quietly return nothing.
    if pages is not None and not hasattr(pages, "__len__"):
        pages = list(pages)

    if mode == "auto":
        text_rows = pdf_pages(path, mode="text", pages=pages, dpi=dpi, cache=cache)
        if not text_rows:
            return text_rows
        mean_chars = sum(r["n_chars"] for r in text_rows) / len(text_rows)
        if mean_chars < PDF_AUTO_IMAGE_CHARS_THRESHOLD:
            return pdf_pages(path, mode="image", pages=pages, dpi=dpi, cache=cache)
        return text_rows

    abspath = os.path.abspath(path)
    mtime = os.stat(abspath).st_mtime_ns
    key = (abspath, mtime, mode, int(dpi))
    want = None if pages is None else {int(p) for p in pages}

    if cache and key in PDF_PAGE_CACHE:
        stored = PDF_PAGE_CACHE[key]
        if want is None:
            return [dict(r) for r in stored]
        subset = [dict(r) for r in stored if r["page"] in want]
        if len(subset) == len(want):
            return subset

    render = mode in ("image", "both")
    need_text = mode in ("text", "both")
    img_dir = _render_dir(abspath, mtime, dpi) if render else None

    pdfium, fitz = _pick_backends(render)
    if pdfium is not None:
        rows = _parse_pdfium(pdfium, abspath, path, want, need_text,
                             render, img_dir, dpi, cache)
    elif fitz is not None:
        rows = _parse_fitz(fitz, abspath, path, want, need_text,
                           render, img_dir, dpi, cache)
    elif render:
        raise ImportError(
            "pdf_pages(mode='image'|'both') requires pypdfium2 and pillow "
            "(PNG encoding). " + PDF_INSTALL_HINT
        )
    else:
        rows = _parse_pypdf(abspath, want)

    if cache and want is None:
        PDF_PAGE_CACHE[key] = [dict(r) for r in rows]
    return rows


# ------------------------------------------------------------------ outline

def _raw_toc(abspath):
    """Raw ``[[level, title, 1-based page], ...]`` from embedded bookmarks,
    trying pypdfium2 then the user's pymupdf; None when neither yields one."""
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(abspath)
        try:
            entries = []
            for bm in doc.get_toc():
                dest = bm.get_dest()
                idx = dest.get_index() if dest else None
                # Unresolvable destinations become page 0 and are filtered
                # out by the caller.
                entries.append([bm.level + 1, bm.get_title(),
                                (idx + 1) if idx is not None else 0])
            return entries
        finally:
            doc.close()
    except Exception:  # noqa: BLE001
        pass
    try:
        import fitz
        with fitz.open(abspath) as doc:
            return doc.get_toc(simple=True)
    except Exception:  # noqa: BLE001
        return None


def _warn_if_toc_offset(entries, abspath):
    """Best-effort detection of logical-vs-file page numbering.

    Some PDFs (typically LaTeX theses with front matter prepended after the
    hyperref anchors were fixed) embed bookmarks whose page numbers are
    document-logical, so TOC page N is really file page N+offset. Probe a
    few level-1 headings against the actual page text and warn when none
    match. An empty probe text means a missing text layer — "can't verify",
    not "offset" — so stay quiet then.
    """
    try:
        import unicodedata

        def fold(s):
            return "".join(c for c in unicodedata.normalize("NFKD", s)
                           if c.isalnum()).lower()

        probes = [e for e in entries if e["level"] == 1][:3] or entries[:3]
        probed = pdf_pages(abspath, pages=[e["page"] for e in probes], mode="text")
        text_by_page = {r["page"]: r["text"] for r in probed}
        matches = sum(
            1 for e in probes
            if fold(e["heading"])[:40]
            and fold(e["heading"])[:40] in fold(text_by_page.get(e["page"], "")[:1200])
        )
        has_text_layer = any(
            len(text_by_page.get(e["page"], "").strip())
            >= PDF_AUTO_IMAGE_CHARS_THRESHOLD
            for e in probes
        )
        if probes and matches == 0 and has_text_layer:
            print(
                "[pdf_outline] ⚠ embedded TOC page numbers don't match page "
                f"text for any of {len(probes)} sampled entries — the PDF's "
                "bookmarks likely use logical page numbers, not file page "
                "numbers (front-matter offset). Verify one entry against "
                "pdf_pages(path, pages=[N])[0]['text'] before navigating."
            )
    except Exception:  # noqa: BLE001
        pass


def pdf_outline(path):
    """Embedded-bookmark table of contents, in page order:
    ``[{"page": int, "heading": str, "level": int}, ...]``.

    Instant and free — most LaTeX-built arXiv PDFs carry bookmarks. When the
    PDF has none, prints a hint and returns ``[]``; there is no LLM fallback
    in this host, so build your own map by skimming
    ``pdf_pages(path, mode="text")``.

    First move for any structured document::

        for entry in pdf_outline("paper.pdf"):
            print(f"p{entry['page']:>3}", "  " * (entry['level'] - 1) + entry['heading'])
    """
    abspath = os.path.abspath(pdf_resolve(path))
    raw = _raw_toc(abspath)
    if raw:
        entries = [{"page": int(p), "heading": str(t), "level": int(lv)}
                   for lv, t, p in raw if p > 0]
        if entries:
            _warn_if_toc_offset(entries, abspath)
            return entries
    print(
        "[pdf_outline] no embedded outline in this PDF — skim headings via "
        "pdf_pages(path, mode='text') (e.g. print the first lines of each "
        "page) to build your own map."
    )
    return []
