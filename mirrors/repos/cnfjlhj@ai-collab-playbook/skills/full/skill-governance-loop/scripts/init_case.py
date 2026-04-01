#!/usr/bin/env python3
import argparse
import datetime as dt
import re
from pathlib import Path


CASE_TEMPLATE = """# Case

- Date: {date}
- Skill: {skill}
- Current version: {version}
- Request class:
- Why this case exists: {reason}

## Expected behavior

## Observed behavior

## Evidence

- Original user phrasing:
- Files / paths:
- Triggered skill(s):
- Missing skill(s):
- Output problem:

## Failure mode

- should trigger but did not
- should not trigger but did
- triggered but low quality
- overlap / duplication
- belongs in AGENTS.md instead

## Working hypothesis

## Next check
"""


SCORECARD_TEMPLATE = """# Scorecard

- Skill: {skill}
- Version: {version}
- Auditor:
- Date: {date}

| Dimension | Score | Notes |
|---|---:|---|
| Trigger Fit |  |  |
| Scope Discipline |  |  |
| Progressive Disclosure |  |  |
| Structural Integrity |  |  |
| Empirical Gain |  |  |
| Maintenance Cost |  |  |
| Total |  |  |

## Strongest keep evidence

## Strongest disable evidence

## Nearest competing skill

## Routing / content / scope diagnosis
"""


DECISION_TEMPLATE = """# Decision

- Skill: {skill}
- Old version: {version}
- New version:
- Primary decision:
- Confidence:

## Why this decision

## Alternatives considered

- keep-enabled
- keep-disabled
- merge
- split
- archive
- move-to-agents
- move-to-skill

## Required changes

## Validation plan

## Next version hypothesis
"""


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    return slug or "case"


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a skill governance case folder.")
    parser.add_argument("--skill", required=True, help="Skill name under review")
    parser.add_argument("--reason", required=True, help="Short reason or failure slug")
    parser.add_argument(
        "--root",
        default="skill-governance-data",
        help="Root folder where governance artifacts will be stored",
    )
    parser.add_argument(
        "--version",
        default="unknown",
        help="Current skill version or branch label",
    )
    args = parser.parse_args()

    today = dt.date.today().isoformat()
    case_slug = f"{today}-{slugify(args.skill)}-{slugify(args.reason)}"
    case_dir = Path(args.root) / "cases" / case_slug
    case_dir.mkdir(parents=True, exist_ok=True)

    context = {
        "date": today,
        "skill": args.skill,
        "reason": args.reason,
        "version": args.version,
    }

    write_file(case_dir / "case.md", CASE_TEMPLATE.format(**context))
    write_file(case_dir / "scorecard.md", SCORECARD_TEMPLATE.format(**context))
    write_file(case_dir / "decision.md", DECISION_TEMPLATE.format(**context))

    print(case_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
