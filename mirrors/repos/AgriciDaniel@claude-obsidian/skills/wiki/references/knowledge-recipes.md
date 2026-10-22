# Cited glossary and consolidation recipes

These are bounded uses of existing Ingest and Save workflows. They add no
background action, new skill, or automatic merge. Select the vault and source
budget first. Read [provenance.md](provenance.md) and
[operation-transactions.md](operation-transactions.md).

## Glossary from sources

1. Search existing concepts and aliases before proposing terms. List the source
   paths and exact headings, blocks, or line ranges supporting each definition.
2. Draft one definition per meaning, in the source's domain and language.
   Separate a source definition from an editorial simplification. Preserve
   conflicting definitions with their scopes; do not collapse them into consensus.
3. Use a `concept` page or a bounded glossary section. Add aliases only for
   actual equivalent names, and link source pages using specific wikilinks.
   Unknown meanings remain an open question. Do not mint evidence locators.
4. Keep a table with Term, Definition, Evidence, and Assessment. An evidence
   locator is not an accepted assessment by itself. Apply the claim/source rules
   when recording factual definitions. A generated glossary is synthesis, not
   another independent source.
5. For supplied source material, use one Ingest workflow bundle. For explicitly
   selected conversation content, use Save and keep its synthetic origin clear.
   Couple pages, catalogs, ledgers when changed, log, and bounded hot cache.

A definition based only on a title, tag, model recollection, or retrieved snippet
without adequate surrounding source context stays unsupported. Present the full
term list, evidence coverage, and omissions before apply. Report the operation ID
and changed paths, with no claim that the whole vault was covered unless read.

## Consolidate overlapping notes

Consolidation changes canonical knowledge and requires explicit consent for the
identified merge. First return a read-only overlap proposal: source paths and
hashes, proposed destination, unique claims to preserve, contradictions, existing
inbound links, and exact catalog/ledger changes. Similar wording alone does not
prove that meanings are equivalent.

After approval, re-read all targets and rebuild the proposal if any hash changed.
Use one `operation_type: ingest` workflow bundle. Keep the old note as a short
`status: superseded` redirect note with a wikilink and the reason, preserving
unique evidence and stable source/claim identities. Keep original raw payloads
unchanged. Include the merged note, all approved redirect notes, active catalog,
log, hot cache, and changed ledger records in that one bundle.

The transaction engine supports `create` and `replace`, not deletion or rename.
Do not remove files, rewrite unrelated backlinks, or implement a move with host
file tools. If a later cleanup is requested, plan it separately with a backup and
explicit approval. Preserve Dataview, Tasks, Templater, math, and quoted source
regions byte-for-byte unless they are themselves in the approved edit scope.

Inspect with `workflow inspect`, apply the exact reviewed hash once with
`workflow apply`, then run deterministic lint. A successful storage receipt does
not establish editorial correctness; review evidence coverage and each surviving
inbound link. On conflict, rebuild. On interruption, use `transaction recover`.
Do not auto-checkpoint or silently merge contradictory accepted claims.
