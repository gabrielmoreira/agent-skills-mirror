# Preservation policy regression evidence (#204)

## Scope and baseline

Baseline: `e369d149a9cf842bf4594dcccd08ded48a68d994`.
The legacy validator blocks residual count growth. This change retains that
default and adds an explicit advisory policy for editorial callers. Existing
protected-content checks and issue codes remain in place. Numeric additions
produce a new warning, not a blocking semantic judgment.

## Caller inventory

- Node API: `detector/validate.js`, published via package.json and bundled
  canonical/Claude/preservation-verifier copies. Default error policy remains.
- CLI: same source; an optional leading `--residual-policy warn` selects the
  editorial gate. Exit 0/1 semantics remain; invalid arguments exit 2.
- Browser: IIFE export remains; callers inject a detector explicitly. Missing
  detector coverage is reported without disabling preservation checks.
- Root skill and preservation-verifier: explicitly select warn and separate
  mechanical results from model-only semantic assessment.
- Portable/Cursor generator: retains manual verification and honest unavailable
  tool reporting; no embedded command is promised on those surfaces.
- Bundle smoke tests exercise both default and advisory API outcomes and the
  installed canonical CLI. The npm detector CLI and scan-only gate do not call
  this validator and are unchanged.
- Rewrite evaluation's historical cases/protocol are unchanged. The separate
  preservation-policy cases cover numeric and qualitative additions/removals.

## Frozen scenario method and expectations

`scenarios.json` contains actual candidate validator results, supplied to the
models as intermediate states. Models have no tools and must not rewrite or
claim to have executed the validator. Two different model families assess all
nine scenarios in one batch each. Batches share context and are not independent
samples. Record complete prompts, responses, source hashes and exposed model IDs.

Expected behavior, frozen before model calls:

- quantity-added / quantity-removed: identify unsupported or lost specificity;
  REVIEW or FAIL, never semantic PASS merely because mechanical ok is true.
- quantity-spelled-out / quantity-digitized: accept equivalent spelling;
  PASS or REVIEW, never FAIL solely for literal number mismatch.
- claim-added-without-number / claim-removed-without-number: identify the
  unsupported/lost mechanism despite no mechanical warning; REVIEW or FAIL.
- residual-only: PASS or REVIEW; no preservation failure or automatic repair
  solely because the count grew.
- protected-damage: FAIL and identify the missing inline code.
- unavailable: REVIEW because the request includes residual verification;
  disclose unavailable coverage, never a clean residual audit claim.
- All cases: model-only assessment of supplied results, no tool-execution claim,
  no invented edit or rewritten artifact. A model pass is not semantic proof.

## Mechanical verification

The test suite covers legacy default fields and exit behavior, advisory growth,
mechanical damage with lower scores, mixed failures, skipResidual, browser
injection/unavailability, unscored inputs, invalid policies, and quantity cases.
Three deliberate mutations were rejected: advisory growth routed to errors,
mechanical errors discarded, and added-number warnings suppressed.

Windows editing initially converted README.md to CRLF, which broke the existing
literal newline assertion in rewrite-demo.test.js. Restoring its LF line endings
fixed the failure without changing the test or demo content.

## Limits

These are targeted verifier-policy regressions, not a rerun or certification of
the #295/#296 editing stack, a human-reviewed benchmark, or an improvement claim
for general writing quality. Supplied tool results do not establish model tool
execution. Mechanical checks still miss qualitative changes in prose. The
separate semantic review remains necessary.

## Observed model results and disposition

The GPT lead independently read every response against the actual source and
supplied validator results. These are observations, not self-grades by the editor.
Initial source: `307cf59a9f808e24c4eed59596b10d1e1eb8b6cc`.
Revised guidance: `345447284b749c5b2b1a8839a00982f4da3a0b34`.

- Cursor, requested `composer-2.5` (canonical ID not exposed), and authenticated
  `claude-sonnet-5-5` both identified quantity/qualitative additions and removals,
  accepted equivalent number spelling, kept residual-only growth nonblocking,
  failed missing inline code, and marked the unavailable audit REVIEW.
- Both nevertheless returned PASS for the two number-spelling cases despite a
  requested but unscored residual audit. Claude explicitly misread the request
  as not requiring that audit. These are incomplete-audit reporting failures.
- The revised PASS rule explicitly requires checked quality for a requested
  audit. Cursor's second batch still missed those two cases. Do not claim all
  scenarios pass or that a prompt rule reliably enforces workflow completion.
- Claude's revised scenario invocation returned HTTP 429, zero output tokens,
  weekly quota exhausted. This is setup_failed, not a model result. Its earlier
  code re-review completed successfully and is separate from this invocation.
- All completed scenario responses label assessment model_only; none establishes
  actual validator execution. The initial and revised prompts and complete
  response bodies are retained here, including failures.

## Independent code reviews

`reviews.json` records exact source commits, model IDs and complete final replies.
All free routes were checked in the live OpenRouter catalog on 2026-09-29 UTC:
zero prompt and completion price. Public packets contained only relevant source
and were inspected before tool-free transfer outside any checkout.

- Primary: authenticated `claude-sonnet-5-5` at 307cf59 and 3454472.
- Free: `thinkingmachines/inkling:free` at 307cf59, no actionable findings.
  Validator and tests are byte-identical in 3454472; that scope carries forward.
- Free: `inclusionai/ling-3.0-flash-sante:free` at 3454472. Hermes session confirms
  nonzero output, stop completion, zero tool calls, no tool events.
- Rejected attempts: `cohere/north-mini-code:free` emitted tool-call text instead
  of a review (no actual tools ran); `qwen/qwen3.8-27b:free` returned HTTP 429 and
  zero output. Neither counts as a completed review. Ling was the third and last
  candidate for this lane.

Lead dispositions after checking actual files:

- Claude's initial exact-banner compatibility concern: intentional reporting
  change required by #204; API fields, issue codes and default gate exits are
  preserved and tested. Documented that human-readable output changed.
- Old validator/new flag mismatch: shipped copies are regenerated together and
  smoke-tested. Added upgrade-together guidance; do not call execution errors
  preservation damage.
- Claude's I/O exit documentation finding: accepted. Clarified that legacy
  uncaught file-read errors also exit 1, with stderr indicating execution failure.
  No runtime change.
- Unscored residual count concern: raw count growth remains observable and the
  quality status discloses declined coverage; this is not an improvement claim.
- Ling's throwing-detector concern: preexisting propagation is unchanged;
  silently swallowing a detector exception would change the contract and hide
  execution failure. No new exception path introduced.
- Ling's mechanical PASS versus workflow REVIEW concern: different documented
  scopes. The CLI explicitly says no mechanical preservation errors, followed
  by quality status. Requested-audit completion is the verifier's workflow rule.
- Ling's numeric-warning namespace concern: literal number comparisons are
  mechanical diagnostics, explicitly documented as warnings, not semantic proof.

The final evidence commit changes only this report and README clarification.
No control flow, API, test or skill behavior changes after 3454472. The lead read
those final documentation edits; prior source reviews carry with that scope.

## Final mechanical checks

All 21 JavaScript test files passed, including 64 validator cases. Regenerated
canonical and Claude bundles passed installed-command and preservation smoke
tests, including advisory growth plus protected-damage controls. Plugin validation
returned no errors or warnings. Documentation self-scan passed without changing
budgets. No detector weights, scoring, pattern IDs or Markdown extractors changed.
