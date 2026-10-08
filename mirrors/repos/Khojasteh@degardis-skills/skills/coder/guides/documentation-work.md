---
title: Documentation work
applicability:
- When a reader-facing project document is among what the work produces or assesses
- When a change may leave a reader-facing project document untrue
---

Classify the work as creating, revising, or reviewing documentation and as one passage, one document, or a set.

Before gathering evidence or drafting, establish the artifact's reader, their task and prior knowledge, and one outcome with prerequisites, start/end states, and non-goals. The reader is the maintained artifact's consumer, not this run's agent/reviewer/report recipient unless the request or repository makes them the consumer. Use a requester-named reader; otherwise infer a concrete reader only from repository evidence with no competing interpretation. Preserve reader cues in a revision. If plausible readers require different vocabulary, paths, or end states, ask or document only their shared verified path and disclose the gap. Use this reader contract for inclusion and editorial choices.

Choose and preserve a document type and the promise it makes its reader. When it applies, read [[guide:document-types]] before choosing a type or judging a document against one. When it applies, read [[guide:human-api-documentation]] before drafting or reviewing the part of a document that states an interface's contract.

Give each output an explicit temporal scope: current state, release history, before/after migration, deprecation/compatibility, or another stated scope. Current-state material describes supported behavior only, except where an old state still affects a supported compatibility path. For public history, establish release status from the project version, tags or artifacts, and release record, and never present abandoned or unreleased work as a public removal. Judge delta language by purpose and time scope, not words such as “removed” or “previously.”

Find the one home that owns the reader task before gathering evidence: prefer correcting an existing passage, then extending its section, then adding a section, and create a document only when no existing home fits. For a set, map each page to one audience, type, and outcome. Give volatile facts, canonical definitions, full schemas, and exhaustive option lists one home; generate or validate them from source metadata where possible and summarize/link elsewhere. Remove duplicate quick starts, option tables, or instructions in favor of their stronger owner. Preserve useful URLs/headings, update inbound links after moves, and label navigation by reader intent.

In a revision, reconcile the changed passage with the whole document's audience, type, scope, terminology, voice, depth, organization, claims, examples, and assumptions. Use the nearest same-type material only for format, voice, order, terminology, and markup. Preserve conventions unless the requested reader outcome or this guide's document-quality rules require changing one, and report that change. Use established public names. Search changed claims, names, links, and navigation and open implicated pages rather than the whole tree.

Choose implementation detail by reader consequence. Include internals only when readers need them to act correctly or change implementation safely. Use a stability test: if an internal detail can change without changing the document's reader-visible contract or the reader's task, omit or abstract it. Prefer observable behavior, invariants, boundaries, effects, contracts, failures, expectations, and enduring rationale.

Include only material the reader needs or the document type promises. Search trails, edit rationale, verification narration, rejected alternatives, and assistant-facing instructions are working state unless the reader task needs them. Add meaning the artifact cannot show faster: units, valid values, effects, ordering, or failures. Do not restate names, signatures, types, defaults, or enumerations without adding meaning. Deletion, consolidation, and linking are valid delivery. In a revision, change what the request names and what a corrected claim leaves unusable; add otherwise-true material only when the outcome needs it.

Use progressive disclosure: essential path first, then optional context and advanced variations. Lead sections and paragraphs with the needed conclusion, action, or condition. Give each section one reader task/subject, each paragraph one point, and each sentence one main statement with qualifications beside its claim. Use numbered lists for required sequences, bullets for parallel items, and tables for repeated-field comparisons. Organize by reader task, not implementation hierarchy. Use concise headings in the document's established grammatical style that name the section's subject or reader task. A heading is a label, not a summary of the section. Simplification may remove repetition/background or link deeper material, but not a prerequisite, condition, risk, failure, or limitation. Avoid filler, promotion, choppy fragmentation, and template-shaped uniformity.

If a change leaves a document untrue, update it when authorized or report the change incomplete.
