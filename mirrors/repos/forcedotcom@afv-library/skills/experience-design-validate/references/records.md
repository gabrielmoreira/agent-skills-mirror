# Entities & Objects

> **Skip this reference if the design shows no records, objects, detail pages, status fields, metadata, versioning, collaboration, or workflow surfaces.**

Craft in entity design is felt in how confidently a record presents itself — the calm authority of a well-structured header, the rhythm of metadata that recedes without disappearing, the visual grammar of status that reads at a glance. This reference judges the visual and structural craft of object pages, status systems, metadata treatment, versioning surfaces, collaboration cues, and workflow visualizations.

## Why this matters

Entities are the protagonists of most software — every record a user touches is a small first impression of the product's care and competence. When craft is high, an object feels solid: identity is unmistakable, status reads at a glance, metadata sits politely in the margins, and history feels like a designed surface rather than a log. When craft is low, records feel like form dumps — labels everywhere, statuses competing for attention, timestamps in three formats, and presence indicators that lie about who is there. The difference is the felt sense that someone arranged this carefully versus someone wired it up.

---

## Object Anatomy

- **The header establishes identity at a glance.** The user knows what this thing is, what state it's in, who owns it, and what they can do with it — without scrolling.
- **Read mode is designed, not a disabled form.** Inputs greyed out and read-only is the giveaway of an entity surface that wasn't actually composed for reading. Body content is organized by relevance — what users look at most lives in the default view. Empty optional fields stay quiet.
- **Creation is fast and forward.** Minimum viable fields, then drop the user into the new record. No record is an orphan — every object links back to its parent context.

## Status

- **Statuses are a small, closed set with semantic meaning.** A handful of states the user can hold in mind. "Awaiting approval" reads as designed; "PENDING_APPROVER_REVIEW" leaks the database into the page.
- **Status is communicated by more than color.** A label, an icon shape, or both — never color alone. The mapping holds across the product. Only valid transitions show as actions; invalid moves don't appear as disabled options.

## Metadata

- **System metadata recedes.** Findable but never competing with primary content. Timestamps speak in human time when recent, transitioning to absolute as content ages. People references show face and name together. Reference numbers offer copy in one click.
- **Empty values say something.** A "—" or "Not set" tells the user a value wasn't recorded; blank space hides whether the field even exists. Date and time formats hold across the product.

## History and Versioning

- **History is one click away.** A clear timeline with attribution: who, when, what changed. Diffs are visible, not just listed — additions highlighted, deletions struck through.
- **Viewing a historical version is unmistakable.** A banner makes the time-travel state clear. Restoring creates a new entry — nothing silently lost.

## Collaboration

- **Presence is honest.** Active, idle, and recently-active are visually distinct. A stale "online" indicator is worse than no presence at all.
- **Comments thread, resolve, and notify; conflicts surface rather than silently overwrite.** Ownership is visible and transferable. The user's own permission level is in view — they can tell what they're allowed to do without trying and failing.

## Messaging Surfaces

- **The conversation lives in three calm panels.** List, thread, context. AI-generated content is visually distinct from human messages — a model's reply never silently passes for a person's. System events render as compact inline notes rather than full-width cards.

## Workflow

- **Sequential processes show their steps.** Each node has a status — pending, running, succeeded, failed — and failures explain themselves inline. Cells awaiting computation declare it ("Click to run," "Pending") rather than going blank.
- **Configuration overlays the work, not replaces it.** A side drawer keeps the table visible. Batch progress is honest and cancellable.

---

## Scoring Guide

**Contributes to dimensions: Useful, Coherent, Reliable**

| Score | Criteria |
|-------|----------|
| 9-10 | Entities are instantly identifiable. Status systems are closed and semantic. Metadata recedes politely. History and collaboration are first-class. |
| 7-8 | Entity structure is clear with minor gaps in status discipline or metadata treatment. |
| 5-6 | Status communicated by color alone. Inconsistent metadata. History hidden behind menus. |
| 3-4 | Records read as form dumps. Stale presence. No history. |
| 1-2 | Objects feel disorienting. No coherent identity or status system. |
