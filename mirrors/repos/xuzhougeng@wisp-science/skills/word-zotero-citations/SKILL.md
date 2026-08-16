---
name: word-zotero-citations
description: Build, audit, authorize, recover, or finalize dynamic Zotero citations and bibliographies in Microsoft Word DOCX files with a protected-source, digest-bound workflow. Use for Word–Zotero citation conversion, static OOXML citation audits, mocked/offline validation, Refresh authorization/report review, UI-evidence contracts, run recovery, or rollback proposals; never perform live Word/Zotero integration without separate explicit authorization.
---

# Word–Zotero citations

Use the generic `zotero_mcp.word_citations` workflow to replace citation markers in a DOCX with dynamic Zotero fields while keeping the source immutable and every mutating gate explicit, digest-bound, and auditable.

## Safety boundary

Default to offline and static work.

Do **not** do any of the following unless the user separately authorizes the exact live integration step:

- launch Microsoft Word or create Word COM automation;
- run `refresh_word_zotero.ps1`;
- invoke `ZoteroRefresh` or another Zotero Word macro;
- write to a Zotero library or staging collection;
- contact a Zotero Local API other than an explicitly approved read-only check on `http://127.0.0.1:23119`;
- overwrite the source DOCX, a frozen manifest, audit, authorization, UI-evidence file, report, or finalization record.

Authorization to create or edit implementation files is not authorization to run Word or Zotero. If live authorization is absent, stop at the offline gate and state exactly which live action remains unexecuted.

## Applicability

Use this Skill when the request involves one or more of:

- scanning Word OOXML for DOI, DOI URL, bare DOI, or explicit `PMID: 12345678` markers;
- inferring citation clusters and preserving repeated item occurrences;
- planning or mocking Zotero item resolution and staging;
- constructing or auditing Zotero citation/bibliography fields in DOCX;
- freezing a citation manifest and acceptance counts;
- auditing a candidate before or after Refresh;
- reviewing or producing a digest-bound Refresh authorization contract;
- persisting citation and bibliography UI evidence from an already authorized disposable check;
- finalizing a run, recovering state, or generating a non-destructive rollback proposal;
- implementing, documenting, or testing the generic Word–Zotero package without case-specific historical imports.

Do not use this Skill for ordinary citation-style advice, manual bibliography prose, Zotero library cleanup unrelated to Word fields, or a request that only asks to install Zotero/Word.

## Required inputs

Establish before any phase that needs them:

1. source `.docx` path;
2. target CSL style id or `.csl` path;
3. isolated runs root and stable task id;
4. requested phase and whether only offline/static work is authorized;
5. Zotero library identity and collection only when staging or visibility is in scope;
6. explicit destination/report paths for Refresh and finalization;
7. expected acceptance counts from the frozen manifest.

If a required path, identity, count, or authorization is missing, do not infer it. Continue only with phases that can be proven from available artifacts.

## Workflow

### 1. Discover the implementation and freeze boundaries

Locate the repository rather than assuming a machine-specific path. Confirm that it provides:

- package `zotero_mcp.word_citations`;
- entry point `zotero-word-citations` or module CLI;
- offline tests for the requested phase;
- the PowerShell wrapper only as an inspectable artifact.

Read `references/implementation-map.md` when modifying code or locating phase ownership. Read `references/contracts.md` when assembling, loading, or verifying persisted JSON artifacts. Read `references/live-run-recipe.md` when reproducing a live run end to end, and `references/zotero-mcp-configuration.md` when the Zotero MCP connector is in local-only mode or write tools fail.

### 2. Preflight without mutation

Run the read-only preflight before scanning or creating a run. Treat its status as a gate:

- `blocked`: stop and report failed checks;
- `manual_review`: explain the unresolved condition and do not advance automatically;
- safe/approved read-only result: continue with the requested offline phase.

Preflight must not create run directories, copy the source, connect to Word, or write to Zotero.

### 3. Scan and cluster the DOCX statically

Use OOXML/ZIP parsing, not Word automation. Preserve source size and SHA-256 and verify the expected digest when one is supplied.

Recognize only supported explicit identifiers. Ordinary numbers are never PMIDs. Inspect all relevant Word stories, surface malformed fields, revisions, static references, and unsupported placements, then infer clusters deterministically. Any ambiguous boundary or unsupported story is a manual-review condition, not permission to guess.

### 4. Plan Zotero resolution before any write

Resolve identifiers against a read gateway first. Fail closed on missing or ambiguous matches. If new items would be required, create a staging plan and exact authorization; do not execute it under the default offline boundary.

Keep collection identity, library identity, requested identifiers, planned item keys, and occurrence counts stable. Use mocks or synthetic gateways for validation.

### 5. Build a candidate in an isolated run

Never edit the source in place. Create or verify the isolated run layout, copy to a candidate path, and protect source/candidate digests across every transformation.

Construct valid complex `ADDIN ZOTERO_ITEM CSL_CITATION` fields and one dynamic `ADDIN ZOTERO_BIBL` field with required document preferences and OPC relationships. Preserve repeated occurrences and do not import case-specific scripts from historical projects.

### 6. Freeze manifest and pre-Refresh audit

Assemble the manifest only from accepted upstream scan, cluster, item visibility/staging, and candidate facts. Freeze it write-once using canonical JSON plus SHA-256.

Run the static DOCX audit and compare its observation with manifest acceptance counts. A failed audit blocks authorization. Existing bytes may be accepted only when identical; conflicting bytes or digest drift must fail closed.

### 7. Authorize Refresh, but do not execute it by default

Bind authorization to the exact manifest file/content digests, static audit, protected source, candidate, destination, report, diagnostic path, attempt id, and acceptance counts. Re-verify all paths and digests immediately before any live operation.

The optional Zotero Local API check is read-only and restricted to IPv4 loopback port `23119`. Reject other hosts, ports, credentials, queries, or fragments.

If the user has not separately authorized live integration, finish here with an offline-blocked result and instructions for what would need explicit approval. If live execution is authorized, read `references/live-refresh-protocol.md` in full before any action.

### 8. Audit post-Refresh evidence

After an externally authorized Refresh has produced a destination and report, load and verify those artifacts; never synthesize a successful report. Run a post-Refresh static audit against the frozen manifest and bind it to the destination bytes.

Citation and bibliography UI evidence must come from separate disposable, cancelled checks. Persist each strict evidence record write-once. Require unchanged destination, source, and working-copy digests and stable before/open/after field snapshots.

### 9. Finalize write-once

Assemble finalization only when all required artifacts exist and verify:

- manifest;
- Refresh authorization;
- Refresh report;
- post-Refresh static audit;
- citation UI evidence;
- bibliography UI evidence;
- protected source;
- final destination and acceptance counts.

Freeze the finalization record write-once. Never treat a directory name, a success message, or an unbound screenshot as proof.

### 10. Recover or propose rollback non-destructively

Use the run journal and artifact lineage to recover only to the highest phase whose required files, hashes, parents, and state transitions still verify. Acquire the run lock before state mutation and use stale-lock recovery rules; never break a live lock.

Rollback is a proposal, not an automatic deletion or overwrite. Generate copy-only steps to a new destination and retain every source, candidate, diagnostic, audit, and journal artifact.

Read `references/recovery-and-rollback.md` for transition and lineage details.

## Execution autonomy and confirmation policy

The 2026-08-15 live test revealed that requiring a human confirmation at every
step is unnecessary. Adopt this policy:

- **No confirmation needed** for: reading, scanning, clustering, planning,
  Zotero read/visibility checks, manifest/audit/authorization freezing,
  candidate construction, post-Refresh audits, finalization, and any offline or
  mocked validation. The agent should execute these autonomously and continue
  until it either produces the final deliverable or hits a hard blocker.
- **One confirmation needed** for each distinct live integration family, given
  up front by the user with explicit scope:
  1. writing to Zotero (create the task collection, add collection membership;
     never merge/delete items without separate approval);
  2. launching Word and running the Refresh wrapper with exactly one
     `ZoteroRefresh` call;
  3. launching Word for the two cancelled disposable dialog checks
     (`ZoteroAddEditCitation`, `ZoteroAddEditBibliography`).
- The user may grant a **standing authorization** (e.g. continue until
  success) for a specific task. Under a standing authorization the agent runs
  each live family at most once per distinct attempt, and if a live attempt
  fails it stops that family, fixes the root cause offline (with a regression
  test), creates a fresh attempt id and paths, and only then proceeds. It never
  re-runs the same authorization.
- If the user grants standing authorization, the agent must still stop for a
  genuine human-in-the-loop condition: Zotero login/challenge dialogs, Word
  license/first-run dialogs, ambiguous duplicate-item selection that cannot be
  resolved by the frozen selection rule, or a structural blocker that no
  parameterized retry can fix.

## Dependencies and setup (tell the user before a live run)

Before any phase that touches live Word/Zotero, state these dependencies and
help the user satisfy them:

1. **Zotero desktop** running, with its Local API on `127.0.0.1:23119`.
2. **Microsoft Word** installed (only the Refresh and UI-evidence steps need
   COM automation; scan/build/audit are OOXML-only).
3. **The `zotero_mcp` package** importable from Python. Locate it (installed
   package, repository `src`, or a `.venv`) and tell the user how it will be
   invoked (e.g. `PYTHONPATH` or the interpreter). If it is missing, stop
   with the exact install/locate step instead of guessing.
4. **zotero-mcp hybrid mode** configured: `ZOTERO_LIBRARY_ID` +
   `ZOTERO_API_KEY` in `~/.config/zotero-mcp/config.json` under `client_env`
   (see `references/zotero-mcp-configuration.md`), followed by a connector
   restart. If writes fail with "local-only mode", do not retry; re-check this
   step.
5. Before live execution, show one import check
   (`python -c "import zotero_mcp"`) and confirm the Local API port.

The agent should proactively point the user to
`references/zotero-mcp-configuration.md` (credentials) and
`references/live-run-recipe.md` (end-to-end run) whenever a dependency check
fails or the user asks how to set something up.

## Scripts and reproducibility

All reusable scripts live inside this Skill under `scripts/` (they are copied
into the archive and are usable wherever the Skill is installed):

- `scripts/run_live_workflow.py` — parameterized offline phases
  (`candidate-build`, `authorize`, `post-refresh-audit`, `finalize`).
- `scripts/refresh_word_zotero.ps1` — the one-shot live Word/Zotero Refresh
  wrapper (executed only under authorization).
- `scripts/validate_word_zotero_ui.ps1` — cancelled disposable dialog evidence.
- `scripts/verify_skill.py` — offline structural verification of this tree.

These scripts are generic: they take `--run-root`, `--task-id`, `--source`,
`--selection`, `--style-id` and read `ZOTERO_LIBRARY_ID`/`ZOTERO_API_KEY` from
the zotero-mcp configuration. They must never contain machine-specific paths or
user identity. See `references/live-run-recipe.md` for the end-to-end sequence
and `references/zotero-mcp-configuration.md` for connector setup.

## Final delivery

- The delivery directory contains **exactly two files**: the finalized
  citation DOCX (copied from the finalization-bound destination) and a copy of
  the user's original DOCX. The user's original file itself is never moved or
  modified.
- **Naming and destination are decided by the user.** The agent proposes a
  name (e.g. `<original-stem>_引文完成版.docx`) and a delivery directory, then
  waits for the user to confirm before copying anything. Never invent a final
  name or path.
- Test/intermediate artifacts (candidates, audits, reports, UI working copies,
  diagnostics, manifests, run state) never enter the delivery directory.
  Evidence under the run root is retained by default; deleting it requires an
  explicit user decision.
- Before delivery, verify the SHA-256 of both files against the finalization
  record. If the user has since opened and saved the finalized document in
  Word, the record's hash will differ; in that case deliver the user-confirmed
  version and record its actual hash with a note that the finalization record
  applies to the audited bytes.
- No test, audit, or live integration is rerun for delivery itself.

## Verification

For implementation or Skill changes, use offline/static verification only:

1. focused tests for touched phase(s);
2. complete `tests/word_citations` suite;
3. relevant Ruff checks;
4. PowerShell AST parse without running the wrapper;
5. protected-baseline hash test;
6. full project test suite with explicit exit-code propagation when feasible;
7. `scripts/verify_skill.py` for this Skill tree;
8. bundled `skill-creator/scripts/quick_validate.py` and packaging utility.

Use `references/verification-matrix.md` for exact categories and stop conditions. Never report a passing run when pytest output contains failures, a timeout, or `KeyboardInterrupt`, even if a detached host reports exit code 0.

## Output contract

Report:

- requested and completed phase(s);
- source and destination protection status;
- artifacts created or verified, including paths and SHA-256 where material;
- acceptance counts and gate outcomes;
- tests/lint/static checks with exact pass/fail totals;
- any blocked or manual-review condition;
- whether Word, `ZoteroRefresh`, Zotero Local API, or Zotero writes were executed.

A default offline run must state explicitly: **Word not launched; Refresh wrapper not executed; Zotero not modified.**
