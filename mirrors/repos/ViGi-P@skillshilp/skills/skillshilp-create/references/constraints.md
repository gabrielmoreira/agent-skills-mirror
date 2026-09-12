# Constraints

Use this document to validate newly created Agent Skills.

## Directory

A skill is a self-contained directory containing `SKILL.md` and, optionally, supporting resources.

| Required | Optional |
|----------|----------|
| `SKILL.md` | `references/` |
| | `scripts/` |
| | `assets/` |

Create optional directories only when they provide meaningful value.
Do not create empty or placeholder directories.

The parent directory used to discover or install the skill is outside the skill's portable structure.

`.agents/skills/` is a widely adopted project- and user-level convention for cross-client skill discovery, but it is not required by the Agent Skills specification. Clients may use other discovery directories.

Do not place client-specific discovery directories inside the skill itself. For example, when `.agents/skills/` is the host's discovery directory, the correct structure is:

```text
.agents/
└── skills/
    └── my-skill/
        ├── SKILL.md
        ├── references/
        ├── scripts/
        └── assets/
```

The skill directory is `my-skill/`; `.agents/skills/` is its parent discovery directory.

Do not add product-specific metadata directories, client configs, or product-specific helper scripts when portability is the goal.

---

## Frontmatter

| Field | Required | Rules |
|--------|----------|------|
| `name` | ✓ | 1–64 chars, lowercase letters/numbers/hyphens, no leading/trailing/consecutive hyphens, matches directory |
| `description` | ✓ | Explains **what** the skill does, **when** it should be activated, and what distinguishes it from similar skills (≤1024 chars) |
| `license` | | Include only if applicable |
| `compatibility` | | Include only when environment requirements exist (≤500 chars) |
| `metadata` | | Optional portable key-value metadata |
| `allowed-tools` | | Space-separated string of pre-approved tools; support varies by client |

Use only these portable fields.
Keep descriptions as single-line scalars unless multiline YAML is truly necessary.

---

## SKILL.md

Keep concise.

Contains only:

- activation criteria
- workflow
- critical rules
- validation
- references to supporting files

Move implementation details elsewhere.
Keep `SKILL.md` under 500 lines.

---

## File Placement

| Content | Location |
|---------|----------|
| APIs | `references/` |
| Algorithms | `references/` |
| Schemas | `references/` |
| Templates | `assets/` |
| Example documents | `assets/` |
| Repeated deterministic logic | `scripts/` |

Scripts should be minimal Bash when possible. If Bash is not enough, document the dependency and do not assume it is portable.

---

## References

- Use relative paths.
- Avoid deep reference chains.
- Prefer multiple focused files.
- Link directly from `SKILL.md` to any reference the agent may need.
- Add a table of contents to long reference files.

---

## Validation Checklist

Before returning:

- ✓ Valid frontmatter
- ✓ Directory matches `name`
- ✓ Searchable description
- ✓ Correct file placement
- ✓ No duplicate documentation
- ✓ Progressive disclosure
- ✓ Single responsibility
- ✓ No unnecessary product-specific metadata or scripts
- ✓ Minimal, documented script dependencies
