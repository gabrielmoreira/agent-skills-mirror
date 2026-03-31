#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def read_skill_md(skill_path: Path) -> str:
    skill_md = skill_path / "SKILL.md" if skill_path.is_dir() else skill_path
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found: {skill_md}")
    return skill_md.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}
    frontmatter = parts[1]
    data = {}
    for line in frontmatter.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip().strip("'\"")
    return data


def extract_body(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    parts = text.split("---\n", 2)
    return parts[2] if len(parts) >= 3 else text


def find_path_refs(text: str):
    patterns = re.findall(r"(references/[A-Za-z0-9_./-]+|scripts/[A-Za-z0-9_./-]+|assets/[A-Za-z0-9_./-]+)", text)
    seen = []
    for item in patterns:
        if item not in seen:
            seen.append(item)
    return seen


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def score_skill(skill_path: Path, text: str):
    frontmatter = parse_frontmatter(text)
    body = extract_body(text)
    body_lines = len(body.splitlines())
    word_count = len(re.findall(r"\S+", body))
    desc = frontmatter.get("description", "")
    name = frontmatter.get("name", "")
    version = frontmatter.get("version", "")
    path_refs = find_path_refs(text)

    issues = []
    notes = []

    metadata_score = 0
    if name:
        metadata_score += 8
    else:
        issues.append("missing frontmatter field: name")
    if desc:
        metadata_score += 8
    else:
        issues.append("missing frontmatter field: description")
    if version:
        metadata_score += 4
    else:
        issues.append("missing frontmatter field: version")

    desc_score = 0
    if desc:
        length = len(desc)
        if 140 <= length <= 320:
            desc_score += 8
        elif 80 <= length <= 420:
            desc_score += 5
        else:
            issues.append("description length is outside the preferred range")

        if re.search(r"(use when|should be used when|trigger|asks to)", desc, re.IGNORECASE):
            desc_score += 8
        else:
            issues.append("description does not clearly express trigger conditions")

        if "`" in desc or '"' in desc or "'" in desc:
            desc_score += 4
        else:
            issues.append("description lacks concrete phrase examples")

        if re.search(r"(skill|workflow|review|governance|audit|version)", desc, re.IGNORECASE):
            desc_score += 5
    desc_score = clamp(desc_score, 0, 25)

    structure_score = 0
    if body_lines <= 260:
        structure_score += 8
    elif body_lines <= 500:
        structure_score += 5
    else:
        issues.append("SKILL.md body is large; consider moving detail into references/")

    if path_refs:
        structure_score += 6
    elif body_lines > 220:
        issues.append("large body with no references/ or scripts/ paths")
    else:
        structure_score += 4

    missing_refs = []
    for ref in path_refs:
        if not (skill_path / ref).exists():
            missing_refs.append(ref)
    if missing_refs:
        issues.append(f"referenced paths missing: {', '.join(missing_refs)}")
    else:
        structure_score += 6

    if (skill_path / "scripts").exists() or (skill_path / "references").exists():
        structure_score += 5

    governance_score = 0
    if re.search(r"##\s+When to Use", body, re.IGNORECASE):
        governance_score += 5
    else:
        issues.append("missing explicit 'When to Use' section")

    if re.search(r"(do not use|skip this|do not)", body, re.IGNORECASE):
        governance_score += 5
    else:
        issues.append("missing explicit boundary or skip guidance")

    if re.search(r"^\d+\.", body, re.MULTILINE):
        governance_score += 5
    else:
        issues.append("workflow is not clearly stepwise")

    if re.search(r"(output contract|acceptance|decision)", body, re.IGNORECASE):
        governance_score += 5
    else:
        issues.append("missing explicit output or acceptance contract")

    maintainability_score = 0
    if word_count <= 700:
        maintainability_score += 8
    elif word_count <= 1400:
        maintainability_score += 5
    else:
        issues.append("body word count is high for an always-loaded skill body")

    if version:
        maintainability_score += 4
    if re.search(r"(references/|scripts/)", body):
        maintainability_score += 4
    if re.search(r"(hypothesis|next|iterate|version)", body, re.IGNORECASE):
        maintainability_score += 4

    notes.append(f"body_lines={body_lines}")
    notes.append(f"word_count={word_count}")
    notes.append(f"path_refs={len(path_refs)}")

    breakdown = {
        "Metadata": clamp(metadata_score, 0, 20),
        "Description": clamp(desc_score, 0, 25),
        "Structure": clamp(structure_score, 0, 25),
        "Governance": clamp(governance_score, 0, 20),
        "Maintainability": clamp(maintainability_score, 0, 10),
    }
    total = sum(breakdown.values())

    return frontmatter, breakdown, total, issues, notes


def render_report(skill_path: Path, frontmatter: dict, breakdown: dict, total: int, issues, notes) -> str:
    lines = []
    lines.append(f"# Static Audit: {frontmatter.get('name', skill_path.name)}")
    lines.append("")
    lines.append(f"- Skill path: `{skill_path}`")
    lines.append(f"- Version: `{frontmatter.get('version', 'missing')}`")
    lines.append(f"- Total score: **{total}/100**")
    lines.append("")
    lines.append("## Breakdown")
    for key, value in breakdown.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Findings")
    if issues:
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- no major static issues detected")
    lines.append("")
    lines.append("## Notes")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Reminder")
    lines.append("- This is a static baseline only.")
    lines.append("- Do not treat this score as proof of empirical usefulness.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a static quality audit on a skill folder.")
    parser.add_argument("skill_path", help="Path to the skill directory or SKILL.md")
    parser.add_argument("--report-out", help="Optional markdown report output path")
    args = parser.parse_args()

    target = Path(args.skill_path).resolve()
    base_dir = target if target.is_dir() else target.parent
    text = read_skill_md(target)
    frontmatter, breakdown, total, issues, notes = score_skill(base_dir, text)
    report = render_report(base_dir, frontmatter, breakdown, total, issues, notes)

    if args.report_out:
        Path(args.report_out).write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
