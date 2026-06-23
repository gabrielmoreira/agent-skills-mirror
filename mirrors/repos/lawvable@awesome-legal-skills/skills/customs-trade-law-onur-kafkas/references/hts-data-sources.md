# HTS Data Sources And Revision Protocol

## Purpose

Use this protocol whenever HTS data supports classification, GRI 6 hierarchy, duty rates, Chapter 99 references, quota notes, or source freshness statements.

The goal is not just to fetch a JSON file. The goal is to prove which HTS revision was used, how it was selected, and whether a more current source might exist.

## Source Priority

### 1. Data.gov Catalog Metadata

Data.gov is the preferred discovery point for HTS bulk JSON because its catalog record lists the current year dataset and the available revision distributions.

Discovery pattern:

1. Search Data.gov for `Harmonized Tariff Schedule of the United States`.
2. Prefer the dataset title matching the current calendar year.
3. Inspect the dataset `distribution` list.
4. Select the highest current-year `HTS Revision N (JSON)` distribution.
5. If no current-year revision exists, select the current-year `HTS Basic Edition (JSON)`.
6. Record the Data.gov catalog page, source landing page if present, catalog checked or harvest date if available, selected revision title, and JSON download URL.

Current API guidance is documented by Data.gov at `https://resources.data.gov/catalog-api/`. Data.gov has warned that its API base URL may change as APIs move through `api.data.gov`, so do not treat one API host as permanent. For implementation, prefer a configurable base URL and fall back to the human-readable catalog page when API behavior changes.

Helper script:

```text
python3 scripts/resolve-latest-hts-json.py
python3 scripts/resolve-latest-hts-json.py --year 2026
python3 scripts/resolve-latest-hts-json.py --json
```

The helper is non-authoritative. It resolves and prints catalog metadata; the legal analysis still must record and reason from the selected source.

### 2. USITC HTS Archive

If Data.gov is unavailable or incomplete, use the USITC HTS archive:

```text
https://www.usitc.gov/tata/hts/archive/index.htm
```

Select the current year and highest available revision JSON. Record that Data.gov was unavailable or incomplete and identify the archive page used.

### 3. USITC Current HTS / Release Pages

If the archive cannot be used, use USITC current HTS or release pages:

```text
https://hts.usitc.gov/
https://www.usitc.gov/harmonized_tariff_information
```

This is a fallback for rate checks and chapter files. Record the limitation if a bulk JSON revision cannot be verified.

## Required HTS Source Record

Include this compact block in classification, duty, Chapter 99, and compliance deliverables:

```text
HTS Source Record
- Catalog/source URL: {Data.gov catalog URL or fallback URL}
- Source landing URL: {USITC/source page if provided}
- Catalog checked / harvested: {date or "not available"}
- Selected HTS release: {e.g., 2026 HTS Revision 7 (JSON)}
- JSON download URL: {URL}
- HTS revision used: {revision identifier}
- Analysis date: {date}
- Source limitations: {none / fallback used / API unavailable / notes}
```

## Selection Rules

- Do not hard-code revision-specific USITC file URLs as primary sources.
- Treat revision URLs as artifacts discovered through catalog metadata.
- Do not assume "Basic Edition" is current when current-year revisions exist.
- Do not compare two candidate subheadings by stale hierarchy if a newer current-year revision is available.
- If current-year metadata is internally inconsistent, state the inconsistency and use live USITC REST plus current chapter files until the bulk JSON can be confirmed.

## HTS JSON Schema

The USITC bulk JSON is a flat list. Expected fields include:

| Field | Use |
|---|---|
| `htsno` | HTS number. Empty rows can be labels or grouping headers. |
| `indent` | Hierarchy depth. Required for GRI 6 same-level comparison. |
| `description` | Legal/statistical description for the row. |
| `superior` | Hierarchy label indicator. Treat `true`, `"true"`, and `"True"` as true. |
| `units` | Units of quantity. May be an array or empty. |
| `general` | Column 1 General rate. |
| `special` | Special program rate string and program codes. |
| `other` | Column 2 rate. |
| `footnotes` | Footnotes, including possible Chapter 99 references. |
| `quotaQuantity` | Quota or quantity metadata when present. |
| `additionalDuties` | Additional duty metadata when present. |
| `addiitionalDuties` | Observed misspelling; treat as equivalent to `additionalDuties`. |

## Hierarchy Rules

- Empty `htsno` rows are not throwaway rows. They may carry labels that define the hierarchy.
- `superior: true` rows are grouping labels.
- `indent` controls parent-child relationships.
- GRI 6 comparisons are only between subheadings at the same indentation level under the same parent.
- Use `scripts/hts-hierarchy-builder.py` for local hierarchy exploration when bulk JSON is available.

## Chapter 99 Cross-Reference Review

Before presenting a duty or trade remedy conclusion:

1. Inspect `footnotes` on the target HTS row and parent rows.
2. Inspect `additionalDuties` and `addiitionalDuties`.
3. Search the selected JSON for referenced Chapter 99 subheadings.
4. Verify current status against official USTR, Federal Register, USITC, Commerce, or proclamation sources.
5. Record effective dates, expiration dates, exclusions, and unresolved ambiguity.
