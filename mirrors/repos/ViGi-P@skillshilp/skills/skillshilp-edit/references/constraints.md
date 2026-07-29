# Constraints

Use this document to validate updated Agent Skills.

## Directory

| Required | Optional |
|----------|----------|
| `SKILL.md` | `references/` |
| | `scripts/` |
| | `assets/` |

Preserve the existing directory structure unless a structural change provides meaningful value.

Create optional directories only when they provide meaningful value.

Do not introduce empty or placeholder directories.

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

Unless explicitly requested, preserve existing frontmatter fields that remain valid.

---

## `SKILL.md`

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

Do not relocate content unless doing so clearly improves maintainability or specification compliance.

---

## References

- Use relative paths.
- Avoid deep reference chains.
- Prefer multiple focused files.
- Preserve existing references unless they are incorrect or obsolete.

---

## Validation Checklist

Before returning:

- ✓ Valid frontmatter
- ✓ Directory matches `name`
- ✓ Searchable description
- ✓ Correct file placement
- ✓ Single responsibility
- ✓ No duplicate documentation
- ✓ Progressive disclosure
- ✓ Existing behaviour preserved unless intentionally changed
