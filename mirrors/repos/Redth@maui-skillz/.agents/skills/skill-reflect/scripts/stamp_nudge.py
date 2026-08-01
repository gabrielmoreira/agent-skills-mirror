#!/usr/bin/env python3
"""stamp_nudge.py — Insert, check, or remove the skill-reflect nudge block in a SKILL.md.

Usage:
    python3 stamp_nudge.py <path/to/SKILL.md>           # insert or idempotently update
    python3 stamp_nudge.py <path/to/SKILL.md> --remove  # strip the nudge block
    python3 stamp_nudge.py <path/to/SKILL.md> --check   # exit 1 if nudge block is absent

The nudge block template is resolved relative to this script:
    ../templates/improve-this-skill.md
"""

import sys
import pathlib
import argparse

BEGIN = "<!-- BEGIN skill-reflect nudge -->"
END = "<!-- END skill-reflect nudge -->"

TEMPLATE = (
    pathlib.Path(__file__).resolve().parent.parent
    / "templates"
    / "improve-this-skill.md"
)


def load_template() -> str:
    if not TEMPLATE.exists():
        print(f"error: template not found: {TEMPLATE}", file=sys.stderr)
        sys.exit(2)
    return TEMPLATE.read_text(encoding="utf-8")


def has_block(text: str) -> bool:
    return BEGIN in text and END in text


def stamp(text: str, block: str) -> str:
    """Insert or replace the nudge block idempotently. Never corrupts other content."""
    # Normalize: block ends with exactly one newline
    block = block.rstrip("\n") + "\n"

    if has_block(text):
        # Replace the existing region, preserving surrounding content exactly
        start = text.index(BEGIN)
        end = text.index(END) + len(END)
        # Consume the newline that immediately follows the END marker line
        if end < len(text) and text[end] == "\n":
            end += 1
        return text[:start] + block + text[end:]
    else:
        # Append with a blank-line separator
        base = text.rstrip("\n")
        separator = "\n\n" if base else ""
        return base + separator + block


def strip_block(text: str) -> str:
    """Remove the nudge block and its blank-line separator."""
    start = text.index(BEGIN)
    end = text.index(END) + len(END)
    if end < len(text) and text[end] == "\n":
        end += 1
    prefix = text[:start]
    # Remove the blank separator line that stamp() adds before the block
    if prefix.endswith("\n\n"):
        prefix = prefix[:-1]
    return prefix + text[end:]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stamp (insert/update), check, or remove the skill-reflect nudge block.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "skill_md",
        metavar="SKILL.md",
        help="Path to the target skill file",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--remove",
        action="store_true",
        help="Remove the nudge block from the file",
    )
    group.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the nudge block is absent (no file modifications)",
    )
    args = parser.parse_args()

    target = pathlib.Path(args.skill_md)

    if not target.exists():
        if args.check:
            print(f"ABSENT  {target} — file not found", file=sys.stderr)
            sys.exit(1)
        if args.remove:
            print(f"skip    {target} — file not found; nothing to remove")
            sys.exit(0)
        print(f"error   {target} — file not found", file=sys.stderr)
        sys.exit(2)

    original = target.read_text(encoding="utf-8")

    # --check: read-only exit-code probe
    if args.check:
        if has_block(original):
            print(f"ok      nudge block present in {target}")
            sys.exit(0)
        print(f"ABSENT  nudge block not found in {target}", file=sys.stderr)
        sys.exit(1)

    # --remove: strip the block
    if args.remove:
        if not has_block(original):
            print(f"skip    nudge block not found in {target}; nothing to remove")
            sys.exit(0)
        updated = strip_block(original)
        # Preserve original trailing-newline convention
        if original.endswith("\n") and not updated.endswith("\n"):
            updated += "\n"
        target.write_text(updated, encoding="utf-8")
        print(f"removed nudge block stripped from {target}")
        sys.exit(0)

    # Default: insert or idempotently update
    block = load_template()
    was_present = has_block(original)
    updated = stamp(original, block)
    # Preserve original trailing-newline convention
    if original.endswith("\n") and not updated.endswith("\n"):
        updated += "\n"
    target.write_text(updated, encoding="utf-8")
    action = "updated" if was_present else "stamped"
    print(f"{action}  nudge block written to {target}")


if __name__ == "__main__":
    main()
