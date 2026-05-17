#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
MODE="${2:-summary}"

if [ "$MODE" != "summary" ] && [ "$MODE" != "deep" ]; then
  echo "Usage: $0 [repo-root] [summary|deep]" >&2
  exit 2
fi

if [ ! -d "$ROOT" ]; then
  echo "Repo root not found: $ROOT" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC_REF_CHECKER="$SCRIPT_DIR/check-doc-refs.sh"

DOC_REF_CHECKER="$DOC_REF_CHECKER" python3 - "$ROOT" "$MODE" <<'PY'
import json
import os
import re
import subprocess
import sys
import urllib.parse
from collections import Counter
from pathlib import Path

root = Path(sys.argv[1]).resolve()
mode = sys.argv[2]

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    ".next",
    "__pycache__",
    ".turbo",
    "target",
    ".venv",
    "venv",
    "vendor",
    "coverage",
    ".cache",
    ".parcel-cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

SOURCE_EXTS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".lua",
    ".m",
    ".mm",
    ".md",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
}

MARKER_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
MAKE_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*:(?![=])")
MAKE_CMD_RE = re.compile(r"\bmake\s+([A-Za-z0-9_.-]+)\b")
NPM_CMD_RE = re.compile(r"\b(?:npm|pnpm|yarn|bun)\s+run\s+([A-Za-z0-9:_-]+)\b")
COMMAND_LINE_RE = re.compile(r"^(?:make|npm|pnpm|yarn|bun)\s+")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
URL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
HOTSPOT_WORD_RE = re.compile(r"(hotspot|large file|ownership|owner|boundary|module|owned|owns|负责|边界|模块|热点|大文件)", re.IGNORECASE)
VERIFICATION_WORD_RE = re.compile(
    r"(verification|verify|test|check|make\s+\w+|pytest|go test|cargo test|npm test|npm run|pnpm|yarn|swift test|xcodebuild|验证|测试)",
    re.IGNORECASE,
)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def is_excluded(path: Path) -> bool:
    parts = path.relative_to(root).parts if path.is_absolute() else path.parts
    return any(part in EXCLUDED_DIRS for part in parts)


def read_text(path: Path, limit: int | None = None) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return data[:limit] if limit else data


def iter_files() -> list[Path]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            files = []
            for line in proc.stdout.splitlines():
                path = root / line
                if path.is_file() and not is_excluded(path):
                    files.append(path)
            return files
    except OSError:
        pass

    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        if is_excluded(current):
            continue
        for filename in filenames:
            path = current / filename
            if path.is_file() and not is_excluded(path):
                files.append(path)
    return files


def line_count(path: Path) -> int:
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def print_list(items: list[str], empty: str = "(none)", limit: int | None = None) -> None:
    shown = items if limit is None else items[:limit]
    if not shown:
        print(f"  {empty}")
        return
    for item in shown:
        print(f"  {item}")
    if limit is not None and len(items) > limit:
        print(f"  ... {len(items) - limit} more")


def instruction_paths() -> list[Path]:
    candidates = [
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / ".github" / "copilot-instructions.md",
        root / "GEMINI.md",
    ]
    instructions_dir = root / ".github" / "instructions"
    if instructions_dir.is_dir():
        candidates.extend(sorted(instructions_dir.glob("*.md")))
    return [path for path in candidates if path.is_file() and not is_excluded(path)]


def find_text_signal(paths: list[Path], patterns: list[str]) -> bool:
    regexes = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for path in paths:
        text = read_text(path, 200_000)
        if any(regex.search(text) for regex in regexes):
            return True
    return False


def parse_makefile() -> tuple[set[str], list[str]]:
    makefile = root / "Makefile"
    targets: set[str] = set()
    commands: list[str] = []
    if not makefile.is_file():
        return targets, commands
    for line in read_text(makefile).splitlines():
        match = MAKE_RE.match(line)
        if not match:
            continue
        target = match.group(1)
        if target.startswith("."):
            continue
        targets.add(target)
        if re.search(r"(test|check|lint|type|build|package|verify|smoke)", target, re.IGNORECASE):
            commands.append(f"make {target}")
    return targets, commands


def parse_package_json() -> tuple[set[str], list[str]]:
    package = root / "package.json"
    script_names: set[str] = set()
    commands: list[str] = []
    if not package.is_file():
        return script_names, commands
    try:
        data = json.loads(read_text(package))
    except json.JSONDecodeError:
        return script_names, commands
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return script_names, commands
    for name in sorted(scripts):
        script_names.add(name)
        if re.search(r"(test|check|lint|type|build|verify)", name, re.IGNORECASE):
            commands.append(f"npm run {name}")
    return script_names, commands


def parse_ci_commands() -> list[str]:
    workflows = sorted((root / ".github" / "workflows").glob("*.yml"))
    workflows += sorted((root / ".github" / "workflows").glob("*.yaml"))
    commands: list[str] = []
    for workflow in workflows:
        for raw in read_text(workflow).splitlines():
            line = raw.strip()
            if line.startswith("- run:"):
                command = line.split("- run:", 1)[1].strip().strip("'\"")
            elif line.startswith("run:"):
                command = line.split("run:", 1)[1].strip().strip("'\"")
            else:
                continue
            if command and command != "|":
                commands.append(f"{rel(workflow)}: {command}")
    return commands


def scan_markdown_links() -> list[str]:
    missing: list[str] = []
    markdown_files = [path for path in files if path.suffix.lower() == ".md"]
    for path in markdown_files:
        for lineno, line in enumerate(read_text(path).splitlines(), 1):
            for raw in MARKDOWN_LINK_RE.findall(line):
                target = raw.strip().split()[0].strip("<>")
                if not target or target.startswith("#") or URL_RE.match(target):
                    continue
                target = urllib.parse.unquote(target.split("#", 1)[0])
                if not target:
                    continue
                full = (path.parent / target).resolve()
                if not full.exists():
                    missing.append(f"{rel(path)}:{lineno} -> {target}")
    return missing


def verification_surface(instruction_files: list[Path]) -> tuple[list[str], list[str], set[str], set[str]]:
    make_targets, make_commands = parse_makefile()
    package_scripts, package_commands = parse_package_json()
    commands = make_commands + package_commands + parse_ci_commands()

    if (root / "Cargo.toml").is_file():
        commands.extend(["cargo test", "cargo check"])
    if (root / "go.mod").is_file():
        commands.append("go test ./...")
    if (root / "pyproject.toml").is_file() or (root / "pytest.ini").is_file():
        commands.append("pytest")
    if (root / "pom.xml").is_file():
        commands.append("mvn test")
    if (root / "deno.json").is_file() or (root / "deno.jsonc").is_file():
        commands.append("deno test")

    missing: list[str] = []
    for path in instruction_files:
        text = read_text(path, 200_000)
        snippets: list[str] = []
        for raw_line in text.splitlines():
            snippets.extend(re.findall(r"`([^`]+)`", raw_line))
            stripped = raw_line.strip().strip("`")
            if COMMAND_LINE_RE.match(stripped):
                snippets.append(stripped)
        for snippet in snippets:
            for target in MAKE_CMD_RE.findall(snippet):
                if target not in make_targets:
                    missing.append(f"{rel(path)} references missing make target: {target}")
            for script in NPM_CMD_RE.findall(snippet):
                if script not in package_scripts:
                    missing.append(f"{rel(path)} references missing package script: {script}")

    unique_commands = list(dict.fromkeys(commands))
    unique_missing = list(dict.fromkeys(missing))
    return unique_commands, unique_missing, make_targets, package_scripts


def hotspot_ownership_surface(
    records: list[tuple[int, int, Path]],
    instruction_files: list[Path],
) -> tuple[str, list[str], list[str], list[str]]:
    if mode != "deep":
        return "SKIPPED", [], [], []
    if not records:
        return "PASS", [], [], []

    snippets: list[str] = []
    for path in instruction_files:
        snippets.append(f"\n# {rel(path)}\n{read_text(path, 200_000)}")
    instruction_text = "\n".join(snippets)
    lower_text = instruction_text.lower()
    instruction_lines = instruction_text.splitlines()

    documented: list[str] = []
    missing: list[str] = []
    for lines, _size, path in records:
        relative = rel(path)
        relative_lower = relative.lower()
        indices: list[int] = []
        start = 0
        while True:
            index = lower_text.find(relative_lower, start)
            if index < 0:
                break
            indices.append(index)
            start = index + len(relative_lower)

        if not indices:
            missing.append(f"{relative} lines={lines} reason=not mentioned in agent instructions")
            continue

        saw_hotspot_context = False
        saw_verification_context = False
        has_documented_entry = False
        for index in indices:
            window = lower_text[max(0, index - 700) : index + len(relative_lower) + 700]
            line_no = lower_text[:index].count("\n")
            local_lines = instruction_lines[max(0, line_no - 1) : line_no + 4]
            local_context = "\n".join(local_lines)
            has_hotspot_context = bool(HOTSPOT_WORD_RE.search(window))
            has_verification_context = bool(VERIFICATION_WORD_RE.search(local_context))
            saw_hotspot_context = saw_hotspot_context or has_hotspot_context
            saw_verification_context = saw_verification_context or has_verification_context
            if has_hotspot_context and has_verification_context:
                has_documented_entry = True
                break

        if has_documented_entry:
            documented.append(f"{relative} lines={lines}")
        else:
            reasons = []
            if not saw_hotspot_context:
                reasons.append("missing ownership/boundary context")
            if not saw_verification_context:
                reasons.append("missing verification context")
            if saw_hotspot_context and saw_verification_context:
                reasons.append("ownership and verification are not in the same hotspot entry")
            missing.append(f"{relative} lines={lines} reason={'; '.join(reasons)}")

    findings: list[str] = []
    if missing:
        findings.append("large source files lack hotspot ownership or verification map")
    return ("WARN" if missing else "PASS"), documented, missing, findings


files = iter_files()
tracked_count = len(files)
extensions = Counter(path.suffix.lower() or "(none)" for path in files)
detected_manifests = [
    name
    for name in [
        "Makefile",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "pyproject.toml",
        "pytest.ini",
        "pom.xml",
        "deno.json",
        "deno.jsonc",
    ]
    if (root / name).is_file()
]
workflow_count = len(list((root / ".github" / "workflows").glob("*.yml"))) if (root / ".github" / "workflows").is_dir() else 0
workflow_count += len(list((root / ".github" / "workflows").glob("*.yaml"))) if (root / ".github" / "workflows").is_dir() else 0
if workflow_count:
    detected_manifests.append(f".github/workflows ({workflow_count})")

source_files = [path for path in files if path.suffix.lower() in SOURCE_EXTS]
source_stats = []
for path in source_files:
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    source_stats.append((line_count(path), size, path))
source_stats.sort(key=lambda item: (item[0], item[1]), reverse=True)

dir_counts: Counter[str] = Counter()
for path in files:
    relative_parts = Path(rel(path)).parts
    top = relative_parts[0] if len(relative_parts) > 1 else "."
    dir_counts[top] += 1

instruction_files = instruction_paths()
project_map = find_text_signal(
    instruction_files,
    [r"repository map", r"project map", r"repo map", r"\bproject\b", r"目录", r"仓库", r"结构"],
)
instruction_verification = find_text_signal(
    instruction_files,
    [r"verification", r"test plan", r"make test", r"npm test", r"pytest", r"cargo test", r"验证", r"测试"],
)
boundaries = find_text_signal(
    instruction_files,
    [r"not for", r"do not", r"non-?goals?", r"scope", r"boundar", r"never", r"avoid", r"边界", r"非目标", r"不要"],
)
commands, missing_references, make_targets, package_scripts = verification_surface(instruction_files)
stable_make_targets = sorted(make_targets & {"check", "test", "verify"})
wrapper_warnings: list[str] = []
if len(commands) >= 2 and (root / "Makefile").is_file() and not stable_make_targets:
    wrapper_warnings.append("multiple verification commands discovered but Makefile lacks check/test/verify wrapper")

decision_artifacts = {
    "docs_dir": (root / "docs").is_dir(),
    "specs_dir": (root / "specs").is_dir(),
    "specify_dir": (root / ".specify").is_dir(),
    "handoff_md": any(path.name.upper() == "HANDOFF.MD" for path in root.glob("*.md")),
    "changelog": any(path.name.upper().startswith("CHANGELOG") for path in root.glob("*")),
    "issue_templates": (root / ".github" / "ISSUE_TEMPLATE").exists(),
    "pr_template": any(
        path.is_file()
        for path in [
            root / ".github" / "pull_request_template.md",
            root / ".github" / "PULL_REQUEST_TEMPLATE.md",
        ]
    ),
}

todo_counts: Counter[str] = Counter()
todo_total = 0
for path in source_files:
    text = read_text(path, 200_000)
    count = len(MARKER_RE.findall(text))
    if count:
        todo_counts[rel(path)] += count
        todo_total += count

large_line_limit = 1200 if mode == "summary" else 800
large_file_records = [(lines, size, path) for lines, size, path in source_stats if lines >= large_line_limit]
large_files = [f"{rel(path)} lines={lines} bytes={size}" for lines, size, path in large_file_records]
todo_hotspots = [f"{path} markers={count}" for path, count in todo_counts.most_common(8 if mode == "deep" else 5)]

doc_ref_status = "unavailable"
doc_ref_detail = ""
checker = os.environ.get("DOC_REF_CHECKER")
if checker and Path(checker).is_file():
    proc = subprocess.run(
        ["bash", checker, str(root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    doc_ref_status = "pass" if proc.returncode == 0 else "fail"
    if proc.stdout.strip():
        first_lines = proc.stdout.strip().splitlines()[:8]
        doc_ref_detail = " | ".join(first_lines)

has_instruction_surface = bool(instruction_files)
has_command_surface = bool(commands)
context_warnings = []
verification_warnings = []
drift_warnings = []

if not has_instruction_surface:
    context_warnings.append("no agent instruction surface")
if has_instruction_surface and not project_map:
    context_warnings.append("instructions lack project map")
if has_instruction_surface and not instruction_verification:
    context_warnings.append("instructions lack verification guidance")
if has_instruction_surface and not boundaries:
    context_warnings.append("instructions lack scope/boundary language")
if not has_command_surface:
    verification_warnings.append("no executable verification command discovered")
if missing_references:
    verification_warnings.append("instruction references missing commands")
if todo_total >= (50 if mode == "summary" else 25):
    drift_warnings.append("TODO/FIXME/HACK/XXX markers are concentrated")
hotspot_status, documented_hotspots, missing_hotspot_ownership, hotspot_findings = hotspot_ownership_surface(
    large_file_records,
    instruction_files,
)
if large_files and mode != "deep":
    drift_warnings.append("large source files need ownership or module boundaries")
if hotspot_status == "WARN":
    drift_warnings.extend(hotspot_findings)
if doc_ref_status == "fail":
    drift_warnings.append("broken documentation references")

markdown_missing: list[str] = []
markdown_link_status = "SKIPPED"
if mode == "deep":
    markdown_missing = scan_markdown_links()
    markdown_link_status = "WARN" if markdown_missing else "PASS"
    if markdown_missing:
        drift_warnings.append("broken Markdown links")

context_status = "FAIL" if not has_instruction_surface else ("WARN" if context_warnings else "PASS")
verification_status = "FAIL" if not has_command_surface else ("WARN" if verification_warnings else "PASS")
decision_status = "PASS"
wrapper_status = "WARN" if wrapper_warnings else "PASS"
drift_status = "WARN" if drift_warnings else "PASS"

if context_status == "FAIL" or verification_status == "FAIL" or doc_ref_status == "fail":
    overall = "FAIL"
elif "WARN" in {
    context_status,
    verification_status,
    decision_status,
    wrapper_status,
    drift_status,
    markdown_link_status,
    hotspot_status,
}:
    overall = "WARN"
else:
    overall = "PASS"

top_ext = [f"{ext} files={count}" for ext, count in extensions.most_common(10)]
largest_sources = [
    f"{rel(path)} lines={lines} bytes={size}"
    for lines, size, path in source_stats[: (10 if mode == "deep" else 5)]
]
largest_dirs = [f"{directory} files={count}" for directory, count in dir_counts.most_common(8)]

print("=== PROJECT SHAPE ===")
print(f"maintainability_status: {overall}")
print(f"mode: {mode}")
print(f"tracked_files: {tracked_count}")
print("top_extensions:")
print_list(top_ext)
print("largest_source_files:")
print_list(largest_sources)
print("largest_directories:")
print_list(largest_dirs)

print("=== AI CONTEXT SURFACE ===")
print(f"context_status: {context_status}")
print(f"AGENTS.md: {'yes' if (root / 'AGENTS.md').is_file() else 'no'}")
print(f"CLAUDE.md: {'yes' if (root / 'CLAUDE.md').is_file() else 'no'}")
print(f".github/copilot-instructions.md: {'yes' if (root / '.github' / 'copilot-instructions.md').is_file() else 'no'}")
github_instruction_count = len(list((root / ".github" / "instructions").glob("*.md"))) if (root / ".github" / "instructions").is_dir() else 0
print(f".github/instructions/*.md: {github_instruction_count}")
print(f"GEMINI.md: {'yes' if (root / 'GEMINI.md').is_file() else 'no'}")
print(f"project_map: {'yes' if project_map else 'no'}")
print(f"verification_guidance: {'yes' if instruction_verification else 'no'}")
print(f"boundary_guidance: {'yes' if boundaries else 'no'}")
print("context_findings:")
print_list(context_warnings)
print("instruction_files:")
print_list([rel(path) for path in instruction_files])

print("=== VERIFICATION SURFACE ===")
print(f"verification_status: {verification_status}")
print("detected_manifests:")
print_list(detected_manifests)
print("commands:")
print_list(commands, limit=12 if mode == "summary" else None)
print("missing_referenced_commands:")
print_list(missing_references, limit=10 if mode == "summary" else None)
print("verification_findings:")
print_list(verification_warnings)

print("=== VERIFICATION WRAPPER SURFACE ===")
print(f"wrapper_status: {wrapper_status}")
print(f"makefile_present: {'yes' if (root / 'Makefile').is_file() else 'no'}")
print("stable_make_targets:")
print_list([f"make {target}" for target in stable_make_targets])
print("wrapper_findings:")
print_list(wrapper_warnings)

print("=== DECISION ARTIFACTS ===")
print(f"decision_artifacts_status: {decision_status}")
for key, value in decision_artifacts.items():
    print(f"{key}: {'yes' if value else 'no'}")

print("=== DRIFT MARKERS ===")
print(f"drift_status: {drift_status}")
print(f"todo_markers: {todo_total}")
print("todo_hotspots:")
print_list(todo_hotspots)
print("large_source_files:")
print_list(large_files[: (10 if mode == "deep" else 5)])
print(f"broken_doc_references: {doc_ref_status}")
if doc_ref_detail and (mode == "deep" or doc_ref_status == "fail"):
    print(f"broken_doc_reference_detail: {doc_ref_detail}")
print("drift_findings:")
print_list(drift_warnings)

print("=== HOTSPOT OWNERSHIP SURFACE ===")
print(f"hotspot_ownership_status: {hotspot_status}")
print(f"large_hotspot_threshold_lines: {large_line_limit if mode == 'deep' else '(deep mode only)'}")
print("documented_hotspots:")
if mode == "deep":
    print_list(documented_hotspots)
else:
    print("  (skipped: deep mode only)")
print("missing_hotspot_ownership:")
if mode == "deep":
    print_list(missing_hotspot_ownership)
else:
    print("  (skipped: deep mode only)")
print("hotspot_ownership_findings:")
if mode == "deep":
    print_list(hotspot_findings)
else:
    print("  (skipped: deep mode only)")

print("=== MARKDOWN LINK SURFACE ===")
print(f"markdown_link_status: {markdown_link_status}")
print("missing_markdown_links:")
if mode == "deep":
    print_list(markdown_missing, limit=20)
else:
    print("  (skipped: deep mode only)")
PY
