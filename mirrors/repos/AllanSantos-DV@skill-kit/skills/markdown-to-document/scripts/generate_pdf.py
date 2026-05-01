"""
Generate a PDF from Markdown or HTML input.

Usage:
    python generate_pdf.py input.md -o output.pdf
    python generate_pdf.py input.md -o output.pdf --css style.css
    python generate_pdf.py input.html -o output.pdf --css style.css
    python generate_pdf.py input.md -o output.pdf --engine xhtml2pdf
    python generate_pdf.py input.md -o output.pdf --engine fpdf2
    python generate_pdf.py input.md -o output.pdf --engine weasyprint

Input formats:
    Markdown (.md): Converted to HTML internally, then rendered to PDF.
    HTML (.html, .htm): Rendered directly to PDF.

Engines (tried in order if --engine not specified):
    1. xhtml2pdf  — pip install xhtml2pdf markdown  (zero native deps)
    2. fpdf2      — pip install fpdf2 markdown       (zero native deps)
    3. weasyprint — pip install weasyprint markdown   (requires GTK3/Pango)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from io import BytesIO
from pathlib import Path


def _ensure_package(import_name: str, pip_name: str | None = None) -> bool:
    """Try to import a package; auto-install if non-interactive. Returns True if available."""
    pip_name = pip_name or import_name
    try:
        __import__(import_name)
        return True
    except (ImportError, OSError):
        pass

    if sys.stdin.isatty():
        answer = input(f'Package "{pip_name}" is not installed. Install it now? [Y/n] ').strip().lower()
        if answer in ("", "y", "yes"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            return True
        return False
    else:
        print(f"Auto-installing missing package: {pip_name}", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        __import__(import_name)  # verify
        return True


DEFAULT_CSS = """
@page {
    size: A4;
    margin: 2cm;
}
body {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}
h1 { color: #1a5276; border-bottom: 2px solid #1a5276; padding-bottom: 0.3em; }
h2 { color: #2e86c1; margin-top: 1.5em; page-break-after: avoid; }
h3 { color: #2874a6; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; page-break-inside: avoid; }
th { background-color: #1a5276; color: white; padding: 8px 12px; text-align: left; }
td { border: 1px solid #ddd; padding: 8px 12px; }
tr:nth-child(even) { background-color: #f8f8f8; }
pre { background-color: #f4f4f4; padding: 1em; border-radius: 4px; font-size: 10pt; page-break-inside: avoid; }
code { font-family: "Cascadia Code", "Fira Code", "Consolas", monospace; font-size: 10pt; }
blockquote { border-left: 4px solid #2e86c1; margin: 1em 0; padding: 0.5em 1em; color: #555; }
"""

ENGINES = ["xhtml2pdf", "fpdf2", "weasyprint"]


def md_to_html(md_text: str) -> str:
    """Convert Markdown to HTML."""
    if not _ensure_package("markdown"):
        print("Error: markdown is required for Markdown input.", file=sys.stderr)
        sys.exit(1)

    import markdown
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc", "attr_list"]
    )
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>{DEFAULT_CSS}</style></head>
<body>
{html_body}
</body>
</html>"""


def _render_xhtml2pdf(html_content: str, output_path: Path, css_path: Path | None) -> None:
    """Render PDF using xhtml2pdf (zero native deps)."""
    from xhtml2pdf import pisa

    if css_path:
        css_text = css_path.read_text(encoding="utf-8")
        html_content = html_content.replace(
            "<head>",
            f"<head><style>{css_text}</style>",
            1,
        )
    elif "<style>" not in html_content:
        html_content = html_content.replace(
            "<head>",
            f"<head><style>{DEFAULT_CSS}</style>",
            1,
        )

    result = BytesIO()
    status = pisa.CreatePDF(html_content, dest=result)
    if status.err:
        print(f"Error: xhtml2pdf reported {status.err} error(s).", file=sys.stderr)
        sys.exit(1)
    output_path.write_bytes(result.getvalue())


def _render_fpdf2(html_content: str, output_path: Path, css_path: Path | None) -> None:
    """Render PDF using fpdf2 (zero native deps, basic HTML rendering)."""
    from fpdf import FPDF

    # Extract just the body content for fpdf2's write_html
    body_start = html_content.find("<body>")
    body_end = html_content.find("</body>")
    if body_start != -1 and body_end != -1:
        body_html = html_content[body_start + 6:body_end]
    else:
        body_html = html_content

    # Replace common Unicode chars that Helvetica can't handle
    replacements = {"\u2014": "--", "\u2013": "-", "\u2018": "'", "\u2019": "'",
                    "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u2022": "*"}
    for char, repl in replacements.items():
        body_html = body_html.replace(char, repl)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.write_html(body_html)
    pdf.output(str(output_path))


def _render_weasyprint(html_content: str, output_path: Path, css_path: Path | None) -> None:
    """Render PDF using WeasyPrint (requires GTK3/Pango native libs)."""
    import weasyprint

    stylesheets = []
    if css_path:
        stylesheets.append(weasyprint.CSS(filename=str(css_path)))

    weasyprint.HTML(string=html_content).write_pdf(
        str(output_path),
        stylesheets=stylesheets if stylesheets else None,
    )


_ENGINE_MAP = {
    "xhtml2pdf": _render_xhtml2pdf,
    "fpdf2": _render_fpdf2,
    "weasyprint": _render_weasyprint,
}


def _detect_engine(preferred: str | None) -> str:
    """Return the first available engine, respecting user preference. Offers install if missing."""
    _import_map = {"xhtml2pdf": ("xhtml2pdf", "xhtml2pdf"), "fpdf2": ("fpdf", "fpdf2"), "weasyprint": ("weasyprint", "weasyprint")}
    order = [preferred] if preferred else ENGINES

    # First pass — check what's already installed
    for name in order:
        import_name, _ = _import_map[name]
        try:
            __import__(import_name)
            return name
        except (ImportError, OSError):
            continue

    # Nothing installed — offer to install the best option
    for name in (order if preferred else ENGINES):
        import_name, pip_name = _import_map[name]
        if _ensure_package(import_name, pip_name):
            return name

    print("Error: No PDF engine available and installation was declined.", file=sys.stderr)
    sys.exit(1)


def generate(input_path: Path, output_path: Path, css_path: Path | None, engine: str | None = None) -> None:
    """Generate PDF from input file."""
    text = input_path.read_text(encoding="utf-8")

    if input_path.suffix.lower() in (".md", ".markdown", ".txt"):
        html_content = md_to_html(text)
    else:
        html_content = text

    engine_name = _detect_engine(engine)
    print(f"Using engine: {engine_name}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _ENGINE_MAP[engine_name](html_content, output_path, css_path)
    print(f"Generated: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a PDF from Markdown or HTML input."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to Markdown (.md) or HTML (.html) input file."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output.pdf"),
        help="Output file path (default: output.pdf)."
    )
    parser.add_argument(
        "--css",
        type=Path,
        default=None,
        help="Path to CSS stylesheet for PDF styling. If not provided, a default style is used."
    )
    parser.add_argument(
        "--engine",
        choices=ENGINES,
        default=None,
        help="PDF engine to use. Auto-detected if not specified (tries xhtml2pdf → fpdf2 → weasyprint)."
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    if args.css and not args.css.is_file():
        print(f"Error: CSS file not found: {args.css}", file=sys.stderr)
        sys.exit(1)

    generate(args.input, args.output, args.css, args.engine)


if __name__ == "__main__":
    main()
