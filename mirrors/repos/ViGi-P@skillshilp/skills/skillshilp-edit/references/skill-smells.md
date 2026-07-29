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
