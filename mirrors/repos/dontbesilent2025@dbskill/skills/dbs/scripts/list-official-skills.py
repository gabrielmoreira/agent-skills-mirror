#!/usr/bin/env python3
"""列出当前版本登记且已经安装的正式 dbskill Skill。"""

from __future__ import annotations

import json
from pathlib import Path


def find_project_root(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        if (candidate / ".claude-plugin" / "marketplace.json").is_file():
            return candidate
    return None


def read_frontmatter_description(skill_path: Path) -> str:
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return ""

    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            break
        if not line.startswith("description:"):
            continue

        value = line.removeprefix("description:").strip()
        if value not in {"", "|", ">"}:
            return value.strip('"\'')

        parts: list[str] = []
        for continuation in lines[index + 1 :]:
            if continuation == "---" or (
                continuation and not continuation[0].isspace()
            ):
                break
            stripped = continuation.strip()
            if stripped:
                parts.append(stripped)
        return " ".join(parts)

    return ""


def locate_installed_skill(name: str, search_roots: list[Path]) -> Path | None:
    for root in search_roots:
        candidate = root / name
        if (candidate / "SKILL.md").is_file():
            return candidate.resolve()
    return None


def load_catalog(skill_dir: Path, project_root: Path | None) -> list[dict[str, str]]:
    if project_root is not None:
        marketplace_path = project_root / ".claude-plugin" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        return [
            {
                "name": plugin.get("name", ""),
                "description": plugin.get("description", ""),
            }
            for plugin in marketplace.get("plugins", [])
        ]

    snapshot_path = skill_dir / "references" / "official-skill-names.txt"
    if not snapshot_path.is_file():
        raise SystemExit("未找到 Marketplace 或正式 Skill 名称快照")
    return [
        {"name": line.strip(), "description": ""}
        for line in snapshot_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def main() -> int:
    skill_dir = Path(__file__).resolve().parent.parent
    project_root = find_project_root(skill_dir)
    catalog = load_catalog(skill_dir, project_root)

    search_roots = [skill_dir.parent]
    if project_root is not None:
        search_roots.insert(0, project_root / "skills")
    user_root = Path.home()
    search_roots.extend(
        [
            user_root / ".agents" / "skills",
            user_root / ".codex" / "skills",
            user_root / ".claude" / "skills",
        ]
    )

    results: list[dict[str, str]] = []
    for entry in catalog:
        name = entry.get("name", "")
        if not name or name == "dbs" or "beta" in name or "private" in name:
            continue

        skill_dir_path = locate_installed_skill(name, search_roots)
        if skill_dir_path is None:
            continue
        skill_path = skill_dir_path / "SKILL.md"

        results.append(
            {
                "name": name,
                "description": entry.get("description", "")
                or read_frontmatter_description(skill_path),
                "source": str(skill_dir_path),
            }
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
