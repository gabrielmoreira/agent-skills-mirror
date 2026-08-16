#!/usr/bin/env python3
"""Offline structural verification for the word-zotero-citations Skill."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path, PurePosixPath

SKILL_NAME = "word-zotero-citations"
REQUIRED_REFERENCES = {
    "references/contracts.md",
    "references/implementation-map.md",
    "references/live-refresh-protocol.md",
    "references/recovery-and-rollback.md",
    "references/verification-matrix.md",
    "references/zotero-mcp-configuration.md",
    "references/live-run-recipe.md",
}
REQUIRED_EVALS = {
    "evals/trigger-cases.json",
    "evals/task-cases.json",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_PARTS = {"__pycache__", ".git"}
PATH_REFERENCE_RE = re.compile(r"`((?:references|scripts|assets|evals)/[^`]+)`")


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")
    values: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            raise ValueError(f"invalid frontmatter line: {raw_line!r}")
        key, value = raw_line.split(":", 1)
        values[key.strip()] = value.strip()
    return values, text[end + 5 :]


def _load_cases(path: Path, expected_kind: str) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise TypeError(f"{path.name} must contain a JSON array")
    seen: set[str] = set()
    for index, case in enumerate(data):
        if not isinstance(case, dict):
            raise TypeError(f"{path.name}[{index}] must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{path.name}[{index}].id must be a non-empty string")
        if case_id in seen:
            raise ValueError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if case.get("kind") != expected_kind:
            raise ValueError(f"{case_id}: expected kind {expected_kind!r}")
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"{case_id}: prompt must be a non-empty string")
    return data


def _validate_eval_definitions(root: Path) -> None:
    trigger_cases = _load_cases(root / "evals" / "trigger-cases.json", "trigger")
    trigger_count = sum(case.get("should_trigger") is True for case in trigger_cases)
    nontrigger_count = sum(case.get("should_trigger") is False for case in trigger_cases)
    if trigger_count < 3 or nontrigger_count < 3:
        raise ValueError("trigger-cases.json requires at least 3 trigger and 3 non-trigger cases")
    for case in trigger_cases:
        if not isinstance(case.get("expected_reason"), str) or not case["expected_reason"].strip():
            raise ValueError(f"{case['id']}: expected_reason must be non-empty")

    task_cases = _load_cases(root / "evals" / "task-cases.json", "task")
    if len(task_cases) < 3:
        raise ValueError("task-cases.json requires at least 3 representative tasks")
    for case in task_cases:
        signals = case.get("expected_signals")
        failures = case.get("fatal_failures")
        if not isinstance(signals, list) or not signals or not all(isinstance(item, str) and item for item in signals):
            raise ValueError(f"{case['id']}: expected_signals must be a non-empty string array")
        if not isinstance(failures, list) or not failures or not all(
            isinstance(item, str) and item for item in failures
        ):
            raise ValueError(f"{case['id']}: fatal_failures must be a non-empty string array")


def _validate_python_scripts(root: Path) -> None:
    for path in sorted((root / "scripts").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                continue
            if isinstance(node, ast.Assign):
                continue
            if isinstance(node, ast.AnnAssign) and node.value is not None:
                continue
            if isinstance(node, ast.If):
                test = node.test
                if (
                    isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value == "__main__"
                ):
                    continue
            raise ValueError(f"{path.name}: unexpected top-level executable statement on line {node.lineno}")


def _validate_tree(root: Path) -> None:
    if root.name != SKILL_NAME:
        raise ValueError(f"folder name must be {SKILL_NAME!r}")
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        raise ValueError("SKILL.md is required")
    text = skill_md.read_text(encoding="utf-8")
    frontmatter, body = _frontmatter(text)
    if set(frontmatter) != {"name", "description"}:
        raise ValueError("frontmatter must contain only name and description")
    if frontmatter["name"] != SKILL_NAME:
        raise ValueError("frontmatter name does not match folder")
    description = frontmatter["description"]
    if len(description) < 80 or "Word" not in description or "Zotero" not in description:
        raise ValueError("description must clearly state capability and trigger context")
    if "## Safety boundary" not in body or "## Output contract" not in body:
        raise ValueError("SKILL.md is missing required safety/output sections")

    expected = REQUIRED_REFERENCES | REQUIRED_EVALS | {"scripts/verify_skill.py", "scripts/run_live_workflow.py", "scripts/refresh_word_zotero.ps1", "scripts/validate_word_zotero_ui.ps1", "assets/templates/offline-run-summary.md"}
    missing = sorted(relative for relative in expected if not (root / relative).is_file())
    if missing:
        raise ValueError(f"missing required files: {', '.join(missing)}")

    for reference in PATH_REFERENCE_RE.findall(text):
        pure = PurePosixPath(reference)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"unsafe local reference: {reference}")
        if not (root / Path(*pure.parts)).is_file():
            raise ValueError(f"broken local reference: {reference}")

    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in FORBIDDEN_PARTS for part in relative.parts):
            raise ValueError(f"forbidden path in Skill tree: {relative}")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise ValueError(f"forbidden compiled file: {relative}")
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed: {relative}")

    _validate_eval_definitions(root)
    _validate_python_scripts(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.skill_directory.expanduser().resolve()
    try:
        _validate_tree(root)
    except (OSError, UnicodeError, TypeError, ValueError, json.JSONDecodeError, SyntaxError) as exc:
        print(f"Skill verification failed: {exc}", file=sys.stderr)
        return 1
    files = sum(1 for path in root.rglob("*") if path.is_file())
    print(f"Skill verification passed: {root} ({files} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
