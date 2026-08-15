---
name: cvss-score-extraction
version: 1.1.1
description: "Selects one CVSS base score from untrusted Trivy/Grype JSON: version-major then NVD then GHSA then Red Hat, coerce 0.0-10.0, map official buckets, keep float|None until display. Trigger when a scanner finding must become a comparable number for reports or High/Critical triage. Not a CVSS v4 parser, not a live NVD/GHSA poller, and not Microsoft/Oracle vendor risk indexes."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# CVSS Score Extraction from Vulnerability Data

This skill turns messy, machine-generated, *untrusted* scanner output into a single trustworthy CVSS score your security report can stand behind — and is explicit when no such score exists rather than inventing one.

Scanners such as Trivy and Grype rarely give you one clean number: they attach several competing scores from different databases, sometimes for the same CVE, and sometimes none at all. The code here resolves that ambiguity through a defined source-priority cascade with full validation.

## When to Use

Reach for this skill when you are turning vulnerability data into decisions or documents:

- **Extracting CVSS scores from scan results (Trivy, Grype, etc.)** — the score is the field humans and dashboards sort on, so getting it right drives everything downstream.
- **Generating security reports that need standardized severity metrics** — a consistent 0–10 score lets you compare findings across packages and tools.
- **Implementing fallback logic when the primary database lacks a score** — real reports break when one source is missing; you need a defined cascade, not an exception.
- **Prioritizing remediation against authoritative assessments** — engineers have limited time; the score decides what gets fixed first.
- **Building automated triage pipelines** — automation must behave predictably on partial and malformed data, which is exactly what the validation here is for.

### Do Not Use

Each item below is out of scope for a concrete reason:

- **When the data has no CVSS fields at all** — fall back to the scanner's qualitative `Severity` label instead. Forcing a numeric score onto label-only data invents precision that does not exist.
- **For CVSS v4 scoring** — v4 introduced a new metric model and vector format this skill does not parse. Feeding v4 vectors through v3 logic silently mislabels findings.
- **When you need real-time scores** — embedded scanner data is a point-in-time snapshot. If a score may have been revised since the scan, query the NVD/GHSA APIs live rather than trusting cached fields.
- **For non-CVE identifiers with no CVSS mapping** — vendor-internal advisory IDs often carry no CVSS at all, so extraction has nothing to work with.
- **When vendor-specific scoring is the only source** — schemes like Microsoft's Exploitability Index or Oracle's risk matrix are not CVSS and are not directly comparable to a CVSS base score.
- **Deprecation note** — CVSS v2 uses a different, less expressive metric model; this skill consults it only as a last-resort fallback. Prefer v3/v3.1 for any new assessment, and you can disable the v2 fallback entirely (see below).
- **Security note** — scanner output is data from an external tool and can be truncated or tampered with. Every function here treats its input as untrusted and rejects scores outside the spec-defined range, so corrupt data fails closed (becomes "no score") instead of propagating a fake severity.

## Prerequisites

- **Python 3.10+** — the implementation uses `from __future__ import annotations`, `match`-compatible type unions, and `dataclass(frozen=True)`.
- **mypy** (optional but recommended) — type-check the modules to catch shape errors: `pip install mypy`
- **A Trivy or Grype JSON report** — generate one with `trivy image --format json -o report.json <image>` or `grype <image> -o json > report.json`.
- **Windows host (PowerShell)** — all commands below assume PowerShell. On Windows, use `python` (not `python3`). Path separators in commands use backslashes for Windows, but `pathlib.Path` in the code handles both.

## Procedure

### Overview

CVSS gives every vulnerability a single number from 0.0 to 10.0 so that unrelated findings can be ranked on one scale. That comparability is the whole point: it is what lets a report say "fix this one before that one." The difficulty is that the number you want is buried inside a nested structure with multiple potential providers, so extraction is really a *selection* problem — choosing the most authoritative, most modern score that is actually present.

### Step 1 — Understand the CVSS scale and severity buckets

CVSS maps a numeric score onto a qualitative severity bucket:

| Score Range | Severity Level | Description        |
|-------------|----------------|--------------------|
| 0.0         | None           | No impact          |
| 0.1–3.9     | **Low**        | Minimal impact     |
| 4.0–6.9     | **Medium**     | Moderate impact    |
| 7.0–8.9     | **High**       | Significant impact |
| 9.0–10.0    | **Critical**   | Severe impact      |

These boundaries matter because alerting and SLAs are usually written against the *bucket* ("page on Critical, ticket on High"), not the raw number. If your bucketing logic is off by a tenth at a boundary, you can silently miss pages, so the mapping in this skill matches the official ranges exactly.

**CVSS Versions:**

- **CVSS v2** — legacy model on a 0–10 scale, but with different metrics that are *not* interchangeable with v3.
- **CVSS v3** — the current standard with refined exploitability and impact metrics.
- **CVSS v3.1** — a minor clarification of v3; scores are read the same way.
- **CVSS v4** — the newest version; out of scope here.

Prefer a v3/v3.1 score whenever one exists, because mixing v2 and v3 numbers in the same report compares values produced by different formulas.

### Step 2 — Understand the source priority cascade

A single scan often carries several independent scorings of the same CVE, because the scanner aggregates upstream databases.

**Common sources (ordered by priority):**

1. **NVD (National Vulnerability Database)** — maintained by NIST. Broadest, most consistently reviewed coverage. **Priority: highest.**
2. **GHSA (GitHub Security Advisory)** — community-curated, excellent for the open-source package ecosystem. **Priority: medium.**
3. **Red Hat Security Data** — a single distribution's impact analysis, often scored for a hardened/back-ported build. **Priority: lowest.**

**Why more than one source exists:**

- Coverage gaps: no single database scores every CVE, so you need fallbacks.
- Legitimate disagreement: the same CVE can score differently depending on how a vendor builds and ships the affected component.
- Recency: one source may have an updated score while another still shows the original.

The cascade is:

```
NVD → GHSA → Red Hat → (no score)
```

**Why this order:** NVD is the most comprehensive and independently reviewed, so it is the default authority. GHSA comes next because it is high-quality but community-curated. Vendor feeds like Red Hat sit last because they reflect one distribution's view, which can legitimately differ from the upstream score — useful as a fallback, but not the number you want to lead with when a broader assessment exists.

### Step 3 — Understand the data structure

Trivy (and similar tools) nest CVSS data per source. A single finding looks like this — note that the three sources here do **not** all agree:

```json
{
  "VulnerabilityID": "CVE-2021-44906",
  "PkgName": "minimist",
  "InstalledVersion": "1.2.5",
  "FixedVersion": "1.2.6",
  "Severity": "CRITICAL",
  "Title": "minimist: prototype pollution",
  "CVSS": {
    "nvd": {
      "V2Vector": "AV:N/AC:L/Au:N/C:P/I:P/A:P",
      "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "V2Score": 7.5,
      "V3Score": 9.8
    },
    "ghsa": {
      "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "V3Score": 9.8
    },
    "redhat": {
      "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L",
      "V3Score": 5.3
    }
  }
}
```

Red Hat scores this CVE **5.3** while NVD scores it **9.8** — the same flaw, assessed against a different build. The priority order is what decides your report shows 9.8, not 5.3. This is precisely why a defined cascade beats "grab the first score you find."

### Step 4 — Create the core extraction module

Save this as `cvss_extraction.py`. The implementation treats scanner output as **untrusted input** — that single decision drives every design choice:

- Public functions accept `object`, not a convenient `dict` or `Any`. Using `object` (rather than `typing.Any`) keeps the type checker switched *on*: it forces an explicit `isinstance` narrowing at every step instead of letting unchecked attribute access slip through. `Any` would silence exactly the errors we want to catch.
- Scores are validated against the spec range `0.0–10.0`, so corrupt or tampered values fail closed (treated as "no score") instead of poisoning a report.
- The result is a small typed object, not a `float | "N/A"` union. Mixing a sentinel string into a numeric field forces every caller to re-check the type before doing arithmetic; a `float | None` score plus a separate formatter keeps the data clean and pushes the "N/A" string to the presentation edge.

```python
"""cvss_extraction.py — typed, defensive CVSS score extraction.

Every public function treats its argument as untrusted: scanner output is
machine-generated JSON that can be truncated, reshaped by a tool upgrade, or
deliberately tampered with. We therefore narrow `object` to concrete types at
each step instead of trusting the shape, and we reject any score that falls
outside the CVSS-defined 0.0-10.0 range.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Literal

# Ordered most-authoritative first. NVD (NIST) has the broadest, most
# consistently reviewed coverage; GHSA is excellent for the open-source
# ecosystem but community-curated; vendor feeds such as Red Hat reflect a
# single distribution's impact analysis and can legitimately differ from the
# upstream score, so they sit last.
SOURCE_PRIORITY: Final[tuple[str, ...]] = ("nvd", "ghsa", "redhat")

# The CVSS specification bounds every base score to this closed interval.
SCORE_MIN: Final[float] = 0.0
SCORE_MAX: Final[float] = 10.0


class Severity(str, Enum):
    """Qualitative severity buckets defined by the CVSS v3 specification."""

    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


def severity_from_score(score: float | None) -> Severity:
    """Map a numeric CVSS score onto its qualitative bucket.

    Alerting and SLAs key off the bucket, so the boundaries must match the
    official ranges exactly: 0.0 is None, 0.1-3.9 Low, 4.0-6.9 Medium,
    7.0-8.9 High, 9.0-10.0 Critical. A missing score is UNKNOWN rather than
    None, because "we have no data" is operationally different from "the
    vendor scored this as harmless."
    """
    if score is None:
        return Severity.UNKNOWN
    if score == 0.0:
        return Severity.NONE
    if score < 4.0:
        return Severity.LOW
    if score < 7.0:
        return Severity.MEDIUM
    if score < 9.0:
        return Severity.HIGH
    return Severity.CRITICAL


def _coerce_score(raw: object) -> float | None:
    """Return a valid CVSS score, or None when the value cannot be trusted.

    `raw` comes straight from parsed JSON, so it may be a string, list, null,
    or a number outside the legal range. We accept only a real number inside
    0.0-10.0. `bool` is special-cased because in Python `bool` subclasses
    `int`; without this guard `True` would be accepted as the score 1.0.
    """
    if isinstance(raw, bool):
        return None
    if not isinstance(raw, (int, float)):
        return None
    score = float(raw)
    if not SCORE_MIN <= score <= SCORE_MAX:
        return None
    return score


@dataclass(frozen=True)
class CvssResult:
    """The outcome of a single extraction attempt.

    Keeping `score` as `float | None` (instead of the older `float | "N/A"`
    union) means downstream code never has to guard against a string sneaking
    into a comparison. The literal "N/A" is a presentation concern and lives
    in `format_score`, at the edge of the system.
    """

    score: float | None
    version: Literal["v2", "v3"] | None
    source: str | None

    @property
    def is_available(self) -> bool:
        return self.score is not None

    @property
    def severity(self) -> Severity:
        return severity_from_score(self.score)


_UNAVAILABLE: Final[CvssResult] = CvssResult(score=None, version=None, source=None)


def extract_cvss(vuln_data: object, *, allow_v2_fallback: bool = True) -> CvssResult:
    """Extract the best available CVSS score from one vulnerability record.

    Resolution order is deliberately *version-major, source-minor*: every
    source is checked for a v3 score before any v2 score is considered. A v3
    score from a lower-priority source is still more comparable across a modern
    report than a legacy v2 score, and CVSS v2 uses a metric model that is not
    interchangeable with v3. v2 is consulted only as a last resort, and can be
    turned off entirely for pipelines that must stay v3-consistent.

    Args:
        vuln_data: A single vulnerability object, treated as untrusted input.
        allow_v2_fallback: When False, never return a v2 score even if it is
            the only score present.

    Returns:
        A CvssResult; ``is_available`` is False when no usable score was found.
    """
    if not isinstance(vuln_data, dict):
        return _UNAVAILABLE

    cvss_block = vuln_data.get("CVSS")
    if not isinstance(cvss_block, dict):
        return _UNAVAILABLE

    for source in SOURCE_PRIORITY:
        entry = cvss_block.get(source)
        if not isinstance(entry, dict):
            continue
        score = _coerce_score(entry.get("V3Score"))
        if score is not None:
            return CvssResult(score=score, version="v3", source=source)

    if allow_v2_fallback:
        for source in SOURCE_PRIORITY:
            entry = cvss_block.get(source)
            if not isinstance(entry, dict):
                continue
            score = _coerce_score(entry.get("V2Score"))
            if score is not None:
                return CvssResult(score=score, version="v2", source=source)

    return _UNAVAILABLE


def format_score(result: CvssResult) -> str:
    """Render a score for display, using "N/A" only at the presentation edge."""
    if result.score is None:
        return "N/A"
    return f"{result.score:.1f}"
```

### Step 5 — Create the Trivy report parser

Save this as `trivy_ingest.py`. It walks Trivy's `Results → Vulnerabilities` nesting while staying just as defensive about shape. A malformed or missing report is surfaced as a precise exception rather than an empty list, because an "all clear" result that actually came from a broken scan is the most dangerous failure mode in a security pipeline.

```python
"""trivy_ingest.py — turn a Trivy JSON report into typed records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from cvss_extraction import CvssResult, extract_cvss


@dataclass(frozen=True)
class VulnerabilityRecord:
    """A normalized, report-ready view of one finding."""

    package: str
    installed_version: str
    cve_id: str
    reported_severity: str
    cvss: CvssResult
    fixed_version: str | None
    title: str


def _as_str(raw: object, default: str) -> str:
    """Coerce an untrusted JSON value to a non-empty string, or a default."""
    return raw if isinstance(raw, str) and raw.strip() else default


def _as_optional_str(raw: object) -> str | None:
    """Like _as_str, but preserve the difference between empty and absent."""
    return raw if isinstance(raw, str) and raw.strip() else None


def _to_record(vuln: dict[str, object]) -> VulnerabilityRecord:
    return VulnerabilityRecord(
        package=_as_str(vuln.get("PkgName"), "unknown"),
        installed_version=_as_str(vuln.get("InstalledVersion"), "unknown"),
        cve_id=_as_str(vuln.get("VulnerabilityID"), "UNKNOWN-ID"),
        reported_severity=_as_str(vuln.get("Severity"), "UNKNOWN").upper(),
        cvss=extract_cvss(vuln),
        fixed_version=_as_optional_str(vuln.get("FixedVersion")),
        title=_as_str(vuln.get("Title"), "No description provided"),
    )


def parse_trivy_report(path: str | Path) -> list[VulnerabilityRecord]:
    """Read a Trivy JSON report and return typed records.

    Failures become precise, actionable exceptions instead of silent empty
    results: a missing or malformed report almost always means a broken scan
    step the operator must fix, and hiding it would let a non-scan masquerade
    as a clean bill of health.
    """
    report_path = Path(path)
    try:
        with report_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Trivy report not found: {report_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Trivy report is not valid JSON ({report_path}): {exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise ValueError("Trivy report root must be a JSON object")

    records: list[VulnerabilityRecord] = []
    results = raw.get("Results")
    if not isinstance(results, list):
        # A report with no Results array is legitimate: nothing was scanned or
        # nothing was found. Return empty rather than raising.
        return records

    for result in results:
        if not isinstance(result, dict):
            continue
        vulnerabilities = result.get("Vulnerabilities")
        if not isinstance(vulnerabilities, list):
            continue
        for vuln in vulnerabilities:
            if isinstance(vuln, dict):
                records.append(_to_record(vuln))

    return records
```

### Step 6 — Use the common patterns

All patterns build on the single `extract_cvss` call, so there is one well-tested code path instead of several variants that drift apart over time.

**Pattern 1 — numeric value, formatted only for display:**

```python
from cvss_extraction import extract_cvss, format_score

result = extract_cvss(vuln)

numeric_score: float | None = result.score   # 9.8, or None when absent
display_score: str = format_score(result)     # "9.8", or "N/A" for display
```

Keep the machine-readable value (`float | None`) separate from the human-readable string. Reports render `display_score`; any thresholding or sorting uses `numeric_score` without first stripping a sentinel.

**Pattern 2 — full provenance for audit-grade reports:**

```python
if result.is_available:
    print(f"{result.score:.1f} ({result.version}, source={result.source})")
    # e.g. "9.8 (v3, source=nvd)"
```

When two sources disagree (recall NVD 9.8 vs Red Hat 5.3), an auditor needs to see *which* source and *which* version produced the number, not just the number.

**Pattern 3 — qualitative bucket from the same result:**

```python
bucket = result.severity   # e.g. Severity.CRITICAL; Severity.UNKNOWN if absent
```

The bucket is derived from the score by the spec's official ranges, so deriving it here guarantees the table's severity column and your alerting agree.

### Step 7 — Implement threshold filtering for triage

Triage usually asks a yes/no question: "is this urgent enough to act on now?" Prefer the numeric score because it is comparable across findings, but when no score exists, fall back to the scanner's own label rather than dropping the finding — an *unscored* CVE is more dangerous to ignore than a scored one, so absence of data must never silently downgrade it.

```python
from cvss_extraction import extract_cvss


def is_high_priority(vuln_data: object, *, threshold: float = 7.0) -> bool:
    """Decide whether a finding warrants urgent remediation.

    Uses the numeric CVSS score when available. When it is absent, falls back
    to the scanner's qualitative severity label so unscored findings are never
    silently dropped.
    """
    result = extract_cvss(vuln_data)
    if result.is_available:
        return result.score is not None and result.score >= threshold

    # No numeric score — use the scanner's own label as a conservative fallback.
    if isinstance(vuln_data, dict):
        severity = vuln_data.get("Severity")
        if isinstance(severity, str):
            return severity.upper() in ("HIGH", "CRITICAL")
    return False
```

### Step 8 — Generate a report

Save this as `generate_report.py`. It ties the pieces together: ingests a Trivy report and prints a severity-sorted table. It imports the two modules defined above (`cvss_extraction.py` and `trivy_ingest.py`), so there is no duplicated logic.

```python
"""generate_report.py — print a CVSS-annotated vulnerability table."""

from __future__ import annotations

import sys

from cvss_extraction import format_score
from trivy_ingest import VulnerabilityRecord, parse_trivy_report


def render_table(records: list[VulnerabilityRecord]) -> str:
    header = (
        f"{'Package':<20} {'CVE ID':<18} {'CVSS':<6} "
        f"{'Source':<8} {'Severity':<10}"
    )
    lines = [header, "-" * len(header)]

    # Sort most-severe first so the table leads with what to fix now. Unscored
    # findings sort to the bottom (key -1.0) but are still listed, never dropped.
    ordered = sorted(
        records,
        key=lambda r: r.cvss.score if r.cvss.score is not None else -1.0,
        reverse=True,
    )
    for record in ordered:
        lines.append(
            f"{record.package:<20} "
            f"{record.cve_id:<18} "
            f"{format_score(record.cvss):<6} "
            f"{(record.cvss.source or '-'):<8} "
            f"{record.cvss.severity.value:<10}"
        )
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python generate_report.py <trivy_report.json>", file=sys.stderr)
        return 2
    try:
        records = parse_trivy_report(argv[1])
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(render_table(records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

Running it against the sample data shown earlier prints the NVD score (9.8), not the Red Hat score (5.3), and labels the row `Critical`:

```
Package              CVE ID             CVSS   Source   Severity
-----------------------------------------------------------------
minimist             CVE-2021-44906     9.8    nvd      Critical
```

On Windows (PowerShell):

```powershell
python generate_report.py .\trivy_report.json
```

## Examples

### Complete test suite

Save this as `tests/test_cvss_extraction.py`. It covers the priority cascade, the v2 fallback toggle, malformed input, and the score-validation guards.

```python
"""tests/test_cvss_extraction.py — behavioral tests for the extractor."""

from __future__ import annotations

import unittest

from cvss_extraction import (
    CvssResult,
    Severity,
    extract_cvss,
    format_score,
    severity_from_score,
)


class ExtractCvssTests(unittest.TestCase):
    def test_prefers_nvd_v3(self) -> None:
        vuln = {"CVSS": {"nvd": {"V3Score": 9.8}, "ghsa": {"V3Score": 7.1}}}
        result = extract_cvss(vuln)
        self.assertEqual(result.score, 9.8)
        self.assertEqual(result.version, "v3")
        self.assertEqual(result.source, "nvd")

    def test_falls_back_to_ghsa_when_nvd_missing(self) -> None:
        vuln = {"CVSS": {"ghsa": {"V3Score": 7.1}}}
        result = extract_cvss(vuln)
        self.assertEqual(result.source, "ghsa")
        self.assertEqual(result.score, 7.1)

    def test_falls_back_to_redhat_last(self) -> None:
        vuln = {"CVSS": {"redhat": {"V3Score": 5.3}}}
        self.assertEqual(extract_cvss(vuln).source, "redhat")

    def test_v3_from_lower_source_beats_v2_from_higher_source(self) -> None:
        vuln = {"CVSS": {"nvd": {"V2Score": 7.5}, "ghsa": {"V3Score": 6.1}}}
        result = extract_cvss(vuln)
        self.assertEqual(result.version, "v3")
        self.assertEqual(result.source, "ghsa")

    def test_v2_fallback_when_no_v3(self) -> None:
        vuln = {"CVSS": {"nvd": {"V2Score": 7.5}}}
        result = extract_cvss(vuln)
        self.assertEqual(result.version, "v2")
        self.assertEqual(result.score, 7.5)

    def test_v2_fallback_can_be_disabled(self) -> None:
        vuln = {"CVSS": {"nvd": {"V2Score": 7.5}}}
        self.assertFalse(extract_cvss(vuln, allow_v2_fallback=False).is_available)

    def test_missing_cvss_block_is_unavailable(self) -> None:
        self.assertFalse(extract_cvss({"Severity": "HIGH"}).is_available)

    def test_non_dict_input_is_unavailable(self) -> None:
        self.assertFalse(extract_cvss(None).is_available)
        self.assertFalse(extract_cvss("not-a-dict").is_available)

    def test_rejects_out_of_range_score(self) -> None:
        # The corrupt 42.0 is skipped; the next valid source wins.
        vuln = {"CVSS": {"nvd": {"V3Score": 42.0}, "ghsa": {"V3Score": 8.0}}}
        result = extract_cvss(vuln)
        self.assertEqual(result.score, 8.0)
        self.assertEqual(result.source, "ghsa")

    def test_rejects_bool_masquerading_as_score(self) -> None:
        self.assertFalse(extract_cvss({"CVSS": {"nvd": {"V3Score": True}}}).is_available)

    def test_rejects_string_score(self) -> None:
        self.assertFalse(extract_cvss({"CVSS": {"nvd": {"V3Score": "9.8"}}}).is_available)


class SeverityTests(unittest.TestCase):
    def test_buckets_match_spec_boundaries(self) -> None:
        self.assertEqual(severity_from_score(0.0), Severity.NONE)
        self.assertEqual(severity_from_score(3.9), Severity.LOW)
        self.assertEqual(severity_from_score(4.0), Severity.MEDIUM)
        self.assertEqual(severity_from_score(6.9), Severity.MEDIUM)
        self.assertEqual(severity_from_score(7.0), Severity.HIGH)
        self.assertEqual(severity_from_score(9.0), Severity.CRITICAL)
        self.assertEqual(severity_from_score(None), Severity.UNKNOWN)


class FormatScoreTests(unittest.TestCase):
    def test_formats_number_to_one_decimal(self) -> None:
        self.assertEqual(format_score(CvssResult(9.8, "v3", "nvd")), "9.8")

    def test_formats_missing_as_na(self) -> None:
        self.assertEqual(format_score(CvssResult(None, None, None)), "N/A")


if __name__ == "__main__":
    unittest.main()
```

## Pitfalls

1. **Never mix CVSS versions in the same report.** A v2 score and a v3 score are not interchangeable — they use different metric models. The extractor is *version-major, source-minor*: it checks every source for a v3 score before considering any v2 score. If you need strict v3 consistency, pass `allow_v2_fallback=False`.
2. **Never trust a single source blindly.** NVD, GHSA, and Red Hat can legitimately disagree (e.g., NVD 9.8 vs Red Hat 5.3 for the same CVE). The priority cascade resolves this to the most authoritative available view, but you should record provenance in detailed reports so auditors can reconcile.
3. **Respect the source hierarchy.** NVD first, then GHSA, then vendor feeds — so divergent scores resolve to the most authoritative available view.
4. **Validate at the boundary.** Treat scanner JSON as untrusted: narrow types with `isinstance` and bound scores to 0.0–10.0 so tampered data fails safely. A `bool` value like `True` would be accepted as score `1.0` without the explicit `isinstance(raw, bool)` guard because `bool` subclasses `int` in Python.
5. **Keep data and presentation separate.** Store `float | None`; render "N/A" only when displaying. This stops sentinel strings from leaking into logic — a `float | "N/A"` union forces every caller to re-check the type before doing arithmetic.
6. **Record provenance in detailed reports.** Note the version and source next to the score so a reader can reconcile disagreements between databases.
7. **Never silently drop unscored findings.** An unscored CVE is more dangerous to ignore than a scored one. When no numeric score exists, fall back to the scanner's qualitative `Severity` label for triage decisions.
8. **Do not parse CVSS v4 vectors with v3 logic.** v4 introduced a new metric model and vector format. Feeding v4 vectors through v3 logic silently mislabels findings.
9. **Do not treat scanner data as real-time.** Embedded scanner data is a point-in-time snapshot. If a score may have been revised since the scan, query the NVD/GHSA APIs live.
10. **A broken scan must not look like a clean bill of health.** `parse_trivy_report` raises precise exceptions on missing or malformed files rather than returning an empty list, because an "all clear" from a broken scan is the most dangerous failure mode in a security pipeline.

## Verification

Run these checks to confirm the extraction logic is correct:

```powershell
# 1. Type-check the modules (requires mypy)
python -m mypy cvss_extraction.py trivy_ingest.py

# 2. Run the test suite
python -m unittest discover -s tests -p 'test_*.py'

# 3. Generate a report from a real Trivy scan
python generate_report.py .\trivy_report.json
```

Checklist — verify each behavior:

- [ ] Basic extraction returns the NVD v3 score when NVD data is present
- [ ] Fallback works: NVD missing → GHSA score is used and `source == "ghsa"`
- [ ] Fallback works: NVD/GHSA missing → Red Hat score is used
- [ ] Cross-version rule holds: a v3 score from GHSA beats a v2 score from NVD
- [ ] v2 fallback returns the NVD v2 score when no v3 exists anywhere
- [ ] `allow_v2_fallback=False` yields no score rather than a v2 score
- [ ] No usable score → `is_available` is False (the "N/A" case)
- [ ] Malformed input (None, list, string, missing `CVSS`) is handled safely
- [ ] Out-of-range, boolean, and string scores are rejected by `_coerce_score`
- [ ] `severity_from_score` returns the correct bucket at every range boundary
- [ ] Threshold filtering falls back to the severity label when no score exists
- [ ] `parse_trivy_report` raises a clear error on a missing or non-JSON file

## Related skills

- **vulnerability-scanning** — for scanning container images and filesystems
- **security-report-generation** — for building comprehensive security reports
- **cve-enrichment** — for enriching CVE data with additional context
- **compliance-checking** — for mapping CVSS scores to compliance frameworks
