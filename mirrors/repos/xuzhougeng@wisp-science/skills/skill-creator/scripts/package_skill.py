#!/usr/bin/env python3
"""Zip a validated skill folder into a distributable `<name>.skill` archive.

Usage: python package_skill.py <skill-directory> [output-directory]

Validates first (via quick_validate.check_skill), then writes the archive with
the skill folder name as the top-level entry. Build junk (__pycache__,
node_modules, *.pyc, .DS_Store) and a root-level `evals/` folder are skipped.
"""

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from quick_validate import check_skill

SKIP_ANYWHERE = {"__pycache__", "node_modules", ".DS_Store"}
SKIP_SUFFIXES = {".pyc"}
SKIP_AT_ROOT = {"evals"}


def _included(rel):
    """rel is relative to the skill folder itself."""
    if rel.parts and rel.parts[0] in SKIP_AT_ROOT:
        return False
    if set(rel.parts) & SKIP_ANYWHERE:
        return False
    return rel.suffix not in SKIP_SUFFIXES


def package(skill_dir, out_dir=None):
    """Return the written archive path, raising ValueError on a bad skill."""
    skill_dir = Path(skill_dir).resolve()
    problems = check_skill(skill_dir)
    if problems:
        raise ValueError("; ".join(problems))

    out_dir = Path(out_dir).resolve() if out_dir else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{skill_dir.name}.skill"

    files = sorted(
        p for p in skill_dir.rglob("*")
        if p.is_file() and _included(p.relative_to(skill_dir))
    )
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, Path(skill_dir.name) / p.relative_to(skill_dir))
    return archive, files


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__.strip().splitlines()[2])
        return 1
    try:
        archive, files = package(argv[1], argv[2] if len(argv) == 3 else None)
    except ValueError as e:
        print(f"validation failed: {e}")
        return 1
    for p in files:
        print(f"  + {Path(p).relative_to(Path(argv[1]).resolve())}")
    print(f"wrote {archive} ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
