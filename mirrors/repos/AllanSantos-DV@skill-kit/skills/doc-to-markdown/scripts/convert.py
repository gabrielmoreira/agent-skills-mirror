"""
Convert a single document to Markdown for LLM consumption.

Usage:
    python convert.py document.docx                    # prints to stdout
    python convert.py document.docx -o output.md       # saves to file
    python convert.py report.pdf --tool pdfplumber      # force specific tool
    python convert.py scan.png --ocr                    # OCR mode
    python convert.py file.docx --no-frontmatter        # skip YAML header
    python convert.py project.mpp -o project.md         # MS Project
    python convert.py project.mpp --tool mpxj           # force mpxj

Supported formats: .docx, .doc, .xlsx, .xls, .csv, .pptx, .ppt, .pdf, .html, .epub,
    .png, .jpg, .jpeg, .gif, .bmp, .tiff, .mp3, .wav, .m4a, .ipynb, .zip, .msg,
    .mpp, .mspdi, .mpx (MS Project — requires Java 11+)
Requires: pip install markitdown (or pip install 'markitdown[all]' for OCR)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".docx", ".doc", ".xlsx", ".xls", ".csv",
    ".pptx", ".ppt", ".pdf", ".html", ".htm", ".epub",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff",
    ".mp3", ".wav", ".m4a",
    ".ipynb", ".zip", ".msg",
    ".mpp", ".mspdi", ".mpx",  # MS Project
}

TOOL_CHOICES = ["markitdown", "pandoc", "pdfplumber", "mammoth", "mpxj"]


def convert_markitdown(input_path: Path, *, enable_ocr: bool = False) -> str:
    try:
        from markitdown import MarkItDown
    except ImportError:
        pkg = "'markitdown[all]'" if enable_ocr else "markitdown"
        print(f"Error: markitdown is not installed. Run: pip install {pkg}", file=sys.stderr)
        sys.exit(1)

    kwargs: dict = {}
    if enable_ocr:
        try:
            kwargs["enable_llm_extraction"] = False  # OCR only, no LLM
        except Exception:
            pass

    md = MarkItDown(**kwargs)
    result = md.convert(str(input_path))
    return result.text_content


def convert_pdfplumber(input_path: Path) -> str:
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber is not installed. Run: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = []
    with pdfplumber.open(str(input_path)) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            parts.append(f"## Page {i}\n")
            text = page.extract_text()
            if text:
                parts.append(text + "\n")
            tables = page.extract_tables()
            for table in tables:
                if not table or not table[0]:
                    continue
                header = "| " + " | ".join(str(c or "") for c in table[0]) + " |"
                sep = "| " + " | ".join("---" for _ in table[0]) + " |"
                rows = "\n".join(
                    "| " + " | ".join(str(c or "") for c in row) + " |"
                    for row in table[1:]
                )
                parts.append(f"{header}\n{sep}\n{rows}\n")
    return "\n".join(parts)


def convert_pandoc(input_path: Path) -> str:
    import subprocess

    try:
        result = subprocess.run(
            ["pandoc", "-f", _pandoc_format(input_path), "-t", "markdown", str(input_path)],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        print("Error: pandoc is not installed. See https://pandoc.org/installing.html", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: pandoc failed: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def _pandoc_format(path: Path) -> str:
    mapping = {
        ".docx": "docx", ".doc": "doc", ".html": "html", ".htm": "html",
        ".epub": "epub", ".csv": "csv", ".pptx": "pptx",
    }
    return mapping.get(path.suffix.lower(), "")


def convert_mammoth(input_path: Path) -> str:
    try:
        import mammoth
    except ImportError:
        print("Error: mammoth is not installed. Run: pip install mammoth", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    if result.messages:
        for msg in result.messages:
            print(f"Warning: {msg}", file=sys.stderr)
    return result.value


# ---------------------------------------------------------------------------
# MS Project conversion via MPXJ
# ---------------------------------------------------------------------------

# Java helpers shared with markdown-to-document/scripts/analyze_template.py


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


def _check_java(min_version: int = 11) -> str | None:
    """Check if Java is available and meets the minimum version. Returns java path or None."""
    resolver = Path(__file__).parent / "runtime_resolver.py"
    if resolver.is_file():
        try:
            result = subprocess.run(
                [sys.executable, str(resolver), "java",
                 "--min-version", str(min_version)],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                info = json.loads(result.stdout)
                if info.get("found"):
                    return info.get("path")
        except Exception:
            pass

    java_cmd = "java"
    try:
        result = subprocess.run(
            [java_cmd, "-version"],
            capture_output=True, text=True, timeout=10
        )
        if result.stderr or result.stdout:
            return java_cmd
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _resolve_java_home(java_path: str) -> Path | None:
    """Resolve the actual JAVA_HOME from a java executable path."""
    resolved = Path(java_path).resolve()
    if resolved.parent.name.lower() == "bin":
        return resolved.parent.parent
    try:
        result = subprocess.run(
            [java_path, "-XshowSettings:properties", "-version"],
            capture_output=True, text=True, timeout=10,
        )
        for line in (result.stderr or "").splitlines():
            if "java.home" in line and "=" in line:
                return Path(line.split("=", 1)[1].strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _find_jvm_dll(jdk_home: Path) -> str | None:
    """Locate the JVM shared library inside a JDK home directory."""
    if sys.platform == "win32":
        candidates = [
            jdk_home / "bin" / "server" / "jvm.dll",
            jdk_home / "bin" / "client" / "jvm.dll",
        ]
    elif sys.platform == "darwin":
        candidates = [
            jdk_home / "lib" / "server" / "libjvm.dylib",
            jdk_home / "lib" / "client" / "libjvm.dylib",
        ]
    else:
        candidates = [
            jdk_home / "lib" / "server" / "libjvm.so",
            jdk_home / "lib" / "client" / "libjvm.so",
        ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def _bootstrap_jvm() -> None:
    """Ensure JVM is started with MPXJ on classpath."""
    java_path = _check_java(min_version=11)
    if not java_path:
        print("Error: Java 11+ is required for MS Project conversion.", file=sys.stderr)
        print("Install: choco install temurin17 (Windows) or apt install openjdk-17-jdk (Linux)", file=sys.stderr)
        sys.exit(1)

    jdk_home = _resolve_java_home(java_path)
    jvm_path = _find_jvm_dll(jdk_home) if jdk_home else None
    if jdk_home:
        os.environ["JAVA_HOME"] = str(jdk_home)

    _ensure_package("mpxj")
    _ensure_package("jpype", "jpype1")

    import mpxj  # noqa: F401 — adds MPXJ jars to classpath
    import jpype
    if not jpype.isJVMStarted():
        try:
            if jvm_path:
                jpype.startJVM(jvm_path)
            else:
                jpype.startJVM()
        except Exception as e:
            print(f"Error starting JVM: {e}", file=sys.stderr)
            sys.exit(1)


def _format_date(dt) -> str:
    """Convert a Java LocalDateTime/LocalDate to 'YYYY-MM-DD' string."""
    if dt is None:
        return "—"
    try:
        return str(dt).split("T")[0]
    except Exception:
        return str(dt)


def _format_duration(dur) -> str:
    """Convert an MPXJ Duration to a human string like '5d' or '8h'."""
    if dur is None:
        return "—"
    try:
        val = dur.getDuration()
        units = str(dur.getUnits())
        if "HOUR" in units:
            return f"{val}h"
        if "WEEK" in units:
            return f"{val}w"
        if "MINUTE" in units:
            return f"{val}m"
        return f"{val}d"
    except Exception:
        return str(dur)


def convert_mpp(input_path: Path) -> str:
    """Convert MS Project file (.mpp, .mspdi, .mpx) to Markdown."""
    _bootstrap_jvm()

    from org.mpxj.reader import UniversalProjectReader

    reader = UniversalProjectReader()
    project = reader.read(str(input_path))
    if project is None:
        print(f"Error: MPXJ could not read '{input_path}'.", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = []

    # --- Project header ---
    props = project.getProjectProperties()
    name = str(props.getName() or input_path.stem)
    parts.append(f"# Project: {name}\n")

    start = _format_date(props.getStartDate())
    finish = _format_date(props.getFinishDate())
    cal = project.getDefaultCalendar()
    cal_name = str(cal.getName()) if cal else "Standard"
    parts.append(f"**Start:** {start} | **Finish:** {finish} | **Calendar:** {cal_name}\n")

    # --- Properties table ---
    hours_per_day = 8.0
    try:
        mpd = props.getMinutesPerDay()
        if mpd:
            hours_per_day = round(float(mpd.getDuration()) / 60, 1)
    except Exception:
        pass

    days_per_month = 20
    try:
        dpm = props.getDaysPerMonth()
        if dpm is not None:
            days_per_month = int(dpm)
    except Exception:
        pass

    author = str(props.getAuthor() or "")

    parts.append("\n## Project Properties\n")
    parts.append("| Property | Value |")
    parts.append("|----------|-------|")
    parts.append(f"| Hours per Day | {hours_per_day} |")
    parts.append(f"| Days per Month | {days_per_month} |")
    if author:
        parts.append(f"| Author | {author} |")

    # --- Resources table ---
    all_resources = list(project.getResources())
    named_resources = [r for r in all_resources if r.getName()]
    if named_resources:
        parts.append("\n## Resources\n")
        parts.append("| Name | Type | Group |")
        parts.append("|------|------|-------|")
        for r in named_resources:
            rname = str(r.getName())
            rtype = str(r.getType() or "Work")
            rgroup = str(r.getGroup() or "")
            parts.append(f"| {rname} | {rtype} | {rgroup} |")

    # --- Tasks table ---
    all_tasks = list(project.getTasks())
    tasks = [t for t in all_tasks if t.getID() is not None and int(t.getID()) > 0 and t.getName()]
    if tasks:
        parts.append("\n## Tasks\n")
        parts.append("| # | WBS | Task | Start | Finish | Duration | Predecessors | Resources |")
        parts.append("|---|-----|------|-------|--------|----------|-------------|-----------|")
        for i, task in enumerate(tasks, 1):
            wbs = str(task.getWBS() or "")
            tname = str(task.getName())
            tstart = _format_date(task.getStart())
            tfinish = _format_date(task.getFinish())
            dur = _format_duration(task.getDuration())

            # Predecessors
            preds: list[str] = []
            try:
                for pred in (task.getPredecessors() or []):
                    pred_task = pred.getTargetTask()
                    if pred_task:
                        preds.append(str(pred_task.getID()))
            except Exception:
                pass
            pred_str = ", ".join(preds) if preds else "—"

            # Resources
            res_names: list[str] = []
            try:
                for ra in (task.getResourceAssignments() or []):
                    r = ra.getResource()
                    if r and r.getName():
                        res_names.append(str(r.getName()))
            except Exception:
                pass
            res_str = ", ".join(res_names) if res_names else "—"

            parts.append(f"| {i} | {wbs} | {tname} | {tstart} | {tfinish} | {dur} | {pred_str} | {res_str} |")

    # --- Summary ---
    milestone_count = sum(1 for t in tasks if t.getMilestone())
    parts.append("\n## Summary\n")
    parts.append(f"- **Total tasks:** {len(tasks)}")
    parts.append(f"- **Milestones:** {milestone_count}")
    parts.append(f"- **Resources:** {len(named_resources)}")
    parts.append(f"- **Duration:** {start} to {finish}")

    return "\n".join(parts)


def build_frontmatter(input_path: Path) -> str:
    source = input_path.name
    date = datetime.now().strftime("%Y-%m-%d")
    fmt = input_path.suffix.lstrip(".").lower()
    return f'---\nsource: "{source}"\nconverted: "{date}"\nformat: "{fmt}"\n---\n\n'


def detect_tool(input_path: Path) -> str:
    ext = input_path.suffix.lower()
    if ext in (".mpp", ".mspdi", ".mpx"):
        return "mpxj"
    return "markitdown"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a single document to Markdown for LLM consumption."
    )
    parser.add_argument("input", help="Path to the source file")
    parser.add_argument("-o", "--output", help="Output .md path (default: stdout)")
    parser.add_argument(
        "--no-frontmatter", action="store_true", help="Skip YAML frontmatter generation"
    )
    parser.add_argument(
        "-t", "--tool", choices=TOOL_CHOICES,
        help="Force a specific conversion tool (default: auto-detect)",
    )
    parser.add_argument(
        "--ocr", action="store_true",
        help="Enable OCR for images/scanned documents (requires markitdown[all])",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()

    if not input_path.is_file():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = input_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS and not args.ocr and not args.tool:
        print(
            f"Error: unsupported format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    tool = args.tool or detect_tool(input_path)

    converters = {
        "markitdown": lambda: convert_markitdown(input_path, enable_ocr=args.ocr),
        "pdfplumber": lambda: convert_pdfplumber(input_path),
        "pandoc": lambda: convert_pandoc(input_path),
        "mammoth": lambda: convert_mammoth(input_path),
        "mpxj": lambda: convert_mpp(input_path),
    }

    try:
        content = converters[tool]()
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.no_frontmatter:
        content = build_frontmatter(input_path) + content

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Saved: {output_path}")
    else:
        sys.stdout.write(content)


if __name__ == "__main__":
    main()
