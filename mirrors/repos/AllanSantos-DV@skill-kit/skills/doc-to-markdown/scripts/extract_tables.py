"""
Extract tables from PDF or Excel files as Markdown tables.

Usage:
    python extract_tables.py report.pdf                    # all tables from all pages
    python extract_tables.py report.pdf -p 1,3,5           # specific pages
    python extract_tables.py data.xlsx                     # all sheets
    python extract_tables.py data.xlsx -s "Sales"          # specific sheet
    python extract_tables.py data.xlsx -o tables.md        # save to file

Requires: pip install pdfplumber pandas tabulate openpyxl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PDF_EXTENSIONS = {".pdf"}
EXCEL_EXTENSIONS = {".xlsx", ".xls"}
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS | EXCEL_EXTENSIONS


def parse_pages(page_spec: str) -> list[int]:
    """Parse a page specification like '1,3,5' or '1-10' into a list of page numbers (1-based)."""
    pages: list[int] = []
    for part in page_spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))
    return pages


def table_to_markdown(table: list[list]) -> str:
    """Convert a 2D list to a Markdown table string."""
    if not table or not table[0]:
        return ""
    header = "| " + " | ".join(str(c or "") for c in table[0]) + " |"
    sep = "| " + " | ".join("---" for _ in table[0]) + " |"
    rows = "\n".join(
        "| " + " | ".join(str(c or "") for c in row) + " |"
        for row in table[1:]
    )
    return f"{header}\n{sep}\n{rows}"


def extract_from_pdf(input_path: Path, pages: list[int] | None) -> str:
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber is not installed. Run: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = []
    table_count = 0

    with pdfplumber.open(str(input_path)) as pdf:
        total_pages = len(pdf.pages)
        target_pages = pages if pages else list(range(1, total_pages + 1))

        for page_num in target_pages:
            if page_num < 1 or page_num > total_pages:
                print(
                    f"Warning: page {page_num} out of range (1-{total_pages}), skipping.",
                    file=sys.stderr,
                )
                continue

            page = pdf.pages[page_num - 1]  # pdfplumber uses 0-based index
            tables = page.extract_tables()

            if not tables:
                continue

            parts.append(f"## Page {page_num}\n")
            for i, table in enumerate(tables, 1):
                md_table = table_to_markdown(table)
                if md_table:
                    table_count += 1
                    parts.append(f"### Table {i}\n")
                    parts.append(md_table + "\n")

    if table_count == 0:
        print("No tables found in the specified pages.", file=sys.stderr)

    return "\n".join(parts)


def extract_from_excel(input_path: Path, sheet_name: str | None) -> str:
    try:
        import pandas as pd
    except ImportError:
        print(
            "Error: pandas is not installed. Run: pip install pandas tabulate openpyxl",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        # tabulate is required for pandas .to_markdown()
        import tabulate as _  # noqa: F811
    except ImportError:
        print(
            "Error: tabulate is not installed. Run: pip install tabulate",
            file=sys.stderr,
        )
        sys.exit(1)

    parts: list[str] = []

    try:
        if sheet_name:
            df = pd.read_excel(str(input_path), sheet_name=sheet_name)
            parts.append(f"## Sheet: {sheet_name}\n")
            parts.append(df.to_markdown(index=False) + "\n")
        else:
            sheets = pd.read_excel(str(input_path), sheet_name=None)
            for name, df in sheets.items():
                parts.append(f"## Sheet: {name}\n")
                parts.append(df.to_markdown(index=False) + "\n")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF or Excel files as Markdown tables."
    )
    parser.add_argument("input", help="Path to PDF or Excel file")
    parser.add_argument("-o", "--output", help="Output .md path (default: stdout)")
    parser.add_argument(
        "-s", "--sheet",
        help="Sheet name for Excel files (default: all sheets)",
    )
    parser.add_argument(
        "-p", "--page",
        help='Page number(s) for PDFs (e.g., "1,3,5" or "1-10", default: all pages)',
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()

    if not input_path.is_file():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = input_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(
            f"Error: unsupported format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    if ext in PDF_EXTENSIONS:
        if args.sheet:
            print("Warning: --sheet is ignored for PDF files.", file=sys.stderr)
        pages = parse_pages(args.page) if args.page else None
        content = extract_from_pdf(input_path, pages)
    else:
        if args.page:
            print("Warning: --page is ignored for Excel files.", file=sys.stderr)
        content = extract_from_excel(input_path, args.sheet)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Saved: {output_path}")
    else:
        sys.stdout.write(content)


if __name__ == "__main__":
    main()
