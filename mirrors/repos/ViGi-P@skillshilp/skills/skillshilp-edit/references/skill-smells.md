# Skill Smells

Review every updated Agent Skill before returning it.

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
| Unnecessary rewrites | Make the smallest effective change |
| Behavioural regressions | Preserve existing behaviour unless intentionally changed |
| Broken activation criteria | Preserve discoverability unless intentionally updated |
| Unnecessary renames | Preserve names unless they improve clarity or correctness |
| Broken references | Update all affected relative paths |
| Missing concrete examples | Validate intended behaviour against 2–3 realistic requests |
| Unsupported frontmatter | Use only portable spec fields |
| Oversized `SKILL.md` | Move conditional detail into references |
| Leaked validation context | Forward-test with raw task artifacts only |
| Excessive output dumping | Summarize written files instead of pasting full contents |
| Spec drift | Recheck constraints before returning changes |

---

## Review Checklist

Before returning the updated Agent Skill:

- ✓ Behaviour preserved unless intentionally changed
- ✓ Activation criteria preserved unless intentionally changed
- ✓ Specification compliant
- ✓ Easily discoverable
- ✓ Single responsibility
- ✓ Composition-friendly
- ✓ Modular
- ✓ Maintainable
- ✓ Progressive disclosure
- ✓ Minimal duplication
- ✓ Token-efficient
- ✓ No broken references
- ✓ Portable frontmatter and resources
- ✓ Existing examples or behaviours still work
