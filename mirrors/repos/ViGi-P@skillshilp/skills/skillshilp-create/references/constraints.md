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

---

## Frontmatter

| Field | Required | Rules |
|--------|----------|------|
| `name` | ✓ | 1–64 chars, lowercase letters/numbers/hyphens, no leading/trailing/consecutive hyphens, matches directory |
| `description` | ✓ | Explains **what** the skill does, **when** it should be activated, and what distinguishes it from similar skills (≤1024 chars) |
| `license` | | Include only if applicable |
| `compatibility` | | Include only when environment requirements exist |
| `metadata` | | Optional metadata |
| `allowed-tools` | | Optional |

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

---

## File Placement

| Content | Location |
|---------|----------|
| APIs | `references/` |
| Algorithms | `references/` |
| Schemas | `references/` |
| Templates | `assets/` |
| Example documents | `assets/` |
| Executable logic | `scripts/` |

---

## References

- Use relative paths.
- Avoid deep reference chains.
- Prefer multiple focused files.

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
