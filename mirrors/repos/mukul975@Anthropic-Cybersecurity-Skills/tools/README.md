# Skill Validation Tools

## validate-skill.py

Validate SKILL.md metadata before submitting a PR.

### Usage

```bash
# Validate a single skill
python tools/validate-skill.py skills/my-new-skill/

# Validate all skills
python tools/validate-skill.py --all
```

### What it checks

- SKILL.md exists in the skill directory
- Valid YAML frontmatter (between `---` markers)
- Required fields present: `name`, `description`, `domain`, `subdomain`, `tags`, `version`, `author`, `license`
- Name is kebab-case, 1–64 characters
- Description is at least 50 characters (agentskills.io caps it at 1024; `tools/validate-agentskills.py` enforces that)
- Domain is `cybersecurity`
- Subdomain is from the allowed list
- Tags is a list with at least 2 items

### Requirements

Python 3.8+ and PyYAML (`pip install pyyaml`).

All frontmatter is parsed by `skill_frontmatter.py`, the single PyYAML-backed loader. It replaced three hand-rolled regex parsers that silently truncated multi-line descriptions to their first line — that bug shipped 604 of 817 descriptions broken in `index.json`. Do not reintroduce regex frontmatter parsing; CI fails the build if it detects any.
