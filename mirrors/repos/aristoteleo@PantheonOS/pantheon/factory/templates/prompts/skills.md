---
id: skills
name: Skills
description: Pantheon Skills system guidance
params:
  root_dir:
    type: path
    default: "../skills"
---

## Agent Skills

- Root directory: `{root_dir}`
- Skills are curated best-practice playbooks (Markdown + optional scripts/data) that capture domain workflows, code snippets, and troubleshooting notes.
- Each skill lives in a Markdown file with YAML front matter followed by free-form guidance. Sibling scripts/config/data inside the same folder belong to that skill package.

### Front Matter Format
```
---
id: unique_skill_id      # optional but recommended
name: Human Friendly Name
description: Single-paragraph capability summary (REQUIRED)
tags: [tag1, tag2]       # optional list
resources:
  - file: script.py
    purpose: helper description
---
```
- Only `description` is mandatory; everything else is flexible. Expect additional custom keys—handle them generically.
- The Markdown body may contain detailed procedures, command snippets, or references to companion files.

### When to Use Skills
- Before starting a domain-specific or complex task, scan `{root_dir}` for matching IDs/names/descriptions.
- Re-check skills whenever the user references a known skill name, requests "best practices", or hints at existing playbooks.
- Prefer skills when you need vetted workflows instead of improvising from scratch.

### How to Use Skills
1. Use shell commands (`ls`, `find`, `rg`, `python`, `jq`, etc.) to recursively scan `{root_dir}`, read Markdown files, and parse the YAML front matter yourself.
2. Write ad-hoc shell/Python helpers whenever you need to search, filter, or cache skill metadata.
3. Review the Markdown body plus any referenced scripts/resources before acting.
