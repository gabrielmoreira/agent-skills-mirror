# Reference-loading preparation review (#205)

This report records offline preparation, not an editing comparison. The
production skill still requires the full reference; no selective default or
quality, token-saving or latency result is claimed. #205 and umbrella #199
remain open. Accept #206's editing policy before freezing model comparisons.

A fresh agent exercised the documented CLI from pinned policy commit
`174336f7c784d028af81d9886f835204e7a90d71`, assembled full, focused and
ambiguous-focus prompts, checked integrity, and exercised invalid/missing-input
paths. Its [original review](independent-review.md) and
[recheck](independent-recheck.md) are retained without rewriting their findings.
These are same-family tool/workflow reviews, not independent-family editing
adjudication or executed model-provider receipts.

| Finding | Resolution |
|---|---|
| Required-only focus selected no rule families | Reject always-included IDs as focus, alone or mixed with rules; regression tests cover both. Empty focus still falls back to all modules. |
| Source commit did not identify the assembler | Record and verify the executing generator hash; hash the parsed configuration and preserve it. A changed generator requires a new pack. The later model method must additionally freeze protocol/input hashes and model settings. |
| False-agency fixture could reward an unjustified edit | Keep the personification contrast and add hidden-choice, supplied-actor and emergent-change cases. Criteria now follow the source's applicability gate. |
| Generic clean/exhaustive instructions could overstate focused coverage | Both arms receive an explicit coverage instruction: global fidelity/protection still apply, but clean claims, residual review and stop reasons must be limited to assembled families. Model behavior remains to be evaluated. |
| Recheck: configuration key order changed a supposedly canonical hash | Serialize supported keys in fixed mode/modules order; test reversed key order and reject unknown keys. This final small repair was checked locally after the independent recheck. |
| PR review: fenced example headings could become separate modules | Recognize heading boundaries outside backtick/tilde fences. A committed-fixture test keeps fake rule/profile headings and shorter nested fences inside the enclosing focused rule. |

The [final full](full-trace.json), [focused](focused-trace.json) and
[fallback](fallback-trace.json) traces record the final generator and prompt
hashes. Their configurations are retained alongside them. They can be rebuilt
from the named policy commit and this tool revision. The source splits into
81 ordered modules; each rule keeps its examples and exceptions. Full assembly
matches the canonical flattened policy apart from the shared experimental
index and coverage instructions. The final traces supersede the earlier
review's prompt hashes for the repaired tool; earlier artifacts remain
historical evidence of the findings.

The independent recheck describes its intermediate generator
`51cd43b41c503e346ca645d26bd9fc5468c11860d64a90973940c13c6fbf9c11`.
The configuration-hash repair initially produced `70309e5a...`; the subsequent
fenced-example repair produced the final generator
`d440af2f1fb749d589c2a5c6463b988146b90c6e1a0a0a4c082501ba517b8bab`.
All three committed traces were regenerated with that final generator, whose
exact bytes are retained in [generator-source.js.txt](generator-source.js.txt).
The earlier recheck remains a historical observation of its named intermediate
tool, not verification of this final source. Receipt-integrity tests compare
the final traces to the retained final source; they do not rewrite earlier
observations to pretend the source never changed.

All 23 npm suites passed; the final targeted suite also passed after the last
configuration-hash repair. It checks full/focused/fallback assembly, complete
indexing, source/config provenance, ten corruption controls and fifteen
synthetic development cases. Self-scan, existing plugin validation and counts
pass; syncing produces no changes to shipped skill or portable files. CI on
the published final head remains a separate check.

Trace usage is unavailable and model latency is null. Prompt bytes and words
are observed context sizes, not token counts. No model/provider was invoked by
this preparation workflow. Missing-reference failure, directory/package parity
and a self-contained full context have mechanical coverage; an installed
selective reader, automatic routing, actual model/tool-read traces and paired
editing outcomes are still future work. Retain full loading on incomplete or
inconclusive evidence.
