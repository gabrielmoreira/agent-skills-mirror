---
name: plugin-authoring
description: "Author and publish GitHub Copilot CLI plugins and plugin marketplaces. Use when asked to create a plugin, package skills, add a marketplace, write plugin.json or marketplace.json, or distribute Copilot CLI customizations."
---

# GitHub Copilot CLI Plugin Authoring

Use these conventions when packaging reusable skills and prompts for the public
GitHub Copilot CLI.

## Single-plugin repository

```text
repository/
├── plugin.json
├── README.md
├── CHANGELOG.md
└── skills/
    └── example-skill/
        ├── SKILL.md
        └── example.prompt.md
```

Example `plugin.json`:

```json
{
  "name": "example-plugin",
  "description": "Focused description of the plugin",
  "version": "1.0.0",
  "author": {
    "name": "Example Author",
    "url": "https://github.com/example"
  },
  "license": "MIT",
  "keywords": ["copilot", "example"],
  "skills": ["skills/"]
}
```

Install directly from GitHub:

```text
copilot plugin install owner/repository
```

## Multi-plugin marketplace

Use a marketplace when one repository contains several independently versioned
plugins:

```text
repository/
├── .github/
│   └── plugin/
│       ├── marketplace.json
│       ├── example-copilot/
│       │   ├── plugin.json
│       │   ├── README.md
│       │   └── skills/
│       └── example-authoring/
│           ├── plugin.json
│           ├── README.md
│           └── skills/
└── README.md
```

Each plugin source directory MUST be self-contained. Do not point its manifest
at skills outside that directory.

Example marketplace:

```json
{
  "name": "example-skills",
  "owner": { "name": "Example Author" },
  "metadata": {
    "description": "Example public Copilot CLI plugins",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "example-copilot",
      "description": "Copilot workflow skills",
      "version": "1.0.0",
      "source": ".github/plugin/example-copilot"
    }
  ]
}
```

Register and install:

```text
copilot plugin marketplace add owner/repository
copilot plugin marketplace browse example-skills
copilot plugin install example-copilot@example-skills
```

Plugins can also be installed directly from a subdirectory:

```text
copilot plugin install owner/repository:.github/plugin/example-copilot
```

## Skills

Every `SKILL.md` begins with valid YAML frontmatter:

```markdown
---
name: example-skill
description: "Specific capability and trigger phrases. Use when asked to..."
---
```

Rules:

- Use kebab-case skill names.
- Make the description specific enough for automatic discovery.
- Include executable patterns, failure modes, and examples.
- Keep organization-specific endpoints, credentials, and private tooling out of
  public skills.
- Prompt templates use `.prompt.md` and include a frontmatter description.

## In-repository discovery

Copilot CLI discovers skills under `.github/skills/`. In a multi-plugin
repository, make `.github/skills/` a directory containing one symlink per skill
that points to its owning plugin.

## Versioning

- Version each focused plugin independently.
- Keep a plugin's `plugin.json` version synchronized with its marketplace entry.
- Change marketplace `metadata.version` only when the catalog structure changes.
- Update the owning plugin README and repository changelog for every release.
- Use semantic versioning and immutable release tags.

## Validation checklist

1. Parse every JSON manifest.
2. Validate YAML frontmatter for every skill and prompt.
3. Confirm every marketplace source contains its own `plugin.json`.
4. Confirm manifest and marketplace versions match.
5. Scan the repository for secrets, private URLs, and internal-only tooling.
6. Install from a clean environment using both marketplace and direct-subdirectory syntax.
