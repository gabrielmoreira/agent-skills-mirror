---
name: academic-pdf-redaction
version: 1.2.1
description: "Redact author-identifying text from academic PDFs for double-blind peer review anonymization — trigger when preparing manuscripts for blind review, anonymizing submissions, or stripping names/affiliations/emails/DOIs from PDFs. Not for scanned image-only PDFs, legal e-discovery, or general PDF merge/extract."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

This skill removes author-identifying information from academic papers before they enter double-blind peer review. The goal is narrow: strip the handful of strings that reveal identity (names, affiliations, contact details, venue self-references) while leaving the scientific content byte-for-byte intact so reviewers can still evaluate the work.

The skill uses PyMuPDF (`fitz`) to search for specific text strings and physically remove the underlying glyphs — not merely paint black boxes over them.

## When to Use

- Preparing an academic paper for double-blind peer review submission.
- Anonymizing a PDF manuscript by removing author names, affiliations, emails, arXiv IDs, DOIs, and venue self-references.
- You have a text-based PDF (not a scanned image) and need targeted string-level redaction.

## Prerequisites

- **Python 3.10+** with **PyMuPDF >= 1.24** installed. Older PyMuPDF releases (before 1.24) carry known parser CVEs that a malicious document can trigger.
- **Install or verify PyMuPDF** (PowerShell, Windows host):

```powershell
pip install "PyMuPDF>=1.24"
python -c "import fitz; print(fitz.__doc__)"
```

- If the PDF is a scanned image with no extractable text layer, this skill cannot help — there are no text glyphs to search for. Those documents need pixel-level redaction after OCR (see [Related skills](#related-skills)).
- The redaction pipeline and `verify_redaction` helper are inlined in this file (Steps 2–4 and Verification). This folder does not ship helper scripts or a references pack.

## Procedure

### Step 1 — Identify the identifying strings to redact

Collect the literal strings and decide which regex patterns to apply. PyMuPDF's `search_for()` only does **literal** substring matching — it cannot take a regular expression. Patterns split into two groups:

**Literal strings** (passed straight to `search_for`):

- **Author full names** — redact the complete name ("John Smith"), never the bare surname ("Smith"). A lone surname collides with unrelated cited authors and would scrub legitimate citations.
- **Affiliations** — institutions and companies ("Duke University", "Acme Research").
- **Venue self-references** — "ICML 2024", "ICML Workshop"; naming the target venue in the body is a common deanonymisation tell.
- **Acknowledgement names** — people thanked by name in the Acknowledgements section.
- **Equal-contribution footnotes** — "Equal contribution", "* Equal contribution".

**Regex patterns** (matched against extracted text first, then concrete hits are looked up with `search_for`):

- **Email addresses** — `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
- **arXiv identifiers** — `arXiv:\d{4}\.\d{4,5}(?:v\d+)?`
- **DOIs** — `10\.\d{4,9}/[-._;()/:A-Za-z0-9]+`

### Step 2 — Run the redaction pipeline

Use `redact_with_pymupdf` from the implementation inlined in Step 4:

```python
from pathlib import Path

result = redact_with_pymupdf(
    input_path=r"~\papers\submission.pdf",
    output_path=r"~\papers\submission_redacted.pdf",
    literal_patterns=[
        "John Smith",
        "Jane Doe",
        "Duke University",
        "Acme Research",
        "ICML 2024",
        "Equal contribution",
        "* Equal contribution",
    ],
    # regex_patterns defaults to email, arXiv ID, and DOI patterns
    min_retained_ratio=0.8,
)

print(f"Pages: {result.pages}")
print(f"Redactions applied: {result.redactions_applied}")
print(f"Retained ratio: {result.retained_ratio:.1%}")
```

### Step 3 — Three rules that keep redaction correct

1. **Stop at the References heading.** Everything from the bibliography onward stays untouched so self-citations survive. The heading is detected as a standalone line (normalized, case-insensitive, trailing colon stripped), not a loose substring — the word "references" appears in ordinary prose, and a substring match would wrongly cut the redaction short or skip half the paper.

2. **Redact only specific text matches.** Search for exact identifying strings and black out just those rectangles. This keeps you from removing surrounding sentences and makes the result auditable.

3. **Verify the output before trusting it.** A bug in a single pattern can silently blank most of a page. Re-open the saved PDF and confirm the page count is unchanged and the bulk of the text (80%+) remains.

### Step 4 — Reference implementation (PyMuPDF / fitz)

Full pipeline (copy into the project; this folder does not ship a helper module). The key components:

```python
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF >= 1.24 — older releases carry known parser CVEs

# Standalone headings that mark the start of back matter we must NOT redact.
_REFERENCE_HEADINGS: frozenset[str] = frozenset(
    {"references", "bibliography", "works cited"}
)

# Regexes run against extracted text first; search_for() only does literal
# matching, so we discover the concrete strings here and feed those back in.
_DEFAULT_REGEXES: Sequence[re.Pattern[str]] = (
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),   # emails
    re.compile(r"arXiv:\d{4}\.\d{4,5}(?:v\d+)?", re.IGNORECASE),     # arXiv IDs
    re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+"),                 # DOIs
)


@dataclass(frozen=True)
class RedactionResult:
    """Stats from a single redaction run, returned for logging and tests."""

    pages: int
    original_chars: int
    redacted_chars: int
    references_page: int | None
    redactions_applied: int

    @property
    def retained_ratio(self) -> float:
        if self.original_chars == 0:
            return 0.0
        return self.redacted_chars / self.original_chars


def _find_references_page(doc: fitz.Document) -> int | None:
    """Index of the first page whose text contains a bibliography heading.

    Matches the heading as a whole line (ignoring case and a trailing colon)
    rather than a substring: "references" appears all over normal prose, and a
    loose match would stop the redaction too early.
    """
    for page_num in range(doc.page_count):
        for raw_line in doc[page_num].get_text().splitlines():
            normalized = raw_line.strip().lower().rstrip(":")
            if normalized in _REFERENCE_HEADINGS:
                return page_num
    return None


def redact_with_pymupdf(
    input_path: str | Path,
    output_path: str | Path,
    literal_patterns: Sequence[str],
    regex_patterns: Sequence[re.Pattern[str]] = _DEFAULT_REGEXES,
    *,
    min_retained_ratio: float = 0.8,
) -> RedactionResult:
    """Redact identifying text from an academic PDF for blind review.

    ``literal_patterns`` (author names, affiliations, venues) are matched
    verbatim. ``regex_patterns`` (emails, arXiv IDs, DOIs) are located in the
    extracted text first, then the concrete matches are redacted. Everything
    from the References heading onward is left intact so self-citations survive.

    Returns a ``RedactionResult`` and raises *before* writing anything if the
    inputs look wrong, so a misconfigured call fails fast instead of producing a
    silently broken document.
    """
    in_path = Path(input_path)
    out_path = Path(output_path)

    # --- Validate inputs up front: cheaper to reject than to debug later. ---
    if not in_path.is_file():
        raise FileNotFoundError(f"Input PDF does not exist: {in_path}")
    if in_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input is not a .pdf file: {in_path}")
    if out_path.resolve() == in_path.resolve():
        raise ValueError(
            "Output path must differ from input — refusing to overwrite the "
            "source PDF, which would destroy the only un-redacted copy."
        )
    if not 0.0 < min_retained_ratio < 1.0:
        raise ValueError(
            f"min_retained_ratio must be in (0, 1); got {min_retained_ratio!r}"
        )

    # Drop blank/whitespace literals: search_for("") matches nothing useful and
    # a stray empty string is a sign the caller built the list incorrectly.
    literals: list[str] = [p.strip() for p in literal_patterns if p and p.strip()]
    if not literals and not regex_patterns:
        raise ValueError(
            "No usable patterns supplied — refusing to run a no-op redaction."
        )

    try:
        doc: fitz.Document = fitz.open(str(in_path))
    except Exception as exc:  # fitz raises a bare RuntimeError on malformed files
        raise RuntimeError(f"Could not open PDF {in_path}: {exc}") from exc

    try:
        original_chars = sum(
            len(doc[i].get_text()) for i in range(doc.page_count)
        )
        if original_chars == 0:
            raise ValueError(
                f"{in_path} has no extractable text — it is likely a scan. OCR it "
                "first; image-only PDFs need pixel redaction, not this skill."
            )

        references_page = _find_references_page(doc)
        redactions_applied = 0

        for page_num in range(doc.page_count):
            # Bibliography onward stays readable: self-citations must survive.
            if references_page is not None and page_num >= references_page:
                continue

            page: fitz.Page = doc[page_num]
            page_text = page.get_text()

            # Build the concrete set of strings to black out on this page.
            targets: set[str] = set(literals)
            for pattern in regex_patterns:
                targets.update(match.group(0) for match in pattern.finditer(page_text))

            for target in targets:
                for rect in page.search_for(target):
                    page.add_redact_annot(rect, fill=(0, 0, 0))
                    redactions_applied += 1

            # apply_redactions() physically deletes the covered glyphs. Without
            # it the text is still extractable under the black box — the classic
            # "redaction" that anyone can copy-paste straight back out.
            page.apply_redactions()

        redacted_chars = sum(
            len(doc[i].get_text()) for i in range(doc.page_count)
        )
        page_count = doc.page_count

        out_path.parent.mkdir(parents=True, exist_ok=True)
        # garbage=4 compacts the file so removed (redacted) objects are truly
        # gone, not just unreferenced; deflate=True keeps the output small.
        doc.save(str(out_path), garbage=4, deflate=True)
    finally:
        doc.close()

    result = RedactionResult(
        pages=page_count,
        original_chars=original_chars,
        redacted_chars=redacted_chars,
        references_page=references_page,
        redactions_applied=redactions_applied,
    )

    # Re-open and sanity-check the file we just wrote; raises on a bad result.
    verify_redaction(in_path, out_path, min_retained_ratio=min_retained_ratio)
    return result
```

## Pitfalls

### Never blank the References section

Self-citations live in the bibliography, and a reviewer uses the bibliography to check how the work relates to prior art. Anonymising it corrupts the evidence the review depends on. The right way to hide self-citation *signals* is to neutralise giveaway phrasing in the body ("in our prior work [12]"), not to delete the reference list.

### Never rely on a deprecated PDF library

As of 2026, PyMuPDF releases before 1.24 carry known parser CVEs that a malicious document can trigger. Pin a current stable release:

```powershell
pip install "PyMuPDF>=1.24"
```

### Never redact regions or pages — only specific strings

Region- or page-level redaction destroys the content a reviewer needs and almost always removes far more than the identifying strings.

```python
import fitz

page: fitz.Page = doc[0]

# AVOID — get_text("blocks") returns every text block on the page, so this
# redacts the entire page and the reviewer is left with nothing to read.
for block in page.get_text("blocks"):
    rect = fitz.Rect(block[:4])
    page.add_redact_annot(rect, fill=(0, 0, 0))

# AVOID — draw_rect() only paints a black box on top. The underlying text is
# untouched and still selectable, so the "redacted" names copy-paste right out.
page.draw_rect(fitz.Rect(0, 0, 600, 100), fill=(0, 0, 0))

# CORRECT — target one known string, black out only its rectangles, then apply.
for rect in page.search_for("John Smith"):
    page.add_redact_annot(rect, fill=(0, 0, 0))
page.apply_redactions()  # actually removes the glyphs, not just covers them
```

### Never redact bare surnames

A lone surname like "Smith" collides with unrelated cited authors and would scrub legitimate citations. Always redact the complete name ("John Smith").

### Never overwrite the source PDF

The output path must differ from the input path. Overwriting the source destroys the only un-redacted copy.

### `apply_redactions()` is mandatory

Without `page.apply_redactions()`, the text is still extractable under the black box — the classic "redaction" that anyone can copy-paste straight back out. The annotation alone does not remove glyphs.

### Scanned PDFs have no text layer

If `original_chars == 0`, the PDF is likely a scan. OCR it first; image-only PDFs need pixel redaction, not this skill.

## Verification

Redaction bugs are easy to ship because the output still *looks* like a PDF. Verification is not optional — it is the step that turns a silent corruption into a loud failure. Re-open the saved file and check it independently of the code that produced it.

Use the verification function inlined below and run it against both the original and redacted PDF:

```python
from __future__ import annotations

from pathlib import Path

import fitz


def verify_redaction(
    original_path: str | Path,
    output_path: str | Path,
    *,
    min_retained_ratio: float = 0.8,
) -> None:
    """Re-open both PDFs and fail loudly if the redaction looks destructive.

    Checks three things, each guarding a real failure mode:
      * page count unchanged       — redaction must not add or drop pages;
      * a sane amount of text left — guards against a fully blanked document;
      * retained ratio >= floor    — guards against an over-broad pattern.

    Raises on any failure; returns None on success.
    """
    orig_path = Path(original_path)
    out_path = Path(output_path)
    if not orig_path.is_file():
        raise FileNotFoundError(f"Original PDF missing: {orig_path}")
    if not out_path.is_file():
        raise FileNotFoundError(f"Redacted PDF missing: {out_path}")
    if not 0.0 < min_retained_ratio < 1.0:
        raise ValueError(
            f"min_retained_ratio must be in (0, 1); got {min_retained_ratio!r}"
        )

    orig: fitz.Document = fitz.open(str(orig_path))
    try:
        redc: fitz.Document = fitz.open(str(out_path))
    except Exception as exc:  # malformed output is itself a redaction failure
        orig.close()
        raise RuntimeError(f"Redacted PDF is unreadable: {exc}") from exc

    try:
        orig_pages = orig.page_count
        redc_pages = redc.page_count
        orig_chars = sum(len(orig[i].get_text()) for i in range(orig_pages))
        redc_chars = sum(len(redc[i].get_text()) for i in range(redc_pages))
    finally:
        orig.close()
        redc.close()

    retained = redc_chars / orig_chars if orig_chars else 0.0
    print(f"Original: {orig_pages} pages, {orig_chars} chars")
    print(f"Redacted: {redc_pages} pages, {redc_chars} chars")
    print(f"Retained: {retained:.1%}")

    if redc_pages != orig_pages:
        raise ValueError(
            f"Page count changed ({orig_pages} -> {redc_pages}); redaction must "
            "never add or remove pages."
        )
    if redc_chars < 1000:
        raise ValueError(
            f"Only {redc_chars} chars remain — the document was almost certainly "
            "blanked. Look for an over-broad pattern or an accidental full-page "
            "redaction."
        )
    if retained < min_retained_ratio:
        raise ValueError(
            f"Retained only {retained:.0%} of the text (floor is "
            f"{min_retained_ratio:.0%}); too much was removed to trust the output."
        )

    print("Verification passed.")
```

### Verification checklist

- [ ] Run the checks below against a known sample paper and confirm they pass.
- [ ] Open the redacted PDF and confirm the References section is fully intact.
- [ ] Confirm `retained_ratio` is at least 0.8 (80% of the original text kept).
- [ ] Try to copy-paste a redacted name out of the saved PDF — it must be gone, not merely hidden under a box.
- [ ] Confirm no exceptions or warnings were raised during the run.
- [ ] Confirm PyMuPDF is >= 1.24 so you are clear of the deprecated-parser CVEs:

```powershell
python -c "import fitz; print(fitz.VersionBind)"
```

## Related Skills

- **Scanned / image-only PDFs** have no text layer for `search_for` to hit. Run OCR to recover text, or use an image-redaction skill that paints over the pixels and re-flattens the page so the original raster is gone.
- **Plain-text or office documents** (`.txt`, `.docx`, `.md`) carry no PDF geometry; a text-redaction skill that operates on the string content is simpler and safer than forcing them through PyMuPDF.
