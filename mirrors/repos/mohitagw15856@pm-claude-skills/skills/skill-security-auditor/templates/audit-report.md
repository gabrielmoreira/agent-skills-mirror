# Skill security audit: [skill/pack] — [date] · auditor: [name/tool+version]

**Scope:** [files reviewed] · **Method:** full read + pattern sweep + script inspection (references/injection-patterns.md)

## Verdict
✅ clean / 🟡 findings, conditional / 🔴 reject — [one line]

## Findings
| # | Severity | Pattern family | Location (file:line) | Evidence (quoted) | Disposition |
|---|---|---|---|---|---|
| | high/med/low | override / exfil / grooming / deferred / trust-borrow / scope-creep | | | |

## Checks performed
- [ ] Instruction-override sweep (incl. role redefinition)
- [ ] Network/exfil choreography (incl. image-URL data channels)
- [ ] Encoded content resolved and judged: [none found / decoded: …]
- [ ] Scripts: file/network behaviour vs stated scope
- [ ] Description-vs-instructions diff (scope creep)
- [ ] Composition risk considered (what this + common tools could do)

## Author communication
[what was asked / explained — for 🟡 dispositions]

**Re-audit trigger:** any update to SKILL.md or scripts/ (this audit binds to content hash: [sha256])
