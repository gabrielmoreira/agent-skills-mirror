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
| Executing repeated logic | Script-backed |
| Generating reusable resources | Template |
| Explaining technical material | Reference Library |
| Evaluating quality | Review |

Use a hybrid only when a single pattern is insufficient.

When editing, preserve the existing pattern unless a different one clearly improves correctness, maintainability, or portability.

---

## Freedom Levels

| Need | Use | Why |
|------|-----|-----|
| Many valid approaches | `SKILL.md` guidance | Preserve agent judgment |
| Detailed but conditional knowledge | `references/` | Load only when needed |
| Repeated fragile operation | `scripts/` | Make execution deterministic |
| Reusable output material | `assets/` | Avoid regenerating templates |

Default to the highest freedom level that remains reliable.

---

## Example-to-Resource Mapping

Use 2–3 realistic requests to decide what belongs where.

| Repeated across examples | Put it in |
|--------------------------|-----------|
| Activation and workflow decisions | `SKILL.md` |
| Long explanations, schemas, APIs, policies | `references/` |
| Commands that must run consistently | `scripts/` |
| Templates, boilerplate, sample files | `assets/` |

---

## Typical Layouts

### Documentation

```text
SKILL.md
references/
```

### Script-backed

```text
SKILL.md
scripts/
references/
```

### Template

```text
SKILL.md
assets/
```

### Hybrid

```text
SKILL.md
references/
scripts/
assets/
```

Create `README.md` only when the user asks for distribution-facing documentation.

---

## Design Rules

- Prefer single responsibility.
- Prefer composition over monolithic skills.
- Minimize directory count.
- Every file should have a clear purpose.
- Separate instructions from reference material.
- Keep `SKILL.md` as the entry point.
- Optimize for progressive disclosure.
- Keep references one level deep from `SKILL.md`.
- Prefer minimal Bash scripts for portable automation.
- Avoid product-specific metadata and helper scripts.
- Preserve structure during edits unless the benefit is clear.
