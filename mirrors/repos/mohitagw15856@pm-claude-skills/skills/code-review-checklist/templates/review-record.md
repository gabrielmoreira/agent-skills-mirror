# Review: [PR title/link] — reviewer: [name]

**Risk class (before reading):** Critical / Elevated / Standard / Light — because [what it touches]
**Provenance:** human / AI-assisted / agent-written *(AI-heavy → also run the ai-code-review skill's modes)*

## Verification actually performed
- [ ] Hand-traced inputs through changed logic: [which inputs]
- [ ] Boundary/error paths checked: [empty/null/duplicate/timeout — findings]
- [ ] State/concurrency: [what else reads these writes]
- [ ] Tests can fail: [broke the impl mentally — which test catches it]
- [ ] Not verified (stated honestly): [e.g. domain math — routed to whom]

## Findings
| Severity | Location | Finding | 
|---|---|---|
| blocking / consider / nit | | |

## Verdict
✅ approve / 🟡 approve pending blockings / 🔴 request changes — [one line]
**Debt knowingly accepted:** [what was let through, on record]
