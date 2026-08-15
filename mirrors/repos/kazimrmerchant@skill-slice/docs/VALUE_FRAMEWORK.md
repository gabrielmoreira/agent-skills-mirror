# VALUE_FRAMEWORK — why a skill earns a public slot

Public Git value is **discoverability + trust + license clarity**, not raw count. Context budget is the scarce resource.

## Anchors

From Anthropic's Agent Skills model and the open skill-creator guidance:

| Principle | Implication |
|-----------|-------------|
| Progressive disclosure | Only `name` + `description` are always-on |
| Description is the trigger | Weak descriptions never fire or false-fire |
| Lean `SKILL.md` | Prefer under ~500 lines; depth in `references/` |
| Imperative procedures | Steps beat encyclopedias |
| Security | Third-party scripts are a risk surface |

## Scorecard (0–100)

| Dimension | Weight | Excellent looks like |
|-----------|-------:|----------------------|
| Clarity | 15% | When + not-for + trigger phrases |
| Actionability | 20% | Numbered workflow, commands, anti-patterns |
| Completeness | 15% | Enough to execute |
| Uniqueness | 15% | One capability owner |
| Demand | 10% | Real workflows |
| Safe-to-publish | 15% | No exploits, secrets, personal paths |
| Maint | 10% | Stable APIs, not a 200KB dump |

**Not value:** file size, template-flood rubric scores, nested mega-packs, machine-only paths.

## Publication rule for this repo

Ship **sibling folders** with catalog **tags** (not parent directories). A QUALITY_KEEP grade alone is not a ticket onto the default branch.
