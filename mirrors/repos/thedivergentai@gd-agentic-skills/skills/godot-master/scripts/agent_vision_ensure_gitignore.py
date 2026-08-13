#!/usr/bin/env python3
"""Ensure project .gitignore covers .gdskills/ vision scratch."""

from __future__ import annotations

import argparse
from pathlib import Path

MARKER = ".gdskills/"


def ensure_gitignore(project_root: Path) -> bool:
    """
    Append `.gdskills/` to .gitignore if missing.
    Returns True if a change was made.
    """
    project_root = Path(project_root).resolve()
    gi = project_root / ".gitignore"
    if gi.is_file():
        text = gi.read_text(encoding="utf-8-sig")
        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped in (MARKER, ".gdskills", ".gdskills/**"):
                return False
            if stripped.startswith(".gdskills/") and not stripped.startswith("#"):
                return False
        suffix = "" if text.endswith("\n") or text == "" else "\n"
        with gi.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"{suffix}\n# GDSkills agent vision scratch (do not commit)\n{MARKER}\n")
        return True
    gi.write_text(
        f"# GDSkills agent vision scratch (do not commit)\n{MARKER}\n",
        encoding="utf-8",
        newline="\n",
    )
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Ensure .gdskills/ is gitignored")
    ap.add_argument("--project-root", type=Path, required=True)
    args = ap.parse_args()
    changed = ensure_gitignore(args.project_root)
    print(f"gitignore_updated={changed} path={args.project_root / '.gitignore'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
