#!/usr/bin/env python3
"""Validate a Wisp skill folder: frontmatter shape, naming, and length limits.

Usage: python quick_validate.py <skill-directory>

Prints every problem found (not just the first) and exits non-zero if any.
"""

import re
import sys
from pathlib import Path

KNOWN_KEYS = {
    "name", "description", "license", "allowed-tools",
    "metadata", "compatibility", "fold_cue", "wisp",
}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500


def _parse_minimal(block):
    """Fallback frontmatter parser for machines without pyyaml.

    Handles what skill frontmatter actually uses: top-level `key: value`
    pairs, quoted scalars, and `>`/`|` block scalars. Nested values are kept
    only as opaque markers since validation never inspects them.
    """
    lines = block.split("\n")
    data, i = {}, 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2).strip()
        i += 1
        body = []
        while i < len(lines) and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
            body.append(lines[i].strip())
            i += 1
        if rest in (">", "|", ">-", "|-", ""):
            data[key] = " ".join(filter(None, body)) if body else {}
        else:
            data[key] = rest.strip("'\"")
    return data


def _frontmatter(text):
    """Return (dict, error) for the YAML block between the leading --- fences."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None, "SKILL.md must open with a `---` fenced YAML frontmatter block"
    try:
        import yaml
    except ModuleNotFoundError:
        return _parse_minimal(m.group(1)), None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return None, f"frontmatter is not valid YAML: {e}"
    if not isinstance(data, dict):
        return None, "frontmatter must be a YAML mapping"
    return data, None


def check_skill(skill_dir):
    """Return a list of problem strings; empty list means the skill passes."""
    skill_dir = Path(skill_dir)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_md} does not exist"]

    fm, err = _frontmatter(skill_md.read_text(encoding="utf-8"))
    if err:
        return [err]

    problems = []
    problems += [
        f"unknown frontmatter key `{k}` (known: {', '.join(sorted(KNOWN_KEYS))})"
        for k in sorted(set(fm) - KNOWN_KEYS)
    ]

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        problems.append("frontmatter needs a non-empty string `name`")
    else:
        name = name.strip()
        if not NAME_RE.fullmatch(name):
            problems.append(
                f"`name: {name}` must be kebab-case: lowercase/digit runs joined by single hyphens"
            )
        if len(name) > MAX_NAME:
            problems.append(f"`name` exceeds {MAX_NAME} chars ({len(name)})")
        if name != skill_dir.resolve().name:
            problems.append(
                f"`name: {name}` should match its folder `{skill_dir.resolve().name}`"
            )

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        problems.append("frontmatter needs a non-empty string `description`")
    else:
        if len(desc) > MAX_DESCRIPTION:
            problems.append(f"`description` exceeds {MAX_DESCRIPTION} chars ({len(desc)})")
        if "<" in desc or ">" in desc:
            problems.append("`description` must not contain angle brackets")

    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            problems.append("`compatibility` must be a string when present")
        elif len(compat) > MAX_COMPATIBILITY:
            problems.append(f"`compatibility` exceeds {MAX_COMPATIBILITY} chars ({len(compat)})")

    return problems


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2])
        return 1
    problems = check_skill(argv[1])
    for p in problems:
        print(f"FAIL: {p}")
    if not problems:
        print("OK: skill passes validation")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
