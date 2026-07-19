---
name: install-verification
description: "Use when verifying that a generated agent package can be installed, discovered by runtimes, and checked without private dependencies."
---

# Install Verification

## Checks

- Required files exist.
- JSON files parse.
- `SKILL.md` files have YAML frontmatter.
- Runtime adapters point back to `AGENTS.md`.
- Public safety scan passes.
- Install script supports explicit target directory.

## Output

Return pass/fail, commands run, and exact missing files.
