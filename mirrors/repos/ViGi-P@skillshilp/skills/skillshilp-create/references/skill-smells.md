# Skill Smells

Review every newly created Agent Skill before returning it.

| Smell | Preferred Fix |
|-------|----------------|
| God skill | Split into focused skills |
| Multiple responsibilities | Separate capabilities |
| Generic description | Add searchable activation criteria |
| Bloated `SKILL.md` | Move details into `references/` |
| Embedded templates | Move to `assets/` |
| Embedded schemas | Move to `assets/` |
| Embedded executable logic | Move to `scripts/` |
| Duplicate documentation | Keep one source of truth |
| Hidden assumptions | Document dependencies |
| Empty directories | Remove them |
| Dead references | Link or delete them |
| Undocumented scripts | Document requirements |
| Unnecessary scripts | Use Markdown or references instead |
| Non-portable scripts | Prefer minimal Bash or document dependency |
| Tight coupling | Separate responsibilities |
| Token waste | Remove repetition |
| Poor activation criteria | Make discovery explicit |
| Weak directory structure | Remove unnecessary hierarchy |
| Missing validation | Review against constraints and patterns |
| Premature abstraction | Create only directories and files that provide meaningful value |
| Over-engineering | Prefer the simplest architecture that satisfies the requirements |
| Missing composition opportunities | Split reusable capabilities into separate skills when appropriate |
| Missing concrete examples | Validate design against 2–3 realistic requests |
| Unsupported frontmatter | Use only portable spec fields |
| Oversized `SKILL.md` | Move conditional detail into references |
| Leaked validation context | Forward-test with raw task artifacts only |
| Excessive output dumping | Summarize written files instead of pasting full contents |

---

## Review Checklist

Before returning the newly created Agent Skill:

- ✓ Specification compliant
- ✓ Easily discoverable
- ✓ Single responsibility
- ✓ Composition-friendly
- ✓ Modular
- ✓ Maintainable
- ✓ Progressive disclosure
- ✓ Minimal duplication
- ✓ Token-efficient
- ✓ Portable frontmatter and resources
- ✓ Concrete examples support the architecture
