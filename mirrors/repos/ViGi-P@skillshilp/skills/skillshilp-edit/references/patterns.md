# Architectural Patterns

Choose the simplest pattern that fully represents the capability.

| Pattern | Primary Value | Typical Structure |
|---------|---------------|-------------------|
| Documentation | Instructions and guidance | `SKILL.md` + `references/` |
| Script-backed | Executable logic | `SKILL.md` + `scripts/` |
| Template | Reusable resources | `SKILL.md` + `assets/` |
| Reference Library | Large technical documentation | `SKILL.md` + `references/` |
| Review | Validation and quality assurance | `SKILL.md` + `references/` |

---

## Pattern Selection

| If the capability is primarily... | Choose... |
|-----------------------------------|-----------|
| Teaching or guiding | Documentation |
| Executing logic | Script-backed |
| Generating reusable resources | Template |
| Explaining technical material | Reference Library |
| Evaluating quality | Review |

Use a hybrid only when a single pattern is insufficient.

---

## Typical Layouts

### Documentation

```text
SKILL.md
README.md          # optional
references/
```

### Script-backed

```text
SKILL.md
README.md          # optional
scripts/
references/
```

### Template

```text
SKILL.md
README.md          # optional
assets/
```

### Hybrid

```text
SKILL.md
README.md          # optional
references/
scripts/
assets/
```

---

## Design Rules

- Prefer single responsibility.
- Prefer composition over monolithic skills.
- Minimize directory count.
- Every file should have a clear purpose.
- Separate instructions from reference material.
- Keep `SKILL.md` as the entry point.
- Optimize for progressive disclosure.
