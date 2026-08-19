# Contract And Ownership

## Contents

1. Project flow
2. Runtime path ownership
3. Output language contract
4. Stable identities and references
5. Rule classes
6. Trust and file safety

## Project flow

```text
development? -> screenplay -> assets -> image prompts
                         \-> storyboard -> video prompts
                         \-> confirmed production -> review -> delivery
```

This is a routing map, not a mandatory waterfall. Direct entry is valid, and Look Development is optional.
Each artifact records only the project files it directly read. There is no recursive stale-propagation graph.

## Runtime path ownership

`project_tool.py` does not contain a registry mapping business paths to skill names. The first published artifact
claims its output paths in project state, and another artifact cannot silently overwrite those paths. Input,
delivery and machine-state roots remain protected regardless of owner name.

Each skill's own stage contract describes its semantic responsibility. An artifact may project another artifact's
facts but may not silently redefine them. A reviewer requests changes; the responsible skill edits its source.

## Output language contract

| Field | Governs | Default |
|---|---|---|
| `short-drama.json#/language` | creator-facing artifacts, findings, status and Dashboard | `zh-CN` |
| `short-drama.json#/format/prompt_language` | copyable image/video prompt bodies | `en` |

Creator-facing prose follows `language`. Prompt bodies follow `prompt_language`. Depicted speech and on-screen text
come from accepted story/asset facts, not from either description-language setting.

## Stable identities and references

Use stable IDs such as `EP001`, `SC001`, `BLK-...`, `CHAR-...`, `LOOK-...`, `LOC-...`, `PROP-...`,
`SHOT-...`, `KEY-...` and `MOTION-...`. Display names may change without changing identity.

For cross-artifact references, a file declares each upstream snapshot once, and every reference names that
declaration plus the record it points at.

A `.jsonl` file declares them on its first line:

```json
{"record_type":"sources","schema_version":"1.0.0","sources":{"screenplay-index":{"owner":"short-drama-write","artifact":"剧集/EP001/screenplay-index.jsonl"}}}
```

A `.json` file uses a top-level `"sources"` object with the same entries. A reference is then:

```json
{"src": "screenplay-index", "record_id": "BLK-EP001-SC001-A01", "field": "/text"}
```

`sources` keys are short, lowercase and derived from the artifact filename; each is unique and stable inside its
file, and one artifact is declared under one key. `owner` and the project-relative `artifact` identify authority.
`record_id` and `field` are optional selectors, and a reference pointing at a whole artifact keeps `src` alone.
`authority` (`accepted` or `candidate`) belongs to the individual reference, because one snapshot can be read at
different authority levels by different references. Do not copy whole authoritative values into consumers, and do
not create self-references. A `sources` entry names the artifact the file was written against by `owner` and
`artifact` only — no digest. Bytes are compared by the tool, in lifecycle state and delivery checksums, and that is not
user-supplied lifecycle evidence and does not drive transitive invalidation.

## Rule classes

- `structural_invariant`: locally provable; a script may block.
- `reviewed_invariant`: semantic obligation; a reviewer may request revision.
- `craft_default`: usually useful, but creator intent may override it.
- `taste_option`: present alternatives; never block by itself.

Word counts, shot counts, emotional curves and patterns seen elsewhere are not structural invariants unless the
creator explicitly chose them as format constraints.

## Trust and file safety

Deterministic suite scripts do not make outbound connections. Confirmed production may launch a project-external,
locally configured adapter without a shell; that adapter owns any provider SDK/API access and reads credentials from
its environment or system store. Released skills do not retrieve external or private production sources at runtime.
Do not ship private identifiers, plot passages, prompt sentences, URLs, user data or credentials.

Creator input under `输入/` is immutable to publication commands. Machine state lives under `.short-drama/` and
delivery under `交付/`; neither is an owner publication target. Text/JSON publication validates all sources before
writing and replaces each target atomically under one project lock. A crash cannot expose a partially written file;
rerun the command to continue. Unknown external edits are never silently overwritten.

Legacy v0.3 state remains readable. The next state-changing command rewrites only the compact artifact record; old
transaction and propagation fields are not carried forward.
