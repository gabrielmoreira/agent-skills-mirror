#!/usr/bin/env python3
"""
Scaffold a domain-specific paper expert agent based on PaperClaw architecture.

Usage:
    python init_domain_agent.py --domain <domain_slug> --output <output_dir>
    python init_domain_agent.py --domain bioinfo-ml --output ~/agents/bioinfo-ml
    python init_domain_agent.py --domain cv-3d --output ~/agents/cv-3d \\
        --paperclaw-skills /work/work/PaperClaw/skills
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"

PAPERCLAW_SKILL_NAMES = [
    "arxiv-search",
    "semantic-scholar",
    "paper-review",
    "daily-search",
    "weekly-report",
]


def create_directory_structure(output_dir: Path) -> None:
    """Create all required directories."""
    dirs = [
        output_dir / "agent",
        output_dir / "skills",
        output_dir / "workspace" / "papers",
        output_dir / "workspace" / "reports",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"  [+] Created directory structure under {output_dir}")


def copy_agent_templates(output_dir: Path, domain_slug: str) -> None:
    """Copy models.json, schedules.json, and AGENT.md.template to agent/."""
    agent_dir = output_dir / "agent"

    # models.json
    models_src = TEMPLATES_DIR / "models.json"
    if models_src.exists():
        shutil.copy2(models_src, agent_dir / "models.json")
        print(f"  [+] Copied models.json → agent/models.json")
    else:
        # Write a minimal inline template
        minimal_models = {
            "providers": {
                "default": {
                    "baseUrl": "YOUR_API_BASE_URL",
                    "apiKey": "YOUR_API_KEY_HERE",
                    "api": "openai-completions",
                    "headers": {},
                    "models": [{
                        "id": "YOUR_MODEL_ID",
                        "name": "Domain Expert Model",
                        "reasoning": False,
                        "input": ["text"],
                        "contextWindow": 128000,
                        "maxTokens": 8192,
                        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
                    }]
                }
            }
        }
        with open(agent_dir / "models.json", "w") as f:
            json.dump(minimal_models, f, indent=2)
        print(f"  [+] Created minimal models.json → agent/models.json")

    # schedules.json
    schedules_src = TEMPLATES_DIR / "schedules.json"
    if schedules_src.exists():
        shutil.copy2(schedules_src, agent_dir / "schedules.json")
        print(f"  [+] Copied schedules.json → agent/schedules.json")

    # AGENT.md — copy template with domain_slug substituted in header
    agent_md_src = TEMPLATES_DIR / "AGENT.md.template"
    agent_md_dst = agent_dir / "AGENT.md"
    if agent_md_src.exists():
        content = agent_md_src.read_text(encoding="utf-8")
        # Replace the most visible placeholder to remind the user
        content = content.replace("{{AGENT_NAME}}", domain_slug.upper())
        agent_md_dst.write_text(content, encoding="utf-8")
        print(f"  [+] Created AGENT.md template → agent/AGENT.md (fill in {{{{ }}}} placeholders)")
    else:
        # Create a minimal stub
        stub = f"# {domain_slug.upper()} Paper Expert\n\n## 角色定位\n\n[TODO: Fill in domain expert role]\n\n## 关键词库\n\n[TODO: Add domain keywords]\n\n## 核心任务\n\n[TODO: Add 4 tasks]\n"
        agent_md_dst.write_text(stub, encoding="utf-8")
        print(f"  [+] Created AGENT.md stub → agent/AGENT.md")


def copy_paperclaw_skills(output_dir: Path, paperclaw_skills_path: str) -> None:
    """Copy all 5 skills from PaperClaw into the new agent's skills/ directory."""
    skills_src = Path(paperclaw_skills_path).expanduser().resolve()
    skills_dst = output_dir / "skills"

    if not skills_src.exists():
        print(f"  [!] PaperClaw skills path not found: {skills_src}")
        print(f"  [!] Skipping skill copy. Manually copy skills from PaperClaw.")
        return

    copied = []
    missing = []
    for skill_name in PAPERCLAW_SKILL_NAMES:
        src = skills_src / skill_name
        dst = skills_dst / skill_name
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            copied.append(skill_name)
        else:
            missing.append(skill_name)

    if copied:
        print(f"  [+] Copied skills: {', '.join(copied)}")
    if missing:
        print(f"  [!] Missing skills (not found in source): {', '.join(missing)}")


def create_skill_stubs(output_dir: Path) -> None:
    """Create empty skill stub directories if PaperClaw skills were not copied."""
    skills_dst = output_dir / "skills"
    created = []
    for skill_name in PAPERCLAW_SKILL_NAMES:
        skill_dir = skills_dst / skill_name
        if not skill_dir.exists():
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ndescription: [TODO: Copy from PaperClaw and adapt]\n---\n\n# {skill_name}\n\n[TODO: Copy content from PaperClaw/skills/{skill_name}/SKILL.md]\n",
                encoding="utf-8"
            )
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            created.append(skill_name)
    if created:
        print(f"  [+] Created skill stubs: {', '.join(created)}")


def init_workspace(output_dir: Path) -> None:
    """Initialize workspace files."""
    workspace = output_dir / "workspace"

    # evaluated_papers.json — empty registry
    registry_path = workspace / "evaluated_papers.json"
    if not registry_path.exists():
        registry_path.write_text("[]", encoding="utf-8")
        print(f"  [+] Initialized workspace/evaluated_papers.json (empty registry)")

    # papers/ directory is already created
    # reports/ directory is already created


def print_next_steps(output_dir: Path, domain_slug: str) -> None:
    """Print post-generation instructions."""
    print()
    print("=" * 60)
    print(f"Agent scaffolded at: {output_dir}")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Fill in AGENT.md placeholders ({{...}}):")
    print(f"   {output_dir}/agent/AGENT.md")
    print()
    print("2. Adapt skill SKILL.md files:")
    print(f"   - skills/arxiv-search/SKILL.md  → replace keyword list")
    print(f"   - skills/paper-review/SKILL.md  → replace 4 scoring dimensions + 10 questions")
    print(f"   - skills/daily-search/SKILL.md  → update domain name in task text")
    print(f"   - skills/weekly-report/SKILL.md → update domain name in report title")
    print()
    print("3. Set LLM credentials:")
    print(f"   {output_dir}/agent/models.json")
    print()
    print("4. Open OpenClaw and point it to:")
    print(f"   {output_dir}/agent/")
    print()
    print("5. Test with: 'Search for recent papers on <your core topic>'")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a domain-specific PaperClaw-style paper expert agent"
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="Domain slug (lowercase, hyphenated). E.g.: bioinfo-ml, cv-3d, quantum-ml"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory path. E.g.: ~/agents/bioinfo-ml"
    )
    parser.add_argument(
        "--paperclaw-skills",
        default=None,
        help="Path to PaperClaw's skills/ directory. If provided, copies all 5 skills."
    )

    args = parser.parse_args()

    output_dir = Path(args.output).expanduser().resolve()

    if output_dir.exists() and any(output_dir.iterdir()):
        print(f"Warning: output directory {output_dir} already exists and is not empty.")
        response = input("Continue and overwrite? [y/N] ").strip().lower()
        if response != "y":
            print("Aborted.")
            sys.exit(0)

    print(f"\nScaffolding domain agent: {args.domain}")
    print(f"Output: {output_dir}\n")

    create_directory_structure(output_dir)
    copy_agent_templates(output_dir, args.domain)

    if args.paperclaw_skills:
        copy_paperclaw_skills(output_dir, args.paperclaw_skills)
    else:
        print(f"  [!] --paperclaw-skills not provided. Creating skill stubs.")
        create_skill_stubs(output_dir)

    init_workspace(output_dir)
    print_next_steps(output_dir, args.domain)


if __name__ == "__main__":
    main()
