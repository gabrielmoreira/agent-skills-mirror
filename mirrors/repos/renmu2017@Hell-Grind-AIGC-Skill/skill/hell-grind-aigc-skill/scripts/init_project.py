#!/usr/bin/env python3
"""Safely initialize a model-agnostic AIGC video project."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "project-template"
PROJECT_ID_PATTERN = re.compile(r"^PRJ-[A-Z0-9][A-Z0-9-]{1,61}$")
ASPECT_RATIO_PATTERN = re.compile(r"^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$")


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").upper()
    return slug[:32] or "PROJECT"


def yaml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")


def normalize_aspect_ratio(value: str) -> str:
    normalized = value.strip()
    match = ASPECT_RATIO_PATTERN.fullmatch(normalized)
    if not match or any(float(part) <= 0 for part in match.groups()):
        raise ValueError("aspect ratio must use positive W:H values, for example 16:9 or 2.39:1")
    return normalized


def replace_placeholders(root: Path, values: dict[str, str]) -> None:
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        text = path.read_text(encoding="utf-8")
        for key, value in values.items():
            text = text.replace("{{" + key + "}}", value)
        path.write_text(text, encoding="utf-8")


def initialize_project(name: str, output: Path, project_id: str, aspect_ratio: str) -> Path:
    if not TEMPLATE_ROOT.is_dir():
        raise ValueError(f"Project template is missing: {TEMPLATE_ROOT}")
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise ValueError("project ID must match PRJ-[A-Z0-9-]")
    if not name.strip():
        raise ValueError("project name cannot be empty")
    aspect_ratio = normalize_aspect_ratio(aspect_ratio)
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(f"refusing to overwrite non-empty target: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".hell-grind-init-", dir=output.parent))
    try:
        shutil.copytree(TEMPLATE_ROOT, staging, dirs_exist_ok=True)
        replace_placeholders(
            staging,
            {
                "PROJECT_ID": project_id,
                "PROJECT_NAME": yaml_string(name.strip()),
                "CREATED_DATE": date.today().isoformat(),
                "ASPECT_RATIO": yaml_string(aspect_ratio),
            },
        )
        if output.exists():
            output.rmdir()
        staging.rename(output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Human-readable project name")
    parser.add_argument("--output", required=True, type=Path, help="New or empty project directory")
    parser.add_argument("--project-id", help="Stable ID beginning with PRJ-")
    parser.add_argument("--aspect-ratio", default="16:9", help="Delivery aspect ratio")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_id = args.project_id or f"PRJ-{date.today().strftime('%Y%m%d')}-{slugify(args.name)}"
    try:
        output = initialize_project(args.name, args.output.expanduser().resolve(), project_id, args.aspect_ratio)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(f"Created {project_id} at {output}")
    print("Schema version: 2")
    print("Network requests: 0; database operations: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
