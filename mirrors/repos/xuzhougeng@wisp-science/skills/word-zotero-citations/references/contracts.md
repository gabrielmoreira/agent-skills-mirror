# Persisted contracts

Every frozen artifact is strict, canonical, digest-bound, and write-once. Treat JSON files as evidence, not as editable configuration.

## Common rules

1. Resolve paths before binding them.
2. Require regular files where the contract says a file must already exist.
3. Require new outputs to remain within their authorized run root unless the contract explicitly protects an external source.
4. Keep source, candidate, destination, report, diagnostic, and evidence paths pairwise distinct where applicable.
5. Reject unknown JSON fields, wrong scalar types, invalid enums, missing keys, non-canonical digest values, and path drift.
6. Canonicalize JSON deterministically and terminate persisted JSON with one newline.
7. On first freeze, create atomically.
8. On a repeated freeze, accept only byte-identical content and return idempotently.
9. If existing bytes differ, raise a conflict; never overwrite or “repair” evidence in place.
10. Recompute file SHA-256 when loading. A self-declared digest is not sufficient.

## Manifest

The citation manifest binds:

- task/run identity and source path/size/SHA-256;
- style and Zotero library/collection identity;
- upstream scan, clustering, and staging/visibility digests;
- normalized item data and item keys;
- every placement, occurrence, and item order;
- expected citation-field, item-occurrence, unique-item-key, bibliography-field, references-heading, and formal-Refresh counts.

The manifest is the frozen acceptance authority for all downstream gates. Repeated identifiers remain repeated occurrences even when they share one item key.

## Static audit

A static audit binds the audited DOCX bytes and manifest, then records:

- parsed citation and bibliography fields;
- item keys and normalized identifiers in citation payloads;
- document preferences and package metadata;
- references heading count;
- residual identifiers and revision facts;
- a phase-specific acceptance report.

Use `build` before Refresh and `post_refresh` after an authorized Refresh. A post-Refresh audit requires the formal refresh count and final destination bytes expected by the manifest.
After Refresh, Zotero manages the citation payload: `citationItems[].id` (and `itemData.id`) become local database numbers and the visible result is rendered in the document style (e.g. author-year for APA) instead of the provisional superscript. The post-Refresh audit therefore binds identity through the stable `uris` item keys, DOI/PMID `itemData`, and placement order. The build-phase audit still strictly requires 8-character item keys and the superscript placeholder. Candidate construction must also preserve every namespace declaration referenced by `mc:Ignorable`; dropping them makes Word reject the document as corrupted.

## Refresh authorization

The authorization is an exact capability for one attempt. It binds:

- manifest path, raw file SHA-256, and semantic manifest SHA-256;
- pre-Refresh static audit path and digests;
- source path/size/SHA-256 outside the run root;
- candidate path/size/SHA-256 inside the run root;
- destination, report, and diagnostic paths;
- run root, task id, attempt id;
- all acceptance counts.

Re-verify the authorization immediately before any Word action. If any path, digest, size, count, or identity changes, authorization is invalid and must not be reused.

## Zotero Local API visibility

The optional visibility verifier is read-only and mockable. Accept only:

```text
http://127.0.0.1:23119
```

Reject:

- hostnames, IPv6, or another IPv4 address;
- any other port or scheme;
- username/password credentials;
- query strings or fragments;
- redirects to a different origin;
- item keys or collection identity that differ from authorization.

Do not generalize this check into a write channel.

## Refresh report

A successful report must be produced by the live wrapper after the authorized attempt. It records, at minimum, exact identity/path bindings, before/after snapshots, macro invocation count, source/candidate protection results, and final destination facts.

Never create a fake success report to unblock finalization. Synthetic reports are allowed only inside explicitly labeled tests and must not be placed in a real run.

## UI evidence

Persist two separate records:

- citation dialog evidence;
- bibliography dialog evidence.

Each record binds the authorization and exact destination/source/working-copy bytes, dialog mode and recognition signal, field snapshots before/open/after cancel, and booleans proving:

- a disposable working copy was used;
- UI edits were cancelled;
- destination was unchanged;
- source was unchanged;
- working copy was unchanged.

Screenshots or prose without these bindings are supplementary only and cannot satisfy finalization.

## Finalization

The finalization record binds:

- manifest file/content digests;
- authorization file/content digests;
- Refresh report file digest;
- post-Refresh audit file/content digests;
- citation and bibliography UI-evidence file/content digests;
- source path/size/SHA-256;
- destination path/size/SHA-256;
- all accepted final counts.

Finalization status is valid only while every bound artifact still verifies. Moving, replacing, editing, or truncating an artifact invalidates the chain.

## Artifact lineage and journal

Every state transition records a write-once journal event and artifact lineage entry. A child artifact names its parent digests. Recovery may advance only through contiguous, allowed transitions whose required artifacts and parents still verify.

Do not infer completion from files alone when the journal contradicts them. Do not infer completion from the journal when files or hashes are missing.
