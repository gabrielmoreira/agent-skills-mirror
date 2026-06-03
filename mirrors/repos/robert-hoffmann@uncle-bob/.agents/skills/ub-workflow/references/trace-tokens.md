# Trace Tokens

Use this reference when searching old workflow decisions, adding lookup
metadata, or deciding where trace identifiers belong.

## Purpose

Trace tokens are stable search anchors for routed workflow lookup. They are not
mini-closeouts, metadata blobs, or execution authorization.

The forward lookup path is:

1. start with `status.md` and `WORKFLOW_ATLAS.md`;
2. use `SOURCE_PACK_ATLAS.md` for retained research;
3. use `SOURCE_ATLAS.md` for source-code routing;
4. use the initiative `index.md` `Trace Routes` table for old workflow facts
   through a triggered T3 lookup;
5. open discoveries, sprint packs, closeouts, decision logs, or evidence only
   through a routed trigger.

## Owner-Only Policy

Trace tokens live only in routing owners:

1. `status.md` when a trace is current posture;
2. `wave.md`;
3. `initiative.md`;
4. `roadmap.md`;
5. `index.md`;
6. `retained-note.md`;
7. source-pack `00-readme.md`;
8. workflow atlases when they route trace lookup.

Do not add trace tokens to discoveries, sprint packs, decision logs, closeouts,
or evidence indexes. Those artifacts keep normal prose, decisions, validation
summaries, and evidence links.

## Token Format

Use compact trace tokens:

```text
Trace token: `DH-W11-I01-S10-CLOSEOUT: bounded_action_review_runtime_proof_passed`
```

Rules:

1. project prefix is optional; Dark Horse uses `DH-`;
2. IDs use wave, initiative when relevant, artifact number, and token kind;
3. the payload is one short `lower_snake_case` summary;
4. do not put semicolon `key=value` chains in the token payload;
5. put searchable facets in `tags` and `Trace Routes`, not the token line.

Common token kinds:

```text
PATH-A
PREVIEW
START
CLOSEOUT
VALIDATION
EVIDENCE
INVENTORY
TRANSITION
AUDIT
```

## Owner Metadata

Routing owners may add frontmatter fields when trace lookup would benefit:

```yaml
trace_ids            : [DH-W11-I01-S10-CLOSEOUT]
tags                 : [agentloop, action-review, provider-live-smoke]
```

Use `lower-kebab-case` tags. Keep tags stable, few, and search-oriented.

## Trace Routes

Each initiative `index.md` should include a compact `Trace Routes` table:

```markdown
## Trace Routes

| Trace ID | Kind | Status | Tags | Owner | Evidence | Read Trigger |
| --- | --- | --- | --- | --- | --- | --- |
| `DH-W11-I01-S10-CLOSEOUT` | sprint closeout | passed | agentloop, action-review | `sprints/.../closeout.md` | `sprints/.../evidence/index.md` | reconstructing Sprint 10 result |
```

Keep one row per meaningful accepted discovery, completed sprint, audit,
transition, or durable retained decision. Do not duplicate closeout prose in
the table.

## Cleanup Rule

When normalizing older artifacts, remove dense token lines from non-owner
artifacts. If the token was the only place a material fact existed, preserve
that fact as nearby prose before removing the token.

Do not create a separate trace atlas. Use existing atlases plus initiative
indexes.
