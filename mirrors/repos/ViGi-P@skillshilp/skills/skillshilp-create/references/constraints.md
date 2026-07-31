# Constraints

Use this document to validate newly created Agent Skills.

## Directory

| Required | Optional |
|----------|----------|
| `SKILL.md` | `references/` |
| | `scripts/` |
| | `assets/` |

Create optional directories only when they provide meaningful value.
Do not create empty or placeholder directories.
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
